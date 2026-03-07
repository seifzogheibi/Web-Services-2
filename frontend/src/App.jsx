import { useState } from "react";

const API = "http://127.0.0.1:8000";

function App() {
  const [foods, setFoods] = useState([]);
  const [query, setQuery] = useState("");
  const [externalFoods, setExternalFoods] = useState([]);

  async function fetchFoods() {
    const res = await fetch(`${API}/foods`);
    const data = await res.json();
    setFoods(data);
  }

  async function searchExternal() {
    const res = await fetch(`${API}/external/openfoodfacts/search?query=${query}`);
    const data = await res.json();
    setExternalFoods(data);
  }

  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1>Nutrition API Demo</h1>

      <button onClick={fetchFoods}>Load Foods</button>

      <h2>Foods</h2>
      <ul>
        {foods.map((food) => (
          <li key={food.id}>
            {food.name} — {food.calories_per_100g} kcal
          </li>
        ))}
      </ul>

      <h2>Search Open Food Facts</h2>

      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search food"
      />

      <ul>
        {externalFoods.map((food) => (
          <li key={food.external_id}>
            {food.name} — {food.brand} — {food.calories_per_100g ?? "N/A"} kcal
          </li>
        ))}
      </ul>

      <button onClick={searchExternal}>Search</button>
    </div>
  );
}

export default App;