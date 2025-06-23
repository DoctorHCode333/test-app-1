export async function GetTranscriptURLFromConvId(conversationid) {
  try {
    const data = await apiInstance.getAnalyticsConversationDetails(conversationid);
    let participants = data.participants;
    
    // Use for...of loop instead of map for async operations
    for (const participant of participants) {
      if (participant.purpose === "customer" || participant.purpose === "external") {
        let sessiondetails = participant.sessions[0];
        console.log(sessiondetails);
        
        let cid = sessiondetails.sessionId;
        console.log("session id", cid);
        
        try {
          let transcriptUrlData = await stapi.getSpeechandtextanalyticsConversationCommunicationTranscripturl(conversationid, cid);
          
          // Return the URL as soon as we find it
          return transcriptUrlData.url;
          
        } catch (error) {
          console.error(`Error while requesting transcript for ${conversationid} with session ${cid}:`, error);
          // Continue to next participant instead of breaking
          continue;
        }
      }
    }
    
    // If no transcript URL found
    throw new Error(`No transcript URL found for conversation ${conversationid}`);
    
  } catch (error) {
    console.error(`Error processing conversation ${conversationid}:`, error);
    throw error; // Re-throw to let caller handle
  }
}

// Alternative version if you need ALL transcript URLs from all participants
export async function GetAllTranscriptURLsFromConvId(conversationid) {
  try {
    const data = await apiInstance.getAnalyticsConversationDetails(conversationid);
    let participants = data.participants;
    const transcriptUrls = [];
    
    for (const participant of participants) {
      if (participant.purpose === "customer" || participant.purpose === "external") {
        let sessiondetails = participant.sessions[0];
        let cid = sessiondetails.sessionId;
        
        try {
          let transcriptUrlData = await stapi.getSpeechandtextanalyticsConversationCommunicationTranscripturl(conversationid, cid);
          
          transcriptUrls.push({
            sessionId: cid,
            url: transcriptUrlData.url,
            participant: participant
          });
          
        } catch (error) {
          console.error(`Error while requesting transcript for ${conversationid} with session ${cid}:`, error);
          // Add failed attempt to results for tracking
          transcriptUrls.push({
            sessionId: cid,
            url: null,
            error: error.message,
            participant: participant
          });
        }
      }
    }
    
    return transcriptUrls;
    
  } catch (error) {
    console.error(`Error processing conversation ${conversationid}:`, error);
    throw error;
  }
}

// Usage examples:

// Get first available transcript URL
async function example1() {
  try {
    const url = await GetTranscriptURLFromConvId("conv-123");
    console.log("Transcript URL:", url);
  } catch (error) {
    console.error("Failed to get transcript:", error);
  }
}

// Get all transcript URLs
async function example2() {
  try {
    const results = await GetAllTranscriptURLsFromConvId("conv-123");
    const successfulUrls = results.filter(r => r.url && !r.error);
    const failedAttempts = results.filter(r => r.error);
    
    console.log("Successful URLs:", successfulUrls);
    console.log("Failed attempts:", failedAttempts);
  } catch (error) {
    console.error("Failed to process conversation:", error);
  }
}
