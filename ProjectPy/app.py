from flask import Flask, render_template, request, redirect, url_for
import psycopg2
# import jinja2
import requests
from bs4 import BeautifulSoup

# Даем имя нашему приложения на Python с указанием папки с html файлами
app = Flask(__name__, template_folder='templates')


# Определение новой функции для подключения к базе данных
def get_connection():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="1212",
        host="localhost",
        port="5432"
    )
    return conn


# Функция для получения списка сотрудников
def get_employees():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees ORDER BY employee_id ASC")
    rows = cur.fetchall()
    conn.close()
    return rows


# Роут заказа
@app.route('/order', methods=['GET'])
def order():
    if request.method == 'GET':
        conn = get_connection()
        cur = conn.cursor()
        with conn.cursor():
            query = f'SELECT * FROM orders ORDER BY order_id ASC'
            cur.execute(query)
            result = cur.fetchall()
        if conn:
            conn.close()
        return render_template('order.html', products=result)
    else:
        pass
    return app.send_static_file('order.html')


# Функция для выполнения запросов в базу данных
def execute_query(query, params=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    cur.close()
    conn.close()


# Добавление нового сотрудника
@app.route("/add", methods=["POST"])
def add_employee():
    if request.method == "POST":
        last_name = request.form["last_name"]
        first_name = request.form["first_name"]
        middle_name = request.form["middle_name"]
        position = request.form["position"]
        address = request.form["address"]
        phone = request.form["phone"]
        public_number = request.form["public_number"]
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO employees \
            (last_name, first_name, middle_name, position, address, phone, public_number)\
                VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (last_name, first_name, middle_name, position, address, phone, public_number))
        conn.commit()
    return redirect(url_for('director'))


# Роут обновления сотрудников
@app.route("/update", methods=["POST"])
def update_employee():
    if request.method == "POST":
        id = request.form["id"]
        last_name = request.form["last_name"]
        first_name = request.form["first_name"]
        middle_name = request.form["middle_name"]
        position = request.form["position"]
        address = request.form["address"]
        phone = request.form["phone"]
        public_number = request.form["public_number"]
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE employees SET \
            last_name=%s, first_name=%s, middle_name=%s, position=%s, address=%s, phone=%s, public_number=%s \
            WHERE id=%s", (last_name, first_name, middle_name, position, address, phone, public_number, id))
        conn.commit()
    return redirect(url_for('director'))


# Роут обновления сотрудников
@app.route("/update1", methods=["POST"])
def update_employee1():
    if request.method == "POST":
        id = request.form["id"]
        last_name = request.form["last_name"]
        first_name = request.form["first_name"]
        middle_name = request.form["middle_name"]
        position = request.form["position"]
        address = request.form["address"]
        phone = request.form["phone"]
        public_number = request.form["public_number"]
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE employees SET \
            last_name=%s, first_name=%s, middle_name=%s, position=%s, address=%s, phone=%s, public_number=%s \
            WHERE id=%s", (last_name, first_name, middle_name, position, address, phone, public_number, id))
        conn.commit()
    return redirect(url_for('deputydirector'))


# Роут для удаления записи из базы данных
@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        id = request.form['id']
        execute_query('DELETE FROM employees WHERE id = %s', (id,))
        return "Запись удалена"
    else:
        return redirect(url_for('delete'))

    # Главная страница


@app.route('/')
def index():
    return render_template('index.html')


# Поиск информации о клиенте 
@app.route('/search', methods=['POST'])
def search():
    client_name = request.form['name']
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients WHERE client_name = %s", (client_name,))
    client = cur.fetchone()
    if client:
        total_purchase = client[2]
        current_balance = client[3]
        credit_limit = client[4]
        current_debt = client[5]
        remaining_credit = credit_limit - current_debt
        comment = client[7]
        return render_template('search.html', client_name=client_name, total_purchase=total_purchase,
                               current_balance=current_balance, credit_limit=credit_limit,
                               current_debt=current_debt, remaining_credit=remaining_credit,
                               comment=comment)
    else:
        return render_template('search.html', name=client_name, error='Клиент не найден')

    # Роут поиска


