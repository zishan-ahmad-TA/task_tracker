import {
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import Login from "./components/shared/Login";
import AdminPage from "./pages/AdminPage";
import MemberPage from "./pages/MemberPage";
import ManagerPage from "./pages/ManagerPage";
import useAuth from "./hooks/useAuth";


const App = () => {
  const { userDetails, loading } = useAuth();

  if (loading) return;

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
            <MemberPage userDetails={userDetails}/>
          ) : userDetails?.role === "manager" ? (
            <ManagerPage userDetails={userDetails}/>
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
