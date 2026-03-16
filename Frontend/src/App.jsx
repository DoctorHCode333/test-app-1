import { useEffect, useState } from "react";

import {useSelector,useDispatch} from "react-redux"
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import "./App.css";
import "./index.css";
import 'primereact/resources/themes/lara-light-indigo/theme.css';
import 'primereact/resources/primereact.min.css';
import 'primeicons/primeicons.css';
import 'primeflex/primeflex.css';
import Login from "./Components/login"; 
import DID_Dashboard from "./Components/DID_Dashboard";
import HLD_Architecture from "./Components/HLD_architecture";
import { authenticate } from "./utils/genesysCloudApi";

import {setUsersData} from "./Redux/actions"

// const ProtectedRoute = ({ children }) => {
//   const token = localStorage.getItem("authToken");
//   return token ? children : <Navigate to="/VOYA_CLIENT_APP" replace/>;
// };

const App = (props) => {
  const dispatch = useDispatch();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
     getPlatformClientData();
  }, [])
  
  async function getPlatformClientData() {
    try {
      const data = await authenticate();
      // const result = await getUsersData();        
      // dispatch(setUsersData(result))
      console.log('AUTH', data);
      setIsAuthenticated(true);
    } catch (err) {
      console.error(err);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <i className="pi pi-spin pi-spinner" style={{ fontSize: '2rem' }}></i>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route
          path="/VOYA_CLIENT_APP"
          element={isAuthenticated ? <HLD_Architecture {...props} /> : <div>Authentication failed</div>}
        />
      </Routes>
    </Router>
  );
};

export default App;
