import { Navigate, Outlet, Route, Routes } from "react-router-dom";

import { useAuth } from "./auth";
import AppShell from "./components/AppShell";
import InvestPage from "./pages/InvestPage";
import LoginPage from "./pages/LoginPage";
import OnboardingPage from "./pages/OnboardingPage";
import SignupPage from "./pages/SignupPage";
import StrategyLoadingPage from "./pages/StrategyLoadingPage";
import StrategyResultPage from "./pages/StrategyResultPage";
import OverviewPage from "./pages/app/OverviewPage";
import ProfilePage from "./pages/app/ProfilePage";
import SimulationPage from "./pages/app/SimulationPage";
import StrategyPage from "./pages/app/StrategyPage";

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
        <Route path="/app" element={<AppShell />}>
          <Route index element={<Navigate to="/app/overview" replace />} />
          <Route path="overview" element={<OverviewPage />} />
          <Route path="strategy" element={<StrategyPage />} />
          <Route path="simulation" element={<SimulationPage />} />
          <Route path="profile" element={<ProfilePage />} />
        </Route>
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
