def generate_wordcloud_image_negative(dateRange,filters,maxWordLength):
    startDate = dateRange['startDate']
    endDate = dateRange['endDate']

    connection = oracledb.connect(
        user="GEN_IXNDB",
        password="Knu54h#I4dmE6ghghhgP9a",
        dsn="ctip.apptoapp.org:1545245541/ctip_Srvc.oracle.db"
    )
    queryNegatvive = """
        SELECT PHRASE
        FROM NSENTIMENTPHRASES
        WHERE TRUNC(STARTDATE) BETWEEN TO_DATE(:start_date, 'YYYY-MM-DD') AND TO_DATE(:end_date, 'YYYY-MM-DD')
    """

    df = pd.read_sql(queryNegatvive, con=connection, params={
        'start_date':startDate,
        'end_date':endDate
    })
    connection.close()

    text_data = " ".join(df['PHRASE'].dropna().astype(str)).lower()
    text_data = re.sub(r'[^a-z\s]', '', text_data)

    words = text_data.split()


    stopWords = set(STOPWORDS)
    customStopWords = {'something', 'oh', 'go', 'anything', 'know', 'you', 'just',
                       'really', 'like', 'done', 'another', 'keep', 'from', 'also',
                       'okay', 'want', 'could', 'would', 'customer', 'call', 'recording',
                       'say', 'said', 'thing', 'get', 'got', 'make', 'dont', 'thats', 'well',
                       'will', 'going', 'one', 'two', 'three', 'four', 'five', 'six', 'seven'
                        'weve', 'yeah', 'didnt', 'mean','gonna', 'somebody', 'getting', 'saying',
                       'telling', 'calling', 'shouldnt', 'theyre', 'called', 'already'
                        'theres', 'havent', 'supposed', 'doesnt','uh', 'um', 'hmm', 'ah',
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

                       }
    stopWords.update(customStopWords)

    filterWords = [word for word in words if word not in stopWords and len(word) > maxWordLength]
    # print(filterWords)
    word_freq = Counter(filterWords)
    top_1000 = Counter(dict(word_freq.most_common(1000)))


    cleaned_final_data = Counter({word:count for word, count in top_1000.items() if word not in customStopWords})
    print(cleaned_final_data)

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
