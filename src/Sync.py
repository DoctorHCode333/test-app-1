package longtime.automation;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.URL;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.sql.Types;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.TimeZone;
import java.util.concurrent.TimeUnit;
import java.util.logging.FileHandler;
import java.util.logging.SimpleFormatter;

import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import java.io.FileOutputStream;
import java.io.IOException;

import jakarta.mail.Message;
import jakarta.mail.Transport;
import jakarta.mail.internet.InternetAddress;
import jakarta.mail.internet.MimeMessage;

import org.json.JSONArray;
import org.json.JSONObject;

import com.mypurecloud.sdk.v2.ApiClient;
import com.mypurecloud.sdk.v2.ApiException;
import com.mypurecloud.sdk.v2.ApiResponse;
import com.mypurecloud.sdk.v2.Configuration;
import com.mypurecloud.sdk.v2.PureCloudRegionHosts;
import com.mypurecloud.sdk.v2.api.AnalyticsApi;
import com.mypurecloud.sdk.v2.api.ConversationsApi;
import com.mypurecloud.sdk.v2.api.SpeechTextAnalyticsApi;
import com.mypurecloud.sdk.v2.api.UsersApi;
import com.mypurecloud.sdk.v2.extensions.AuthResponse;
import com.mypurecloud.sdk.v2.model.AnalyticsConversation;
import com.mypurecloud.sdk.v2.model.AnalyticsConversationAsyncQueryResponse;
import com.mypurecloud.sdk.v2.model.AnalyticsParticipant;
import com.mypurecloud.sdk.v2.model.AnalyticsSession;
import com.mypurecloud.sdk.v2.model.AsyncConversationQuery;
import com.mypurecloud.sdk.v2.model.AsyncQueryResponse;
import com.mypurecloud.sdk.v2.model.AsyncQueryStatus;
import com.mypurecloud.sdk.v2.model.ConversationMetrics;
import com.mypurecloud.sdk.v2.model.DataAvailabilityResponse;
import com.mypurecloud.sdk.v2.model.SegmentDetailQueryFilter;
import com.mypurecloud.sdk.v2.model.SegmentDetailQueryPredicate;
import com.mypurecloud.sdk.v2.model.TranscriptUrl;
import com.mypurecloud.sdk.v2.model.User;
import com.mypurecloud.sdk.v2.model.UserEntityListing;
import com.mypurecloud.sdk.v2.model.AnalyticsConversationSegment.SegmentTypeEnum;
import com.mypurecloud.sdk.v2.model.AnalyticsParticipant.PurposeEnum;
import com.mypurecloud.sdk.v2.model.AsyncConversationQuery.OrderEnum;
import com.mypurecloud.sdk.v2.model.AsyncQueryStatus.StateEnum;
import com.mypurecloud.sdk.v2.model.SegmentDetailQueryFilter.TypeEnum;
import com.mypurecloud.sdk.v2.model.SegmentDetailQueryPredicate.DimensionEnum;

public class BulkMessageTranscriptBatchJob {