@app.route("/search")
def search_employee():
    return render_template("search.html")


# Роут создания заказа
@app.route('/create_order', methods=['GET', 'POST'])
def new_order():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT client_name FROM clients ORDER BY client_id ASC")
    clients = cur.fetchall()
    cur.execute("SELECT product_name FROM products ORDER BY product_id ASC")
    product = cur.fetchall()
    if request.method == 'POST':
        client_name = request.form['client_name']
        product_name = request.form['product_name']
        sale_type = request.form['sale_type']
        quantity = int(request.form['quantity'])
        cur.execute("SELECT price FROM products WHERE product_name = %s", (product_name,))
        price = cur.fetchone()[0]
        cur.execute("SELECT total_purchase FROM clients WHERE client_name = %s", (client_name,))
        total_purchase = cur.fetchone()[0]
        cur.execute("SELECT current_balance FROM clients WHERE client_name = %s", (client_name,))
        current_balance = cur.fetchone()[0]
        cur.execute("SELECT credit_limit FROM clients WHERE client_name = %s", (client_name,))
        credit_limit = cur.fetchone()[0]
        cur.execute("SELECT current_debt FROM clients WHERE client_name = %s", (client_name,))
        current_debt = cur.fetchone()[0]
        cur.execute("SELECT remaining_credit FROM clients WHERE client_name = %s", (client_name,))
        remaining_credit = cur.fetchone()[0]
        cur.execute("SELECT comment FROM clients WHERE client_name = %s", (client_name,))
        cur.execute("SELECT product_quantity FROM products WHERE product_name = %s", (product_name,))
        product_quantity = cur.fetchone()[0]
        if sale_type == 'cash':
            cur.execute("UPDATE clients SET total_purchase = %s WHERE client_name = %s",
                        (total_purchase + price * quantity, client_name))
            cur.execute("UPDATE products SET product_quantity = %s WHERE product_name = %s",
                        (product_quantity - quantity, product_name))
            total_price = price * quantity
        elif sale_type == 'credit':
            if current_balance + price * quantity > credit_limit * 0.9:
                return 'You have reached your credit limit'
            cur.execute(
                "UPDATE clients SET total_purchase = %s, current_debt = %s, remaining_credit = %s WHERE client_name = %s",
                (total_purchase + price * quantity, current_debt * remaining_credit - price * quantity,
                 credit_limit * 0.9 - (current_balance + price * quantity), client_name))
            cur.execute("UPDATE products SET quantity = %s WHERE product_name = %s",
                        (product_quantity - quantity, product_name))
            total_price = price * quantity
        elif sale_type == 'cashless':
            cur.execute("UPDATE clients SET total_purchase = %s WHERE client_name = %s",
                        (total_purchase + price * quantity, client_name))
            cur.execute("UPDATE clients SET current_balance = %s WHERE client_name = %s",
                        (current_balance - price * quantity, client_name))
            cur.execute("UPDATE products SET product_quantity = %s WHERE product_name = %s",
                        (product_quantity - quantity, product_name))
            total_price = price * quantity
        elif sale_type == 'settlement':
            cur.execute(
                "UPDATE clients SET total_purchase = %s, current_debt = %s, remaining_credit = %s WHERE client_name = %s",
                (
                    total_purchase + price * quantity, current_debt - price * quantity,
                    remaining_credit + price * quantity, client_name))
            cur.execute("UPDATE products SET product_quantity = %s WHERE product_name = %s",
                        (product_quantity - quantity, product_name))
            total_price = price * quantity
        else:
            return 'Invalid sale type'
        cur.execute(
            "INSERT INTO orders (client_name, product_name, sale_type, quantity, total_price) VALUES (%s, %s, %s, %s, %s)",
            (client_name, product_name, sale_type, quantity, total_price))
        conn.commit()
    return render_template('create_order.html', clients=clients, products=product)


