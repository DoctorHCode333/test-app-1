from flask import Flask, send_file, jsonify
from flask_cors import CORS  # ← Add this
import io
import oracledb
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import re
from collections import Counter

app = Flask(__name__)
CORS(app)  # ← Enable CORS for all routes

# If needed, restrict origins:
# CORS(app, origins=["http://localhost:3000"])

def generate_wordcloud_image():
    connection = oracledb.connect(
        # Your DB connection config
    )
    query = """
        SELECT PHRASE
        FROM PSENTIMENTPHRASES
        WHERE STARTDATE >TO_TIMESTAMP('2025-06-01 12:00:00 AM', 'YYYY-MM-DD HH:MI:SS AM') AND 
        STARTDATE < TO_TIMESTAMP('2025-06-05 12:00:00 AM', 'YYYY-MM-DD HH:MI:SS AM')
    """
    df = pd.read_sql(query, con=connection)
    connection.close()

    text_data = " ".join(df['PHRASE'].dropna().astype(str)).lower()
    text_data = re.sub(r'[^a-z\s]', '', text_data)
    words = text_data.split()

    stopWords = set(STOPWORDS)
    customStopWords = [ ... ]  # Your same custom stop words here
    stopWords.update(customStopWords)

    filterWords = [word for word in words if word not in stopWords and len(word) > 5]
    word_freq = Counter(filterWords)

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq)

    img_io = io.BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(img_io, format='PNG')
    plt.close()
    img_io.seek(0)
    return img_io

@app.route('/api/wordcloud', methods=['GET'])
def get_wordcloud():
    try:
        img_stream = generate_wordcloud_image()
        return send_file(img_stream, mimetype='image/png', as_attachment=False)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)




import React, { useState } from 'react';

const WordCloudViewer = () => {
  const [imageSrc, setImageSrc] = useState(null);

  const fetchWordCloud = async () => {
    const response = await fetch('http://localhost:5000/api/wordcloud');
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    setImageSrc(url);
  };

  return (
    <div>
      <button onClick={fetchWordCloud} className="p-2 bg-blue-600 text-white rounded">
        Generate Word Cloud
      </button>

      {imageSrc && (
        <div className="mt-4">
          <img src={imageSrc} alt="Word Cloud" style={{ maxWidth: '100%' }} />
          <a href={imageSrc} download="wordcloud.png" className="mt-2 block text-blue-700 underline">
            Download Word Cloud
          </a>
        </div>
      )}
    </div>
  );
};

export default WordCloudViewer;

-- Step 1: Build JSON of topic → phrases
WITH topic_phrase_json AS (
  SELECT
    CONVERSATION_ID,
    TOPICNAME,
    '[' || LISTAGG('"' || TOPICPHRASE || '"', ',') 
           WITHIN GROUP (ORDER BY TOPICPHRASE) || ']' AS phrase_list
  FROM (
    SELECT DISTINCT CONVERSATION_ID, TOPICNAME, TOPICPHRASE
    FROM HIST_TOPICS_IXNS
    WHERE STARTDATE > TO_TIMESTAMP('2024-01-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS')
      AND STARTDATE < TO_TIMESTAMP('2024-12-31 23:59:59', 'YYYY-MM-DD HH24:MI:SS')
  )
  GROUP BY CONVERSATION_ID, TOPICNAME
),

-- Step 2: Combine into one JSON object per conversation
json_per_conversation AS (
  SELECT
    CONVERSATION_ID,
    '{' || LISTAGG('"' || TOPICNAME || '":' || phrase_list, ',') 
           WITHIN GROUP (ORDER BY TOPICNAME) || '}' AS TOPIC_PHRASES_JSON
  FROM topic_phrase_json
  GROUP BY CONVERSATION_ID
),

-- Step 3: Select one representative row per conversation
one_row_per_convo AS (
  SELECT *
  FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY CONVERSATION_ID ORDER BY STARTDATE) AS rn
    FROM HIST_TOPICS_IXNS
    WHERE STARTDATE > TO_TIMESTAMP('2024-01-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS')
      AND STARTDATE < TO_TIMESTAMP('2024-12-31 23:59:59', 'YYYY-MM-DD HH24:MI:SS')
  )
  WHERE rn = 1  -- Only keep one row per conversation
)

-- Final: Join everything together
SELECT
  o.CONVERSATION_ID,
  o.CALL_DURATION,
  o.AGENT_DURATION,
  o.SENTIMENT_SCORE,
  -- Add more fields as needed
  j.TOPIC_PHRASES_JSON
FROM one_row_per_convo o
JOIN json_per_conversation j
  ON o.CONVERSATION_ID = j.CONVERSATION_ID;
