import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AppNavbar from "../components/AppNavbar";

const API = "http://127.0.0.1:8000";

function GoalsPage() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token") || "";
  const userEmail = localStorage.getItem("user_email") || "";

  const [me, setMe] = useState(null);
  const [loadingGoals, setLoadingGoals] = useState(true);
  const [statusMessage, setStatusMessage] = useState("");

  const [goals, setGoals] = useState({
    daily_calorie_goal: "",
    daily_protein_goal: "",
    daily_carbs_goal: "",
    daily_fat_goal: "",
  });

  async function fetchMe() {
    try {
      const res = await fetch(`${API}/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await res.json();

      if (!res.ok) {
        setStatusMessage(data.detail || "Could not load your goals.");
        setLoadingGoals(false);
        return;
      }

      setMe(data);

      setGoals({
        daily_calorie_goal:
          data.daily_calorie_goal != null ? String(data.daily_calorie_goal) : "",
        daily_protein_goal:
          data.daily_protein_goal != null ? String(data.daily_protein_goal) : "",
        daily_carbs_goal:
          data.daily_carbs_goal != null ? String(data.daily_carbs_goal) : "",
        daily_fat_goal:
          data.daily_fat_goal != null ? String(data.daily_fat_goal) : "",
      });

      setLoadingGoals(false);
    } catch {
      setStatusMessage("Could not load your goals.");
      setLoadingGoals(false);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setStatusMessage("");

    try {
      const res = await fetch(`${API}/auth/goals`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          daily_calorie_goal: Number(goals.daily_calorie_goal),
          daily_protein_goal: Number(goals.daily_protein_goal),
          daily_carbs_goal: Number(goals.daily_carbs_goal),
          daily_fat_goal: Number(goals.daily_fat_goal),
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        setStatusMessage(data.detail || "Could not save goals.");
        return;
      }

      navigate("/dashboard");
    } catch {
      setStatusMessage("Could not save goals.");
    }
  }

  useEffect(() => {
    fetchMe();
  }, []);

  return (
    <div className="bg-light min-vh-100">
      <AppNavbar
        showAuthButtons={false}
        showUser
        email={me?.email || userEmail}
      />

      <div className="goals-wrapper">
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-12 col-lg-6">
              <div className="card border-0 shadow-sm fade-in-up">
                <div className="card-body p-4 p-md-5">
                  <h1 className="h2 fw-bold text-center mb-2">Set Your Goals</h1>
                  <p className="text-muted text-center mb-4">
                    Choose your daily nutrition targets
                  </p>

                  {loadingGoals ? (
                    <p className="text-center text-muted mb-0">Loading goals...</p>
                  ) : (
                    <form onSubmit={handleSubmit}>
                      <div className="mb-3">
                        <label className="form-label">Daily Calorie Goal</label>
                        <input
                          type="number"
                          min="0"
                          className="form-control"
                          value={goals.daily_calorie_goal}
                          onChange={(e) =>
                            setGoals({
                              ...goals,
                              daily_calorie_goal: e.target.value,
                            })
                          }
                          required
                        />
                      </div>

                      <div className="mb-3">
                        <label className="form-label">Daily Protein Goal (g)</label>
                        <input
                          type="number"
                          min="0"
                          className="form-control"
                          value={goals.daily_protein_goal}
                          onChange={(e) =>
                            setGoals({
                              ...goals,
                              daily_protein_goal: e.target.value,
                            })
                          }
                          required
                        />
                      </div>

                      <div className="mb-3">
                        <label className="form-label">Daily Carbs Goal (g)</label>
                        <input
                          type="number"
                          min="0"
                          className="form-control"
                          value={goals.daily_carbs_goal}
                          onChange={(e) =>
                            setGoals({
                              ...goals,
                              daily_carbs_goal: e.target.value,
                            })
                          }
                          required
                        />
                      </div>

                      <div className="mb-4">
                        <label className="form-label">Daily Fat Goal (g)</label>
                        <input
                          type="number"
                          min="0"
                          className="form-control"
                          value={goals.daily_fat_goal}
                          onChange={(e) =>
                            setGoals({
                              ...goals,
                              daily_fat_goal: e.target.value,
                            })
                          }
                          required
                        />
                      </div>

                      <button type="submit" className="btn btn-dark w-100">
                        Save Goals
                      </button>
                    </form>
                  )}

                  {statusMessage && (
                    <div className="alert alert-secondary mt-3 mb-0">
                      {statusMessage}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default GoalsPage;