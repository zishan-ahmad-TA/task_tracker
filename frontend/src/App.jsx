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
import Loader from "./components/ui-elements/Loader";


const App = () => {
  const { userDetails, loading } = useAuth();

  if (loading) {
    return <Loader />
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
