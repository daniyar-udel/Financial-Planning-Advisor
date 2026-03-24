import { Link, NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../auth";

const appNavItems = [
  { to: "/app/overview", label: "Overview" },
  { to: "/app/strategy", label: "Strategy" },
  { to: "/app/simulation", label: "Simulation" },
  { to: "/app/profile", label: "Profile" },
];

export default function AppShell() {
  const { user, logoutUser } = useAuth();

  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <div>
          <div className="eyebrow">Private Area</div>
          <h2>AI Investment Strategy Advisor</h2>
          <p>
            Your post-onboarding workspace for reviewing strategy, simulations, and profile data.
          </p>
        </div>

        <nav className="app-nav">
          {appNavItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `app-nav-link${isActive ? " app-nav-link-active" : ""}`}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="app-sidebar-footer">
          <p>{user?.full_name}</p>
          <div className="app-shell-actions">
            <Link className="secondary-button link-button" to="/invest">
              Public page
            </Link>
            <button className="primary-button slim-button" onClick={logoutUser} type="button">
              Log out
            </button>
          </div>
        </div>
      </aside>

      <section className="app-content">
        <Outlet />
      </section>
    </div>
  );
}
