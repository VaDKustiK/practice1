import sqlite3

DB_PATH = "shoe_store.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS supplier (
            supplier_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manufacturer (
            manufacturer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer_name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS category (
            category_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pickup_point (
            pickup_point_id INTEGER PRIMARY KEY AUTOINCREMENT,
            address         TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS role (
            role_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id   INTEGER NOT NULL REFERENCES role(role_id),
            full_name TEXT NOT NULL,
            login     TEXT NOT NULL UNIQUE,
            password  TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product (
            product_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            article         TEXT NOT NULL UNIQUE,
            name            TEXT NOT NULL,
            unit            TEXT NOT NULL DEFAULT 'шт.',
            price           REAL NOT NULL CHECK(price >= 0),
            supplier_id     INTEGER NOT NULL REFERENCES supplier(supplier_id),
            manufacturer_id INTEGER NOT NULL REFERENCES manufacturer(manufacturer_id),
            category_id     INTEGER NOT NULL REFERENCES category(category_id),
            discount        INTEGER NOT NULL DEFAULT 0 CHECK(discount >= 0 AND discount <= 100),
            stock_qty       INTEGER NOT NULL DEFAULT 0 CHECK(stock_qty >= 0),
            description     TEXT,
            photo_path      TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "order" (
            order_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            articles        TEXT NOT NULL,
            order_date      TEXT NOT NULL,
            delivery_date   TEXT NOT NULL,
            pickup_point_id INTEGER NOT NULL REFERENCES pickup_point(pickup_point_id),
            user_id         INTEGER NOT NULL REFERENCES user(user_id),
            pickup_code     TEXT NOT NULL,
            status          TEXT NOT NULL DEFAULT 'Новый'
        )
    """)

    conn.commit()
    conn.close()


def get_all_products(search=None, supplier_id=None, sort=None):
    conn = get_connection()

    query = """
        SELECT
            p.*,
            s.supplier_name,
            m.manufacturer_name,
            c.category_name
        FROM product p
        JOIN supplier s ON p.supplier_id = s.supplier_id
        JOIN manufacturer m ON p.manufacturer_id = m.manufacturer_id
        JOIN category c ON p.category_id = c.category_id
        WHERE 1=1
    """

    params = []

    if search:
        query += """ AND (
            p.name LIKE ? OR
            p.article LIKE ? OR
            p.description LIKE ? OR
            m.manufacturer_name LIKE ? OR
            s.supplier_name LIKE ? OR
            c.category_name LIKE ?
        )"""
        search_pattern = f"%{search}%"
        # same LIKE pattern is reused for all searchable columns
        params.extend([search_pattern] * 6)

    if supplier_id:
        query += " AND p.supplier_id = ?"
        params.append(supplier_id)

    if sort == "asc":
        query += " ORDER BY p.stock_qty ASC"
    elif sort == "desc":
        query += " ORDER BY p.stock_qty DESC"
    else:
        # Stable default order keeps list consistent when sort is not requested
        query += " ORDER BY p.product_id"

    cursor = conn.cursor()
    cursor.execute(query, params)
    products = cursor.fetchall()
    conn.close()

    return products


def get_product_by_id(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM product WHERE product_id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product


def add_product(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO product (
            article, name, unit, price, supplier_id, manufacturer_id,
            category_id, discount, stock_qty, description, photo_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['article'],
        data['name'],
        data['unit'],
        data['price'],
        data['supplier_id'],
        data['manufacturer_id'],
        data['category_id'],
        data['discount'],
        data['stock_qty'],
        data.get('description'),
        data.get('photo_path') # not required, can return None
    ))

    conn.commit()
    conn.close()


def update_product(product_id, data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE product SET
            name = ?,
            unit = ?,
            price = ?,
            supplier_id = ?,
            manufacturer_id = ?,
            category_id = ?,
            discount = ?,
            stock_qty = ?,
            description = ?,
            photo_path = ?
        WHERE product_id = ?
    """, (
        data['name'],
        data['unit'],
        data['price'],
        data['supplier_id'],
        data['manufacturer_id'],
        data['category_id'],
        data['discount'],
        data['stock_qty'],
        data.get('description'),
        data.get('photo_path'),
        product_id
    ))

    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM product WHERE product_id = ?", (product_id,))
    conn.commit()
    conn.close()


def product_in_orders(article):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT COUNT(*) FROM "order" WHERE articles LIKE ?',
        (f'%{article}%',)
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


def get_all_orders():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            o.*,
            pp.address,
            u.full_name
        FROM "order" o
        JOIN pickup_point pp ON o.pickup_point_id = pp.pickup_point_id
        JOIN user u ON o.user_id = u.user_id
        ORDER BY o.order_id DESC
    """)

    orders = cursor.fetchall()
    conn.close()
    return orders


def get_order_by_id(order_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM "order" WHERE order_id = ?', (order_id,))
    order = cursor.fetchone()
    conn.close()
    return order


def add_order(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO "order" (
            articles, order_date, delivery_date, pickup_point_id,
            user_id, pickup_code, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data['articles'],
        data['order_date'],
        data['delivery_date'],
        data['pickup_point_id'],
        data['user_id'],
        data['pickup_code'],
        data['status']
    ))

    conn.commit()
    conn.close()


def update_order(order_id, data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE "order" SET
            articles = ?,
            order_date = ?,
            delivery_date = ?,
            pickup_point_id = ?,
            user_id = ?,
            pickup_code = ?,
            status = ?
        WHERE order_id = ?
    """, (
        data['articles'],
        data['order_date'],
        data['delivery_date'],
        data['pickup_point_id'],
        data['user_id'],
        data['pickup_code'],
        data['status'],
        order_id
    ))

    conn.commit()
    conn.close()


def delete_order(order_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM "order" WHERE order_id = ?', (order_id,))
    conn.commit()
    conn.close()


def get_suppliers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM supplier ORDER BY supplier_name")
    suppliers = cursor.fetchall()
    conn.close()
    return suppliers


def get_manufacturers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM manufacturer ORDER BY manufacturer_name")
    manufacturers = cursor.fetchall()
    conn.close()
    return manufacturers


def get_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM category ORDER BY category_name")
    categories = cursor.fetchall()
    conn.close()
    return categories


def get_pickup_points():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pickup_point ORDER BY address")
    pickup_points = cursor.fetchall()
    conn.close()
    return pickup_points


def get_clients():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.user_id, u.full_name
        FROM user u
        JOIN role r ON u.role_id = r.role_id
        WHERE r.role_name = 'Авторизированный клиент'
        ORDER BY u.full_name
    """)
    clients = cursor.fetchall()
    conn.close()
    return clients


def authenticate_user(login, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.user_id, u.full_name, r.role_name
        FROM user u
        JOIN role r ON u.role_id = r.role_id
        WHERE u.login = ? AND u.password = ?
    """, (login, password))

    user = cursor.fetchone()
    conn.close()

    return user
