# Fridge2Feast AI - System Architecture & Capstone Validation

> **Fridge2Feast AI is a Python + Streamlit application powered by Google Gemini.**

## 1. System Overview

Fridge2Feast AI is a zero-waste culinary decision intelligence platform engineered natively in **Python 3.11, Streamlit, Pandas, Google Gemini (GenAI Python SDK), Plotly, and Pydantic**.

The architecture enforces a strict boundary between **Generative Multimodal AI responsibilities** (vision pattern recognition, semantic extraction, chef instructions, Sous-Chef natural dialogue) and **Deterministic Python/Pandas logic** (inventory schemas, mathematical multi-objective scoring, food waste urgency calculations, precision/recall verification, and runtime feedback metrics).

---

## 2. Gemini Model Configuration & Fallback Policy

1. **Strict Format Validation**: Configured model names from `GEMINI_MODEL` (or secrets) are validated against standard `gemini-*` prefixes. If an invalid or token string is encountered, the gateway logs a warning and safely defaults to `gemini-2.5-flash`.
2. **Focused Same-Model Retry**: The gateway retries the SAME configured model using bounded exponential backoff (`[0.8s, 1.6s]`) on transient network or capacity errors (`503`, `429`, `408`).
3. **No Random Cycling**: The engine never randomly cycles through unrequested models upon configuration errors to prevent masking setup defects.
4. **Structured Error Categories**:
   - `VALIDATION_ERROR` (Invalid pre-call preferences or payload)
   - `AUTHENTICATION_REQUIRED` / `AUTH_ERROR` (Invalid or missing API key)
   - `RATE_LIMITED` / `RATE_LIMIT_ERROR` (Quota limit exceeded)
   - `SERVICE_UNAVAILABLE` (Transient high demand or 503)
   - `TIMEOUT_ERROR` (Network or latency timeout)
   - `SCHEMA_VALIDATION_ERROR` (Response failed Pydantic schema validation)
   - `INTERNAL_ERROR` (Unexpected runtime exception)

---

## 3. AI vs Application Logic Division

| Domain | Gemini AI Responsibilities | Deterministic Python / Pandas Logic |
| :--- | :--- | :--- |
| **Vision & Scanner** | Multimodal visual identification, category tag inference, quantity estimation, uncertainty detection | In-memory stream handling, Pydantic response validation, confidence classification, DataFrame table transformations |
| **Inventory & Freshness** | Semantic culinary grouping | Shelf-life estimation lookup, Waste Risk score computation (0–100), urgency level assignment (`HIGH`, `MEDIUM`, `LOW`), use-by window calculations |
| **Decision & Optimization** | Recipe drafting, culinary step sequencing, nutrition approximation, waste-saving context notes | Multi-objective scoring algorithm (6 objective weights), ingredient utilization %, cost delta vs budget, diet/allergen filtering |
| **Meal Planning & Leftovers** | Daily schedule curation, creative leftover repurposing | Calendar scheduling structure, missing ingredient shopping list aggregation, dietary constraint enforcement |
| **Evaluation & Feedback** | Contextual responses | Precision/recall calculation (when ground truth configured), Human-in-the-loop audit counters, Latency profiling (ms), Success rate analytics |

---

## 3. Privacy, Security & Isolation Guarantees

1. **No API Keys in Source Code**: Gemini API key is loaded lazily from `st.secrets` or `os.environ["GEMINI_API_KEY"]` via `get_gemini_client()`.
2. **Ephemeral In-Memory Processing**: All uploaded images and camera snapshots are held strictly in memory buffers (`BytesIO`) during analysis and are **never written to disk, saved in local storage, or permanently logged**.
3. **Session-Scoped Isolation**: All user state resides exclusively within `st.session_state`. No cross-user or cross-session state leakage is possible.
4. **Prompt Injection & Schema Defenses**: All Gemini API calls use strict `Pydantic` schemas (`response_schema=...`) and `response_mime_type="application/json"` to ensure verified structured outputs.
5. **No Password Storage**: Authentication uses lightweight session-scoped identity verification with no raw passwords persisted.
6. **Safe Telemetry & Observability**: Centralized logger never records raw user prompt texts, images, or authentication tokens.

---

## 4. Multi-Objective Optimization Math

The decision engine ranks recipes application-side using transparent weights across 6 key metrics:

$$\text{Optimization Score} = w_1 \cdot \text{Utilization} + w_2 \cdot \text{WasteRisk} + w_3 \cdot \text{Craving} + w_4 \cdot \text{Budget} + w_5 \cdot \text{Diet} + w_6 \cdot \text{Time}$$

### Default Balanced Weights:
- **Fridge Ingredient Utilization ($w_1$)**: 30%
- **Urgent Waste Risk Reduction ($w_2$)**: 25%
- **Craving & Taste Fit ($w_3$)**: 15%
- **Budget & Cost Fit ($w_4$)**: 10%
- **Dietary Compatibility ($w_5$)**: 10%
- **Preparation Speed ($w_6$)**: 10%

Users can dynamically select optimization objectives (Minimum Food Waste, Lowest Cost, Best Craving Match, Fastest Meal, Nutrition, or Balanced), modifying the application-side ranking weights with full explainability.

---

## 5. Food Safety Disclaimer

Visual AI models cannot evaluate microbiological safety, bacterial activity, or pathogen presence. The application explicitly frames all shelf-life calculations as **AI-estimated guidance** and instructs users to verify package dates, aroma, visual texture, and official food safety guidelines before consumption.
