 # 🍽️ Smart Kitchen Assistant
  
  **Your intelligent companion for effortless meal planning and zero food waste.**

  ![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat-square&logo=python&logoColor=white)
  ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393.svg?style=flat-square&logo=fastapi&logoColor=white)
  ![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-FF4B4B.svg?style=flat-square&logo=streamlit&logoColor=white)
  ![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)
</div>

<br />

A polished, intelligent web application that generates personalized meal plans based on user diets, allergies, and current home inventory — helping users reduce food waste and make meal-time decisions effortless.

## 📸 Sneak Peek
> <img width="1919" height="907" alt="Ekran görüntüsü 2026-05-17 215200" src="https://github.com/user-attachments/assets/26f7aa8c-54ef-46ce-b5f4-0cf2f575b6ce" />
> <img width="1876" height="823" alt="Ekran görüntüsü 2026-05-17 215805" src="https://github.com/user-attachments/assets/4fc8e549-6157-4882-a7c3-d1ade10f51f9" />
> <img width="1348" height="911" alt="localhost_8501_Meal_Planner" src="https://github.com/user-attachments/assets/e9f1c2fb-cfa0-4e28-93bc-da0d82a277af" />
> <img width="1901" height="859" alt="Ekran görüntüsü 2026-05-17 220629" src="https://github.com/user-attachments/assets/85873689-0700-4c1c-ae57-e99584ed197c" />
> <img width="1521" height="813" alt="Ekran görüntüsü 2026-05-17 220809" src="https://github.com/user-attachments/assets/2984ece8-57c7-4ed2-8022-1b02fc217b3e" />
> <img width="1626" height="853" alt="Ekran görüntüsü 2026-05-17 220911" src="https://github.com/user-attachments/assets/a51e6df0-7cbd-47b9-854d-3e54adab4086" />


---

## ✨ Key Features

- **Dynamic Meal Planner:** Generates meal plans across categories (Main Course, Soup, Salad, Dessert) tailored to user preferences.
- **Smart Filtering:** Enforces strict matching for allergies and diets (vegan, keto, etc.) and runs a fail-safe to exclude beverages from breakfast suggestions.
- **Inventory Matching:** Compares recipe ingredient lists against the user's home inventory and auto-adds missing items to a Shopping List.
- **Favorites System:** Save, view, and manage favorite recipes for quick access directly from your dashboard.
- **Optimized Architecture:** Tabbed UI with Lazy Loading; API calls are made only when a tab is opened. Frontend is modularized for clarity and reusability.

---


## 🛠️ Tech Stack

* **Frontend:** Streamlit, Streamlit-Cookies-Controller (Session Management)
* **Backend:** FastAPI, Uvicorn, SQLAlchemy
* **Database:** SQLite
* **AI & Computer Vision:** Ultralytics (YOLO), OpenCV, NumPy, NetworkX
* **External APIs:** Spoonacular API (Recipe & Ingredient Data)
* **Utilities:** ReportLab (PDF Export), Pydantic (Data Validation)

---

## 🏗️ Architecture Overview

This project adopts a **decoupled client-server architecture**, ensuring that the user interface and business logic remain strictly separated. This design pattern guarantees high maintainability, independent scalability, and a seamless developer experience.

### 🌊 Data Flow & System Design
1. **User Interaction:** The user interacts with the Streamlit frontend, navigating through different features via the `pages/` directory.
2. **API Communication:** Frontend utilities (like `ui_utils.py` and `user_db.py`) issue HTTP/REST requests to the backend only when specific actions are triggered.
3. **Business Logic & AI:** FastAPI handles incoming requests asynchronously. It delegates complex tasks to `services/` and `api_process.py`, interacts with the `ai_model`, and enforces data validation using Pydantic.
4. **Database & Rendering:** The backend queries the local `smartkitchen.db` via SQLAlchemy. It returns clean JSON responses, which Streamlit parses and renders into interactive UI components.

### 🧩 Core Modules & Directory Tree

