[![Maintainability](https://qlty.sh/gh/VaDKustiK/projects/practice1/maintainability.svg)](https://qlty.sh/gh/VaDKustiK/projects/practice1)


# ООО «Обувь» — Обувной магазин

Веб приложение обувного магазина, созданное с использованием Flask, SQLite, и Bootstrap 5.

## Project Structure

```
shoe_store/
├── app.py                  # Flask app with all routes
├── database.py             # Database initialization and CRUD functions
├── import_data.py          # Excel data import module
├── requirements.txt        # Python dependencies
├── shoe_store.db           # SQLite database (auto-created on first run)
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── login.html
│   ├── products.html
│   ├── product_form.html
│   ├── orders.html
│   └── order_form.html
├── static/
│   ├── style.css           # Brand color overrides
│   └── images/             # Product photos
│       ├── logo.png        # Logo for login page
│       └── picture.png     # Placeholder for missing product photos
└── resources/              # Excel files for data import
    ├── Tovar.xlsx
    ├── user_import.xlsx
    ├── Пункты_выдачи_import.xlsx
    └── Заказ_import.xlsx
```