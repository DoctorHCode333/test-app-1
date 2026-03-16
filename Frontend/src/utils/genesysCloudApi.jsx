import { useSelector } from "react-redux";
import { clientConfig } from "../clientConfig";
import platformClient from "purecloud-platform-client-v2";

const client = platformClient.ApiClient.instance;
const { clientId, redirectUri } = clientConfig;

client.setEnvironment(platformClient.PureCloudRegionHosts.us_west_2); // Genesys Cloud region

const cache = {};
const convApi = new platformClient.ConversationsApi();
const userApi = new platformClient.UsersApi();
const telephonyApi = new platformClient.TelephonyProvidersEdgeApi();

export async function authenticate() {
  return client
    .loginImplicitGrant(clientId, redirectUri, { state: "state" })
    .then((data) => {
      return data;
    })
    .catch((err) => {
      console.error(err);
    });
}

// Get all DIDs from Genesys Cloud
export async function getDIDs(pageSize = 100, pageNumber = 1, ownerType = null) {
  try {
    const opts = {
      pageSize: pageSize,
      pageNumber: pageNumber,
      sortBy: "number",
      sortOrder: "ASC"
    };
    
    // If ownerType is specified, add it to filter
    if (ownerType) {
      opts.ownerType = ownerType;
    }
    
    const response = await telephonyApi.getTelephonyProvidersEdgesDids(opts);
    return response;
  } catch (err) {
    console.error("Error fetching DIDs:", err);
    throw err;
  }
}

// Get all DID Pools from Genesys Cloud
export async function getDIDPools(pageSize = 100, pageNumber = 1) {
  try {
    const opts = {
      pageSize: pageSize,
      pageNumber: pageNumber,
      sortBy: "startPhoneNumber",
      sortOrder: "ASC"
    };
    
    const response = await telephonyApi.getTelephonyProvidersEdgesDidpools(opts);
    return response;
  } catch (err) {
    console.error("Error fetching DID Pools:", err);
    throw err;
  }
}

// Get all DID Pools with pagination handling
export async function getAllDIDPools() {
  try {
    let allPools = [];
    let pageNumber = 1;
    const pageSize = 100;
    let hasMore = true;

    while (hasMore) {
      const response = await getDIDPools(pageSize, pageNumber);
      if (response.entities && response.entities.length > 0) {
        allPools = [...allPools, ...response.entities];
        pageNumber++;
        hasMore = response.entities.length === pageSize;
      } else {
        hasMore = false;
      }
    }

    return allPools;
  } catch (err) {
    console.error("Error fetching all DID Pools:", err);
    throw err;
  }
}

// Get all DIDs with pagination handling - fetches assigned DIDs from main API
// and generates unassigned DIDs from DID Pools
export async function getAllDIDs() {
  try {
    // First, get all assigned DIDs from the main DIDs endpoint
    let assignedDIDs = [];
    let pageNumber = 1;
    const pageSize = 100;
    let hasMore = true;

    while (hasMore) {
      const response = await getDIDs(pageSize, pageNumber);
      console.log("Assigned DIDs response:", response);
      
      if (response.entities && response.entities.length > 0) {
        assignedDIDs = [...assignedDIDs, ...response.entities];
        pageNumber++;
        hasMore = response.entities.length === pageSize;
      } else {
        hasMore = false;
      }
    }

    // Create a Set of assigned phone numbers for quick lookup
    const assignedNumbers = new Set(
      assignedDIDs.map(did => did.phoneNumber || did.number)
    );

    // Get all DID Pools to identify all possible DIDs
    const didPools = await getAllDIDPools();
    console.log("DID Pools:", didPools);

    // Generate all DIDs from pools and mark unassigned ones
    let allDIDs = [...assignedDIDs];

    for (const pool of didPools) {
      // Each pool has startPhoneNumber and endPhoneNumber
      const startNum = pool.startPhoneNumber;
      const endNum = pool.endPhoneNumber;
      
      if (startNum && endNum) {
        // Generate all numbers in the range
        const poolDIDs = generatePhoneNumberRange(startNum, endNum);
        
        for (const phoneNum of poolDIDs) {
          // If this number is not in assigned DIDs, add it as unassigned
          if (!assignedNumbers.has(phoneNum)) {
            allDIDs.push({
              id: `unassigned-${phoneNum}`,
              phoneNumber: phoneNum,
              number: phoneNum,
              name: null,
              owner: null,
              ownerType: null,
              state: "active",
              didPool: {
                id: pool.id,
                name: pool.name || `${pool.startPhoneNumber} - ${pool.endPhoneNumber}`
              },
              isUnassigned: true
            });
          }
        }
      }
    }

    console.log(`Total DIDs: ${allDIDs.length} (Assigned: ${assignedDIDs.length}, Unassigned: ${allDIDs.length - assignedDIDs.length})`);
    return allDIDs;
  } catch (err) {
    console.error("Error fetching all DIDs:", err);
    throw err;
  }
}

// Helper function to generate phone number range
function generatePhoneNumberRange(start, end) {
  const phoneNumbers = [];
  
  // Extract numeric parts (remove non-numeric characters except +)
  const cleanStart = start.replace(/[^\d+]/g, '');
  const cleanEnd = end.replace(/[^\d+]/g, '');
  
  // Get the prefix (like +1) and the numeric part
  const hasPlus = cleanStart.startsWith('+');
  const prefix = hasPlus ? '+' : '';
  
  const startDigits = cleanStart.replace('+', '');
  const endDigits = cleanEnd.replace('+', '');
  
  // Convert to BigInt for large number handling
  const startInt = BigInt(startDigits);
  const endInt = BigInt(endDigits);
  
  // Generate all numbers in range
  for (let i = startInt; i <= endInt; i++) {
    const numStr = i.toString();
    // Format back to phone number format
    phoneNumbers.push(prefix + numStr);
  }
  
  return phoneNumbers;
}