@app.route('/create_barter_order', methods=['POST', 'GET'])
def create_barter_order():
    conn = get_connection()
    cur = conn.cursor()

    client_name = request.form['client_name']
    product_in = request.form['product_in']
    quantity_in = request.form['quantity_in']
    price_in = get_product_price(product_in) * quantity_in
    product_out = request.form['product_out']
    quantity_out = request.form['quantity_out']
    price_out = get_product_price(product_out) * quantity_out
    if request.method == 'POST':
        if price_in == price_out:
            total_price = 0

            cur.execute(
                "INSERT INTO orders (client_name, product_name, sale_type, quantity, total_price) VALUES (%s, %s, %s, %s, %s)",
                (client_name, product_out, "barter", quantity_out, total_price))
            cur.execute("UPDATE products SET product_quantity = product_quantity + %s WHERE product_name = %s",
                        (quantity_in, product_in))
            cur.execute("UPDATE products SET product_quantity = product_quantity - %s WHERE product_name = %s",
                        (quantity_out, product_out))
            conn.commit()
            cur.close()
            return redirect(url_for('order'))
        elif price_in > price_out:
            total_price = 0
            remains = price_in - price_out
            cur.execute("UPDATE clients SET current_balance = current_balance + %s WHERE client_name = %s",
                        (remains, client_name))
            cur.execute(
                "INSERT INTO orders (client_name, product_name, sale_type, quantity, total_price) VALUES (%s, %s, %s, %s, %s)",
                (client_name, product_out, "barter", quantity_out, total_price))
            cur.execute("UPDATE products SET product_quantity = product_quantity + %s WHERE product_name = %s",
                        (quantity_in, product_in))
            cur.execute("UPDATE products SET product_quantity = product_quantity - %s WHERE product_name = %s",
                        (quantity_out, product_out))
            conn.commit()
            cur.close()
            return redirect(url_for('order'))
        elif price_in < price_out:
            remains = price_out - price_in
            cur.execute("UPDATE clients SET total_purchase = total_purchase - %s WHERE client_name = %s",
                        (remains, client_name))
            cur.execute(
                "INSERT INTO orders (client_name, product_name, sale_type, quantity, total_price) VALUES (%s, %s, %s, %s, %s)",
                (client_name, product_out, "barter", quantity_out, remains))
            cur.execute("UPDATE products SET product_quantity = product_quantity + %s WHERE product_name = %s",
                        (quantity_in, product_in))
            cur.execute("UPDATE products SET product_quantity = product_quantity - %s WHERE product_name = %s",
                        (quantity_out, product_out))
            conn.commit()
            cur.close()
            return redirect(url_for('order'))
        else:
            return "Error: Products are not equal in price"

    else:
        return redirect(url_for('order'))


# Роут стоимости товара
def get_product_price(product_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT price FROM products WHERE product_name = %s", (product_name,))
    price = cur.fetchone()[0]
    cur.close()
    return price


# Роут товара
@app.route('/products', methods=['POST', 'GET'])
def products():
    if request.method == 'GET':
        conn = get_connection()
        cur = conn.cursor()
        with conn.cursor():
            query = f'SELECT * FROM products ORDER BY product_id ASC'
            cur.execute(query)
            result = cur.fetchall()
        if conn:
            conn.close()
        return render_template('products.html', products=result)
    else:
        pass
    return app.send_static_file('products.html')


# Роут добавления товара
@app.route("/add_p", methods=["POST"])
def add_p():
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        quantity = request.form["quantity"]
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO products (product_name, price, product_quantity) VALUES (%s, %s, %s)",
                    (name, price, quantity))
        conn.commit()
    return redirect(url_for('products'))


# Роут изменения количества товара
@app.route("/update_quantity/<int:product_id>", methods=["POST"])
def update_quantity(product_id):
    if request.method == "POST":
        quantity_change = int(request.form['quantity_change'])
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET product_quantity = product_quantity + %s WHERE product_id = %s",
                    (quantity_change, product_id))
        conn.commit()
    return redirect(url_for('products'))


# Роут изменения стоимости товара
@app.route("/update_price/<int:product_id>", methods=["POST"])
def update_price(product_id):
    if request.method == "POST":
        price_change = int(request.form['price_change'])
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET price = %s WHERE product_id = %s", (price_change, product_id))
        conn.commit()
    return redirect(url_for('products'))


