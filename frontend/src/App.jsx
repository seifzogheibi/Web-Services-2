import { Routes, Route, Navigate } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import GoalsPage from "./pages/GoalsPage";
import DashboardPage from "./pages/DashboardPage";
import FoodLibraryPage from "./pages/FoodLibraryPage";

function App() {
  const token = localStorage.getItem("token");

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route
        path="/goals"
        element={token ? <GoalsPage /> : <Navigate to="/login" />}
      />
      <Route
        path="/dashboard"
        element={token ? <DashboardPage /> : <Navigate to="/login" />}
      />
      <Route
        path="/library"
        element={token ? <FoodLibraryPage /> : <Navigate to="/login" />}
      />

      <Route path="*" element={<Navigate to={token ? "/dashboard" : "/"} />} />
    </Routes>
  );
}

export default App;