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
