
import oracledb
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Step 1: Connect to Oracle DB (thin mode)
connection = oracledb.connect(
    user="USERNAME",
    password="PASSWORD",
    dsn="HOST:PORT/SERVICE_NAME"
)

# Step 2: Query the database
query = """
    SELECT column_with_text
    FROM your_table
    WHERE ROWNUM <= 1000
"""
df = pd.read_sql(query, con=connection)

# Step 3: Close the connection
connection.close()

# Step 4: Combine all text into one string
text_data = " ".join(df['column_with_text'].dropna().astype(str))

# Step 5: Generate the word cloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_data)

# Step 6: Display the word cloud
plt.figure(figsize=(15, 7))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title("Word Cloud from Oracle DB Text Data")
plt.show()
