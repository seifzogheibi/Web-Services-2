import { useState } from "react";
import { Link } from "react-router-dom";
import AppNavbar from "../components/AppNavbar";

const API = import.meta.env.VITE_API_URL;

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [statusMessage, setStatusMessage] = useState("");

  /*
  Submit login credentials to the backend using form-encoded data,
  store the returned JWT token, then route the user either to the
  dashboard or to the goals page depending on whether nutrition goals
  have already been set for the account.
*/
  async function handleLogin(e) {
    e.preventDefault();
    setStatusMessage("");

    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);
      formData.append("grant_type", "password");

      const res = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData.toString(),
      });

      const data = await res.json();

      if (!res.ok) {
        setStatusMessage(data.detail || "Login failed.");
        return;
      }

      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user_email", email);

      const meRes = await fetch(`${API}/auth/me`, {
        headers: {
          Authorization: `Bearer ${data.access_token}`,
        },
      });

      const meData = await meRes.json();

      if (!meRes.ok) {
        setStatusMessage(meData.detail || "Could not load your profile.");
        return;
      }

      const hasGoals =
        meData.daily_calorie_goal != null &&
        meData.daily_protein_goal != null &&
        meData.daily_carbs_goal != null &&
        meData.daily_fat_goal != null;

    window.location.href = hasGoals ? "/dashboard" : "/goals";
    } catch {
      setStatusMessage("Could not sign in.");
    }
  }

  return (
    <div className="bg-light min-vh-100">
      <AppNavbar />

      <div className="auth-wrapper">
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-12 col-md-8 col-lg-5">
              <div className="card border-0 shadow-sm auth-card">
                <div className="card-body p-4 p-md-5">
                  <h1 className="h2 fw-bold text-center mb-2">Sign In</h1>
                  <p className="text-muted text-center mb-4">
                    Access your nutrition dashboard
                  </p>

                  <form onSubmit={handleLogin}>
                    <div className="mb-3">
                      <label className="form-label">Email</label>
                      <input
                        type="email"
                        className="form-control"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Enter your email"
                        required
                      />
                    </div>

                    <div className="mb-3">
                      <label className="form-label">Password</label>
                      <input
                        type="password"
                        className="form-control"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Enter your password"
                        required
                      />
                    </div>

                    <button type="submit" className="btn btn-dark w-100">
                      Sign In
                    </button>
                  </form>

                  {statusMessage && (
                    <div className="alert alert-secondary mt-3 mb-0">
                      {statusMessage}
                    </div>
                  )}

                  <p className="text-center text-muted mt-4 mb-0">
                    Don’t have an account?{" "}
                    <Link to="/register" className="fw-semibold">
                      Sign Up
                    </Link>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;