```text
📦 Project Structure
 ┣ 📂 ai_model            # AI/ML model scripts and processing logic
 ┣ 📂 Backend             # FastAPI Server & Business Logic
 ┃ ┣ 📂 routers           # Feature-specific API endpoints (e.g., recipes, users)
 ┃ ┣ 📂 services          # Core business logic and external API integrations
 ┃ ┣ 📜 api_process.py    # API request handling and processing utilities
 ┃ ┣ 📜 database.py       # Database connection setup and session management
 ┃ ┣ 📜 init_db.py        # Database initialization script
 ┃ ┣ 📜 main.py           # FastAPI application entry point
 ┃ ┣ 📜 models.py         # SQLAlchemy database models
 ┃ ┣ 📜 schemas.py        # Pydantic data validation schemas
 ┃ ┗ 📜 smartkitchen.db   # Local SQLite database file
 ┣ 📂 Frontend            # Streamlit Web Application
 ┃ ┣ 📂 assets            # Static files (images, icons, etc.)
 ┃ ┣ 📂 pages             # Streamlit multi-page routing files (e.g., Meal Planner)
 ┃ ┣ 📂 views             # UI view templates and sub-modules
 ┃ ┣ 📜 auth_utils.py     # Authentication helpers and session state management
 ┃ ┣ 📜 Home.py           # Main Streamlit UI entry point (Dashboard)
 ┃ ┣ 📜 home_styles.py    # Custom CSS and styling components
 ┃ ┣ 📜 ui_components.py  # Reusable Streamlit UI widgets (cards, forms)
 ┃ ┣ 📜 ui_utils.py       # General frontend helper functions
 ┃ ┗ 📜 user_db.py        # Frontend-side local DB interaction helpers
 ┣ 📜 .env                # Environment variables (API keys, DB URLs)
```
## 🚀 Installation & Setup

Follow these structured steps to set up the **Smart Kitchen Assistant** locally on your machine.

### 1. Clone the Repository
Open your terminal or PowerShell and run the following commands to clone the project and navigate into its root directory:
```bash
git clone [https://github.com/GizemCoskun0/TriNova.git](https://github.com/GizemCoskun0/TriNova.git)
cd TriNova

```

### 2. Set Up a Virtual Environment

It is highly recommended to isolate the project dependencies using a virtual environment:

* **Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1

```


* **Windows (Command Prompt / cmd):**
```cmd
python -m venv venv
.\venv\Scripts\activate.bat

```


* **macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate

```



---

### 3. Backend Configuration

Install the required microservice dependencies, prepare your database schema, and fire up the FastAPI server:

```bash
# Upgrade pip to avoid installation conflicts
pip install --upgrade pip

# Install required packages for backend development
pip install -r Backend/requirements.txt

# Run the database initialization script to generate SQLite tables
python Backend/init_db.py

# Launch the FastAPI local server with hot-reloading active
uvicorn Backend.main:app --reload --host 127.0.0.1 --port 8000

```

> 💡 **Verification:** Keep this terminal open. You can verify that the backend is live by opening your browser and visiting the interactive documentation at `http://127.0.0.1:8000/docs`.

---

### 4. Frontend Configuration

Open a **new terminal tab or window** (keep the backend environment running), reactivate your virtual environment, and boot up the Streamlit interface:

```bash
# Ensure frontend core packages are installed
pip install streamlit requests

# Launch the interactive user interface
streamlit run Frontend/Home.py

```

### 🌐 Accessing the Application

Once both layers are successfully running, open your web browser and navigate to:

* **Frontend UI:** `http://localhost:8501`
* **Backend API Base:** `http://127.0.0.1:8000`

## 🔑 Environment Variables

Create a `.env` file in the project root (or provide these via your environment manager). At minimum, set:

```env
SPOONACULAR_API_KEY=your_spoonacular_api_key_here
```

* `SPOONACULAR_API_KEY` — Required to fetch recipe and ingredient metadata from Spoonacular.
* `DATABASE_URL` — Optional: defaults to a local SQLite file if unset.

