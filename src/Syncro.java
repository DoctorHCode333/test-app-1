WITH phrase_data AS (
  SELECT
    lob,
    topicname,
    topicphrase,
    COUNT(*) AS phrase_count
  FROM hist_topics_ixns
  WHERE 
    TRUNC(startdate) BETWEEN TO_DATE(:fromDate, 'YYYY-MM-DD') 
                         AND TO_DATE(:toDate, 'YYYY-MM-DD')
    AND topicname NOT LIKE 'PAL%' 
    AND topicname NOT LIKE 'Chat%'
  GROUP BY lob, topicname, topicphrase
),
conversation_counts AS (
  SELECT 
    lob,
    topicname,
    COUNT(DISTINCT conversation_id) AS topic_count
  FROM hist_topics_ixns
  WHERE 
    TRUNC(startdate) BETWEEN TO_DATE(:fromDate, 'YYYY-MM-DD') 
                         AND TO_DATE(:toDate, 'YYYY-MM-DD')
    AND topicname NOT LIKE 'PAL%' 
    AND topicname NOT LIKE 'Chat%'
  GROUP BY lob, topicname
)
SELECT 
  cc.lob,
  cc.topicname,
  cc.topic_count,
  ROUND(cc.topic_count * 100.0 / SUM(cc.topic_count) OVER (PARTITION BY cc.lob), 2) AS percentage_in_lob,

  -- Distinct Phrases (joined with @@@)
  XMLCAST(
    XMLAGG(
      XMLELEMENT(e, pd.topicphrase || '@@@')
      ORDER BY pd.topicphrase
    ) AS CLOB
  ) AS distinct_phrases,

  -- Phrase Counts (joined with commas, just numbers)
  XMLCAST(
    XMLAGG(
      XMLELEMENT(e, TO_CHAR(pd.phrase_count) || ',')
      ORDER BY pd.topicphrase
    ) AS CLOB
  ) AS phrase_counts

FROM conversation_counts cc
JOIN phrase_data pd
  ON cc.lob = pd.lob AND cc.topicname = pd.topicname
ORDER BY cc.lob, cc.topicname;
