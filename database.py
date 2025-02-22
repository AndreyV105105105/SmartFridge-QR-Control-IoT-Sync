import sqlite3
import json
from datetime import datetime, timedelta


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
                number INTEGER NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                nutrition_info TEXT,
                measurement_type TEXT NOT NULL,
                added_history TEXT,
                removed_history TEXT,
                is_notification_read BOOLEAN DEFAULT 0
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

    def add_product_in_bd(self, product_data):
        """Добавляет продукт в таблицу products."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")

        try:
            nutrition_info_json = json.dumps(product_data.get('nutrition_info', {}))
            added_history = json.dumps({'1': datetime.now().isoformat()})

            self.cursor.execute("""
                INSERT INTO products (product_name, product_type, manufacture_date, expiry_date, number, quantity, unit, nutrition_info, measurement_type, added_history, removed_history)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_data["product_name"],
                product_data["product_type"],
                product_data["manufacture_date"],
                product_data["expiry_date"],
                1,
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

    def update_product_quantity(self, product_name, expiry_date, status_number=True):
        """Обновляет количество продукта."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")

        try:
            current_product = self.get_product_in_bd(product_name, expiry_date)
            if not current_product:
                return False, f"Продукт с name = {product_name} и expiry_date = {expiry_date} не найден"
            self.cursor.execute("SELECT number FROM products WHERE product_name = ? AND expiry_date = ?",
                                (product_name, expiry_date,))
            now_number = int(self.cursor.fetchone()[0])
            if status_number:
                now_number += 1
                n = current_product.get("added_history", "{}")
                added_history = json.loads(n)
                added_history[str(now_number)] = datetime.now().isoformat()
                added_history_json = json.dumps(added_history)
                self.cursor.execute("""
                                  UPDATE products
                                  SET number = ?,
                                  added_history = ?
                                  WHERE product_name = ? AND expiry_date = ?
                                """, (now_number, added_history_json, product_name, expiry_date,))
                self.conn.commit()
            else:
                now_number -= 1
                if now_number < 0:
                    now_number = 0
                else:
                    n = current_product.get("removed_history", "{}")
                    removed_history = json.loads(n)
                    if str(1) not in removed_history:
                        removed_history[str(1)] = [datetime.now().isoformat()]
                    else:
                        removed_history[str(1)].append(datetime.now().isoformat())
                    removed_history_json = json.dumps(removed_history)
                    self.cursor.execute("""
                                      UPDATE products
                                      SET number = ?,
                                      removed_history = ?
                                      WHERE product_name = ? AND expiry_date = ?
                                    """, (now_number, removed_history_json, product_name, expiry_date,))
                    self.conn.commit()
            return now_number, f"Количество продукта с name = {product_name} и expiry_date = {expiry_date} обновлено"
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
            if row[5] > 0:
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


    def _row_to_dict(self, row):
        """Преобразует строку из БД в словарь."""
        nutrition_info = row[8]
        return {
            "id": row[0],
            "product_name": row[1],
            "product_type": row[2],
            "manufacture_date": row[3],
            "expiry_date": row[4],
            "number": row[5],
            "quantity": row[6],
            "unit": row[7],
            "nutrition_info": json.loads(nutrition_info) if nutrition_info else None,
            "measurement_type": row[9],
            "added_history": row[10] if row[10] else None,
            "removed_history": row[11] if row[11] else None
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

    def add_to_shopping_list(self, product_id, product_name, quantity):
        """Добавляет продукт в список покупок."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")

        try:
            self.cursor.execute("""
                INSERT INTO shopping_list (id, product_name, quantity)
                VALUES (?, ?, ?)
            """, (product_id, product_name, quantity,))
            self.conn.commit()
            return True, "Продукт успешно добавлен в список покупок."
        except Exception as e:
            self.conn.rollback()
            return False, f"Ошибка добавления продукта в список покупок: {e}"

    def update_shopping_list_quantity(self, product_name, new_quantity):
        """Обновляет количество продукта."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")
        try:
            self.cursor.execute("""
                  UPDATE shopping_list
                  SET quantity = ?
                  WHERE product_name = ?
                """, (int(new_quantity), product_name,))
            self.conn.commit()
            return product_name, f"Количество продукта в корзине с name = {product_name} обновлено"
        except Exception as e:
            self.conn.rollback()
            return False, f"Ошибка при обновлении количества продукта: {e}"

    def remove_from_shopping_list(self, product_name):
        """Удаляет продукт из списка покупок по product_name."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")

        try:
            self.cursor.execute("DELETE FROM shopping_list WHERE product_name = ?", (product_name,))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return True, "Продукт успешно удален из списка покупок."
            else:
                return False, "Продукт с таким product_name не найден в списке покупок."
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

    def get_count_of_notifications(self):
        products0 = self.get_products_expiring_soon(0)
        products1 = self.get_products_expiring_soon(1)
        new_notifications = False
        if len(products0) != 0 or len(products1) != 0:
            new_notifications = True
        notification_count = 0
        id0 = []
        for e in products0:
            id0.append(e['id'])
        id1 = []
        for e in products1:
            id1.append(e['id'])
        id1 = list(set(id1) - set(id0))
        products1_1 = []
        for e in products1:
            if e['id'] in id1:
                products1_1.append(e)
        notification_count += len(products1_1) + len(products0)
        return new_notifications, notification_count, products0, products1_1

    def get_products_expiring_soon(self, days=7):
        """Получает продукты, у которых истекает срок годности в течение days дней."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")

        today = datetime.now().date()
        cutoff_date = today + timedelta(days=days)
        self.cursor.execute("SELECT * FROM products WHERE expiry_date BETWEEN ? AND ? and is_notification_read = 0",
                            (today.isoformat(), cutoff_date.isoformat()))
        rows = self.cursor.fetchall()
        products = []
        for row in rows:
            product = self._row_to_dict(row)
            products.append(product)
        return products

    def update_products_expiring_soon(self, product_id):
        """Получает продукты, у которых истекает срок годности в течение days дней."""
        if not self.conn or not self.cursor:
            raise Exception("Нет подключения к БД. Сначала нужно вызвать connect()")

        self.cursor.execute(
        'UPDATE products SET is_notification_read = 1 WHERE id = ?',
        (product_id,)
    )
        self.conn.commit()
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
        end_date = (datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
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
            n = product.get("added_history", "{}")
            if n:
                added_history = json.loads(n)
                for number, date_str in added_history.items():
                    added_date = datetime.fromisoformat(date_str)
                    if start_datetime <= added_date <= end_datetime:
                        added_count += 1

            n = product.get("removed_history", "{}")
            if n:
                removed_history = json.loads(n)
                for number, date_str in removed_history.items():
                    for e in date_str:
                        removed_date = datetime.fromisoformat(e)
                        if start_datetime <= removed_date <= end_datetime:
                            removed_count += 1

            n = product.get("added_history", "{}")
            if n:
                last_added_quantity = 0
                last_added_date = None
                added_history = json.loads(n)
                for number, date_str in added_history.items():
                    added_date = datetime.fromisoformat(date_str)
                    if start_datetime <= added_date <= end_datetime:
                        if not last_added_date or added_date > last_added_date:
                            last_added_quantity = int(number)
                            last_added_date = added_date
                if last_added_quantity != 0:
                    if product["product_name"] not in quantity_diffs:
                        quantity_diffs[product["product_name"]] = [last_added_quantity, 0]
                    else:
                        quantity_diffs[product["product_name"]] = [quantity_diffs[product["product_name"]][0] + last_added_quantity, quantity_diffs[product["product_name"]][1]]
            n = product.get("removed_history", "{}")
            if n:
                last_removed_quantity = 0
                last_removed_date = None
                removed_history = json.loads(n)
                for number, date_str in removed_history.items():
                    for e in date_str:
                        removed_date = datetime.fromisoformat(e)
                        if start_datetime <= removed_date <= end_datetime:
                            if not last_removed_date or removed_date > last_removed_date:
                                last_removed_quantity += int(number)
                                last_removed_date = removed_date
                if last_removed_quantity != 0:
                    if product["product_name"] not in quantity_diffs:
                        quantity_diffs[product["product_name"]] = [0, last_removed_quantity]
                    else:
                        print(last_removed_quantity)
                        print(quantity_diffs)
                        print(product)
                        print(product["product_name"])
                        print(quantity_diffs.get(product["product_name"]))
                        print(quantity_diffs[product["product_name"]][1])
                        quantity_diffs[product["product_name"]] = [quantity_diffs[product["product_name"]][0], quantity_diffs[product["product_name"]][1] + last_removed_quantity]
        print(quantity_diffs)
        return {
            "added_count": added_count,
            "removed_count": removed_count,
            "quantity_diffs": [{"product_name": name, 'diff': [diff[0], diff[1]]} for name, diff in
                               quantity_diffs.items()]
        }
