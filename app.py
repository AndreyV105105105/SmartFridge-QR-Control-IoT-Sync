from flask import Flask, render_template, url_for, request, Flask, render_template, request, redirect, url_for
from database import DatabaseManager
from user_agents import parse

dm = DatabaseManager()
dm.connect()
dm.create_tables()

app = Flask(__name__)


products = dm.get_all_products()
products.sort(key=lambda x: x['product_name'])

# cart = []

@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    user_agent_parsed = parse(user_agent)
    parameter_value = user_agent_parsed.is_mobile

    search_query = request.args.get('search', '')
    selected_category = request.args.get('product_type', '')

    filtered_products = [
        p for p in products
        if (search_query.lower() in p['product_name'].lower()) and
           (selected_category == '' or p['product_type'] == selected_category)
    ]
    return render_template('index.html', products=filtered_products, search_query=search_query,
                           product_type=selected_category, parameter_value=parameter_value)

@app.route('/product/<int:product_id>')
def product(product_id):
    product_info = next((p for p in products if p['id'] == product_id), None)
    return render_template('product.html', product=product_info)

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


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
