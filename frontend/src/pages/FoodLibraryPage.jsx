import { useEffect, useState } from "react";
import AppNavbar from "../components/AppNavbar";

const API = "http://127.0.0.1:8000";


function FoodLibraryPage() {
  const token = localStorage.getItem("token") || "";
  const userEmail = localStorage.getItem("user_email") || "";

  const [me, setMe] = useState(null);
  const [foods, setFoods] = useState([]);
  const [query, setQuery] = useState("");
  const [externalFoods, setExternalFoods] = useState([]);
  const [externalLoading, setExternalLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");

  const [maxCalories, setMaxCalories] = useState("");
  const [minProtein, setMinProtein] = useState("");

  const [foodForm, setFoodForm] = useState({
    name: "",
    brand: "",
    calories_per_100g: "",
    protein_per_100g: "",
    carbs_per_100g: "",
    fat_per_100g: "",
    source: "manual",
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
    if (token) headers.Authorization = `Bearer ${token}`;
    if (json) headers["Content-Type"] = "application/json";
    return headers;
  }

  function formatFoodName(name) {
    if (!name) return "Unknown food";
  
    return name
      .toLowerCase()
      .replace(/\b\w/g, (char) => char.toUpperCase());
  }

  async function fetchMe() {
    try {
      const res = await fetch(`${API}/auth/me`, {
        headers: getAuthHeaders(false),
      });
      const data = await res.json();
      if (res.ok) setMe(data);
    } catch {}
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
      setStatusMessage("Could not load food library.");
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

      const data = await res.json().catch(() => null);

      if (!res.ok) {
        throw new Error(data?.detail ? JSON.stringify(data.detail) : "Create food failed");
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

  async function handleDeleteFood(foodId) {
    const confirmed = window.confirm("Delete this food from the Food Library?");
    if (!confirmed) return;

    try {
      const res = await fetch(`${API}/foods/${foodId}`, {
        method: "DELETE",
        headers: getAuthHeaders(false),
      });

      const data = await res.json().catch(() => null);

      if (!res.ok) {
        throw new Error(data?.detail ? JSON.stringify(data.detail) : "Delete failed");
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

      const data = await res.json().catch(() => null);

      if (!res.ok) {
        throw new Error(data?.detail ? JSON.stringify(data.detail) : "Update failed");
      }

      await fetchFoods();
      cancelEditingFood();
      setStatusMessage("Food updated successfully.");
    } catch (error) {
      setStatusMessage(`Could not update food: ${error.message}`);
    }
  }

  async function searchExternal(customQuery = null) {
    const finalQuery = (customQuery ?? query).trim();

    if (!finalQuery) {
      setStatusMessage("Enter a search term first.");
      return;
    }

    setExternalLoading(true);
    setStatusMessage("");

    try {
      const params = new URLSearchParams();
      params.append("query", finalQuery);

      if (maxCalories !== "") {
        params.append("max_calories", maxCalories);
      }

      if (minProtein !== "") {
        params.append("min_protein", minProtein);
      }

      const res = await fetch(`${API}/external/usda/search?${params.toString()}`, {
        headers: getAuthHeaders(false),
      });

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
      const res = await fetch(`${API}/external/usda/import`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          external_id: externalId,
        }),
      });

      const data = await res.json().catch(() => null);

      if (!res.ok) {
        throw new Error(data?.detail || "Import failed");
      }

      await fetchFoods();
      setStatusMessage("Food imported successfully.");
    } catch (error) {
      setStatusMessage(`Could not import food: ${error.message}`);
    }
  }

  useEffect(() => {
    fetchMe();
    fetchFoods();
  }, []);

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
          <h1 className="fw-bold">Food Library</h1>
          <p className="text-muted mb-0">
            Create, import, edit, and manage your foods
          </p>
        </div>

        <div className="card border-0 shadow-sm mb-4 fade-in-up">
          <div className="card-body p-4">
            <div className="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
              <div>
                <h2 className="h4 mb-1">Search External Foods</h2>
            <div>
              <p className="text-muted mb-1">
                Search USDA foods and refine results with optional filters
              </p>
              <p className="small text-muted mb-0">
                All calories and macros shown are based on 100g values.
              </p>
            </div>
              </div>
            </div>

            <div className="row g-3 mb-3">
              <div className="col-12 col-lg-12 mt-2">
                <input
                  className="form-control"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search USDA foods"
                />
              </div>

              <div className="col-12 col-md-6 col-lg-3">
                <input
                  type="number"
                  className="form-control"
                  placeholder="Max calories (per 100g)"
                  value={maxCalories}
                  min="0"
                  onChange={(e) => setMaxCalories(e.target.value)}
                />
              </div>

              <div className="col-12 col-md-6 col-lg-3">
                <input
                  type="number"
                  className="form-control"
                  placeholder="Min protein (per 100g)"
                  min="0"
                  value={minProtein}
                  onChange={(e) => setMinProtein(e.target.value)}
                />
              </div>

              <div className="col-12 col-lg-2">
                <button
                  className="btn btn-dark w-100"
                  onClick={() => searchExternal()}
                  disabled={externalLoading}
                >
                  {externalLoading ? "Searching..." : "Search"}
                </button>
              </div>
            </div>

            {externalLoading ? (
              <div className="search-loading-box text-center">
                <div className="spinner-border text-dark" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
                <div className="spinner-text">Searching external foods...</div>
              </div>
            ) : externalFoods.length > 0 ? (
              <div className="d-grid gap-3 fade-in-up">
                {externalFoods.map((food) => (
                  <div
                    key={food.external_id}
                    className="card border-0 shadow-sm external-food-result-card"
                  >
                    <div className="card-body d-flex justify-content-between align-items-center flex-wrap gap-3">
                      <div>
                        <div className="fw-bold fs-5">{formatFoodName(food.name)}</div>
                        <div className="text-muted mb-2">
                          {food.brand || "No brand"}
                        </div>
                        <div className="small">
                          {food.calories_per_100g ?? "N/A"} kcal ·{" "}
                          {food.protein_per_100g ?? "N/A"}g protein ·{" "}
                          {food.carbs_per_100g ?? "N/A"}g carbs ·{" "}
                          {food.fat_per_100g ?? "N/A"}g fat
                        </div>
                      </div>

                      <button
                        className="btn btn-outline-dark"
                        onClick={() => importExternalFood(food.external_id)}
                      >
                        Import
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : null}
          </div>
        </div>

        <div className="row g-4">
          <div className="col-12 col-lg-5">
            <div className="card border-0 shadow-sm mb-4 fade-in-up-delay-1">
              <div className="card-body">
                <h2 className="h5 mb-3">Add Custom Food</h2>
                <form onSubmit={handleCreateFood} className="d-grid gap-2">
                  <input
                    className="form-control"
                    placeholder="Food name"
                    value={foodForm.name}
                    onChange={(e) => setFoodForm({ ...foodForm, name: e.target.value })}
                    required
                  />
                  <input
                    className="form-control"
                    placeholder="Brand"
                    value={foodForm.brand}
                    onChange={(e) => setFoodForm({ ...foodForm, brand: e.target.value })}
                  />
                  <input
                    className="form-control"
                    type="number"
                    step="any"
                    min="0"
                    placeholder="Calories per 100g"
                    value={foodForm.calories_per_100g}
                    onChange={(e) =>
                      setFoodForm({ ...foodForm, calories_per_100g: e.target.value })
                    }
                    required
                  />
                  <input
                    className="form-control"
                    type="number"
                    step="any"
                    placeholder="Protein per 100g"
                    min="0"
                    value={foodForm.protein_per_100g}
                    onChange={(e) =>
                      setFoodForm({ ...foodForm, protein_per_100g: e.target.value })
                    }
                    required
                  />
                  <input
                    className="form-control"
                    type="number"
                    step="any"
                    placeholder="Carbs per 100g"
                    min="0"
                    value={foodForm.carbs_per_100g}
                    onChange={(e) =>
                      setFoodForm({ ...foodForm, carbs_per_100g: e.target.value })
                    }
                    required
                  />
                  <input
                    className="form-control"
                    type="number"
                    step="any"
                    placeholder="Fat per 100g"
                    min="0"
                    value={foodForm.fat_per_100g}
                    onChange={(e) =>
                      setFoodForm({ ...foodForm, fat_per_100g: e.target.value })
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

          <div className="col-12 col-lg-7">
            <div className="card border-0 shadow-sm fade-in-up-delay-2">
              <div className="card-body">
                <div className="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
                  <h2 className="h5 mb-0">Your Foods</h2>
                  <button className="btn btn-outline-dark btn-sm" onClick={fetchFoods}>
                    Refresh Food Library
                  </button>
                </div>

                {foods.length === 0 ? (
                  <div className="empty-state">No foods available yet.</div>
                ) : (
                  <ul className="list-group">
                    {[...foods]
                      .sort((a, b) => a.name.localeCompare(b.name))
                      .map((food) => (
                        <li key={food.id} className="list-group-item">
                          <div className="d-flex justify-content-between align-items-start flex-wrap gap-2">
                            <div>
                              <strong>{formatFoodName(food.name)}</strong> — {food.brand || "No brand"} —{" "}
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
          </div>
        </div>
      </div>
    </div>
  );
}

export default FoodLibraryPage;