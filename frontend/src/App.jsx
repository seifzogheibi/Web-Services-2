import { useEffect, useMemo, useState } from "react";

const API = "http://127.0.0.1:8000";
const MEAL_SECTIONS = ["Breakfast", "Lunch", "Dinner", "Snack"];

function App() {
  const [foods, setFoods] = useState([]);
  const [query, setQuery] = useState("");
  const [externalFoods, setExternalFoods] = useState([]);
  const [selectedDate, setSelectedDate] = useState(
    new Date().toISOString().slice(0, 10)
  );
  const [dailySummary, setDailySummary] = useState(null);
  const [statusMessage, setStatusMessage] = useState("");
  const [mealsForDate, setMealsForDate] = useState([]);

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

  async function fetchFoods() {
    try {
      const res = await fetch(`${API}/foods/`);
      if (!res.ok) throw new Error("Failed to load foods");
      const data = await res.json();
      setFoods(data);
      setStatusMessage("Food library loaded.");
    } catch (error) {
      setStatusMessage("Could not load food library.");
    }
  }

  async function searchExternal() {
    try {
      const res = await fetch(
        `${API}/external/openfoodfacts/search?query=${encodeURIComponent(query)}`
      );
      if (!res.ok) throw new Error("Search failed");
      const data = await res.json();
      setExternalFoods(data);
      setStatusMessage("External foods loaded.");
    } catch (error) {
      setStatusMessage("Could not search external foods.");
    }
  }

  async function importExternalFood(barcode) {
    try {
      const res = await fetch(`${API}/external/openfoodfacts/import`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ barcode }),
      });

      if (!res.ok) throw new Error("Import failed");

      await fetchFoods();
      setStatusMessage("Food imported into your Food Library.");
    } catch (error) {
      setStatusMessage("Could not import external food.");
    }
  }

  async function fetchMealsForDate(date = selectedDate) {
    try {
      const res = await fetch(`${API}/meals/by-date?date=${date}`);
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
      const res = await fetch(`${API}/analytics/daily?date=${date}`);
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
        headers: {
          "Content-Type": "application/json",
        },
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
          headers: {
            "Content-Type": "application/json",
          },
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
        headers: {
          "Content-Type": "application/json",
        },
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
        headers: {
          "Content-Type": "application/json",
        },
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

  async function importExternalFood(externalId) {
    try {
      const res = await fetch(`${API}/external/openfoodfacts/import`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          barcode: externalId,
        }),
      });
  
      if (!res.ok) {
        throw new Error("Import failed");
      }
  
      setStatusMessage("Food imported successfully.");
  
      // refresh food library so the new food appears
      fetchFoods();
    } catch (error) {
      setStatusMessage("Could not import food.");
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
        headers: {
          "Content-Type": "application/json",
        },
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

  useEffect(() => {
    fetchFoods();
    fetchMealsForDate(selectedDate);
    fetchDailySummary(selectedDate);
  }, []);

  const groupedSections = useMemo(() => {
    const result = {};
    for (const section of MEAL_SECTIONS) {
      result[section] = getSectionItems(section);
    }
    return result;
  }, [mealsForDate]);

  return (
    <div
      style={{
        padding: "40px",
        fontFamily: "Arial",
        maxWidth: "1100px",
        margin: "0 auto",
      }}
    >
      <h1>Food Diary for: {selectedDate}</h1>
      <p>{statusMessage}</p>

      <div style={{ marginBottom: "24px" }}>
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
        />
        <button
          onClick={() => {
            fetchMealsForDate(selectedDate);
            fetchDailySummary(selectedDate);
          }}
          style={{ marginLeft: "8px" }}
        >
          Load Diary
        </button>
      </div>

      <hr />

      {MEAL_SECTIONS.map((section) => (
        <div key={section} style={{ marginTop: "24px", marginBottom: "24px" }}>
          <h2>{section}</h2>

          {groupedSections[section].length === 0 ? (
            <p>No foods logged for {section.toLowerCase()} yet.</p>
          ) : (
            <ul>
              {groupedSections[section].map((item) => (
              <li key={item.id} style={{ marginBottom: "8px" }}>
                {item.food?.name || `Food ID ${item.food_id}`} — {item.grams}g
                <button
                  style={{ marginLeft: "8px" }}
                  onClick={() => handleEditMealItem(item)}
                >
                  Edit
                </button>
                <button
                  style={{ marginLeft: "8px" }}
                  onClick={() => handleDeleteMealItem(item.id)}
                >
                  Delete
                </button>
              </li>
            ))}
            </ul>
          )}

          <div style={{ display: "grid", gap: "8px", maxWidth: "500px", marginTop: "12px" }}>
            <select
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

            <input
              type="number"
              step="any"
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

            <button type="button" onClick={() => handleAddFoodToSection(section)}>
              Add to {section}
            </button>
          </div>
        </div>
      ))}

      <hr />

      <h2>Nutrition Summary for: {selectedDate}</h2>
      {dailySummary ? (
        <div style={{ marginBottom: "24px" }}>
          <p>
            <strong>Calories:</strong> {dailySummary.total_calories}
          </p>
          <p>
            <strong>Protein:</strong> {dailySummary.total_protein}
          </p>
          <p>
            <strong>Carbs:</strong> {dailySummary.total_carbs}
          </p>
          <p>
            <strong>Fat:</strong> {dailySummary.total_fat}
          </p>
        </div>
      ) : (
        <p>No nutrition summary loaded yet.</p>
      )}

      <hr />

      <h2>Add Custom Food</h2>
      <form
        onSubmit={handleCreateFood}
        style={{ display: "grid", gap: "8px", marginBottom: "24px", maxWidth: "600px" }}
      >
        <input
          placeholder="Food name"
          value={foodForm.name}
          onChange={(e) => setFoodForm({ ...foodForm, name: e.target.value })}
        />
        <input
          placeholder="Brand"
          value={foodForm.brand}
          onChange={(e) => setFoodForm({ ...foodForm, brand: e.target.value })}
        />
        <input
          type="number"
          step="any"
          placeholder="Calories per 100g"
          value={foodForm.calories_per_100g}
          onChange={(e) =>
            setFoodForm({ ...foodForm, calories_per_100g: e.target.value })
          }
        />
        <input
          type="number"
          step="any"
          placeholder="Protein per 100g"
          value={foodForm.protein_per_100g}
          onChange={(e) =>
            setFoodForm({ ...foodForm, protein_per_100g: e.target.value })
          }
        />
        <input
          type="number"
          step="any"
          placeholder="Carbs per 100g"
          value={foodForm.carbs_per_100g}
          onChange={(e) =>
            setFoodForm({ ...foodForm, carbs_per_100g: e.target.value })
          }
        />
        <input
          type="number"
          step="any"
          placeholder="Fat per 100g"
          value={foodForm.fat_per_100g}
          onChange={(e) =>
            setFoodForm({ ...foodForm, fat_per_100g: e.target.value })
          }
        />
        <button type="submit">Add Custom Food</button>
      </form>
    <hr />
      
    <h2>Food Library</h2>
      <button onClick={fetchFoods}>Refresh Food Library</button>
      <ul style={{ marginTop: "12px", marginBottom: "24px" }}>
      {foods.length === 0 ? (
          <li>No foods available yet.</li>
        ) : (
          [...foods]
            .sort((a, b) => a.name.localeCompare(b.name))
            .map((food) => (
            <li key={food.id} style={{ marginBottom: "16px" }}>
              <div>
                {food.name} — {food.brand || "No brand"} — {food.calories_per_100g} kcal - ({food.source})
                <button
                  style={{ marginLeft: "8px" }}
                  onClick={() => startEditingFood(food)}
                >
                  Edit
                </button>
                <button
                  style={{ marginLeft: "8px" }}
                  onClick={() => handleDeleteFood(food.id)}
                >
                  Delete
                </button>
              </div>

              {editingFoodId === food.id && (
                <div
                  style={{
                    marginTop: "10px",
                    padding: "12px",
                    border: "1px solid #666",
                    borderRadius: "8px",
                    display: "grid",
                    gap: "8px",
                    maxWidth: "500px",
                  }}
                >
                  <input
                    placeholder="Food name"
                    value={editFoodForm.name}
                    onChange={(e) =>
                      setEditFoodForm({ ...editFoodForm, name: e.target.value })
                    }
                  />
                  <input
                    placeholder="Brand"
                    value={editFoodForm.brand}
                    onChange={(e) =>
                      setEditFoodForm({ ...editFoodForm, brand: e.target.value })
                    }
                  />
                  <input
                    type="number"
                    step="any"
                    placeholder="Calories per 100g"
                    value={editFoodForm.calories_per_100g}
                    onChange={(e) =>
                      setEditFoodForm({
                        ...editFoodForm,
                        calories_per_100g: e.target.value,
                      })
                    }
                  />
                  <input
                    type="number"
                    step="any"
                    placeholder="Protein per 100g"
                    value={editFoodForm.protein_per_100g}
                    onChange={(e) =>
                      setEditFoodForm({
                        ...editFoodForm,
                        protein_per_100g: e.target.value,
                      })
                    }
                  />
                  <input
                    type="number"
                    step="any"
                    placeholder="Carbs per 100g"
                    value={editFoodForm.carbs_per_100g}
                    onChange={(e) =>
                      setEditFoodForm({
                        ...editFoodForm,
                        carbs_per_100g: e.target.value,
                      })
                    }
                  />
                  <input
                    type="number"
                    step="any"
                    placeholder="Fat per 100g"
                    value={editFoodForm.fat_per_100g}
                    onChange={(e) =>
                      setEditFoodForm({
                        ...editFoodForm,
                        fat_per_100g: e.target.value,
                      })
                    }
                  />

                  <div style={{ display: "flex", gap: "8px" }}>
                    <button type="button" onClick={() => saveEditedFood(food.id)}>
                      Save
                    </button>
                    <button type="button" onClick={cancelEditingFood}>
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </li>
          ))
        )}
      </ul>
    <hr />

    <h2>Search External Foods</h2>
      <div style={{ marginBottom: "12px" }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search external foods"
        />
        <button onClick={searchExternal} style={{ marginLeft: "8px" }}>
          Search External Foods
        </button>
      </div>

      <ul style={{ marginBottom: "24px" }}>
        {externalFoods.map((food) => (
          <li key={food.external_id} style={{ marginBottom: "10px" }}>
            {food.name} — {food.brand} — {food.calories_per_100g ?? "N/A"} kcal
            <button
              onClick={() => importExternalFood(food.external_id)}
              style={{ marginLeft: "8px" }}
            >
              Import
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;