import { Link, useLocation, useNavigate } from "react-router-dom";

function AppNavbar({ showAuthButtons = true, showUser = false, email = "" }) {
  const navigate = useNavigate();
  const location = useLocation();

  function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user_email");
    navigate("/");
  }

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar navbar-expand-lg bg-white border-bottom py-4 app-navbar">
      <div className="container">
      <Link to="/" className="navbar-brand fw-bold app-navbar-brand">
          Nutrition Tracker
        </Link>

        {showUser && (
          <div className="d-flex align-items-center gap-3">
            <div className="d-flex align-items-center gap-2">
              <Link
                to="/dashboard"
                className={`btn app-nav-btn ${
                  isActive("/dashboard") ? "btn-dark" : "btn-outline-dark"
                }`}
              >
                Dashboard
              </Link>
              <Link
                to="/library"
                className={`btn app-nav-btn ${
                  isActive("/library") ? "btn-dark" : "btn-outline-dark"
                }`}
              >
                Food Library
              </Link>
              <Link
                to="/goals"
                className={`btn app-nav-btn ${
                  isActive("/goals") ? "btn-dark" : "btn-outline-dark"
                }`}
              >
                Goals
              </Link>
            </div>

            <span className="text-muted app-navbar-user">
              {email ? `Signed in as: ${email}` : "Signed in"}
            </span>

            <button className="btn btn-outline-dark app-nav-btn" onClick={handleLogout}>
              Logout
            </button>
          </div>
        )}

        {showAuthButtons && !showUser && (
          <div className="d-flex align-items-center gap-3">
            <Link to="/login" className="btn btn-outline-dark btn-sm">
              Sign In
            </Link>
            <Link to="/register" className="btn btn-dark btn-sm">
              Sign Up
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}

export default AppNavbar;