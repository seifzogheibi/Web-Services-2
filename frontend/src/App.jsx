import { useEffect, useMemo, useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";

const API = "http://127.0.0.1:8000";
const MEAL_SECTIONS = ["Breakfast", "Lunch", "Dinner", "Snack"];

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [me, setMe] = useState(null);

  const [authMode, setAuthMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [foods, setFoods] = useState([]);
  const [query, setQuery] = useState("");
  const [externalFoods, setExternalFoods] = useState([]);
  const [selectedDate, setSelectedDate] = useState(
    new Date().toISOString().slice(0, 10)
  );
  const [dailySummary, setDailySummary] = useState(null);
  const [statusMessage, setStatusMessage] = useState("");
  const [mealsForDate, setMealsForDate] = useState([]);
  const [externalLoading, setExternalLoading] = useState(false);

  const [foodForm, setFoodForm] = useState({
    name: "",
    brand: "",
    calories_per_100g: "",
    protein_per_100g: "",
    carbs_per_100g: "",
    fat_per_100g: "",
    source: "manual",
  });

  const [mealForms, setMealForms] = useState({
    Breakfast: { food_id: "", grams: "" },
    Lunch: { food_id: "", grams: "" },
    Dinner: { food_id: "", grams: "" },
    Snack: { food_id: "", grams: "" },
  });

  const [editingFoodId, setEditingFoodId] = useState(null);
  const [editFoodForm, setEditFoodForm] = useState({
    name: "",
    brand: "",
    calories_per_100g: "",
    protein_per_100g: "",
    carbs_per_100g: "",
    fat_per_100g: "",
  });

  function getAuthHeaders(json = true) {
    const headers = {};
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    if (json) {
      headers["Content-Type"] = "application/json";
    }
    return headers;
  }

  function formatDisplayDate(dateString) {
    const [year, month, day] = dateString.split("-");
    return `${day}-${month}-${year}`;
  }

  function normalizeMealName(name) {
    const value = name.trim().toLowerCase();

    if (value === "breakfast") return "Breakfast";
    if (value === "lunch") return "Lunch";
    if (value === "dinner") return "Dinner";
    if (value === "snack" || value === "snacks") return "Snack";

    return null;
  }

  function getSectionItems(sectionName) {
    return mealsForDate
      .filter((meal) => normalizeMealName(meal.name) === sectionName)
      .flatMap((meal) => meal.items || []);
  }

  async function fetchMe(authToken = token) {
    if (!authToken) return;

    try {
      const res = await fetch(`${API}/auth/me`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      if (!res.ok) {
        localStorage.removeItem("token");
        setToken("");
        setMe(null);
        return;
      }

      const data = await res.json();
      setMe(data);
    } catch (error) {
      localStorage.removeItem("token");
      setToken("");
      setMe(null);
    }
  }

  async function handleRegister(e) {
    e.preventDefault();
    setStatusMessage("");

    try {
      const res = await fetch(`${API}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setStatusMessage(data.detail || "Registration failed.");
        return;
      }

      setStatusMessage("Registration successful. Please sign in.");
      setAuthMode("login");
      setPassword("");
    } catch (error) {
      setStatusMessage("Could not register.");
    }
  }

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
      setToken(data.access_token);
      setStatusMessage("Signed in successfully.");
      setPassword("");
    } catch (error) {
      setStatusMessage("Could not sign in.");
    }
  }

  function handleLogout() {
    localStorage.removeItem("token");
    setToken("");
    setMe(null);
    setFoods([]);
    setExternalFoods([]);
    setMealsForDate([]);
    setDailySummary(null);
    setStatusMessage("Signed out.");
    setEditingFoodId(null);
  }

  async function fetchFoods() {
    try {
      const res = await fetch(`${API}/foods/`, {
        headers: getAuthHeaders(false),
      });
      if (!res.ok) throw new Error("Failed to load foods");
      const data = await res.json();
      setFoods(data);
      setStatusMessage("Food library loaded.");
    } catch (error) {
      setStatusMessage("Could not load food library.");
    }
  }

  async function searchExternal() {
    if (!query.trim()) {
      setStatusMessage("Enter a search term first.");
      return;
    }
  
    setExternalLoading(true);
    setStatusMessage("");
  
    try {
      const res = await fetch(
        `${API}/external/openfoodfacts/search?query=${encodeURIComponent(query)}`,
        {
          headers: getAuthHeaders(false),
        }
      );
  
      const data = await res.json().catch(() => null);
  
      if (!res.ok) {
        setExternalFoods([]);
        throw new Error(data?.detail || "Search failed");
      }
  
      setExternalFoods(data);
      setStatusMessage(`Loaded ${data.length} external foods.`);
    } catch (error) {
      setExternalFoods([]);
      setStatusMessage(`Could not search external foods: ${error.message}`);
    } finally {
      setExternalLoading(false);
    }
  }

  async function importExternalFood(externalId) {
    try {
      const res = await fetch(`${API}/external/openfoodfacts/import`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          barcode: externalId,
        }),
      });

      if (!res.ok) {
        throw new Error("Import failed");
      }

      await fetchFoods();
      setStatusMessage("Food imported successfully.");
    } catch (error) {
      setStatusMessage("Could not import food.");
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
      setStatusMessage("Food diary loaded.");
    } catch (error) {
      setStatusMessage("Could not load food diary.");
    }
  }

  async function fetchDailySummary(date = selectedDate) {
    try {
      const res = await fetch(`${API}/analytics/daily?date=${date}`, {
        headers: getAuthHeaders(false),
      });
      if (!res.ok) throw new Error("Summary failed");
      const data = await res.json();
      setDailySummary(data);
    } catch (error) {
      setStatusMessage("Could not load nutrition summary.");
    }
  }

  async function handleCreateFood(e) {
    e.preventDefault();

    try {
      const res = await fetch(`${API}/foods/`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          ...foodForm,
          calories_per_100g: Number(foodForm.calories_per_100g),
          protein_per_100g: Number(foodForm.protein_per_100g),
          carbs_per_100g: Number(foodForm.carbs_per_100g),
          fat_per_100g: Number(foodForm.fat_per_100g),
        }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => null);
        throw new Error(
          errorData?.detail
            ? JSON.stringify(errorData.detail)
            : "Create food failed"
        );
      }

      setFoodForm({
        name: "",
        brand: "",
        calories_per_100g: "",
        protein_per_100g: "",
        carbs_per_100g: "",
        fat_per_100g: "",
        source: "manual",
      });

      await fetchFoods();
      setStatusMessage("Custom food added successfully.");
    } catch (error) {
      setStatusMessage(`Could not add custom food: ${error.message}`);
    }
  }

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
      setStatusMessage(`${sectionName} updated successfully.`);
    } catch (error) {
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
      setStatusMessage("Logged food deleted successfully.");
    } catch (error) {
      setStatusMessage("Could not delete logged food.");
    }
  }

  async function handleEditMealItem(item) {
    const newGrams = window.prompt("Enter new grams:", item.grams);

    if (!newGrams) return;

    try {
      const res = await fetch(`${API}/meals/items/${item.id}`, {
        method: "PATCH",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          food_id: item.food_id,
          grams: Number(newGrams),
        }),
      });

      if (!res.ok) throw new Error("Edit failed");

      await fetchMealsForDate(selectedDate);
      await fetchDailySummary(selectedDate);
      setStatusMessage("Logged food updated successfully.");
    } catch (error) {
      setStatusMessage("Could not update logged food.");
    }
  }

  async function handleDeleteFood(foodId) {
    const confirmed = window.confirm("Delete this food from the Food Library?");
    if (!confirmed) return;

    try {
      const res = await fetch(`${API}/foods/${foodId}`, {
        method: "DELETE",
        headers: getAuthHeaders(false),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => null);
        throw new Error(
          errorData?.detail
            ? JSON.stringify(errorData.detail)
            : "Delete failed"
        );
      }

      await fetchFoods();
      setStatusMessage("Food deleted successfully.");
    } catch (error) {
      setStatusMessage(`Could not delete food: ${error.message}`);
    }
  }

  function startEditingFood(food) {
    setEditingFoodId(food.id);
    setEditFoodForm({
      name: food.name || "",
      brand: food.brand || "",
      calories_per_100g: food.calories_per_100g ?? "",
      protein_per_100g: food.protein_per_100g ?? "",
      carbs_per_100g: food.carbs_per_100g ?? "",
      fat_per_100g: food.fat_per_100g ?? "",
    });
  }

  function cancelEditingFood() {
    setEditingFoodId(null);
    setEditFoodForm({
      name: "",
      brand: "",
      calories_per_100g: "",
      protein_per_100g: "",
      carbs_per_100g: "",
      fat_per_100g: "",
    });
  }

  async function saveEditedFood(foodId) {
    try {
      const res = await fetch(`${API}/foods/${foodId}`, {
        method: "PATCH",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          name: editFoodForm.name,
          brand: editFoodForm.brand,
          calories_per_100g: Number(editFoodForm.calories_per_100g),
          protein_per_100g: Number(editFoodForm.protein_per_100g),
          carbs_per_100g: Number(editFoodForm.carbs_per_100g),
          fat_per_100g: Number(editFoodForm.fat_per_100g),
        }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => null);
        throw new Error(
          errorData?.detail
            ? JSON.stringify(errorData.detail)
            : "Update failed"
        );
      }

      await fetchFoods();
      cancelEditingFood();
      setStatusMessage("Food updated successfully.");
    } catch (error) {
      setStatusMessage(`Could not update food: ${error.message}`);
    }
  }

  useEffect(() => {
    if (token) {
      fetchMe(token);
    }
  }, [token]);

  useEffect(() => {
    if (!token) return;
    fetchFoods();
    fetchMealsForDate(selectedDate);
    fetchDailySummary(selectedDate);
  }, [token]);

  const groupedSections = useMemo(() => {
    const result = {};
    for (const section of MEAL_SECTIONS) {
      result[section] = getSectionItems(section);
    }
    return result;
  }, [mealsForDate]);

  if (!token) {
    return (
      <div className="min-vh-100 d-flex align-items-center bg-light">
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-12 col-md-8 col-lg-5">
              <div className="card shadow-sm border-0">
                <div className="card-body p-4 p-md-5">
                  <div className="text-center mb-4">
                    <h1 className="h2 fw-bold mb-2">Nutrition Tracker</h1>
                    <p className="text-muted mb-0">
                      {authMode === "login"
                        ? "Sign in to access your food diary"
                        : "Create an account to start tracking"}
                    </p>
                  </div>

                  <form onSubmit={authMode === "login" ? handleLogin : handleRegister}>
                    <div className="mb-3">
                      <label className="form-label">Email</label>
                      <input
                        type="email"
                        className="form-control"
                        placeholder="Enter your email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                      />
                    </div>

                    <div className="mb-3">
                      <label className="form-label">Password</label>
                      <input
                        type="password"
                        className="form-control"
                        placeholder="Enter your password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                      />
                    </div>

                    <button type="submit" className="btn btn-dark w-100">
                      {authMode === "login" ? "Sign In" : "Create Account"}
                    </button>
                  </form>

                  <button
                    className="btn btn-outline-secondary w-100 mt-3"
                    onClick={() =>
                      setAuthMode(authMode === "login" ? "register" : "login")
                    }
                  >
                    {authMode === "login"
                      ? "Need an account? Sign Up"
                      : "Already have an account? Sign In"}
                  </button>

                  {statusMessage && (
                    <div className="alert alert-secondary mt-3 mb-0" role="alert">
                      {statusMessage}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-light min-vh-100">
      <nav className="navbar navbar-expand-lg bg-white border-bottom">
        <div className="container">
          <span className="navbar-brand fw-bold">Nutrition Tracker</span>
          <div className="d-flex align-items-center gap-3">
            <span className="text-muted small">
              Signed in as: {me?.email || "Loading..."}
            </span>
            <button className="btn btn-outline-dark btn-sm" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="container py-4">
        {statusMessage && (
          <div className="alert alert-secondary" role="alert">
            {statusMessage}
          </div>
        )}

        <div className="card shadow-sm border-0 mb-4">
          <div className="card-body">
            <h1 className="h3 mb-3">Food Diary for: {formatDisplayDate(selectedDate)}</h1>
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
                }}
              >
                Load Diary
              </button>
            </div>
          </div>
        </div>

        <div className="row g-4">
          <div className="col-12 col-lg-8">
            {MEAL_SECTIONS.map((section) => (
              <div key={section} className="card shadow-sm border-0 mb-4">
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
                            {item.food?.name || `Food ID ${item.food_id}`} — {item.grams}g
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
                            {food.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="col-12 col-md-3">
                      <input
                        type="number"
                        step="any"
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

          <div className="col-12 col-lg-4">
            <div className="card shadow-sm border-0 mb-4">
              <div className="card-body">
                <h2 className="h5 mb-3">Nutrition Summary</h2>
                {dailySummary ? (
                  <div className="d-grid gap-2">
                    <div className="d-flex justify-content-between">
                      <strong>Calories</strong>
                      <span>{dailySummary.total_calories}</span>
                    </div>
                    <div className="d-flex justify-content-between">
                      <strong>Protein</strong>
                      <span>{dailySummary.total_protein}</span>
                    </div>
                    <div className="d-flex justify-content-between">
                      <strong>Carbs</strong>
                      <span>{dailySummary.total_carbs}</span>
                    </div>
                    <div className="d-flex justify-content-between">
                      <strong>Fat</strong>
                      <span>{dailySummary.total_fat}</span>
                    </div>
                  </div>
                ) : (
                  <p className="text-muted mb-0">No nutrition summary loaded yet.</p>
                )}
              </div>
            </div>

            <div className="card shadow-sm border-0 mb-4">
              <div className="card-body">
                <h2 className="h5 mb-3">Add Custom Food</h2>
                <form onSubmit={handleCreateFood} className="d-grid gap-2">
                  <input
                    className="form-control"
                    placeholder="Food name"
                    value={foodForm.name}
                    onChange={(e) =>
                      setFoodForm({ ...foodForm, name: e.target.value })
                    }
                    required
                  />
                  <input
                    className="form-control"
                    placeholder="Brand"
                    value={foodForm.brand}
                    onChange={(e) =>
                      setFoodForm({ ...foodForm, brand: e.target.value })
                    }
                  />
                  <input
                    className="form-control"
                    type="number"
                    step="any"
                    placeholder="Calories per 100g"
                    value={foodForm.calories_per_100g}
                    onChange={(e) =>
                      setFoodForm({
                        ...foodForm,
                        calories_per_100g: e.target.value,
                      })
                    }
                    required
                  />
                  <input
                    className="form-control"
                    type="number"
                    step="any"
                    placeholder="Protein per 100g"
                    value={foodForm.protein_per_100g}
                    onChange={(e) =>
                      setFoodForm({
                        ...foodForm,
                        protein_per_100g: e.target.value,
                      })
                    }
                    required
                  />
                  <input
                    className="form-control"
                    type="number"
                    step="any"
                    placeholder="Carbs per 100g"
                    value={foodForm.carbs_per_100g}
                    onChange={(e) =>
                      setFoodForm({
                        ...foodForm,
                        carbs_per_100g: e.target.value,
                      })
                    }
                    required
                  />
                  <input
                    className="form-control"
                    type="number"
                    step="any"
                    placeholder="Fat per 100g"
                    value={foodForm.fat_per_100g}
                    onChange={(e) =>
                      setFoodForm({
                        ...foodForm,
                        fat_per_100g: e.target.value,
                      })
                    }
                    required
                  />
                  <button type="submit" className="btn btn-dark">
                    Add Custom Food
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>

        <div className="card shadow-sm border-0 mb-4">
          <div className="card-body">
            <div className="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
              <h2 className="h5 mb-0">Food Library</h2>
              <button className="btn btn-outline-dark btn-sm" onClick={fetchFoods}>
                Refresh Food Library
              </button>
            </div>

            {foods.length === 0 ? (
              <p className="text-muted mb-0">No foods available yet.</p>
            ) : (
              <ul className="list-group">
                {[...foods]
                  .sort((a, b) => a.name.localeCompare(b.name))
                  .map((food) => (
                    <li key={food.id} className="list-group-item">
                      <div className="d-flex justify-content-between align-items-start flex-wrap gap-2">
                        <div>
                          <strong>{food.name}</strong> — {food.brand || "No brand"} —{" "}
                          {food.calories_per_100g} kcal ({food.source})
                        </div>
                        <div className="d-flex gap-2">
                          <button
                            className="btn btn-sm btn-outline-secondary"
                            onClick={() => startEditingFood(food)}
                          >
                            Edit
                          </button>
                          <button
                            className="btn btn-sm btn-outline-danger"
                            onClick={() => handleDeleteFood(food.id)}
                          >
                            Delete
                          </button>
                        </div>
                      </div>

                      {editingFoodId === food.id && (
                        <div className="mt-3 p-3 border rounded">
                          <div className="row g-2">
                            <div className="col-12 col-md-6">
                              <input
                                className="form-control"
                                placeholder="Food name"
                                value={editFoodForm.name}
                                onChange={(e) =>
                                  setEditFoodForm({
                                    ...editFoodForm,
                                    name: e.target.value,
                                  })
                                }
                              />
                            </div>
                            <div className="col-12 col-md-6">
                              <input
                                className="form-control"
                                placeholder="Brand"
                                value={editFoodForm.brand}
                                onChange={(e) =>
                                  setEditFoodForm({
                                    ...editFoodForm,
                                    brand: e.target.value,
                                  })
                                }
                              />
                            </div>
                            <div className="col-12 col-md-3">
                              <input
                                className="form-control"
                                type="number"
                                step="any"
                                placeholder="Calories"
                                value={editFoodForm.calories_per_100g}
                                onChange={(e) =>
                                  setEditFoodForm({
                                    ...editFoodForm,
                                    calories_per_100g: e.target.value,
                                  })
                                }
                              />
                            </div>
                            <div className="col-12 col-md-3">
                              <input
                                className="form-control"
                                type="number"
                                step="any"
                                placeholder="Protein"
                                value={editFoodForm.protein_per_100g}
                                onChange={(e) =>
                                  setEditFoodForm({
                                    ...editFoodForm,
                                    protein_per_100g: e.target.value,
                                  })
                                }
                              />
                            </div>
                            <div className="col-12 col-md-3">
                              <input
                                className="form-control"
                                type="number"
                                step="any"
                                placeholder="Carbs"
                                value={editFoodForm.carbs_per_100g}
                                onChange={(e) =>
                                  setEditFoodForm({
                                    ...editFoodForm,
                                    carbs_per_100g: e.target.value,
                                  })
                                }
                              />
                            </div>
                            <div className="col-12 col-md-3">
                              <input
                                className="form-control"
                                type="number"
                                step="any"
                                placeholder="Fat"
                                value={editFoodForm.fat_per_100g}
                                onChange={(e) =>
                                  setEditFoodForm({
                                    ...editFoodForm,
                                    fat_per_100g: e.target.value,
                                  })
                                }
                              />
                            </div>
                          </div>

                          <div className="d-flex gap-2 mt-3">
                            <button
                              className="btn btn-dark btn-sm"
                              type="button"
                              onClick={() => saveEditedFood(food.id)}
                            >
                              Save
                            </button>
                            <button
                              className="btn btn-outline-secondary btn-sm"
                              type="button"
                              onClick={cancelEditingFood}
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      )}
                    </li>
                  ))}
              </ul>
            )}
          </div>
        </div>

        <div className="card shadow-sm border-0">
          <div className="card-body">
            <h2 className="h5 mb-3">Search External Foods</h2>
            <div className="row g-2 mb-3">
              <div className="col-12 col-md-8">
                <input
                  className="form-control"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search external foods"
                />
              </div>
              <div className="col-12 col-md-4">
              <button className="btn btn-dark w-100" onClick={searchExternal} disabled={externalLoading}>
                {externalLoading ? "Searching..." : "Search External Foods"}
              </button>
              </div>
            </div>

            {externalFoods.length > 0 && (
              <ul className="list-group">
                {externalFoods.map((food) => (
                  <li
                    key={food.external_id}
                    className="list-group-item d-flex justify-content-between align-items-center flex-wrap gap-2"
                  >
                    <span>
                      {food.name} — {food.brand} —{" "}
                      {food.calories_per_100g ?? "N/A"} kcal
                    </span>
                    <button
                      className="btn btn-outline-dark btn-sm"
                      onClick={() => importExternalFood(food.external_id)}
                    >
                      Import
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;