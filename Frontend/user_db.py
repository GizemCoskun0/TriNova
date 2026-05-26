import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "Backend" / "smartkitchen.db"


def create_connection():
    return sqlite3.connect(DB_PATH)


def register_user(username, email, password):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
        """,
            (username, email, password),
        )

        conn.commit()
        conn.close()
        return True

    except sqlite3.IntegrityError:
        conn.close()
        return False


def check_login(email, password):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, username, email
        FROM users
        WHERE email = ? AND password = ?
    """,
        (email, password),
    )

    user = cursor.fetchone()
    conn.close()

    return user


def get_dashboard_data(email):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, username, email
        FROM users
        WHERE email = ?
    """,
        (email,),
    )
    user = cursor.fetchone()

    if not user:
        conn.close()
        return None

    user_id = user[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM inventory
        WHERE user_id = ?
    """,
        (user_id,),
    )
    inventory_count = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM shopping_list_items
        WHERE user_email = ? AND is_checked = 0
    """,
        (email,),
    )
    shopping_count = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM meal_plans
        WHERE user_email = ?
    """,
        (email,),
    )
    meal_plan_count = cursor.fetchone()[0]

    try:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM favorite_recipes
            WHERE user_email = ?
        """,
            (email,),
        )
        favorite_count = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        favorite_count = 0

    cursor.execute(
        """
        SELECT diets.name
        FROM diets
        JOIN user_diets ON diets.id = user_diets.diet_id
        WHERE user_diets.user_id = ?
        LIMIT 1
    """,
        (user_id,),
    )
    diet_result = cursor.fetchone()
    diet = diet_result[0] if diet_result else "None"

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM user_allergies
        WHERE user_id = ?
    """,
        (user_id,),
    )
    allergy_count = cursor.fetchone()[0]

    conn.close()

    return {
        "inventory_count": inventory_count,
        "shopping_count": shopping_count,
        "meal_plan_count": meal_plan_count,
        "favorite_count": favorite_count,
        "diet": diet,
        "allergy_count": allergy_count,
    }
