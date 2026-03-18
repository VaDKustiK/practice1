from flask import Flask
from flask import render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename
from PIL import Image

from database import (
    init_db,
    authenticate_user,
    get_all_products,
    get_product_by_id,
    add_product,
    update_product,
    delete_product,
    product_in_orders,
    get_all_orders,
    get_order_by_id,
    add_order,
    update_order,
    delete_order,
    get_suppliers,
    get_manufacturers,
    get_categories,
    get_pickup_points,
    get_clients
)

from import_data import import_if_empty

app = Flask(__name__)
app.secret_key = "verysecretkey"

UPLOAD_FOLDER = "static/images"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
init_db()
import_if_empty()


def require_role(*roles):
    # return a redirect response when access is denied
    # route handlers can early-return this value
    if "role" not in session:
        return redirect(url_for("login"))
    if session["role"] not in roles:
        flash("Недостаточно прав доступа.", "danger")
        return redirect(url_for("products"))
    return None


def save_product_photo(file, old_path=None):
    if not file or file.filename == "":
        return old_path
    # replace previous custom image file but never delete the shared placeholder
    if old_path and os.path.exists(old_path) and 'picture.png' not in old_path:
        try:
            os.remove(old_path)
        except Exception:
            pass

    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)

    img = Image.open(file)
    img = img.resize((300, 200), Image.LANCZOS)
    img.save(save_path)
    # static URL generation works on Windows
    return save_path.replace("\\", "/")


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if "guest" in request.form:
            session["full_name"] = "Гость"
            session["role"] = "Гость"
            return redirect(url_for("products"))

        login_input = request.form.get("login", "")
        password_input = request.form.get("password", "")

        user = authenticate_user(login_input, password_input)
        if user:
            session["user_id"] = user["user_id"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role_name"]
            return redirect(url_for("products"))

        flash("Неверный логин или пароль.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/products")
def products():
    if "role" not in session:
        return redirect(url_for("login"))

    search = request.args.get("search", "")
    supplier_id = request.args.get("supplier_id", "")
    sort = request.args.get("sort", "")

    product_list = get_all_products(
        search=search or None,
        supplier_id=int(supplier_id) if supplier_id else None,
        sort=sort or None
    )

    return render_template(
        "products.html",
        products=product_list,
        suppliers=get_suppliers(),
        search=search,
        selected_supplier=supplier_id,
        sort=sort
    )


@app.route("/products/add", methods=["GET", "POST"])
def product_add():
    check = require_role("Администратор")
    if check:
        return check

    if request.method == "POST":
        photo = request.files.get("photo")
        photo_path = save_product_photo(photo)

        product_data = {
            "article": request.form["article"],
            "name": request.form["name"],
            "unit": request.form["unit"],
            "price": float(request.form["price"]),
            "supplier_id": int(request.form["supplier_id"]),
            "manufacturer_id": int(request.form["manufacturer_id"]),
            "category_id": int(request.form["category_id"]),
            "discount": int(request.form.get("discount", 0)),
            "stock_qty": int(request.form["stock_qty"]),
            "description": request.form.get("description", "").strip() or None,
            "photo_path": photo_path
        }

        try:
            add_product(product_data)
            flash("Товар успешно добавлен.", "success")
            return redirect(url_for("products"))
        except Exception as e:
            flash(f"Ошибка при добавлении товара: {str(e)}", "danger")

    return render_template(
        "product_form.html",
        product=None,
        suppliers=get_suppliers(),
        manufacturers=get_manufacturers(),
        categories=get_categories()
    )


@app.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
def product_edit(product_id):
    check = require_role("Администратор")
    if check:
        return check

    product = get_product_by_id(product_id)
    if not product:
        flash("Товар не найден.", "danger")
        return redirect(url_for("products"))

    locked_product_id = session.get("product_edit_lock_id")
    if request.method == "GET":
        if locked_product_id and locked_product_id != product_id:
            flash(
                "Уже открыто другое окно редактирования товара. "
                "Сначала сохраните или отмените текущее редактирование.",
                "warning"
            )
            return redirect(url_for("products"))
        session["product_edit_lock_id"] = product_id

    if request.method == "POST":
        if locked_product_id and locked_product_id != product_id:
            flash("Невозможно редактировать несколько товаров одновременно.", "warning")
            return redirect(url_for("products"))

        photo = request.files.get("photo")
        photo_path = save_product_photo(photo, product["photo_path"])

        product_data = {
            "name": request.form["name"],
            "unit": request.form["unit"],
            "price": float(request.form["price"]),
            "supplier_id": int(request.form["supplier_id"]),
            "manufacturer_id": int(request.form["manufacturer_id"]),
            "category_id": int(request.form["category_id"]),
            "discount": int(request.form.get("discount", 0)),
            "stock_qty": int(request.form["stock_qty"]),
            "description": request.form.get("description", "").strip() or None,
            "photo_path": photo_path
        }

        try:
            update_product(product_id, product_data)
            session.pop("product_edit_lock_id", None)
            flash("Товар успешно обновлен.", "success")
            return redirect(url_for("products"))
        except Exception as e:
            flash(f"Ошибка при обновлении товара: {str(e)}", "danger")

    return render_template(
        "product_form.html",
        product=product,
        suppliers=get_suppliers(),
        manufacturers=get_manufacturers(),
        categories=get_categories()
    )


@app.route("/products/edit/unlock", methods=["POST"])
def product_edit_unlock():
    check = require_role("Администратор")
    if check:
        return check

    session.pop("product_edit_lock_id", None)
    return redirect(url_for("products"))


@app.route("/products/delete/<int:product_id>", methods=["POST"])
def product_delete(product_id):
    check = require_role("Администратор")
    if check:
        return check

    product = get_product_by_id(product_id)
    if not product:
        flash("Товар не найден.", "danger")
        return redirect(url_for("products"))

    if product_in_orders(product["article"]):
        flash(
            f"Товар «{product['name']}» нельзя удалить: он в заказах.",
            "danger"
        )
        return redirect(url_for("products"))

    try:
        if product["photo_path"] and os.path.exists(product["photo_path"]):
            if 'picture.png' not in product["photo_path"]:
                os.remove(product["photo_path"])

        delete_product(product_id)
        flash("Товар успешно удален.", "success")
    except Exception as e:
        flash(f"Ошибка при удалении товара: {str(e)}", "danger")

    return redirect(url_for("products"))


@app.route("/orders")
def orders():
    check = require_role("Менеджер", "Администратор")
    if check:
        return check

    order_list = get_all_orders()
    return render_template("orders.html", orders=order_list)


@app.route("/orders/add", methods=["GET", "POST"])
def order_add():
    check = require_role("Администратор")
    if check:
        return check

    if request.method == "POST":
        order_data = {
            "articles": request.form["articles"],
            "order_date": request.form["order_date"],
            "delivery_date": request.form["delivery_date"],
            "pickup_point_id": int(request.form["pickup_point_id"]),
            "user_id": int(request.form["user_id"]),
            "pickup_code": request.form["pickup_code"],
            "status": request.form["status"]
        }

        try:
            add_order(order_data)
            flash("Заказ успешно добавлен.", "success")
            return redirect(url_for("orders"))
        except Exception as e:
            flash(f"Ошибка при добавлении заказа: {str(e)}", "danger")

    return render_template(
        "order_form.html",
        order=None,
        pickup_points=get_pickup_points(),
        clients=get_clients()
    )


@app.route("/orders/edit/<int:order_id>", methods=["GET", "POST"])
def order_edit(order_id):
    check = require_role("Администратор")
    if check:
        return check

    order = get_order_by_id(order_id)
    if not order:
        flash("Заказ не найден.", "danger")
        return redirect(url_for("orders"))

    if request.method == "POST":
        order_data = {
            "articles": request.form["articles"],
            "order_date": request.form["order_date"],
            "delivery_date": request.form["delivery_date"],
            "pickup_point_id": int(request.form["pickup_point_id"]),
            "user_id": int(request.form["user_id"]),
            "pickup_code": request.form["pickup_code"],
            "status": request.form["status"]
        }

        try:
            update_order(order_id, order_data)
            flash("Заказ успешно обновлен.", "success")
            return redirect(url_for("orders"))
        except Exception as e:
            flash(f"Ошибка при обновлении заказа: {str(e)}", "danger")

    return render_template(
        "order_form.html",
        order=order,
        pickup_points=get_pickup_points(),
        clients=get_clients()
    )


@app.route("/orders/delete/<int:order_id>", methods=["POST"])
def order_delete(order_id):
    check = require_role("Администратор")
    if check:
        return check

    order = get_order_by_id(order_id)
    if not order:
        flash("Заказ не найден.", "danger")
        return redirect(url_for("orders"))

    try:
        delete_order(order_id)
        flash("Заказ успешно удален.", "success")
    except Exception as e:
        flash(f"Ошибка при удалении заказа: {str(e)}", "danger")

    return redirect(url_for("orders"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
