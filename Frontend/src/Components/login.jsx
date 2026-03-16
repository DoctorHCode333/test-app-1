import React, { useState, useEffect, useRef } from "react";
import {
  Eye,
  EyeOff,
  User,
  Lock,
  Shield,
  AlertTriangle,
  CheckCircle,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import voyaLogo from "../assets/VoyaLogo.png";
import Voya_Logo_2 from "../assets/Voya_Logo_2.png";
import Voya_Scenic from "../assets/Voya_Scenic.jpeg";
import {setUsersData} from "../Redux/actions.jsx";


const Login = (props) => {
  const dispatch = useDispatch();
  const { isLoggedIn, setIsLoggedIn } = props;
  const [formData, setFormData] = useState({
    loginId: "",
    password: "",
  });
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState(""); // 'success', 'error', 'info'
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const [userInfo, setUserInfo] = useState(null);
  const navigate = useNavigate();

  // Refs for managing timers
  const inactivityTimerRef = useRef(null);
  const refreshTimerRef = useRef(null);
  const pingIntervalRef = useRef(null);

  const INACTIVITY_TIMEOUT = 45 * 60 * 1000; // 15 minutes
  const REFRESH_INTERVAL = 50 * 60 * 1000; // 50 minutes (refresh before 1h expiry)
  const PING_INTERVAL = 2 * 60 * 1000; // 2 minutes

  // Initialize token from localStorage
  useEffect(() => {
    const token = localStorage.getItem("authToken");
    const storedUserInfo = localStorage.getItem("userInfo");

    if (token && storedUserInfo) {
      setIsLoggedIn(true);
      setUserInfo(JSON.parse(storedUserInfo));
      startSessionManagement();
    }
  }, []);

  // Start session management (inactivity timer, token refresh, ping)
  const startSessionManagement = () => {
    startInactivityTimer();
    startTokenRefresh();
    startPingInterval();
  };

  // Stop all session management timers
  const stopSessionManagement = () => {
    if (inactivityTimerRef.current) {
      clearTimeout(inactivityTimerRef.current);
    }
    if (refreshTimerRef.current) {
      clearInterval(refreshTimerRef.current);
    }
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
    }
  };

  // Reset inactivity timer on user activity
  const resetInactivityTimer = () => {
    if (inactivityTimerRef.current) {
      clearTimeout(inactivityTimerRef.current);
    }

    inactivityTimerRef.current = setTimeout(() => {
      handleLogout("Session expired due to inactivity");
    }, INACTIVITY_TIMEOUT);
  };

  // Start inactivity timer and add event listeners
  const startInactivityTimer = () => {
    const events = [
      "mousedown",
      "mousemove",
      "keypress",
      "scroll",
      "touchstart",
      "click",
    ];

    const resetTimer = () => resetInactivityTimer();

    events.forEach((event) => {
      document.addEventListener(event, resetTimer, true);
    });

    resetInactivityTimer();
  };

  // Start automatic token refresh
  const startTokenRefresh = () => {
    refreshTimerRef.current = setInterval(async () => {
      await refreshToken();
    }, REFRESH_INTERVAL);
  };

  // Start ping interval to keep session active
  const startPingInterval = () => {
    pingIntervalRef.current = setInterval(async () => {
      await pingServer();
    }, PING_INTERVAL);
  };

  // Ping server to maintain session
  const pingServer = async () => {
    try {
      const token = localStorage.getItem("authToken");
      if (!token) return;

      const response = await fetch("http://localhost:3001/api/ping", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Ping failed");
      }
    } catch (error) {
      console.error("Ping error:", error);
      handleLogout("Session expired");
    }
  };

  // Refresh JWT token
  const refreshToken = async () => {
    try {
      const token = localStorage.getItem("authToken");
      if (!token) return;

      const response = await fetch("http://localhost:3001/api/refresh", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem("authToken", data.token);
        console.log("Token refreshed successfully");
      } else {
        throw new Error("Token refresh failed");
      }
    } catch (error) {
      console.error("Token refresh error:", error);
      handleLogout("Session expired");
    }
  };

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // Show message with auto-hide
  const showMessage = (text, type = "info") => {
    setMessage(text);
    setMessageType(type);

    setTimeout(() => {
      setMessage("");
      setMessageType("");
    }, 5000);
  };

  // Handle login
  const handleLogin = async (e) => {
    e.preventDefault();

    if (!formData.loginId || !formData.password) {
      showMessage("Please enter both login ID and password", "error");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:3001/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem("authToken", data.token);
        localStorage.setItem("userInfo", JSON.stringify(data.user));
       
        dispatch(setUsersData(data.user)); // Dispatch action to store users data in Redux
        setIsLoggedIn(true);
        setUserInfo(data.user);
        showMessage("Login successful! Redirecting...", "success");

        startSessionManagement();

        // Simulate redirect to main page after 2 seconds
        // setTimeout(() => {
        //   showMessage('Redirected to main application', 'info');
        // }, 2000);
        setTimeout(
          () =>
            navigate("/VOYA_CLIENT_APP/Audio_Redaction_Workspace", {
              replace: true,
            }),
          2000
        );
      } else {
        showMessage(data.message || "Login failed", "error");
      }
    } catch (error) {
      console.error("Login error:", error);
      showMessage("Network error. Please try again.", "error");
    } finally {
      setIsLoading(false);
    }
  };

  // Handle logout
  const handleLogout = async (reason = "Logged out successfully") => {
    try {
      const token = localStorage.getItem("authToken");

      if (token) {
        await fetch("http://localhost:3001/api/logout", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });
      }
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      localStorage.removeItem("authToken");
      localStorage.removeItem("userInfo");

      stopSessionManagement();

      setIsLoggedIn(false);
      setUserInfo(null);
      setFormData({ loginId: "", password: "" });
      showMessage(reason, "info");
      setTimeout(() => navigate("/VOYA_CLIENT_APP", { replace: true }), 2000);
    }
  };

  // Get access level badge color
  const getAccessBadgeColor = (accessType) => {
    switch (accessType) {
      case "admin":
        return "bg-red-100 text-red-800 border-red-200";
      case "user_elevated":
        return "bg-orange-100 text-orange-800 border-orange-200";
      case "user":
        return "bg-green-100 text-green-800 border-green-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  // Get access level icon
  const getAccessIcon = (accessType) => {
    switch (accessType) {
      case "admin":
        return <Shield className="w-4 h-4" />;
      case "user_elevated":
        return <User className="w-4 h-4" />;
      case "user":
        return <User className="w-4 h-4" />;
      default:
        return <User className="w-4 h-4" />;
    }
  };

  // if (isLoggedIn && userInfo) {
  //   return (
  //     <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 flex items-center justify-center p-4">
  //       <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md border border-gray-100">
  //         <div className="text-center mb-6">
  //           <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
  //             <CheckCircle className="w-8 h-8 text-green-600" />
  //           </div>
  //           <h2 className="text-2xl font-bold text-gray-800 mb-2">Welcome Back!</h2>
  //           <p className="text-gray-600">You are successfully logged in</p>
  //         </div>

  //         <div className="space-y-4 mb-6">
  //           <div className="bg-gray-50 rounded-lg p-4">
  //             <div className="flex items-center justify-between mb-2">
  //               <span className="text-sm font-medium text-gray-500">User</span>
  //               <span className="text-sm font-semibold text-gray-800">{userInfo.fullName}</span>
  //             </div>
  //             <div className="flex items-center justify-between mb-2">
  //               <span className="text-sm font-medium text-gray-500">Login ID</span>
  //               <span className="text-sm font-semibold text-gray-800">{userInfo.loginId}</span>
  //             </div>
  //             <div className="flex items-center justify-between mb-2">
  //               <span className="text-sm font-medium text-gray-500">Access Level</span>
  //               <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getAccessBadgeColor(userInfo.accessType)}`}>
  //                 {getAccessIcon(userInfo.accessType)}
  //                 <span className="ml-1 capitalize">{userInfo.accessType.replace('_', ' ')}</span>
  //               </div>
  //             </div>
  //             <div className="flex items-center justify-between">
  //               <span className="text-sm font-medium text-gray-500">Email</span>
  //               <span className="text-sm font-semibold text-gray-800">{userInfo.email}</span>
  //             </div>
  //           </div>
  //         </div>

  //         <button
  //           onClick={() => handleLogout()}
  //           className="w-full bg-red-500 hover:bg-red-600 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200"
  //         >
  //           Logout
  //         </button>

  //         <div className="mt-4 text-center">
  //           <p className="text-xs text-gray-500">
  //             Session will expire after 15 minutes of inactivity
  //           </p>
  //         </div>
  //       </div>s
  //     </div>
  //   );
  // }

  return (
    // <div className="min-h-screen flex items-center justify-center p-4 relative"
    //   style={{
    //     background: "linear-gradient(135deg, #ff4b00 0%,  #ff8000 100%)",
    //     // background: "linear-gradient(135deg, #667eea 0%, #764ba2 35%, #f093fb 70%, #f5576c 100%)",
    //     backgroundAttachment: 'fixed'
    //   }}>

    <div
      className="min-h-screen flex items-center justify-center p-4 relative"
      style={{
        backgroundImage: `url(${Voya_Scenic})`,
        backgroundSize: "cover", // Ensures the image covers the entire area
        backgroundPosition: "center", // Centers the image
        backgroundRepeat: "no-repeat", // Prevents tiling
        backgroundAttachment: "fixed", // Keeps the image fixed during scroll
      }}
    >
      <div className="bg-white rounded-2xl shadow-xl px-6 py-6 w-full max-w-md border border-gray-100">
        <div className="text-center mb-5">
          <img src={Voya_Logo_2} alt="VOYA" />
          {/* <Lock className="w-8 h-8 text-orange-600" /> */}

          <h1 className="text-3xl font-bold text-orange-600 mb-2">Welcome</h1>
          <p className="text-gray-600">Please sign in to your account</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label
              htmlFor="loginId"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Login ID
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <User className="h-5 w-5 text-gray-400" />
              </div>
              <input
                id="loginId"
                name="loginId"
                type="text"
                value={formData.loginId}
                onChange={handleInputChange}
                className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
                placeholder="Enter your login ID"
                disabled={isLoading}
              />
            </div>
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Password
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-gray-400" />
              </div>
              <input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                value={formData.password}
                onChange={handleInputChange}
                className="block w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
                placeholder="Enter your password"
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                disabled={isLoading}
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                ) : (
                  <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                )}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-orange-400 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center"
            //        style={{
            //   background: "linear-gradient(135deg, #ff4b00 0%,  #ff8000 100%)",
            //   // background: "linear-gradient(135deg, #667eea 0%, #764ba2 35%, #f093fb 70%, #f5576c 100%)",
            //   backgroundAttachment: 'fixed'
            // }}
          >
            {isLoading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Signing in...
              </div>
            ) : (
              "Sign In"
            )}
          </button>
        </form>

        {message && (
          <div
            className={`mt-4 p-3 rounded-lg flex items-center ${
              messageType === "success"
                ? "bg-green-50 text-green-800 border border-green-200"
                : messageType === "error"
                ? "bg-red-50 text-red-800 border border-red-200"
                : "bg-blue-50 text-blue-800 border border-blue-200"
            }`}
          >
            {messageType === "error" && (
              <AlertTriangle className="w-4 h-4 mr-2" />
            )}
            {messageType === "success" && (
              <CheckCircle className="w-4 h-4 mr-2" />
            )}
            <span className="text-sm font-medium">{message}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default Login;