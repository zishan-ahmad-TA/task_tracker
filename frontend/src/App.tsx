import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import Login from "./components/shared/Login";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </Router>
  );
};

export default App;
