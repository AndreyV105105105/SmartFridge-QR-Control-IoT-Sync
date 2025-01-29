import sqlite3
import json
from datetime import datetime, timedelta
import uuid


class DatabaseManager:
    def __init__(self, db_name="smart_fridge.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        """Устанавливает соединение с БД."""
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def close(self):
        """Закрывает соединение с БД."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def create_tables(self):
        """Создаёт таблицы, если их нет."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                product_type TEXT NOT NULL,
                manufacture_date DATE NOT NULL,
                expiry_date DATE NOT NULL,
                number REAL NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                nutrition_info TEXT,
                measurement_type TEXT NOT NULL,
                added_history TEXT,
                removed_history TEXT
            )
        """)
        self.cursor.execute("""
          CREATE TABLE IF NOT EXISTS shopping_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            added_at DATETIME DEFAULT CURRENT_TIMESTAMP
           )
       """)
        self.conn.commit()

    def add_product(self, product_data, k=1):
        """Добавляет продукт в таблицу products."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")

        try:
            nutrition_info_json = json.dumps(product_data.get('nutrition_info', {}))
            added_history = json.dumps({str(product_data["quantity"]): datetime.now().isoformat()})

            self.cursor.execute("""
                INSERT INTO products (product_name, product_type, manufacture_date, expiry_date, number, quantity, unit, nutrition_info, measurement_type, added_history, removed_history)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_data["product_name"],
                product_data["product_type"],
                product_data["manufacture_date"],
                product_data["expiry_date"],
                k,
                product_data["quantity"],
                product_data["unit"],
                nutrition_info_json,
                product_data["measurement_type"],
                added_history,
                json.dumps({})
            )
                                )

            self.conn.commit()
            return True, "Продукт успешно добавлен в холодильник."
        except Exception as e:
            self.conn.rollback()
            return False, f"Ошибка добавления продукта: {e}"

    def get_product_in_bd(self, product_name, expiry_date):
        """Получает продукт из таблицы products по ID."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")
        self.cursor.execute("SELECT * FROM products WHERE product_name = ? AND expiry_date = ?", (product_name, expiry_date,))
        row = self.cursor.fetchone()
        if row:
            return self._row_to_dict(row)
        else:
            return None


    def remove_product(self, product_id):
        """Устанавливает количество продукта в 0 по ID."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")

        try:
            current_product = self.get_product_by_id(product_id)
            if not current_product:
                return False, f"Продукт с id = {product_id} не найден"

            removed_history = json.loads(current_product.get("removed_history", "{}"))
            removed_history[str(current_product["number"])] = datetime.now().isoformat()
            removed_history_json = json.dumps(removed_history)

            self.cursor.execute("""
                UPDATE products
                SET number = 0,
                removed_history = ?
                WHERE id = ?
            """, (removed_history_json, product_id,))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return True, "Количество продукта установлено в 0."
            else:
                return False, "Продукт с таким id не найден в холодильнике."
        except Exception as e:
            self.conn.rollback()
            return False, f"Ошибка при обновлении количества продукта: {e}"

    def update_product_number(self, product_id, new_quantity):
        """Обновляет количество продукта."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")

        try:
            current_product = self.get_product_by_id(product_id)
            if not current_product:
                return False, f"Продукт с id = {product_id} не найден"
            added_history = json.loads(current_product.get("added_history", "{}"))
            added_history[str(new_quantity)] = datetime.now().isoformat()
            added_history_json = json.dumps(added_history)

            self.cursor.execute("""
                  UPDATE products
                  SET quantity = ?,
                  added_history = ?
                  WHERE id = ?
                """, (new_quantity, added_history_json, product_id))
            self.conn.commit()
            return True, f"Количество продукта с id = {product_id} обновлено"
        except Exception as e:
            self.conn.rollback()
            return False, f"Ошибка при обновлении количества продукта: {e}"

    def get_all_products(self):
        """Получает все продукты из таблицы products."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")

        self.cursor.execute("SELECT * FROM products")
        rows = self.cursor.fetchall()
        products = []
        for row in rows:
            product = self._row_to_dict(row)
            products.append(product)
        return products

    def get_product_by_id(self, product_id):
        """Получает продукт из таблицы products по ID."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")
        self.cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = self.cursor.fetchone()
        if row:
            return self._row_to_dict(row)
        else:
            return None

    def _row_to_dict(self, row):
        """Преобразует строку из БД в словарь."""
        nutrition_info = row[7]
        return {
            "id": row[0],
            "product_name": row[1],
            "product_type": row[2],
            "manufacture_date": row[3],
            "expiry_date": row[4],
            "quantity": row[5],
            "unit": row[6],
            "nutrition_info": json.loads(nutrition_info) if nutrition_info else None,
            "measurement_type": row[8],
            "added_history": json.loads(row[9]) if row[9] else None,
            "removed_history": json.loads(row[10]) if row[10] else None
        }

    def search_products(self, search_term=None, search_type=None):
        """Поиск продуктов по названию и/или типу."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")
        query = "SELECT * FROM products WHERE 1=1"
        params = []
        if search_term:
            query += " AND product_name LIKE ?"
            params.append(f"%{search_term}%")
        if search_type:
            query += " AND product_type LIKE ?"
            params.append(f"%{search_type}%")

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        products = []
        for row in rows:
            product = self._row_to_dict(row)
            products.append(product)

        return products

    def add_to_shopping_list(self, product_name, quantity):
        """Добавляет продукт в список покупок."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")

        try:
            self.cursor.execute("""
                INSERT INTO shopping_list (product_name, quantity)
                VALUES (?, ?)
            """, (product_name, quantity))
            self.conn.commit()
            return True, "Продукт успешно добавлен в список покупок."
        except Exception as e:
            self.conn.rollback()
            return False, f"Ошибка добавления продукта в список покупок: {e}"

    def remove_from_shopping_list(self, item_id):
        """Удаляет продукт из списка покупок по ID."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")

        try:
            self.cursor.execute("DELETE FROM shopping_list WHERE id = ?", (item_id,))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return True, "Продукт успешно удален из списка покупок."
            else:
                return False, "Продукт с таким id не найден в списке покупок."
        except Exception as e:
            self.conn.rollback()
            return False, f"Ошибка удаления продукта из списка покупок: {e}"

    def get_all_shopping_list(self):
        """Получает весь список покупок."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")

        self.cursor.execute("SELECT * FROM shopping_list")
        rows = self.cursor.fetchall()
        items = []
        for row in rows:
            item = self._shopping_row_to_dict(row)
            items.append(item)
        return items

    def _shopping_row_to_dict(self, row):
        return {
            "id": row[0],
            "product_name": row[1],
            "quantity": row[2],
            "added_at": row[3]
        }

    def get_products_expiring_soon(self, days=7):
        """Получает продукты, у которых истекает срок годности в течение days дней."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")

        today = datetime.now().date()
        cutoff_date = today + timedelta(days=days)
        self.cursor.execute("SELECT * FROM products WHERE expiry_date BETWEEN ? AND ?",
                            (today.isoformat(), cutoff_date.isoformat()))
        rows = self.cursor.fetchall()
        products = []
        for row in rows:
            product = self._row_to_dict(row)
            products.append(product)
        return products

    def get_consumption_analytics(self, start_date, end_date):
        """Получает аналитику потребления продуктов за указанный период."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")

        start_datetime = datetime.fromisoformat(start_date)
        end_datetime = datetime.fromisoformat(end_date)

        self.cursor.execute("SELECT * FROM products")
        rows = self.cursor.fetchall()

        added_count = 0
        added_positive_quantity_count = 0
        removed_count = 0
        quantity_diffs = {}

        for row in rows:
            product = self._row_to_dict(row)
            if product["added_history"]:
                for quantity, date_str in product["added_history"].items():
                    added_date = datetime.fromisoformat(date_str)
                    if start_datetime <= added_date <= end_datetime:
                        added_count += 1
                        if float(quantity) > 0:
                            added_positive_quantity_count += 1

            if product["removed_history"]:
                for quantity, date_str in product["removed_history"].items():
                    removed_date = datetime.fromisoformat(date_str)
                    if start_datetime <= removed_date <= end_datetime:
                        removed_count += 1

            if product["added_history"]:
                last_added_quantity = 0
                last_added_date = None
                for quantity, date_str in product["added_history"].items():
                    added_date = datetime.fromisoformat(date_str)
                    if start_datetime <= added_date <= end_datetime:
                        if not last_added_date or added_date > last_added_date:
                            last_added_quantity = float(quantity)
                            last_added_date = added_date
                if last_added_quantity != 0:
                    quantity_diffs[product["product_name"]] = quantity_diffs.get(product["product_name"],
                                                                                 0) + last_added_quantity
            if product["removed_history"]:
                last_removed_quantity = 0
                last_removed_date = None
                for quantity, date_str in product["removed_history"].items():
                    removed_date = datetime.fromisoformat(date_str)
                    if start_datetime <= removed_date <= end_datetime:
                        if not last_removed_date or removed_date > last_removed_date:
                            last_removed_quantity = float(quantity)
                            last_removed_date = removed_date
                if last_removed_quantity != 0:
                    quantity_diffs[product["product_name"]] = quantity_diffs.get(product["product_name"],
                                                                                 0) - last_removed_quantity

        return {
            "added_count": added_count,
            "added_positive_quantity_count": added_positive_quantity_count,
            "removed_count": removed_count,
            "quantity_diffs": [{"product_name": name, "quantity_diff": diff} for name, diff in quantity_diffs.items()]
        }
