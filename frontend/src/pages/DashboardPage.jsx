import { useEffect, useMemo, useState } from "react";
import AppNavbar from "../components/AppNavbar";

const API = import.meta.env.VITE_API_URL;
const MEAL_SECTIONS = ["Breakfast", "Lunch", "Dinner", "Snack"];

/*
  Reusable progress-ring component used to visualise how close the user is
  to each daily nutrition target. The ring animates smoothly from 0 to the
  current percentage to make dashboard feedback more dynamic.
*/

function ProgressCircle({ label, value, goal }) {
  const safeGoal = Number(goal) || 1;
  const safeValue = Number(value) || 0;
  const targetPercentRaw = Math.round((safeValue / safeGoal) * 100);
  const targetPercentForRing = Math.min(targetPercentRaw, 100);

  const [animatedPercent, setAnimatedPercent] = useState(0);

  /*
  Load the initial dashboard state when the page opens, including the user's
  profile, food library, meals for the selected date, nutrition totals,
  and smart suggestions.
*/
  useEffect(() => {
    const duration = 2200;
    let animationFrame;

    function easeOutCubic(t) {
      return 1 - Math.pow(1 - t, 3);
    }

    function animate(startTime) {
      function step(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = easeOutCubic(progress);
        const nextValue = Math.round(targetPercentForRing * eased);

        setAnimatedPercent(nextValue);

        if (progress < 1) {
          animationFrame = requestAnimationFrame(step);
        }
      }

      animationFrame = requestAnimationFrame(step);
    }

    setAnimatedPercent(0);
    animationFrame = requestAnimationFrame((start) => animate(start));

    return () => cancelAnimationFrame(animationFrame);
  }, [targetPercentForRing]);

  let statusClass = "goal-neutral";
  let statusText = "In progress";

  if (targetPercentRaw >= 100) {
    statusClass = "goal-success";
    statusText = "Goal reached";
  } else if (targetPercentRaw >= 80) {
    statusClass = "goal-warning";
    statusText = "Almost there";
  }

  const displayPercent = targetPercentRaw > 100 ? "100%+" : `${animatedPercent}%`;

  return (
    <div className="progress-circle-card text-center">
      <div
        className="progress-ring mx-auto mb-3"
        style={{
          background: `conic-gradient(var(--accent-dark) ${animatedPercent * 3.6}deg, #e9ecef 0deg)`,
        }}
      >
        <div className="progress-ring-inner">
          <div className="fw-bold fs-5">{displayPercent}</div>
        </div>
      </div>

      <div className="fw-semibold">{label}</div>
      <div className="text-muted small mb-2">
        {Number(safeValue.toFixed(1))} / {goal ?? 0}
      </div>

      <span className={`goal-badge ${statusClass}`}>{statusText}</span>
    </div>
  );
}

