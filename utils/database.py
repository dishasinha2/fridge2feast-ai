"""SQLite Database Management for Fridge2Feast AI."""
import sqlite3
import os
import json
from contextlib import contextmanager
from typing import Generator, Optional

def get_db_path() -> str:
    return os.environ.get("FRIDGE2FEAST_DB_PATH", "fridge2feast.db")


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for SQLite database connection with foreign keys enabled."""
    conn = sqlite3.connect(get_db_path(), timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db() -> None:
    """Initialize all database tables and indexes with corruption self-healing."""
    db_path = get_db_path()
    try:
        _run_init_schema()
    except sqlite3.DatabaseError as e:
        # If database is malformed/corrupted, archive and rebuild cleanly
        if os.path.exists(db_path):
            backup_path = f"{db_path}.corrupt.{os.getpid()}"
            try:
                os.rename(db_path, backup_path)
            except OSError:
                try:
                    os.remove(db_path)
                except OSError:
                    pass
        _run_init_schema()


def _run_init_schema() -> None:
    """Execute SQL table and index creation statements."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")

        # 2. Preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                cuisines TEXT NOT NULL DEFAULT '[]',
                dietary TEXT NOT NULL DEFAULT '[]',
                spice_level TEXT NOT NULL DEFAULT 'Medium',
                default_servings INTEGER NOT NULL DEFAULT 2,
                prioritized_ingredients TEXT NOT NULL DEFAULT '[]',
                avoided_ingredients TEXT NOT NULL DEFAULT '[]',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_preferences_user ON preferences(user_id);")

        # 3. Ingredients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                freshness_status TEXT NOT NULL,
                estimated_shelf_life_days INTEGER NOT NULL,
                storage_advice TEXT,
                confidence REAL DEFAULT 1.0,
                added_date DATE NOT NULL,
                expiry_date DATE NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ingredients_user ON ingredients(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ingredients_expiry ON ingredients(expiry_date);")

        # 4. Recipes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                cuisine TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                dietary_tags TEXT NOT NULL DEFAULT '[]',
                spice_level TEXT NOT NULL DEFAULT 'Medium',
                cooking_time_minutes INTEGER NOT NULL,
                servings INTEGER NOT NULL,
                available_ingredients TEXT NOT NULL,
                additional_ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL,
                tips TEXT NOT NULL DEFAULT '[]',
                waste_saved_score INTEGER DEFAULT 80,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_recipes_user ON recipes(user_id);")

        # 5. Saved recipes junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                recipe_id INTEGER NOT NULL,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, recipe_id),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_saved_recipes_user ON saved_recipes(user_id);")

        # 6. Cooking history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cooking_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                recipe_title TEXT NOT NULL,
                cuisine TEXT NOT NULL,
                servings INTEGER NOT NULL,
                cooked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                rating INTEGER DEFAULT 5,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cooking_history_user ON cooking_history(user_id);")

        # 7. Notifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                ingredient_id INTEGER,
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(ingredient_id) REFERENCES ingredients(id) ON DELETE SET NULL
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);")

