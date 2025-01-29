from flask import Flask, render_template, url_for, request, Flask, render_template, request, redirect, url_for, jsonify
from database import DatabaseManager
from qr_scaner import safe_qr_decode, process_image
from user_agents import parse
import time
from datetime import datetime, timedelta
from pyzbar.pyzbar import decode
from PIL import Image, ImageOps
import io
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


dm = DatabaseManager()
dm.connect()
dm.create_tables()

app = Flask(__name__)

products = []

# cart = []

@app.route('/')
def index():
    products = dm.get_all_products()
    products.sort(key=lambda x: x['product_name'])
    user_agent = request.headers.get('User-Agent')
    user_agent_parsed = parse(user_agent)
    parameter_value = user_agent_parsed.is_mobile

    search_query = request.args.get('search', '')
    selected_category = request.args.get('product_type', '')

    filtered_products = []
    for p in products:
        if ((search_query.lower() in p['product_name'].lower())
                and (selected_category == '' or p['product_type'] == selected_category)):
            if p['unit'] == 'шт.':
                p['quantity'] = int(p['quantity'])
            filtered_products.append(p)

    current_date = datetime.now()
    for e in products:
        exp_date = datetime.strptime(e['expiry_date'], "%Y-%m-%d")
        days_remaining = (exp_date - current_date).days
        if days_remaining > 0:
            e['days'] = days_remaining
        else:
            e['days'] = 0

    # today = datetime.now().date()
    # cutoff_date = today + datetime.timedelta(days=days)
    # now = datetime.now()
    # current_time = now.strftime("%H:%M")
    # if current_time == '6:00':
    #     exp_products_3 = dm.get_products_expiring_soon(3)
    #     exp_products_2 = dm.get_products_expiring_soon(2)
    #     exp_products_1 = dm.get_products_expiring_soon(1)
    #     exp_products_0 = dm.get_products_expiring_soon(0)
    #     print(exp_products_3)
    #     print(1)

    return render_template('index.html', products=filtered_products, search_query=search_query,
                           product_type=selected_category, parameter_value=parameter_value)

@app.route('/product/<int:product_id>')
def product(product_id):
    products = dm.get_all_products()
    products.sort(key=lambda x: x['product_name'])
    user_agent = request.headers.get('User-Agent')
    user_agent_parsed = parse(user_agent)
    parameter_value = user_agent_parsed.is_mobile  # Определяем parameter_value

    product_info = next((p for p in products if p['id'] == product_id), None)
    return render_template('product.html', product=product_info, parameter_value=parameter_value)
# Страница уведомлений
@app.route('/notifications')
def notifications():
    user_agent = request.headers.get('User-Agent')
    user_agent_parsed = parse(user_agent)
    parameter_value = user_agent_parsed.is_mobile

    return render_template('notifications.html',  parameter_value=parameter_value)


# Страница аналитики
@app.route('/analytics')
def analytics():
    user_agent = request.headers.get('User-Agent')
    user_agent_parsed = parse(user_agent)
    parameter_value = user_agent_parsed.is_mobile

    return render_template('analytics.html',  parameter_value=parameter_value)


# Страница списка покупок
@app.route('/shopping-list')
def shopping_list():
    user_agent = request.headers.get('User-Agent')
    user_agent_parsed = parse(user_agent)
    parameter_value = user_agent_parsed.is_mobile

    return render_template('shopping_list.html',  parameter_value=parameter_value)


@app.route('/qr')
def qr():
    user_agent = request.headers.get('User-Agent')
    user_agent_parsed = parse(user_agent)
    parameter_value = user_agent_parsed.is_mobile

    return render_template('qr.html',  parameter_value=parameter_value)


@app.route('/usebd/', methods=['POST'])
def use_bd():
    sp = request.json
    item = dm.get_product_in_bd(sp['product_name'], sp['expiry_date'])
    print(item)
    return jsonify(item)


@app.route('/addproduct/', methods=['POST'])
def add_product():
    sp = request.json
    print(1, sp)
    dm.add_product_in_bd(sp)
    return sp



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

        return jsonify({'success': False, 'message': 'QR code not found'})

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Server error'}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0',
        port=5000,
        debug=False,  # Важно для production!
        threaded=True)