	public static void main(String[] args) {
		//******Version Info*******//////
		//V13
		//Last Modified: - 30 JUNE 2025
		Connection con=null;
		ResultSet rs = null,rs2=null;
		java.util.logging.Logger logger = java.util.logging.Logger.getLogger("Log");
		FileHandler fh = null;
		String conversationid = null;
		DateTimeFormatter formatter1 = DateTimeFormatter.ofPattern("YYYY-MM-dd");
		LocalDate localdate = LocalDate.now().minusDays(1);//Remove in prod
		//LocalDate localdate = LocalDate.now();
		Date intervaldate = new Date();					
		LocalDateTime startTime = LocalDateTime.now();
		LocalDateTime availableTime = LocalDateTime.now();
//		String interval=formatter1.format(localdate.minusDays(1))+"T0"+intervaldate.getTimezoneOffset()/60+":00:00/"+formatter1.format(localdate)+"T0"+intervaldate.getTimezoneOffset()/60+":00:00";
		String interval = "2025-06-16T04:00:00/2025-07-01T04:00:00";
		String selectedDay =interval.substring(0,10);
		String dataAvailabilityDate="";
		logger.info("Job Interval - "+interval);
//		String manual = "";
		String manual = "Manual_"; //Remove In prod
		logger.info(manual + "BOT_Batch");
		int count1 = 0,count=0,count2=0;
		try{
			DateFormat logdateFormat = new SimpleDateFormat("yyyy-MM-dd_HH-mm-ss");
			String dateTimeInfo = logdateFormat.format(new Date());
			fh = new FileHandler(manual +"BotDatalakeJob"+dateTimeInfo+".log");
			logger.addHandler(fh);
			SimpleFormatter formatter = new SimpleFormatter();  
			fh.setFormatter(formatter);

			logger.info("Begin Availability Check");

			// Prod
			String clientId = "f8671153-735b-402b-9f98-c571e2b4eb23";
	    	String clientSecret = "2WFqBHdup5K_2xbJvMLHRYRJTmYiqazJlSWaKUbd5KE";
	    	
	    	
			
		//	String clientSecret = "DKijbZT_lTUw7WlEXCgAPlbEIIGXYIvwT1SQ4P-k9R0";

			// Non Prod
			//			String clientId = "2c1cd0f0-53a9-47be-9f88-25a3d979da5e";
			//			String clientSecret = "DKijbZT_lTUw7WlEXCgAPlbEIIGXYIvwT1SQ4P-k9R0";

			//Set Region
			PureCloudRegionHosts region = PureCloudRegionHosts.us_west_2;

			ApiClient apiClient = ApiClient.Builder.standard().withBasePath(region).build();
			ApiResponse<AuthResponse> authResponse = apiClient.authorizeClientCredentials(clientId, clientSecret);

			// Use the ApiClient instance
			Configuration.setDefaultApiClient(apiClient);

			SpeechTextAnalyticsApi staapi = new SpeechTextAnalyticsApi();
			AnalyticsApi analyticsapi = new AnalyticsApi();
			


			long timediff=-1;
			
			SimpleDateFormat sdfa = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss");
			DataAvailabilityResponse response = new DataAvailabilityResponse();
			
//			logger.info("response"+response);
			
			SimpleDateFormat sdfa1 = new SimpleDateFormat("yyyy-MM-dd");
			sdfa1.setTimeZone(TimeZone.getTimeZone("GMT"));
			int acount=1;
			while(timediff<0){

				if (acount > 1) {
					Thread.sleep(1800000);
				}
				availableTime = LocalDateTime.now();
				response = analyticsapi.getAnalyticsConversationsDetailsJobsAvailability();
				dataAvailabilityDate = response.getDataAvailabilityDate().toString();
				System.out.println(response);
				timediff = sdfa.parse(sdfa1.format(response.getDataAvailabilityDate()) + "T00:00:00").getTime()
						- sdfa.parse(formatter1.format(localdate) + "T00:00:00").getTime();
				System.out.println(timediff);
				acount++;
				if (acount >= 47) {
					throw new RuntimeException("Delay in data availibility is more than 23 Hours");
				}
				logger.info("Begin Availability Check " + acount);		
			}
			
			logger.info("Data Availability Date - "+ dataAvailabilityDate);


			//Rerun code start
			//			DataAvailabilityResponse response = new DataAvailabilityResponse();
			//			response = analyticsapi.getAnalyticsConversationsDetailsJobsAvailability();
			//			logger.info("Availability Date - "+ response.getDataAvailabilityDate().toString());
			//Rerun code end

			logger.info("Begin Run");

			PreparedStatement pstmt = null, pstmt1 = null;

			boolean lastattempt=false;

			String inputLine="",transcript="",transcriptWhole="";

			

			DateFormat dateFormat = new SimpleDateFormat("dd-MMM-yy hh:mm:ss a");
			dateFormat.setTimeZone(TimeZone.getTimeZone("America/New_York"));			

			JSONObject obj;
			JSONArray arrtranscript;
			JSONArray arrphrase;

			List<AnalyticsConversation> convlist = new ArrayList<AnalyticsConversation>();
			List<AnalyticsParticipant> parts = new ArrayList<AnalyticsParticipant>();			
			AnalyticsParticipant part1 = new AnalyticsParticipant();

			Class.forName("oracle.jdbc.driver.OracleDriver");  
//			con=DriverManager.getConnection("jdbc:oracle:thin:@ctip.apptoapp.org:1521/ctip_Srvc.oracle.db","GEN_IXNDB","Knu54h#I4dmE6P9a");
//			con=DriverManager.getConnection("jdbc:oracle:thin:@gsysp-new.apptoapp.org:1521/gsysp_Srvc.oracle.db","GEN_IXNDB","genidb!_pr04_v0y4");
			List<SegmentDetailQueryPredicate> segmentpredicatelist = new ArrayList<SegmentDetailQueryPredicate>();
			SegmentDetailQueryPredicate segmentpredicate = new SegmentDetailQueryPredicate();
			segmentpredicate.setDimension(DimensionEnum.MEDIATYPE);
			segmentpredicate.setValue("message");
			segmentpredicatelist.add(segmentpredicate);	
			segmentpredicate = new SegmentDetailQueryPredicate();
			segmentpredicate.setDimension(DimensionEnum.DIRECTION);
			segmentpredicate.setValue("inbound");
			segmentpredicatelist.add(segmentpredicate);	
			SegmentDetailQueryFilter segmentfilter = new SegmentDetailQueryFilter();
			segmentfilter.setType(TypeEnum.AND);
			segmentfilter.setPredicates(segmentpredicatelist);
			List<SegmentDetailQueryFilter> segmentfilterlist = new ArrayList<SegmentDetailQueryFilter>();
			segmentfilterlist.add(segmentfilter);
			AsyncConversationQuery asyncquery = new AsyncConversationQuery();
			asyncquery.setSegmentFilters(segmentfilterlist);
			asyncquery.setOrder(OrderEnum.ASC);
			boolean capture = false,greatcheck=false;
			String feedback="", lob= "",devicetype = "",interactionreason = "",queue="",customerName="";
			Long callDuration;
			Double sentimentScore, sentimentTrend;
			Workbook workbook = new XSSFWorkbook(); // .xlsx
	        Sheet sheet = workbook.createSheet("June_Data_Part2");
	        
	        String[] headers = { "Start Date","End Date","Conversation ID","Call Duration","Sentiment Score","Sentiment Trend",
	        		"Transcript","Queue","Customer Name","Party_ID","DOB","Email","Interaction Reasons","Device Type",
	        		"Operating System","Exit Reason","Source_App" ,"Delivery_Method","LOB","Client_ID","DNIS","Rsdomain" ,
	        		"Delivery_Method","Agent_Transfer","Retry","Maximum_Queue_Transfer","Session_ID","Information_Line",
	        		"Plan_ID","Number_Of_Plans","MP_Status","ContribAllow","Is_MBH","Has_Benefits","Withdrawal_Allow",
	        		"Custloans_Eligible","Offshore_Excluded","Authentication_Level","Journey_Flag","Data_Action_Journey","BOT_JOURNEY"};
	        String[] participantAttributes = { 
	        		"partyId", "dob","Email","Interaction Reasons","Device Type",
	        		"Operating System","Exit Reason","sourceApp" ,"deliveryMethod","lob","clientId","dnis","rsdomain" ,
	        		"deliveryMethod","AgentTransfer","Retry","MaximumQueueTransfer","SessionID","informationLine",
	        		"PlanID","NumberOfPlans","mpStatus","contribAllow","isMBH","HasBenefits","withdrawalAllow",
	        		"custLoansEligible","offshoreExcluded","AuthenticationLevel","Journey Flag","DataActionJourney","BOT JOURNEY"};
	     // Create header row
	        Row headerRow = sheet.createRow(0);
	        for (int j = 0; j < headers.length; j++) {
	            Cell cell = headerRow.createCell(j);
	            cell.setCellValue(headers[j]);
	        }
		

			asyncquery.setInterval(interval);

			AsyncQueryResponse asyncqueryresponse = new AsyncQueryResponse();
			asyncqueryresponse = analyticsapi.postAnalyticsConversationsDetailsJobs(asyncquery);
			String jobid = asyncqueryresponse.getJobId();
			//			System.out.println(jobid);
			logger.info("Job ID - "+jobid);
			AsyncQueryStatus asyncquerystatus = new AsyncQueryStatus();

			asyncquerystatus = analyticsapi.getAnalyticsConversationsDetailsJob(jobid);
			while(asyncquerystatus.getState()==StateEnum.PENDING){
				asyncquerystatus = analyticsapi.getAnalyticsConversationsDetailsJob(jobid);
				Thread.sleep(30000);
			}
			if(asyncquerystatus.getState()==StateEnum.FULFILLED){
				logger.info("Job complete: Starting Batch-Running...");
				AnalyticsConversationAsyncQueryResponse convasyncqueryresponse = new AnalyticsConversationAsyncQueryResponse();
				convasyncqueryresponse = analyticsapi.getAnalyticsConversationsDetailsJobResults(jobid, "", 1000);

				//System.out.println(convasyncqueryresponse.getDataAvailabilityDate());

				do{	
					convlist = convasyncqueryresponse.getConversations();
					if (convlist.size()>0){
						Date trace = new Date(dateFormat.format(convlist.get(0).getConversationStart()));
						logger.info("First Conversation time:- "+trace);
						Date trace2 = new Date(dateFormat.format(convlist.get(convlist.size()-1).getConversationStart()));
						logger.info("Last Conversation time:- "+trace2+"\n\n");
						
					}
					//convlist.size()
					for(int z=0;z<convlist.size();z++){					
						count1++;
						
						try{
							inputLine = "";
							transcript = "";
							transcriptWhole = "";
							lob="";
							queue="";
							devicetype="";
							interactionreason="";
							capture=false;
							greatcheck=false;
							customerName="";
							callDuration=0L;
							conversationid = convlist.get(z).getConversationId();
							ArrayList<String> conversationData = new ArrayList<>();
//							logger.info("Call "+count1+" - "+conversationid);
//							System.out.println(conversationid+"-"+count1);
							parts = convlist.get(z).getParticipants();
							
							for(int i=0;i<parts.size();i++){
								part1 = parts.get(i);								
								if((part1.getPurpose()==PurposeEnum.CUSTOMER || part1.getPurpose()==PurposeEnum.EXTERNAL)){
									if(lob==""){
										
										Map map = new HashMap<String,String>();
										map = part1.getAttributes();
										//System.out.println(map);
										if(map!=null){
											if(map.get("firstName")!=null&&map.get("lastName")!=null) {
												customerName=map.get("firstName")+" "+map.get("lastName");
											}
											
											for(String attr: participantAttributes) {
												conversationData.add((String) map.get(attr));
											}
										}
									}
									try {
										List<AnalyticsSession> session = part1.getSessions();
										TranscriptUrl transcripturl;
										//System.out.println(conversationid+"        ddd       "+session.get(0).getSessionId());
										String communicationId = session.get(0).getSessionId();
										transcripturl = staapi.getSpeechandtextanalyticsConversationCommunicationTranscripturl(conversationid, communicationId); 
										
										URL oracle = new URL(transcripturl.getUrl());
										BufferedReader in = new BufferedReader(new InputStreamReader(oracle.openStream()));

										while ((inputLine = in.readLine()) != null){
											transcript = transcript + inputLine;
										}
										in.close();
										obj = new JSONObject(transcript);
										arrtranscript = obj.getJSONArray("transcripts"); 
										String purpose="",currentPurpose=" ";
										aa:
										for (int x = 0; x < arrtranscript.length(); x++)
										{	
											arrphrase = arrtranscript.getJSONObject(x).getJSONArray("phrases");
											bb:
											for (int y = 0; y < arrphrase.length(); y++){
												purpose = arrphrase.getJSONObject(y).getString("participantPurpose");
												if(arrphrase.getJSONObject(y).getString("text").equals("")||arrphrase.getJSONObject(y).getString("text")==null){	
													transcriptWhole = transcriptWhole + "";
												}else if(purpose.equals(currentPurpose)){
													transcriptWhole = transcriptWhole +" "+ arrphrase.getJSONObject(y).getString("text");
												}else {
													if(!currentPurpose.equals(" ")) {
														transcriptWhole = transcriptWhole +"\"";
													}					
													currentPurpose = purpose;
													transcriptWhole = transcriptWhole + " "+purpose+": \""+ arrphrase.getJSONObject(y).getString("text");
												}				
											}		
											
										}
										transcriptWhole =transcriptWhole+"\"";
									}catch(ApiException ex5) {
										ex5.printStackTrace();
										System.out.println("In Conversation_ID:- " + conversationid + " - " + ex5.getStatusCode());			
									}
								} else if (part1.getPurpose() == PurposeEnum.ACD) {
									if (queue.equals("")) {
										if (part1.getParticipantName() != null && part1.getParticipantName() != "") {
											queue = part1.getParticipantName();
										}
									} else {
										if (part1.getParticipantName() != null && part1.getParticipantName() != "") {
											queue = queue + "," + part1.getParticipantName();
										}
									}
								}
								
							}
									try{
										
										
										if(!transcriptWhole.equals("")){
											
											ConversationMetrics metrics = new ConversationMetrics();
											metrics=staapi.getSpeechandtextanalyticsConversation(conversationid);
											String startDate = 
													dateFormat.format(convlist.get(z).getConversationStart());
											
											String endDate =
													dateFormat.format(convlist
															.get(z)
															.getConversationEnd());
											callDuration = getDateDiff(
													convlist.get(z)
															.getConversationStart(),
													convlist.get(z)
															.getConversationEnd(),
													TimeUnit.MINUTES);
											
											sentimentScore = metrics.getSentimentScore();
											sentimentTrend = metrics.getSentimentTrend();
											try {
												count2++;
												Row row = sheet.createRow(count2);
												
												row.createCell(0).setCellValue(startDate);
										        row.createCell(1).setCellValue(endDate);
										        row.createCell(2).setCellValue(conversationid);
										        row.createCell(3).setCellValue(callDuration);
										        Cell cell4 = row.createCell(4);
										        if(sentimentScore!=null) {
										        	cell4.setCellValue(sentimentScore);
										        }else {
										        	cell4.setBlank();
										        }
										        Cell cell5 = row.createCell(4);
										        if(sentimentTrend!=null) {
										        	cell5.setCellValue(sentimentTrend);
										        }else {
										        	cell5.setBlank();
										        }
										        row.createCell(6).setCellValue(transcriptWhole);
										        row.createCell(7).setCellValue(queue);
										        Cell cell8 = row.createCell(8);
										        if(!customerName.equals("")&&customerName!=null) {
										        	cell8.setCellValue(customerName);
										        }else {
										        	cell8.setBlank();
										        }
										        
										        // Fill data rows
										        
								                //Row 1 onwards
									            for (int k = 0; k < conversationData.size(); k++) {
									                Cell tempCell = row.createCell(k+9);
									                if(conversationData.get(k)!=null) {
									                	tempCell.setCellValue(conversationData.get(k));
									                }else {
									                	tempCell.setBlank();
									                }
									                		
									            }
										      

										       
										        //for (int j = 0; j < 3; j++) {
										        //    sheet.autoSizeColumn(j);
										        //}
											}catch(Exception ex) {
												System.out.println("error while inserting data for conversation "+conversationid);
												ex.printStackTrace();
											}
											
										}										
									}catch(ApiException ex){
										ex.printStackTrace();
										System.out.println("In Conversation_ID:- " + conversationid + " - " + ex.getStatusCode());
										//System.out.println(ex.getEntityId());
									}finally {
										if(rs2!=null){
											rs2.close();
										}
										if(pstmt1!=null){
											pstmt1.close();
										}

									}
	
							
						}catch(Exception e1){
							logger.info(conversationid +" - "+e1.getMessage());
							e1.printStackTrace();

						}

					}
					if(convasyncqueryresponse.getCursor()==null){
						break;
					}
					convasyncqueryresponse = analyticsapi.getAnalyticsConversationsDetailsJobResults(jobid, convasyncqueryresponse.getCursor(), 1000);
					if(convasyncqueryresponse.getCursor()==null){
						lastattempt = true;
					}
				}while(convasyncqueryresponse.getCursor()!=null || lastattempt);
				
				 
			}
			// Write the file
			
			String downloadPath = "C:\\Harsh_official\\BOT_Batch_JUNE\\June_BOT_Data_Part2.xlsx";
			try (FileOutputStream fileOut = new FileOutputStream(downloadPath)) {
	            workbook.write(fileOut);
	            workbook.close();
	            System.out.println("Excel file 'JuneDataTrial.xlsx' created successfully.");
	        } catch (IOException e) {
	        	 System.out.println("Excel file 'JuneDataTrial.xlsx' creation failed.");
	            e.printStackTrace();
	        }
			
			logger.info("End Run");
						try {
							logger.info("Successfully ran "+manual+"BOT Bulk Download Job Part 2");
							LocalDateTime endTime = LocalDateTime.now();
							Duration duration = Duration.between(startTime,endTime);
							long runTime = duration.toHours();
							Duration delay = Duration.between(startTime,availableTime);
							long delayTime = delay.toHours();
							System.out.println("Batch Job Start Time:- " +startTime);
							System.out.println("Batch Job End   Time:- " +endTime);
							System.out.println("Batch Job Run   Time:- " +runTime);
							System.out.println("Total Number of feedback records updated- "+count);

							logger.info("Batch Job Start Time:- " +startTime);
							logger.info("Batch Job End   Time:- " +endTime);
							logger.info("Batch Job Run   Time:- " +runTime);
							logger.info("Total Number of interaction found- "+count1);
							logger.info("Total Number of feedback records updated- "+count);
							
							
							Properties properties = System.getProperties();
							properties.setProperty("mail.smtp.host", "amersmtpinvip.us.americas.intranet");
							jakarta.mail.Session session1 = jakarta.mail.Session.getDefaultInstance(properties);
							MimeMessage message = new MimeMessage(session1);
							message.setFrom(new InternetAddress("donotreplyextractstatus@voya.com"));
//							message.addRecipient(Message.RecipientType.TO, new InternetAddress("amritha.sasikalaraveendran@voya.com"));
							InternetAddress[] parse = InternetAddress.parse("Harshvardhan.Bawake@voya.com" , true);
							//InternetAddress[] parse = InternetAddress.parse("Harshvardhan.Bawake@voya.com,subith.ou@voya.com,Amritha.SasikalaRaveendran@voya.com,Sumant.Barik@voya.com" , true);
							message.addRecipients(Message.RecipientType.TO, parse);				
							message.setSubject("Successfully ran "+manual+"BOT Batch Job for " + selectedDay);
																														
							
							String body;
							body ="Actual time interval for batch job:- " + interval+"\n\n";
							body =body+"Data Availability Date - "+ dataAvailabilityDate+"\n\n";
							body =body+"Batch Job Start Time:- "+ startTime+"\n";
							body =body+"Batch Job End   Time:- "+ endTime+"\n";
							body =body+"Data availibility delay:-"+ delayTime+" Hours \n";
							body =body+"Batch Job Run   Time:- "+ runTime+" Hours \n";
							
							
							body=body+"Total Number of interactions found- "+count1+"\n";
							body=body+"BOT Feedback : \nNumber of records with feedback updated - "+count+"\n\n";
							message.setText(body);
							//Transport.send(message);
						} catch (Exception ex2) {
			
						}
		}catch(Exception e){
			logger.info("Job Failed - "+e.getMessage());
			e.printStackTrace();

			try {
				logger.info("Failed: The "+manual+"BOT Batch Job for " + selectedDay);
				
				LocalDateTime endTime = LocalDateTime.now();
				Duration duration = Duration.between(startTime,endTime);
				long runTime = duration.toHours();
				Duration delay = Duration.between(startTime,availableTime);
				long delayTime = delay.toHours();
				System.out.println("Batch Job Start Time:- " +startTime);
				System.out.println("Batch Job End   Time:- " +endTime);
				System.out.println("Batch Job Run   Time:- " +runTime);
				System.out.println("Total Number of feedback records updated- "+count);

				logger.info("Batch Job Start Time:- " +startTime);
				logger.info("Batch Job End   Time:- " +endTime);
				logger.info("Batch Job Run   Time:- " +runTime);
				logger.info("Total Number of interactions found- "+count1);
				logger.info("Total Number of feedback records updated- "+count);
				
				
				Properties properties = System.getProperties();			
				properties.setProperty("mail.smtp.host", "amersmtpinvip.us.americas.intranet");
				jakarta.mail.Session session1 = jakarta.mail.Session.getDefaultInstance(properties);
				MimeMessage message = new MimeMessage(session1);
				message.setFrom(new InternetAddress("donotreplyextractstatus@voya.com"));
				InternetAddress[] parse = InternetAddress.parse("Harshvardhan.Bawake@voya.com" , true);
//				InternetAddress[] parse = InternetAddress.parse("Harshvardhan.Bawake@voya.com,subith.ou@voya.com,Amritha.SasikalaRaveendran@voya.com,Sumant.Barik@voya.com" , true);
				message.addRecipients(Message.RecipientType.TO, parse);
				
				message.setSubject("Failed: The "+manual+"BOT Batch Job for " + selectedDay);
				
					
				String body;
				body ="Actual time interval for batch job:- " + interval+"\n\n";
				body =body+"Data Availability Date - "+ dataAvailabilityDate+"\n\n";
				body =body+"Batch Job Start Time:- "+ startTime+"\n";
				body =body+"Batch Job End   Time:- "+ endTime+"\n";
				body =body+"Data availibility delay:-"+ delayTime+" Hours \n";
				body =body+"Batch Job Run   Time:- "+ runTime+" Hours \n";
				
				
				body=body+"Total Number of interactions found- "+count1+"\n";
				body=body+"BOT Feedback : \nNumber of records with feedback updated - "+count+"\n\n";
				
				body=body+"Failed at Conversation ID - "+conversationid;
				message.setText(body);
				//Transport.send(message);
			} catch (Exception ex2) {

			}

		}
		finally {
			if(fh != null){
				fh.flush();
				fh.close();
			}
			if(con!=null){
				try {
					con.close();
				} catch (SQLException ex3) {					

				}
			}
		}


	}
	public static long getDateDiff(Date date1, Date date2, TimeUnit timeUnit) {
		long diffInMillies = date2.getTime() - date1.getTime();
		return timeUnit.convert(diffInMillies, TimeUnit.MILLISECONDS);
	}
}
