from flask import  Flask, render_template, request, jsonify
from database import DatabaseManager
from qr_scaner import safe_qr_decode, process_image
from user_agents import parse
from datetime import datetime
import logging

# создание и подключение необходимых элементов

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dm = DatabaseManager()
dm.connect()
dm.create_tables()

app = Flask(__name__)

products = []

# главная страница
@app.route('/')
def index():
    # получение всех продуктов из БД
    products = dm.get_all_products()
    products.sort(key=lambda x: x['product_name'])

    # скрытие кнопки сканирования на ПК
    user_agent = request.headers.get('User-Agent')
    user_agent_parsed = parse(user_agent)
    parameter_value = user_agent_parsed.is_mobile

    # строка поиска
    search_query = request.args.get('search', '')
    selected_category = request.args.get('product_type', '')

    # поиск по типу товара
    filtered_products = []
    for p in products:
        if ((search_query.lower() in p['product_name'].lower())
                and (selected_category == '' or p['product_type'] == selected_category)):
            filtered_products.append(p)

    # отображение срока годности на главной странице
    current_date = datetime.now()
    for e in products:
        exp_date = datetime.strptime(e['expiry_date'], "%Y-%m-%d")
        days_remaining = (exp_date - current_date).days + 1
        if days_remaining > 0:
            e['days'] = days_remaining
        else:
            e['days'] = 0

    # поиск по категориям
    category = []
    for e in filtered_products:
        category.append(e['product_type'])
    category = list(set(category))
    category.sort()

    # отображение количества уведомлений на кнопке "уведомления"
    count_of_notifications = dm.get_count_of_notifications()
    new_notifications = count_of_notifications[0]
    notification_count = count_of_notifications[1]

    return render_template('index.html', products=filtered_products, search_query=search_query,
                           product_type=selected_category, parameter_value=parameter_value,
                           category=category, new_notifications=new_notifications,
                           notification_count=notification_count)

# страница продукта
@app.route('/product/<int:product_id>')
def product(product_id):
    # скрытие кнопки сканирования на ПК
    user_agent = request.headers.get('User-Agent')
    user_agent_parsed = parse(user_agent)
    parameter_value = user_agent_parsed.is_mobile  # Определяем parameter_value

    # получение нужного товара и информации о нём по id
    products = dm.get_all_products()
    products.sort(key=lambda x: x['product_name'])
    product_info = next((p for p in products if p['id'] == product_id), None)

    # отображение количества уведомлений на кнопке "уведомления"
    count_of_notifications = dm.get_count_of_notifications()
    new_notifications = count_of_notifications[0]
    notification_count = count_of_notifications[1]

    return render_template('product.html', product=product_info,
                           parameter_value=parameter_value, new_notifications=new_notifications,
                           notification_count=notification_count)


# Страница уведомлений
@app.route('/notifications')
def notifications():
    # скрытие кнопки сканирования на ПК
    user_agent = request.headers.get('User-Agent')
    user_agent_parsed = parse(user_agent)
    parameter_value = user_agent_parsed.is_mobile

    # отображение количества уведомлений на кнопке "уведомления
    # передача информации о продуктах, у которых завтра истекает срок годности, или уже истёк"
    count_of_notifications = dm.get_count_of_notifications()
    new_notifications = count_of_notifications[0]
    notification_count = count_of_notifications[1]
    products0 = count_of_notifications[2]
    products1_1 = count_of_notifications[3]

    return render_template('notifications.html',  parameter_value=parameter_value,
                           products1=products1_1, products0=products0, new_notifications=new_notifications,
                           notification_count=notification_count)


# Страница аналитики
@app.route('/analytics')
def analytics():
    # скрытие кнопки сканирования на ПК
    user_agent = request.headers.get('User-Agent')
    user_agent_parsed = parse(user_agent)
    parameter_value = user_agent_parsed.is_mobile

    # отображение количества уведомлений на кнопке "уведомления
    count_of_notifications = dm.get_count_of_notifications()
    new_notifications = count_of_notifications[0]
    notification_count = count_of_notifications[1]

    return render_template('analytics.html',  parameter_value=parameter_value,
                           new_notifications=new_notifications,
                           notification_count=notification_count)


