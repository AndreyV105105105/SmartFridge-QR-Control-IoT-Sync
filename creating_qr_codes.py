import qrcode
import json
import os

products = [
    {
        'product_name': 'Батон',
        'product_type': 'Хлеб',
        'manufacture_date': '2025-02-10',
        'expiry_date': '2025-02-22',
        'quantity': 0.5,
        'unit': 'кг',
        "nutrition_info": {'calories': 250, 'proteins': 5, 'fats': 3, 'carbohydrates': 45},
        'measurement_type': 'вес'
    },
    {
        'product_name': 'Яйцо',
        'product_type': 'Яйца',
        'manufacture_date': '2025-02-01',
        'expiry_date': '2025-02-10',
        'quantity': 12,
        'unit': 'шт.',
        'nutrition_info': {'calories': 155, 'proteins': 13, 'fats': 11, 'carbohydrates': 1},
        'measurement_type': 'штуки'
    },
    {
        'product_name': 'Сыр',
        'product_type': 'Молочка',
        'manufacture_date': '2025-02-05',
        'expiry_date': '2025-02-09',
        'quantity': 0.2,
        'unit': 'кг',
        'nutrition_info': {'calories': 350, 'proteins': 25, 'fats': 27, 'carbohydrates': 1},
        'measurement_type': 'вес'
    },
    {
        'product_name': 'Яблоко',
        'product_type': 'Фрукты',
        'manufacture_date': '2025-02-08',
        'expiry_date': '2025-03-15',
        'quantity': 1,
        'unit': 'кг',
        'nutrition_info': {'calories': 52, 'proteins': 0.3, 'fats': 0.2, 'carbohydrates': 14},
        'measurement_type': 'вес'
    },
    {
        'product_name': 'Морковь',
        'product_type': 'Овощи',
        'manufacture_date': '2025-02-07',
        'expiry_date': '2025-03-20',
        'quantity': 0.5,
        'unit': 'кг',
        'nutrition_info': {'calories': 41, 'proteins': 0.9, 'fats': 0.2, 'carbohydrates': 10},
        'measurement_type': 'вес'
    },
    {
        'product_name': 'Банан',
        'product_type': 'Фрукты',
        'manufacture_date': '2025-02-09',
        'expiry_date': '2025-03-12',
        'quantity': 1,
        'unit': 'кг',
        'nutrition_info': {'calories': 89, 'proteins': 1.1, 'fats': 0.3, 'carbohydrates': 23},
        'measurement_type': 'вес'
    },
    {
        'product_name': 'Помидор',
        'product_type': 'Овощи',
        'manufacture_date': '2025-02-06',
        'expiry_date': '2025-03-18',
        'quantity': 0.5,
        'unit': 'кг',
        'nutrition_info': {'calories': 18, 'proteins': 0.9, 'fats': 0.2, 'carbohydrates': 3.9},
        'measurement_type': 'вес'
    },
    {
        'product_name': 'Груша',
        'product_type': 'Фрукты',
        'manufacture_date': '2025-02-04',
        'expiry_date': '2025-03-10',
        'quantity': 1,
        'unit': 'кг',
        'nutrition_info': {'calories': 57, 'proteins': 0.4, 'fats': 0.1, 'carbohydrates': 15},
        'measurement_type': 'вес'
    },
    {
        'product_name': "Кабачок",
        "product_type": "Овощи",
        "manufacture_date": "2025-02-03",
        "expiry_date": "2025-03-25",
        "quantity": 0.6,
        "unit": "кг",
        "nutrition_info": {"calories": 16, "proteins": 1.2, "fats": 0.2, "carbohydrates": 3.1},
        "measurement_type": "вес"
    },
    {
        "product_name": "Киви",
        "product_type": "Фрукты",
        "manufacture_date": "2025-02-02",
        "expiry_date": "2025-02-08",
        "quantity": 1,
        "unit": "кг",
        "nutrition_info": {"calories": 61, "proteins": 1.1, "fats": 0.5, "carbohydrates": 15},
        "measurement_type": "вес"
    }
]



names = [
    "Bread",
    "Eggs",
    "Cheese",
    "Apple",
    "Carrot",
    "Banana",
    "Tomato",
    "Pear",
    "Zucchini",
    "Kiwi"
]

# Создать директорию для QR-кодов, если она не существует
if not os.path.exists(r"C:\projects\Python\fundamental_python\DATA_BASES\qr_codes"):
    os.makedirs(r"C:\projects\Python\fundamental_python\DATA_BASES\qr_codes")


# Генерация QR-кодов
for prod, n in zip(products, names):

    # Преобразовать словарь в JSON-строку
    product_json = json.dumps(prod, ensure_ascii=False)

    # Создать QR-код
    qr = qrcode.make(product_json)

    # Создать имя файла из переведенного названия
    # Заменить пробелы на подчеркивания и добавить расширение .png
    file_name = fr"C:\projects\Python\fundamental_python\DATA_BASES\qr_codes/{n.replace(' ', '_')}.png"

    # Сохранить QR-код в файл
    qr.save(file_name)