function DashboardPage() {
  const token = localStorage.getItem("token") || "";
  const userEmail = localStorage.getItem("user_email") || "";

  const [me, setMe] = useState(null);
  const [foods, setFoods] = useState([]);
  const [selectedDate, setSelectedDate] = useState(
    new Date().toISOString().slice(0, 10)
  );
  const [dailySummary, setDailySummary] = useState(null);
  const [statusMessage, setStatusMessage] = useState("");
  const [mealsForDate, setMealsForDate] = useState([]);
  const [suggestions, setSuggestions] = useState([]);

  const [mealForms, setMealForms] = useState({
    Breakfast: { food_id: "", grams: "" },
    Lunch: { food_id: "", grams: "" },
    Dinner: { food_id: "", grams: "" },
    Snack: { food_id: "", grams: "" },
  });
  
    /*
    Build request headers for authenticated API calls.
    JSON content type is included by default, but can be disabled for requests
    that only need the bearer token.
    */
  function getAuthHeaders(json = true) {
    const headers = {};
    if (token) headers.Authorization = `Bearer ${token}`;
    if (json) headers["Content-Type"] = "application/json";
    return headers;
  }

  function formatDisplayDate(dateString) {
    const [year, month, day] = dateString.split("-");
    return `${day}-${month}-${year}`;
  }

  
    /*
    Convert food names into a cleaner title-style format before displaying them
    in the dashboard, since imported or stored names may appear in all caps.
    */

  function formatFoodName(name) {
    if (!name) return "Unknown food";
  
    return name
      .toLowerCase()
      .replace(/\b\w/g, (char) => char.toUpperCase());
  }

  /*
  Normalize backend meal names so they map consistently to the fixed frontend
  dashboard sections: Breakfast, Lunch, Dinner, and Snack.
*/
  function normalizeMealName(name) {
    const value = (name || "").trim().toLowerCase();

    if (value === "breakfast") return "Breakfast";
    if (value === "lunch") return "Lunch";
    if (value === "dinner") return "Dinner";
    if (value === "snack" || value === "snacks") return "Snack";

    return null;
  }

  /*
  Group logged meal items under the correct dashboard section by matching
  backend meal records to the normalized frontend meal labels.
*/
  function getSectionItems(sectionName) {
    return mealsForDate
      .filter((meal) => normalizeMealName(meal.name) === sectionName)
      .flatMap((meal) => meal.items || []);
  }

  async function fetchMe() {
    try {
      const res = await fetch(`${API}/auth/me`, {
        headers: getAuthHeaders(false),
      });

      const data = await res.json();

      if (!res.ok) {
        setStatusMessage(data.detail || "Could not load profile.");
        return;
      }

      setMe(data);
    } catch {
      setStatusMessage("Could not load profile.");
    }
  }

  async function fetchFoods() {
    try {
      const res = await fetch(`${API}/foods/`, {
        headers: getAuthHeaders(false),
      });
      if (!res.ok) throw new Error("Failed to load foods");
      const data = await res.json();
      setFoods(data);
    } catch {
      setStatusMessage("Could not load foods.");
    }
  }

  async function fetchMealsForDate(date = selectedDate) {
    try {
      const res = await fetch(`${API}/meals/by-date?date=${date}`, {
        headers: getAuthHeaders(false),
      });
      if (!res.ok) throw new Error("Failed to load diary");
      const data = await res.json();
      setMealsForDate(data);
    } catch {
      setStatusMessage("Could not load food diary.");
    }
  }

  /*
  Load the aggregated nutrition totals for the selected date so progress
  circles can compare the user's consumed values against saved goals.
*/
  async function fetchDailySummary(date = selectedDate) {
    try {
      const res = await fetch(`${API}/analytics/daily?date=${date}`, {
        headers: getAuthHeaders(false),
      });
      if (!res.ok) throw new Error("Summary failed");
      const data = await res.json();
      setDailySummary(data);
    } catch {
      setStatusMessage("Could not load nutrition summary.");
    }
  }

  /*
  Retrieve Smart Goal Gap Suggestions from the backend.
  These suggestions recommend foods from the user's library that best fit
  the remaining calorie and macronutrient gap for the selected day.
*/
  async function fetchSuggestions(date = selectedDate) {
    try {
      const res = await fetch(`${API}/analytics/suggestions?date=${date}`, {
        headers: getAuthHeaders(false),
      });

      if (!res.ok) throw new Error("Suggestions failed");

      const data = await res.json();
      setSuggestions(data);
    } catch {
      setSuggestions([]);
    }
  }

  /*
  Add a selected food and gram quantity into one of the meal sections.
  If the section does not yet exist for the chosen date, a meal record is
  created first and then the food is attached through a meal item.
*/
  async function handleAddFoodToSection(sectionName) {
    const sectionForm = mealForms[sectionName];

    if (!sectionForm.food_id) {
      setStatusMessage(`Choose a food for ${sectionName}.`);
      return;
    }

    if (!sectionForm.grams) {
      setStatusMessage(`Enter grams for ${sectionName}.`);
      return;
    }

    try {
      let existingMeal = mealsForDate.find(
        (meal) => normalizeMealName(meal.name) === sectionName
      );

      if (!existingMeal) {
        const mealRes = await fetch(`${API}/meals/`, {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({
            name: sectionName,
            eaten_at: `${selectedDate}T12:00:00`,
          }),
        });

        if (!mealRes.ok) throw new Error("Could not create meal section");
        existingMeal = await mealRes.json();
      }

      const itemRes = await fetch(`${API}/meals/${existingMeal.id}/items`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          food_id: Number(sectionForm.food_id),
          grams: Number(sectionForm.grams),
        }),
      });

      if (!itemRes.ok) throw new Error("Could not add food to section");

      setMealForms((prev) => ({
        ...prev,
        [sectionName]: { food_id: "", grams: "" },
      }));

      await fetchMealsForDate(selectedDate);
      await fetchDailySummary(selectedDate);
      await fetchSuggestions(selectedDate);
      setStatusMessage(`${sectionName} updated successfully.`);
    } catch {
      setStatusMessage(`Could not update ${sectionName}.`);
    }
  }

  async function handleDeleteMealItem(itemId) {
    try {
      const res = await fetch(`${API}/meals/items/${itemId}`, {
        method: "DELETE",
        headers: getAuthHeaders(false),
      });

      if (!res.ok) throw new Error("Delete failed");

      await fetchMealsForDate(selectedDate);
      await fetchDailySummary(selectedDate);
      await fetchSuggestions(selectedDate);
      setStatusMessage("Logged food deleted successfully.");
    } catch {
      setStatusMessage("Could not delete logged food.");
    }
  }

  /*
  Update the grams for an already logged meal item, then refresh the diary,
  nutrition totals, and suggestions so the dashboard stays in sync.
*/
  async function handleEditMealItem(item) {
    const newGrams = window.prompt("Enter new grams:", item.grams);
    if (!newGrams) return;

    const parsedGrams = Number(newGrams);
    if (Number.isNaN(parsedGrams) || parsedGrams < 0) {
      setStatusMessage("Please enter a valid non-negative number of grams.");
      return;
    }

    try {
      const res = await fetch(`${API}/meals/items/${item.id}`, {
        method: "PATCH",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          food_id: item.food_id,
          grams: parsedGrams,
        }),
      });

      if (!res.ok) throw new Error("Edit failed");

      await fetchMealsForDate(selectedDate);
      await fetchDailySummary(selectedDate);
      await fetchSuggestions(selectedDate);
      setStatusMessage("Logged food updated successfully.");
    } catch {
      setStatusMessage("Could not update logged food.");
    }
  }


  useEffect(() => {
    fetchMe();
    fetchFoods();
    fetchMealsForDate(selectedDate);
    fetchDailySummary(selectedDate);
    fetchSuggestions(selectedDate);
  }, []);

  /*
  Memoize grouped diary data so each meal section can be rendered cleanly
  without recalculating the section mapping on every render.
*/
  const groupedSections = useMemo(() => {
    const result = {};
    for (const section of MEAL_SECTIONS) {
      result[section] = getSectionItems(section);
    }
    return result;
  }, [mealsForDate]);

  const progressValues = {
    calories: dailySummary?.total_calories ?? 0,
    protein: dailySummary?.total_protein ?? 0,
    carbs: dailySummary?.total_carbs ?? 0,
    fat: dailySummary?.total_fat ?? 0,
  };

  return (
    <div className="bg-light min-vh-100">
      <AppNavbar showAuthButtons={false} showUser email={me?.email || userEmail} />

      <div className="container py-5">
        {statusMessage && (
          <div className="alert alert-secondary" role="alert">
            {statusMessage}
          </div>
        )}

        <div className="mb-4">
          <h1 className="fw-bold">Dashboard</h1>
          <p className="text-muted mb-0">Track your daily nutrition progress</p>
        </div>

        <div className="card border-0 shadow-sm mb-4 fade-in-up">
          <div className="card-body p-4">
            <div className="d-flex justify-content-between align-items-center flex-wrap gap-3 mb-4">
              <div>
                <h2 className="h4 mb-1">Today's Progress</h2>
                <p className="text-muted mb-0">
                  Track your progress against your daily goals for {formatDisplayDate(selectedDate)}
                </p>
              </div>

              <div className="d-flex flex-wrap gap-2 align-items-center">
                <input
                  type="date"
                  className="form-control"
                  style={{ maxWidth: "220px" }}
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                />
                <button
                  className="btn btn-dark"
                  onClick={() => {
                    fetchMealsForDate(selectedDate);
                    fetchDailySummary(selectedDate);
                    fetchSuggestions(selectedDate);
                  }}
                >
                  Load Diary
                </button>
              </div>
            </div>

            <div className="row g-4">
              <div className="col-12 col-md-6 col-lg-3">
                <ProgressCircle
                  label="Calories"
                  value={progressValues.calories}
                  goal={me?.daily_calorie_goal}
                />
              </div>
              <div className="col-12 col-md-6 col-lg-3">
                <ProgressCircle
                  label="Protein"
                  value={progressValues.protein}
                  goal={me?.daily_protein_goal}
                />
              </div>
              <div className="col-12 col-md-6 col-lg-3">
                <ProgressCircle
                  label="Carbs"
                  value={progressValues.carbs}
                  goal={me?.daily_carbs_goal}
                />
              </div>
              <div className="col-12 col-md-6 col-lg-3">
                <ProgressCircle
                  label="Fat"
                  value={progressValues.fat}
                  goal={me?.daily_fat_goal}
                />
              </div>
            </div>
          </div>
        </div>

        <div className="card shadow-sm border-0 mb-4 fade-in-up">
          <div className="card-body">
            <h2 className="h5 mb-2">Smart Goal Gap Suggestions</h2>
            <p className="text-muted mb-2">
              Recommended foods based on what you still need today.
            </p>
            <p className="small text-muted mb-3">
              This feature moves the app beyond passive tracking by suggesting foods that best fit your remaining nutrition targets.
            </p>

            {suggestions.length === 0 ? (
              <p className="text-muted mb-0">
                No suggestions available yet. Add foods to your library and set your goals.
              </p>
            ) : (
              <div className="row g-3">
                {suggestions.map((food) => (
                  <div key={food.food_id} className="col-12 col-md-4">
                    <div className="card h-100 border-0 external-food-result-card">
                      <div className="card-body">
                      <h3 className="h6 mb-1">{formatFoodName(food.name)}</h3>
                        <div className="text-muted small mb-2">
                          {food.brand || "No brand"}
                        </div>
                        <div className="small mb-2">
                          {food.calories_per_100g} kcal · {food.protein_per_100g}g protein ·{" "}
                          {food.carbs_per_100g}g carbs · {food.fat_per_100g}g fat
                        </div>
                        <div className="goal-badge goal-neutral">
                          {food.reason}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {MEAL_SECTIONS.map((section) => (
          <div key={section} className="card border-0 shadow-sm mb-4 fade-in-up-delay-1">
            <div className="card-body">
              <h2 className="h5 mb-3">{section}</h2>

              {groupedSections[section].length === 0 ? (
                <p className="text-muted mb-3">
                  No foods logged for {section.toLowerCase()} yet.
                </p>
              ) : (
                <ul className="list-group mb-3">
                  {groupedSections[section].map((item) => (
                    <li
                      key={item.id}
                      className="list-group-item d-flex justify-content-between align-items-center flex-wrap gap-2"
                    >
                      <span>
                      {item.food?.name ? formatFoodName(item.food.name) : `Food ID ${item.food_id}`} — {item.grams}g
                      </span>
                      <div className="d-flex gap-2">
                        <button
                          className="btn btn-sm btn-outline-secondary"
                          onClick={() => handleEditMealItem(item)}
                        >
                          Edit
                        </button>
                        <button
                          className="btn btn-sm btn-outline-danger"
                          onClick={() => handleDeleteMealItem(item.id)}
                        >
                          Delete
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              )}

              <div className="row g-2">
                <div className="col-12 col-md-6">
                  <select
                    className="form-select"
                    value={mealForms[section].food_id}
                    onChange={(e) =>
                      setMealForms((prev) => ({
                        ...prev,
                        [section]: {
                          ...prev[section],
                          food_id: e.target.value,
                        },
                      }))
                    }
                  >
                    <option value="">Choose food from library</option>
                    {foods.map((food) => (
                      <option key={food.id} value={food.id}>
                        {formatFoodName(food.name)}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="col-12 col-md-3">
                  <input
                    type="number"
                    step="any"
                    min="0"
                    className="form-control"
                    placeholder="Grams"
                    value={mealForms[section].grams}
                    onChange={(e) =>
                      setMealForms((prev) => ({
                        ...prev,
                        [section]: {
                          ...prev[section],
                          grams: e.target.value,
                        },
                      }))
                    }
                  />
                </div>

                <div className="col-12 col-md-3">
                  <button
                    type="button"
                    className="btn btn-dark w-100"
                    onClick={() => handleAddFoodToSection(section)}
                  >
                    Add to {section}
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DashboardPage;