*Tip: Store secrets securely in CI/CD or platform-specific secret stores for production deployments.*

---
## 🎯 How It Works & Usage Guide

Follow this step-by-step walkthrough to get the most out of your **Smart Kitchen Assistant**. The application follows a seamless pipeline: **Profile Personalization ➡️ Inventory Tracking ➡️ Intelligent Planning ➡️ Automated Grocery Generation.**
### 🔐 Step 1: Authentication & Onboarding
* Launch the Streamlit application.
* Create a new account via the **Register** tab or access your existing workspace using the **Login** form.
* Secure session state management ensures your digital kitchen stays persistent.

### ⚙️ Step 2: Configure Your Settings (Diet, Allergies & Security)
* Navigate to the **Settings** section (located at the bottom of the navigation menu).
* Select your specific **Dietary Preferences** (e.g., Vegetarian, Vegan, Keto, Paleo).
* Log any food **Allergies or Intolerances** (e.g., Nuts, Gluten, Dairy).
* **Account Management:** You can also securely update your password directly from this page.
> 🧠 **Behind the Scenes:** The FastAPI backend utilizes strict filtering algorithms based on your diet and allergy inputs, ensuring that no unsafe or incompatible recipes are ever recommended.

### 🥫 Step 3: Stock Your Virtual Kitchen (Inventory)
* Head over to the **Inventory** tab.
* Add ingredients that you currently have available in your home pantry, fridge, or kitchen cabinets.
* Keep this updated to maximize the efficiency of the smart matching engine and minimize domestic food waste.

### 🍽️ Step 4: Generate Your Meal Plan
Go to the **Meal Planner** section from the navigation menu. You have two powerful ways to plan your week:

* **Option A: The Magic Planner (1-Click Automated 3-Day Plan)**
    * Click the **🪄 Auto-Generate Full 3-Day Plan** button.
    * The system dynamically builds a comprehensive, structured breakfast-to-drink blueprint matching your strict profile constraints and leveraging your current inventory.
* **Option B: Category-Specific Exploration**
    * Toggle your desired categories (e.g., *Breakfast, Soup, Main Course, Dessert, Drink*).
    * Click **🔄 Get Recommendations** on any category to view curated recipe cards inline, browse detailed structural lists of ingredients, and follow clear step-by-step cooking instructions.
    * Select your target day/meal type and click **➕ Add to Plan**.

### 🛒 Step 5: Master Your Groceries & Export
* **Automated Shopping List:** Once a recipe is added to your current plan, the backend automatically cross-references its ingredients with your home inventory. Any missing components are instantly funneled into your active **Grocery List** as items to buy.
* **Take it Offline:** View your comprehensive overview on the main **Kitchen Dashboard** (complete with your dynamic Favorites counter), and click **📥 Export to PDF** to download a clean, printable copy of your meal matrix.

## 📂 Where To Look in The Codebase

* **Frontend UI:** `Frontend/Home.py`, `Frontend/ui_components.py`, `Frontend/ui_utils.py`
* **Backend Entry:** `Backend/main.py`
* **Routers & Services:** `Backend/routers/`, `Backend/services/`
* **DB Initialization:** `Backend/init_db.py`

---

## 📄 License

This project is licensed under the [MIT License](https://www.google.com/search?q=LICENSE).

---

## 👩‍💻 Developers (Meet the Team)

This project was built with ❤️ and collaboration by an amazing team of developers. Feel free to connect with us!

| Developer | Role / Contribution | GitHub |
| :--- | :--- | :--- |
| **Gizem Coşkun** | Full-Stack & UI Core | [@GizemCoskun0](https://github.com/GizemCoskun0) |
| **Merve Güneş** | AI Integration & Routing  | [@Mervegunes00](https://github.com/Mervegunes00) |
| **Beyza Birben** | Backend & Database Design | [@BeyzaBirben](https://github.com/BeyzaBirben) |

---