# Роут логина
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_connection()
        with conn.cursor() as cursor:
            query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
            cursor.execute(query)
            result = cursor.fetchone()
        if conn:
            conn.close()
        if result:
            if result[1] == 'director':
                return redirect('/director')
            elif result[1] == 'deputydirector':
                return redirect('/deputydirector')
            elif result[1] == 'secretary':
                return redirect('/secretary')
            elif result[1] == 'guest':
                return redirect('/guest')
            else:
                return redirect('/login')
        else:
            return redirect('/login')
    else:
        return render_template('login.html')

    # Роут директора


@app.route('/director', methods=['GET', 'POST'])
def director():
    if request.method == 'GET':
        conn = get_connection()
        cur = conn.cursor()
        with conn.cursor():
            query = f'SELECT * FROM employees ORDER BY id ASC'
            cur.execute(query)
            result = cur.fetchall()
        if conn:
            conn.close()
        return render_template('director.html', employees=result)
    else:
        id = request.form["id"]
        last_name = request.form["last_name"]
        first_name = request.form["first_name"]
        middle_name = request.form["middle_name"]
        position = request.form["position"]
        address = request.form["address"]
        phone = request.form["phone"]
        public_number = request.form["public_number"]
        print(id, last_name, first_name, middle_name, position, address, phone, public_number)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO employees \
            (last_name, first_name, middle_name, position, address, phone)\
                VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (id, last_name, first_name, middle_name, position, address, phone, public_number))
    return app.send_static_file('director.html')


# Роут заместителя директора
@app.route('/deputydirector', methods=['GET', 'POST'])
def deputy_director():
    if request.method == 'GET':
        conn = get_connection()
        cur = conn.cursor()
        with conn.cursor():
            query = f'SELECT * FROM employees ORDER BY id ASC'
            cur.execute(query)
            result = cur.fetchall()
        if conn:
            conn.close()
        return render_template('deputydirector.html', employees=result)
    else:
        id = request.form["id"]
        last_name = request.form["last_name"]
        first_name = request.form["first_name"]
        middle_name = request.form["middle_name"]
        position = request.form["position"]
        address = request.form["address"]
        phone = request.form["phone"]
        public_number = request.form["public_number"]
        print(id, last_name, first_name, middle_name, position, address, phone, public_number)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO employees \
            (last_name, first_name, middle_name, position, address, phone)\
                VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (id, last_name, first_name, middle_name, position, address, phone, public_number))
    return app.send_static_file('deputydirector.html')


# Роут секретаря
@app.route('/secretary', methods=['GET', 'POST'])
def secretary():
    if request.method == 'GET':
        conn = get_connection()
        cur = conn.cursor()
        with conn.cursor():
            query = f'SELECT * FROM employees ORDER BY id ASC'
            cur.execute(query)
            result = cur.fetchall()
        if conn:
            conn.close()
    return render_template('secretary.html', employees=result)


# Роут гостя
app.route('/guest', methods=['GET', 'POST'])


def guest():
    if request.method == 'GET':
        conn = get_connection()
        cur = conn.cursor()
        with conn.cursor():
            query = f'SELECT * FROM employees ORDER BY id ASC'
            cur.execute(query)
            result = cur.fetchall()
        if conn:
            conn.close()
    return render_template('guest.html', employees=result)


# Роут парсинг API
@app.route('/realtime')
def realtime():
    url = "https://openexchangerates.org/api/latest.json?app_id=4beefb5c1ae146168f09d5ffb90360e6&symbols=RUB,EUR,JPY,GBP,CAD,CHF,AUD,CNY,HKD,SEK"
    response = requests.get(url)
    data = response.json()
    return render_template('realtime.html', rates=data['rates'])


# Роут парсинг url
@app.route('/currency')
def currency():
    url = 'https://www.cbr.ru/currency_base/daily/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', attrs={'class': 'data'})
    rows = table.find_all('tr')
    result = ''
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        result += '<tr><td>' + '</td><td>'.join(cols) + '</td></tr>'
    return '<table border="1">' + result + '</table>'


if __name__ == '__main__':
    app.run(debug=True)
