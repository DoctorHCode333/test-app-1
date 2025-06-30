import oracledb
import pandas as pd
from wordcloud import WordCloud,STOPWORDS
import matplotlib.pyplot as plt
import re
from collections import Counter

# Step 1: Connect to Oracle DB (thin mode)

  #DB Detailshere ignore this
connection = oracledb.connect(
    #DB Detailshere ignore this
)

# Step 2: Query the database
query = """
    SELECT PHRASE
    FROM PSENTIMENTPHRASES
    WHERE STARTDATE >TO_TIMESTAMP('2025-06-01 12:00:00 AM', 'YYYY-MM-DD HH:MI:SS AM') AND 
STARTDATE < TO_TIMESTAMP('2025-06-05 12:00:00 AM', 'YYYY-MM-DD HH:MI:SS AM')
"""
df = pd.read_sql(query, con=connection)

# Step 3: Close the connection
connection.close()

# Step 4: Combine all text into one string
text_data = " ".join(df['PHRASE'].dropna().astype(str))

text_data = text_data.lower()

text_data = re.sub(r'[^a-z\s]','',text_data)

words =text_data.split()

stopWords = set(STOPWORDS)

customStopWords = ['something','oh','go','anything','know','you','just',
                   'really','like','done','another','keep','from','also',
                   'okay','want','could','would','customer','call','recording',
                   'say','said','thing','get','got','make','dont','thats','well',
                   'will','going','one','two','three','four','five','six','seven'
                   'weve','yeah','didnt','mean','gonna','somebody','getting','saying',
                   'telling','calling','shouldnt','theyre','called','already'
                   'theres','havent','supposed','doesnt', 'uh', 'um', 'hmm', 'ah',
                   'uhhuh', 'huh', 'alright', 'right', 'yeah', 'yep', 'nope', 'hey',
                   'hi', 'hello', 'bye', 'goodbye', 'thanks', 'thank', 'please',
                   'sure', 'fine', 'maybe', 'sorta', 'kinda', 'actually', 'basically',
                   'literally', 'honestly', 'perhaps', 'probably', 'anyway', 'anyways',
                   'well', 'happened', 'thing', 'stuff', 'lot', 'lots', 'bit', 'little',
                   'ok', 'cool', 'oops', 'ugh', 'uhoh', 'yup', 'nah', 'dunno', 'lemme',
                   'gimme', 'wanna', 'gotta', 'aint', 'isnt', 'wasnt', 'werent','someone',
                   'hasnt', 'havent', 'hadnt', 'wont', 'wouldnt', 'couldnt', 'shouldnt', 'might',
                   'mightve', 'must', 'mustve', 'seems', 'seemed', 'looks', 'looked', 'sounds',
                   'sounded', 'feels', 'felt', 'guess', 'thinking', 'thought', 'believe', 'hope',
                   'wish', 'try', 'tried', 'trying', 'see', 'seen', 'watch', 'watched', 'hear',
                   'heard', 'listen', 'listened', 'talk', 'talked', 'talking', 'speak', 'spoke',
                   'speaking', 'say', 'said', 'telling', 'told', 'ask', 'asked', 'asking'
                   'everything','gotten','almost','sitting'
]

stopWords.update(customStopWords)

filterWords = [word for word in words if word not in stopWords and len(word)>5]

word_freq = Counter(filterWords)

refinedText = " ".join(filterWords)[:500_000]

#print(refinedText)
# Step 5: Generate the word cloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq)
