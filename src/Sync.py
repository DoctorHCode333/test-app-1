import os

os.environ["TCL_LIBRARY"]=r'C:\PY_ENV\pyenv-win\versions\3.9.13\tcl\tcl8.6'
os.environ["TK_LIBRARY"]=r'C:\PY_ENV\pyenv-win\versions\3.9.13\tcl\tk8.6'

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

def generate_wordcloud_image_negative():
    connection = oracledb.connect(
        user="GEN_IXNDB",
        password="Knu54h#I4dmE6P9a",
        dsn="ctip.apptoapp.org:1521/ctip_Srvc.oracle.db"
    )
    queryNegatvive = """
        SELECT PHRASE
        FROM NSENTIMENTPHRASES
        WHERE STARTDATE >TO_TIMESTAMP('2025-06-01 12:00:00 AM', 'YYYY-MM-DD HH:MI:SS AM') AND 
        STARTDATE < TO_TIMESTAMP('2025-06-05 12:00:00 AM', 'YYYY-MM-DD HH:MI:SS AM')
    """

    df = pd.read_sql(queryNegatvive, con=connection)

    connection.close()

    text_data = " ".join(df['PHRASE'].dropna().astype(str)).lower()
    text_data = re.sub(r'[^a-z\s]', '', text_data)
    words = text_data.split()

    stopWords = set(STOPWORDS)
    customStopWords = ['something', 'oh', 'go', 'anything', 'know', 'you', 'just',
                       'really', 'like', 'done', 'another', 'keep', 'from', 'also',
                       'okay', 'want', 'could', 'would', 'customer', 'call', 'recording',
                       'say', 'said', 'thing', 'get', 'got', 'make', 'dont', 'thats', 'well',
                       'will', 'going', 'one', 'two', 'three', 'four', 'five', 'six', 'seven'
                                                                                      'weve', 'yeah', 'didnt', 'mean',
                       'gonna', 'somebody', 'getting', 'saying',
                       'telling', 'calling', 'shouldnt', 'theyre', 'called', 'already'
                                                                             'theres', 'havent', 'supposed', 'doesnt',
                       'uh', 'um', 'hmm', 'ah',
                       'uhhuh', 'huh', 'alright', 'fucking', 'right', 'yeah', 'yep', 'nope', 'hey',
                       'hi', 'hello', 'bye', 'goodbye', 'thanks', 'thank', 'please',
                       'sure', 'fine', 'maybe', 'sorta', 'kinda', 'actually', 'basically',
                       'literally', 'honestly', 'perhaps', 'probably', 'anyway', 'anyways',
                       'well', 'happened', 'thing', 'stuff', 'lot', 'lots', 'bit', 'little',
                       'ok', 'cool', 'oops', 'ugh', 'uhoh', 'yup', 'nah', 'dunno', 'lemme',
                       'gimme', 'wanna', 'gotta', 'aint', 'isnt', 'wasnt', 'werent', 'someone',
                       'hasnt', 'havent', 'hadnt', 'wont', 'wouldnt', 'couldnt', 'shouldnt', 'might',
                       'mightve', 'must', 'mustve', 'seems', 'seemed', 'looks', 'looked', 'sounds',
                       'sounded', 'feels', 'felt', 'guess', 'thinking', 'thought', 'believe', 'hope',
                       'wish', 'try', 'tried', 'trying', 'see', 'seen', 'watch', 'watched', 'hear',
                       'heard', 'listen', 'listened', 'talk', 'talked', 'talking', 'speak', 'spoke',
                       'speaking', 'say', 'said', 'telling', 'told', 'ask', 'asked', 'asking'
                                                                                     'everything', 'gotten', 'almost',
                       'sitting'

                       ]
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


@app.route('/wordCloudNegative', methods=['GET'])
def get_wordcloud_negative():
    try:
        img_stream = generate_wordcloud_image_negative()
        return send_file(img_stream, mimetype='image/png', as_attachment=False)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

def generate_wordcloud_image_positive():
    connection = oracledb.connect(
        user="GEN_IXNDB",
        password="Knu54h#I4dmE6P9a",
        dsn="ctip.apptoapp.org:1521/ctip_Srvc.oracle.db"
    )

    queryPositive = """
            SELECT PHRASE
            FROM PSENTIMENTPHRASES
            WHERE STARTDATE >TO_TIMESTAMP('2025-06-01 12:00:00 AM', 'YYYY-MM-DD HH:MI:SS AM') AND 
            STARTDATE < TO_TIMESTAMP('2025-06-05 12:00:00 AM', 'YYYY-MM-DD HH:MI:SS AM')
        """
    df = pd.read_sql(queryPositive, con=connection)

    connection.close()

    text_data = " ".join(df['PHRASE'].dropna().astype(str)).lower()
    text_data = re.sub(r'[^a-z\s]', '', text_data)
    words = text_data.split()

    stopWords = set(STOPWORDS)
    customStopWords = ['something', 'oh', 'go', 'anything', 'know', 'you', 'just',
                       'really', 'like', 'done', 'another', 'keep', 'from', 'also',
                       'okay', 'want', 'could', 'would', 'customer', 'call', 'recording',
                       'say', 'said', 'thing', 'get', 'got', 'make', 'dont', 'thats', 'well',
                       'will', 'going', 'one', 'two', 'three', 'four', 'five', 'six', 'seven'
                                                                                      'weve', 'yeah', 'didnt', 'mean',
                       'gonna', 'somebody', 'getting', 'saying',
                       'telling', 'calling', 'shouldnt', 'theyre', 'called', 'already'
                                                                             'theres', 'havent', 'supposed', 'doesnt',
                       'uh', 'um', 'hmm', 'ah',
                       'uhhuh', 'huh', 'alright','fucking', 'right', 'yeah', 'yep', 'nope', 'hey',
                       'hi', 'hello', 'bye', 'goodbye', 'thanks', 'thank', 'please',
                       'sure', 'fine', 'maybe', 'sorta', 'kinda', 'actually', 'basically',
                       'literally', 'honestly', 'perhaps', 'probably', 'anyway', 'anyways',
                       'well', 'happened', 'thing', 'stuff', 'lot', 'lots', 'bit', 'little',
                       'ok', 'cool', 'oops', 'ugh', 'uhoh', 'yup', 'nah', 'dunno', 'lemme',
                       'gimme', 'wanna', 'gotta', 'aint', 'isnt', 'wasnt', 'werent', 'someone',
                       'hasnt', 'havent', 'hadnt', 'wont', 'wouldnt', 'couldnt', 'shouldnt', 'might',
                       'mightve', 'must', 'mustve', 'seems', 'seemed', 'looks', 'looked', 'sounds',
                       'sounded', 'feels', 'felt', 'guess', 'thinking', 'thought', 'believe', 'hope',
                       'wish', 'try', 'tried', 'trying', 'see', 'seen', 'watch', 'watched', 'hear',
                       'heard', 'listen', 'listened', 'talk', 'talked', 'talking', 'speak', 'spoke',
                       'speaking', 'say', 'said', 'telling', 'told', 'ask', 'asked', 'asking'
                        'everything', 'gotten', 'almost', 'sitting'
                       ]
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

@app.route('/wordCloudPositive', methods=['GET'])
def get_wordcloud_positive():
    try:
        img_stream = generate_wordcloud_image_positive()
        return send_file(img_stream, mimetype='image/png', as_attachment=False)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Server listening on port 5000")
    app.run(debug=True)
