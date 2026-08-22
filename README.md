# 👨‍🍳 Fridge2Feast AI - Python & Streamlit Capstone Edition

> **Fridge2Feast AI is a Python + Streamlit application powered by Google Gemini.**

Fridge2Feast AI is a zero-waste culinary decision intelligence platform engineered natively with **Python 3.11, Streamlit, Pandas, and Google Gemini Multimodal AI**.

Kitchen state is managed in **session-scoped runtime state** (`st.session_state`). Local accounts are stored in a gitignored SQLite database with salted `scrypt` password hashes; production deployments should replace this local store with a managed identity provider and database.

---

## 🌟 Key Features

- 📸 **Smart Fridge Vision Scanner**: Capture or upload photos of your open fridge or pantry. Gemini AI detects edible ingredients, categories, and estimated quantities directly in memory.
- 🥦 **Pandas Inventory Management**: Edit detected quantities with `st.data_editor`, filter by category, add items manually, and calculate your **Fridge Potential Score**.
- 🍳 **AI Recipe Studio**: Custom culinary preferences (Diet, Cuisine, Cooking Time, Difficulty, Servings, INR Budget, Spice Level, Allergies) generating **exactly 3 zero-waste recipes** (*Best Match*, *Quick Feast*, *Creative Pick*).
- 🍽️ **Recipe Dashboard & KPIs**: Utilization %, missing ingredients cost in INR ₹, step-by-step preparation, chef tips, substitutions, and nutrition estimates.
- 👨‍🍳 **Interactive Step-by-Step Cooking Mode**: Guided progress with celebratory completions.
- 🛒 **Smart Shopping List & Exports**: Instant cost calculation with downloadable **CSV, TXT, and Markdown** exports.
- 💬 **Contextual AI Sous-Chef**: Chat assistant for ingredient swaps, dietary adjustments, and time-saving shortcuts.
- 📖 **Feastbook**: Save and organize favorite recipes in session-scoped runtime state.
- 📊 **Zero-Waste Analytics**: Plotly & Pandas views of verified session inventory, generated recipes, and saved recipes.

---

## 🛠️ Tech Stack & Architecture

- **Runtime & UI**: Python 3.11 + Streamlit
- **AI Core**: Google Gemini API (`google-genai` SDK with `GEMINI_MODEL`, default `gemini-2.5-flash`)
- **Data Engineering**: Pandas & Plotly
- **State Model**: Session-scoped runtime state (`st.session_state`)

---

## 🚀 Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit application
streamlit run app.py
```

### Gemini configuration

Configure `GEMINI_API_KEY` in Streamlit secrets or the environment. For local development only, a root `.env` file is also supported. `GEMINI_MODEL` is optional and defaults to `gemini-2.5-flash`.
