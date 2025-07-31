SELECT topicname,
     COUNT(*) AS total_count,
     count(topicname),
     ROUND((COUNT(*) * 100.0) / SUM(COUNT(*)) OVER (PARTITION BY lob), 2) AS percentage_in_lob,
     lob,
     LISTAGG(ALL_PHRASES, '@@@') WITHIN GROUP (ORDER BY ALL_PHRASES) AS phrases 
FROM (
    SELECT CONVERSATION_ID, topicname, Max(lob) as lob,
           LISTAGG(TOPICPHRASE, '@@@') WITHIN GROUP (ORDER BY TOPICPHRASE) AS all_phrases
    FROM HIST_TOPICS_IXNS 
    WHERE TRUNC(startdate) BETWEEN TO_DATE(:fromDate, 'YYYY-MM-DD') AND TO_DATE(:toDate, 'YYYY-MM-DD')
    AND topicname NOT LIKE 'PAL%' AND topicname NOT LIKE 'Chat%' 
    GROUP BY CONVERSATION_ID, topicname
) 
GROUP BY topicname, lob
ORDER BY topicname, lob;
