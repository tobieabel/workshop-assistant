import sqlite3
from typing import Optional
from dataclasses import dataclass
from contextlib import contextmanager
from datetime import datetime
import os

@dataclass
class Car:
    vin: str
    make: str
    model: str
    year: int

class DatabaseDriver:
    def __init__(self, db_path: str = None):
        # Get the database path from environment or use default
        self.db_path = db_path or os.getenv('DB_PATH', 'auto_db.sqlite')
        
        # If the path contains directories, create them
        db_dir = os.path.dirname(self.db_path)
        if db_dir:  # Only create directories if there's a path
            os.makedirs(db_dir, exist_ok=True)
        
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create cars table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cars (
                    vin TEXT PRIMARY KEY,
                    make TEXT NOT NULL,
                    model TEXT NOT NULL,
                    year INTEGER NOT NULL
                )
            """)
            
            # Create lesson_plans table with is_active column
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lesson_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    upload_date TIMESTAMP NOT NULL,
                    file_size INTEGER NOT NULL,
                    content TEXT,
                    is_active INTEGER DEFAULT 0
                )
            """)
            
            # Create uploads directory if it doesn't exist
            if not os.path.exists('uploads'):
                os.makedirs('uploads')
                
            conn.commit()

    def create_car(self, vin: str, make: str, model: str, year: int) -> Car:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO cars (vin, make, model, year) VALUES (?, ?, ?, ?)",
                (vin, make, model, year)
            )
            conn.commit()
            return Car(vin=vin, make=make, model=model, year=year)

    def get_car_by_vin(self, vin: str) -> Optional[Car]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cars WHERE vin = ?", (vin,))
            row = cursor.fetchone()
            if not row:
                return None
            
            return Car(
                vin=row[0],
                make=row[1],
                model=row[2],
                year=row[3]
            )

    def save_lesson_plan(self, title: str, file_path: str, file_size: int, content: str = None) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO lesson_plans (title, file_path, upload_date, file_size, content) 
                VALUES (?, ?, ?, ?, ?)
                """,
                (title, file_path, datetime.now().isoformat(), file_size, content)
            )
            conn.commit()
            return cursor.lastrowid

    def get_lesson_plan(self, plan_id: int) -> Optional[dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, file_path, upload_date, file_size, content FROM lesson_plans WHERE id = ?", 
                (plan_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            
            return {
                'id': row[0],
                'title': row[1],
                'file_path': row[2],
                'upload_date': row[3],
                'file_size': row[4],
                'content': row[5]
            }

    def get_all_lesson_plans(self) -> list[dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, upload_date, file_size, content, is_active FROM lesson_plans ORDER BY upload_date DESC"
            )
            rows = cursor.fetchall()
            
            return [{
                'id': row[0],
                'title': row[1],
                'upload_date': row[2],
                'file_size': row[3],
                'content': row[4],
                'is_active': bool(row[5])
            } for row in rows]

    def delete_lesson_plan(self, plan_id: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM lesson_plans WHERE id = ?",
                (plan_id,)
            )
            conn.commit()

    def set_active_lesson_plan(self, plan_id: Optional[int]) -> None:
        """Set or clear the active lesson plan"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Clear any existing active plans
            cursor.execute("UPDATE lesson_plans SET is_active = 0")
            
            if plan_id is not None:
                cursor.execute(
                    "UPDATE lesson_plans SET is_active = 1 WHERE id = ?",
                    (plan_id,)
                )
            conn.commit()

    def get_active_lesson_plan(self) -> Optional[dict]:
        """Get the currently active lesson plan"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, file_path, upload_date, file_size, content FROM lesson_plans WHERE is_active = 1"
            )
            row = cursor.fetchone()
            if not row:
                return None
            
            return {
                'id': row[0],
                'title': row[1],
                'file_path': row[2],
                'upload_date': row[3],
                'file_size': row[4],
                'content': row[5]
            }
