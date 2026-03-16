const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const cors = require('cors');
const app = express();
const https = require("https");
const fs = require("fs");

const PORT = 3001;
const SECRET = 'superSecretKey123';

var hostname = "localhost";
app.use(cors());
app.use(express.json());

const INACTIVITY_LIMIT = 120 * 60 * 1000; // 15 minutes in milliseconds

const dbConfig = {
  user: "GEN_IXNDB",
  password: "Knu54h#I4dmE6P9a",
  connectString: "ctip.apptoapp.org:1521/ctip_Srvc.oracle.db",
};

// Function to fetch data from the database
const fetchData = async (query, binds) => {
  const connection = await oracledb.getConnection(dbConfig);
  try {
    const result = await connection.execute(query, binds);
    return result;
  } finally {
    await connection.close();
  }
};


// Mock database with three users having different access levels
let users = {
  Voyagers_Admin: {
    loginId: 'Voyagers_Admin',
    passwordHash: bcrypt.hashSync('Voya_Admin@1468', 10),
    accessType: 'admin',
    lastLogin: null,
    lastActivity: null,
    failedAttempts: 0,
    isLocked: false,
    activeToken: null,
    createdAt: new Date('2024-01-01'),
    email: 'admin@company.com',
    fullName: 'System Administrator',
    clientId: 'VOYA'
  },
  Test_User: {
    loginId: 'Test_User',
    passwordHash: bcrypt.hashSync('Test_User@123', 10),
    accessType: 'user',
    lastLogin: null,
    lastActivity: null,
    failedAttempts: 0,
    isLocked: false,
    activeToken: null,
    createdAt: new Date('2024-02-15'),
    email: 'user@company.com',
    fullName: 'Regular User',
    clientId: 'INGWIN'
  },
  Power_User: {
    loginId: 'Power_User',
    passwordHash: bcrypt.hashSync('power@123', 10),
    accessType: 'elevatedAccess',
    lastLogin: null,
    lastActivity: null,
    failedAttempts: 0,
    isLocked: false,
    activeToken: null,
    createdAt: new Date('2024-03-10'),
    email: 'poweruser@company.com',
    fullName: 'Power User',
    clientId: 'HCAHCR'
  }
};

// Authentication Middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers.authorization;
  const token = authHeader && authHeader.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ message: 'Access token required' });
  }

  try {
    const decoded = jwt.verify(token, SECRET);
    const user = users[decoded.loginId];
    
    if (!user || user.activeToken !== token) {
      return res.status(401).json({ message: 'Invalid or expired session' });
    }

    const now = Date.now();
    if (user.lastActivity && now - user.lastActivity > INACTIVITY_LIMIT) {
      user.activeToken = null;
      user.lastActivity = null;
      return res.status(401).json({ message: 'Session expired due to inactivity' });
    }

    // Update last activity
    user.lastActivity = now;
    req.user = { ...user, loginId: decoded.loginId };
    next();
  } catch (err) {
    console.error('Token verification error:', err);
    return res.status(403).json({ message: 'Invalid token' });
  }
};

