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
),
aggregated AS (
  SELECT
    pd.lob,
    pd.topicname,

    -- CLOB of distinct phrases
    XMLCAST(
      XMLAGG(
        XMLELEMENT(e, pd.topicphrase || '@@@')
        ORDER BY pd.topicphrase
      ) AS CLOB
    ) AS distinct_phrases,

    -- CLOB of counts, just numbers
    XMLCAST(
      XMLAGG(
        XMLELEMENT(e, TO_CHAR(pd.phrase_count) || ',')
        ORDER BY pd.topicphrase
      ) AS CLOB
    ) AS phrase_counts
  FROM phrase_data pd
  GROUP BY pd.lob, pd.topicname
)
SELECT 
  ag.lob,
  ag.topicname,
  cc.topic_count,
  ROUND(cc.topic_count * 100.0 / SUM(cc.topic_count) OVER (PARTITION BY ag.lob), 2) AS percentage_in_lob,
  ag.distinct_phrases,
  ag.phrase_counts
FROM aggregated ag
JOIN conversation_counts cc
  ON ag.lob = cc.lob AND ag.topicname = cc.topicname
ORDER BY ag.lob, ag.topicname;
