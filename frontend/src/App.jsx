import {
  Route,
  Routes,
  Navigate,
  useNavigate,
  useLocation,
} from "react-router-dom";
import Login from "./components/shared/Login";
import AdminPage from "./pages/AdminPage";
import MemberPage from "./pages/MemberPage";
import ManagerPage from "./pages/ManagerPage";
import apiRequest from "./utils/apiRequest";
import { useEffect, useState } from "react";

const App = () => {
  const [userDetails, setUserDetails] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const fetchUserDetails = async () => {
      try {
        const userData = await apiRequest(`/get-userdetails`);
        if (userData) {
          setUserDetails(userData);
        } else {
          navigate("/login");
        }
      } catch (err) {
        console.error("Error fetching user details:", err);
        navigate("/login");
      }
    };

    if (location.pathname !== "/login") {
      fetchUserDetails();
    }
  }, [navigate, location.pathname]);

  if (!userDetails && location.pathname !== "/login") {
    return <div>Loading...</div>;
  }

  return (
    <Routes>
      <Route path="/" element={<Navigate to="/home" />} />
      <Route path="/login" element={<Login />} />
      <Route
        path="/home"
        element={
          userDetails?.role === "admin" ? (
            <AdminPage userDetails={userDetails} />
          ) : userDetails?.role === "member" ? (
            <MemberPage />
          ) : userDetails?.role === "manager" ? (
            <ManagerPage />
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="*"
        element={
          userDetails ? (
            <Navigate to="/home" />
          ) : (
            <Navigate to="/login" />
          )
        }
      />
    </Routes>
  );
};

export default App;