// Login Route
app.post('/api/login', async (req, res) => {
  try {
    const { loginId, password } = req.body;

    if (!loginId || !password) {
      return res.status(400).json({ message: 'Login ID and password are required' });
    }

    const user = users[loginId];
    if (!user) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    if (user.isLocked) {
      return res.status(403).json({ message: 'Account is locked due to multiple failed attempts' });
    }

    const passwordMatch = await bcrypt.compare(password, user.passwordHash);
    if (!passwordMatch) {
      user.failedAttempts += 1;
      if (user.failedAttempts >= 5) {
        user.isLocked = true;
      }
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    // Reset failed attempts on successful login
    user.failedAttempts = 0;
    user.lastLogin = new Date();
    user.lastActivity = Date.now();

    // Create JWT token
    const payload = { 
      loginId: user.loginId, 
      accessType: user.accessType,
      fullName: user.fullName 
    };
    const token = jwt.sign(payload, SECRET, { expiresIn: '1h' });

    // Store active token
    user.activeToken = token;

    res.json({ 
      message: 'Login successful',
      token,
      user: {
        loginId: user.loginId,
        accessType: user.accessType,
        fullName: user.fullName,
        email: user.email,
        lastLogin: user.lastLogin
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

// Logout Route
app.post('/api/logout', authenticateToken, (req, res) => {
  try {
    const user = users[req.user.loginId];
    if (user) {
      user.activeToken = null;
      user.lastActivity = null;
    }
    res.json({ message: 'Logged out successfully' });
  } catch (error) {
    console.error('Logout error:', error);
    res.status(500).json({ message: 'Error during logout' });
  }
});

// Activity Ping Route (for keeping session alive)
app.post('/api/ping', authenticateToken, (req, res) => {
  res.json({ 
    message: 'Activity recorded',
    lastActivity: req.user.lastActivity 
  });
});

// Token Refresh Route
app.post('/api/refresh', authenticateToken, (req, res) => {
  try {
    const user = users[req.user.loginId];
    
    // Generate new token
    const payload = { 
      loginId: user.loginId, 
      accessType: user.accessType,
      fullName: user.fullName 
    };
    const newToken = jwt.sign(payload, SECRET, { expiresIn: '1h' });
    
    // Update active token
    user.activeToken = newToken;
    user.lastActivity = Date.now();

    res.json({ 
      message: 'Token refreshed',
      token: newToken 
    });
  } catch (error) {
    console.error('Token refresh error:', error);
    res.status(500).json({ message: 'Error refreshing token' });
  }
});

// Protected route example
app.get('/api/profile', authenticateToken, (req, res) => {
  const user = users[req.user.loginId];
  res.json({
    loginId: user.loginId,
    accessType: user.accessType,
    fullName: user.fullName,
    email: user.email,
    lastLogin: user.lastLogin,
    createdAt: user.createdAt
  });
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ message: 'Server is running', timestamp: new Date() });
});


app.post('/api/getAllConversations', authenticateToken, async(req, res) => {
  const targetFormatter = "yyyy-MM-dd";
  let fromDate = req.body.startDate;
  let toDate = req.body.endDate;

  // Extract filters
  let clientId = req.body.clientId || [];
  let agentId = req.body.agentId || [];
  let customerName = req.body.agentId || [];
  let ANI = req.body.ANI || [];
  let dnis = req.body.dnis || [];
  

  let connection;

  try {
    // Format and validate input date
    console.log("Past Date", fromDate, " ", toDate);
    fromDate = format(parseISO(fromDate), targetFormatter);
    toDate = format(parseISO(toDate), targetFormatter);
    connection = await oracledb.getConnection(dbConfig);

    let fetchGroupDataCallQuery = ` SELECT STARTDATE, FROM CLOUD_STA_IXNS 
    WHERE 
      TRUNC(startdate) BETWEEN TO_DATE(:fromDate, 'YYYY-MM-DD') AND TO_DATE(:toDate, 'YYYY-MM-DD')`

    fetchGroupDataCallQuery += ` ORDER BY CALLDURATION DESC FETCH FIRST 5000 ROWS ONLY`;

    const convertTime = (utcString) => {
      let utcDate = new Date(utcString);

      let localTimeString = utcDate.toLocaleString();

      return localTimeString;
    };

     const formatTime = (time) => {
      if (time == null) {
        return 0;
      }
 
      let timeString = "";
      const hours =  Math.floor(time/60);
      const minsAct = Math.floor(time);
      const mins = Math.floor(time-hours*60);
      const seconds = Math.round((time - minsAct) * 60);

      if (hours > 0) {
        if (hours > 9) {
          timeString += hours + " : ";
        } else {
          timeString += "0" + hours + " : ";
        }
      } else {
        timeString += "00 : ";
      }

      if (mins > 0) {
        if (mins > 9) {
          timeString += mins + " : ";
        } else {
          timeString += "0" + mins + " : ";
        }
      } else {
        timeString += "00 : ";
      }

      if (seconds > 0) {
        if (seconds > 9) {
          timeString += seconds;
        } else {
          timeString += "0" + seconds;
        }
      } else {
        timeString += "00";
      }

      if (timeString.length > 0) {
        return timeString;
      } else {
        return 0;
      }
    };

    const processTotals = (item) => ({
      //"Start Date": item[0],
      "Start Date": convertTime(item[0]),
      "Conversation ID": item[1],
      LOB: item[3],
      "Market Type": item[16] || "NULL",
      Division: item[27],
      Queue: item[2],
      "Client ID": item[17] || "NA",
      "Work Teams": item[24] || "NULL",
      "Agent Name": item[4],
      ANI: item[18] || "NA",

      "Call Duration": formatTime(item[5]),
      "Agent Duration": formatTime(item[20]),
      "ACW Time": formatTime(item[25]),
      "Call Handle Time": formatTime(item[26]),

      "Customer Talk Time %": item[7] || 0,
      "Agent Talk Time %": item[8] || 0,
      "Silence Time %": item[9] || 0 || 0,
      "IVR Time %": item[10] || 0,
      "Queue Wait Time %": item[11] || 0,
      "Overtalk %": item[12] || 0,
      "Other(Hold/Noise/SP) Time %": item[13] || 0,
      "Overtalk Count": item[14] || 0,
      "Sentiment Score": Math.round(item[6] * 100) || "NA",
      "Sentiment Trend": Math.round(item[15] * 100) || "NA",
    });

    const resp1 = await connection.execute(fetchGroupDataCallQuery, binds1);
    // console.log("2");
    const resp2 = await connection.execute(fetchGroupDataACDQuery, binds2);

    const resp3 = await connection.execute(fetchGroupDataCustomerQuery, binds3);

    const resp4 = await connection.execute(fetchGroupDataAgentQuery, binds4);

    const resp5 = await connection.execute(fetchGroupDataSilenceQuery, binds5);
    const resp6 = await connection.execute(fetchGroupDataIVRQuery, binds6);

    const resp7 = await connection.execute(fetchGroupDataOthersQuery, binds7);

    const resp8 = await connection.execute(fetchGroupDataOvertalkQuery, binds8);
    //console.log(resp1.rows);

    const callStackData = resp1.rows.map((result) => processTotals(result));
    const queueStackData = resp2.rows.map((result) => processTotals(result));
    const customerStackData = resp3.rows.map((result) => processTotals(result));
    const agentStackData = resp4.rows.map((result) => processTotals(result));
    const silenceStackData = resp5.rows.map((result) => processTotals(result));
    const IVRStackData = resp6.rows.map((result) => processTotals(result));
    const otherStackData = resp7.rows.map((result) => processTotals(result));
    const overtalkStackData = resp8.rows.map((result) => processTotals(result));

    res.json({
      // callStackData: resp1.rows,
      callStackData: callStackData,
      queueStackData: queueStackData,
      customerStackData: customerStackData,
      agentStackData: agentStackData,
      silenceStackData: silenceStackData,
      IVRStackData: IVRStackData,
      otherStackData: otherStackData,
      overtalkStackData: overtalkStackData,
    });
  } catch (error) {
    console.error(error);
    res.json({ FeedFail: "True" });
  } finally {
    if (connection) {
      await connection.close();
    }
  }
});

// const privateKey = fs.readFileSync('/GenApps/Certs/certificate_key', 'utf8');
// const certificate = fs.readFileSync('/GenApps/Certs/certificate', 'utf8');

// // create https server using existing certificate and private key
// const server = https.createServer({
//     key: privateKey,
//     cert: certificate
// }, app);

// server.listen(PORT,
//     () => {
//         console.log(`listening to PORT : http://${hostname}:${PORT}`);
//     })


app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});