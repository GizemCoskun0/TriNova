# 🍽️ Smart Kitchen Assistant

A polished, intelligent web application that generates personalized meal plans based on user diets, allergies, and current home inventory — helping users reduce food waste and make meal-time decisions effortless.

---

## ✨ Key Features

- **Dynamic Meal Planner:** Generates meal plans across categories (Main Course, Soup, Salad, Dessert) tailored to user preferences.
- **Smart Filtering:** Enforces strict matching for allergies and diets (vegan, keto, etc.) and runs a fail-safe to exclude beverages from breakfast suggestions.
- **Inventory Matching:** Compares recipe ingredient lists against the user's home inventory and auto-adds missing items to a Shopping List.
- **Favorites System:** Save, view, and manage favorite recipes for quick access.
- **Optimized Architecture:** Tabbed UI with Lazy Loading; API calls are made only when a tab is opened. Frontend is modularized for clarity and reusability.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, SQLite
- **Frontend:** Streamlit 
- **External API:** Spoonacular (recipe & ingredient data)
- **Dev / Ops:** `uvicorn` for local API serving, optional Docker for containerized deployments

---

## 🏗️ Architecture Overview

The project is split into two clear layers for maintainability and independent development:

- **Frontend (Streamlit):** Modular UI components live in [Frontend/ui_components.py](Frontend/ui_components.py) and helpers in [Frontend/ui_utils.py](Frontend/ui_utils.py). The UI uses a tabbed layout with lazy loading so each tab initializes and issues API requests only when clicked.
- **Backend (FastAPI):** Async routes and domain logic are implemented under [Backend/](Backend/). Entry point: [Backend/main.py](Backend/main.py). Routers for features live in [Backend/routers/](Backend/routers/) (for example, [Backend/routers/recipes.py](Backend/routers/recipes.py)). Database models and schema definitions are in [Backend/models.py](Backend/models.py) and [Backend/schemas.py](Backend/schemas.py).

This separation enables independent scaling, easier testing, and a clean developer experience.

---

## 🚀 Installation & Setup

Follow these steps to set up the project locally. Examples use Windows PowerShell; adapt activation commands for your shell if needed.

1) Clone the repo

```bash
git clone <your-repo-url>
cd "Smart Kitchen Assistant"
```

2) Create a virtual environment (recommended)

```powershell
python -m venv venv
.\\venv\\Scripts\\Activate.ps1
# Or for cmd.exe: .\\venv\\Scripts\\activate
```

3) Backend setup

- Install dependencies (if a `Backend/requirements.txt` exists):

```bash
pip install -r Backend/requirements.txt
```

- Or install core packages manually:

```bash
pip install fastapi uvicorn sqlalchemy httpx python-dotenv
# For Postgres support: pip install psycopg2-binary
```

- Initialize the database (SQLite by default):

```bash
python Backend/init_db.py
```

- Run the backend API (development):

```bash
uvicorn Backend.main:app --reload --host 127.0.0.1 --port 8000
```

4) Frontend setup

- Install Streamlit (if no Frontend/requirements.txt):

```bash
pip install streamlit
```

- Run the Streamlit app:

```bash
streamlit run Frontend/Home.py
```

Visit the Streamlit UI in your browser (default: http://localhost:8501) and ensure the backend is running at http://127.0.0.1:8000.

---

## 🔑 Environment Variables

Create a `.env` file in the project root (or provide these via your environment manager). At minimum, set:

```env
SPOONACULAR_API_KEY=your_spoonacular_api_key_here
DATABASE_URL=sqlite:///./smart_kitchen.db  # or your Postgres URL
```

- `SPOONACULAR_API_KEY` — Required to fetch recipe and ingredient metadata from Spoonacular.
- `DATABASE_URL` — Optional: defaults to a local SQLite file if unset.

Tip: store secrets securely in CI/CD or platform-specific secret stores for production deployments.

---

## 🔮 Future Improvements

- Add user authentication + role management and persistent cloud sessions.
- Implement meal-plan export (PDF, calendar invites) and grocery delivery integration.
- Add recommendation engine that learns user preferences over time.
- CI workflow, unit/integration tests, and Docker Compose for end-to-end local development.
- Improve accessibility and responsive layout for mobile-friendly use.

---

## 📂 Where To Look in The Codebase

- Frontend UI: [Frontend/Home.py](Frontend/Home.py), [Frontend/ui_components.py](Frontend/ui_components.py), [Frontend/ui_utils.py](Frontend/ui_utils.py)
- Backend entry: [Backend/main.py](Backend/main.py)
- Routers & services: [Backend/routers/](Backend/routers/), [Backend/services/](Backend/services/)
- DB initialization: [Backend/init_db.py](Backend/init_db.py)

---

If you'd like, I can also:

- add a `requirements.txt` for both backend and frontend,
- add a startup script or Dockerfile, or
- draft contributing guidelines and issue templates for the repo.

Happy to proceed with any of the above — which would you like next?

