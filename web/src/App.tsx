import { Navigate, Outlet, Route, Routes } from "react-router-dom";

import { useAuth } from "./auth";
import DashboardPage from "./pages/DashboardPage";
import InvestPage from "./pages/InvestPage";
import LoginPage from "./pages/LoginPage";
import OnboardingPage from "./pages/OnboardingPage";
import SignupPage from "./pages/SignupPage";
import StrategyLoadingPage from "./pages/StrategyLoadingPage";
import StrategyResultPage from "./pages/StrategyResultPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/invest" replace />} />
      <Route path="/invest" element={<InvestPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route path="/strategy/loading" element={<StrategyLoadingPage />} />
        <Route path="/strategy/result" element={<StrategyResultPage />} />
        <Route path="/app" element={<DashboardPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/invest" replace />} />
    </Routes>
  );
}

function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div className="route-loader">Loading your account...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