# Страница списка покупок
@app.route('/shopping-list')
def shopping_list():
    # скрытие кнопки сканирования на ПК
    user_agent = request.headers.get('User-Agent')
    user_agent_parsed = parse(user_agent)
    parameter_value = user_agent_parsed.is_mobile

    # получение содержания корзины
    cart = dm.get_all_shopping_list()

    # отображение количества уведомлений на кнопке "уведомления
    count_of_notifications = dm.get_count_of_notifications()
    new_notifications = count_of_notifications[0]
    notification_count = count_of_notifications[1]

    return render_template('shopping_list.html',  parameter_value=parameter_value, cart=cart
                           , new_notifications=new_notifications,
                           notification_count=notification_count
                           )

# страница сканирования QR
@app.route('/qr')
def qr():
    # скрытие кнопки сканирования на ПК
    user_agent = request.headers.get('User-Agent')
    user_agent_parsed = parse(user_agent)
    parameter_value = user_agent_parsed.is_mobile

    # отображение количества уведомлений на кнопке "уведомления
    count_of_notifications = dm.get_count_of_notifications()
    new_notifications = count_of_notifications[0]
    notification_count = count_of_notifications[1]

    return render_template('qr.html',  parameter_value=parameter_value,
                           new_notifications=new_notifications,
                           notification_count=notification_count)


# функции запроса к БД, значение понятно из названия
@app.route('/usebd/', methods=['POST'])
def use_bd():
    sp = request.json
    item = dm.get_product_in_bd(sp['product_name'], sp['expiry_date'])
    return jsonify(item)

@app.route('/addtoshoppinglist/', methods=['POST'])
def add_toshoppinglist():
    sp = request.json
    item = dm.add_to_shopping_list(int(sp['id']), sp['product_name'], sp['quantity'])
    return sp

@app.route('/updateshopinglistquantity/', methods=['POST'])
def updateshoping_listquantity():
    sp = request.json
    item = dm.update_shopping_list_quantity(sp['product_name'], sp['quantity'])
    return sp

@app.route('/removefromshoppinglist/', methods=['POST'])
def removefromshopping_list():
    sp = request.json
    item = dm.remove_from_shopping_list(sp['product_name'])
    return sp

@app.route('/addproduct/', methods=['POST'])
def add_product():
    sp = request.json
    dm.add_product_in_bd(sp)
    return sp

@app.route('/del_item/', methods=['POST'])
def delitem():
    sp = request.json
    now_number = dm.update_product_quantity(sp['product_name'], sp['expiry_date'], False)
    now_number = {'number':int(now_number[0])}
    return now_number


@app.route('/add_item/', methods=['POST'])
def additem():
    sp = request.json
    now_number = dm.update_product_quantity(sp['product_name'], sp['expiry_date'], True)
    now_number = {'number': int(now_number[0])}
    return now_number


@app.route('/getanalytics/', methods=['POST'])
def get_analytics():
    sp = request.json
    analytics = dm.get_consumption_analytics(sp['start_date'], sp['end_date'])
    return jsonify(analytics)


@app.route('/mark_as_read/<int:product_id>', methods=['POST'])
def mark_as_read(product_id):
    print(product_id)
    updat = dm.update_products_expiring_soon(product_id)
    return jsonify({'status': 'success'})


# функция необходимая для сканирования QR
@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image part'}), 400

        file = request.files['image']
        if not file or file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Чтение и обработка изображения
        file_stream = file.read()
        img = process_image(file_stream)
        if not img:
            return jsonify({'error': 'Invalid image'}), 400

        # Декодирование с обработкой исключений
        qr_codes = safe_qr_decode(img)

        if qr_codes:
            qr_data = qr_codes[0].data.decode('utf-8')
            logger.info(f"Decoded QR: {qr_data}")
            return jsonify({'success': True, 'qr_data': qr_data})

        return jsonify({'success': False, 'message': 'QR код не найден'})

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Server error'}), 500


# запуск сайта
if __name__ == "__main__":
    app.run(host='0.0.0.0',
        port=5000,
        debug=False,  # Важно для production!
        threaded=True)
