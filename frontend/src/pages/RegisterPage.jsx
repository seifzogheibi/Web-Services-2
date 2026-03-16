import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import AppNavbar from "../components/AppNavbar";

const API = "http://127.0.0.1:8000";

function RegisterPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [statusMessage, setStatusMessage] = useState("");

  async function handleRegister(e) {
    e.preventDefault();
    setStatusMessage("");

    try {
      const res = await fetch(`${API}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setStatusMessage(data.detail || "Registration failed.");
        return;
      }

      setStatusMessage("Registration successful. Please sign in.");
      setTimeout(() => navigate("/login"), 1000);
    } catch {
      setStatusMessage("Could not register.");
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
                  <h1 className="h2 fw-bold text-center mb-2">Create Account</h1>
                  <p className="text-muted text-center mb-4">
                    Start your nutrition journey
                  </p>

                  <form onSubmit={handleRegister}>
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
                        placeholder="Create a password"
                        required
                      />
                    </div>

                    <button type="submit" className="btn btn-dark w-100">
                      Sign Up
                    </button>
                  </form>

                  {statusMessage && (
                    <div className="alert alert-secondary mt-3 mb-0">
                      {statusMessage}
                    </div>
                  )}

                  <p className="text-center text-muted mt-4 mb-0">
                    Already have an account?{" "}
                    <Link to="/login" className="fw-semibold">
                      Sign In
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

export default RegisterPage;