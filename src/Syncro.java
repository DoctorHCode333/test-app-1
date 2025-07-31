 select topicname,
     COUNT(*) AS total_count,
     count(topicname),
     ROUND((COUNT(*) * 100.0) / SUM(COUNT(*)) OVER (PARTITION BY lob), 2) AS percentage_in_lob,
     lob,RTRIM(XMLCAST(XMLAGG(XMLELEMENT(e, ALL_PHRASES || '@@@') ORDER BY ALL_PHRASES) AS CLOB), '@@@') AS phrases FROM (select CONVERSATION_ID, topicname, Max(lob) as lob,RTRIM(XMLCAST(XMLAGG(XMLELEMENT(e, TOPICPHRASE || '@@@') ORDER BY TOPICPHRASE) AS CLOB), '@@@') AS all_phrases
    FROM HIST_TOPICS_IXNS 
    WHERE TRUNC(startdate) BETWEEN TO_DATE(:fromDate, 'YYYY-MM-DD') AND TO_DATE(:toDate, 'YYYY-MM-DD')
    and topicname not like 'PAL%' and topicname not like 'Chat%' GROUP BY CONVERSATION_ID,topicname)  GROUP BY topicname,lob
    ORDER BY topicname,lob;
