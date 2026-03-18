# ООО «Обувь» — Shoe Store Web Application

Complete web application for a shoe store built with Flask, SQLite, and Bootstrap 5.

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

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Adding Excel Data Files

**IMPORTANT:** Before running the application for the first time, you must add the Excel data files to the `resources/` folder.

Place the following files in the `resources/` directory:
- `Tovar.xlsx` — Product data
- `user_import.xlsx` — User accounts
- `Пункты_выдачи_import.xlsx` — Pickup points
- `Заказ_import.xlsx` — Order data

The application will automatically import this data on the first run when the database is empty.

## Running the Application

Start the Flask development server:
```bash
python app.py
```

The application will be available at **http://localhost:5000**

On first run, the application will:
1. Create the SQLite database (`shoe_store.db`)
2. Create all necessary tables
3. Import data from the Excel files in the `resources/` folder

## User Roles and Permissions

The application supports 4 user roles:

| Role | Permissions |
|------|-------------|
| **Гость** (Guest) | View products only (no search/filter) |
| **Авторизированный клиент** (Authorized Client) | View products only (no search/filter) |
| **Менеджер** (Manager) | View products with search/filter, view orders |
| **Администратор** (Admin) | Full access - manage products and orders |

## Features

### Authentication
- User login with username/password
- Guest access (no registration required)
- Session-based authentication

### Product Management (Admin only)
- Add, edit, delete products
- Upload and resize product photos (300×200 px)
- Automatic article generation
- Delete protection (products used in orders cannot be deleted)

### Product Browsing (All users)
- View product catalog with photos
- Color-coded rows:
  - **Light blue** — Out of stock (stock_qty = 0)
  - **Dark green** — High discount (discount > 15%)
- Price display with discount calculation

### Search and Filtering (Manager + Admin)
- Real-time text search across all product fields
- Filter by supplier
- Sort by stock quantity (ascending/descending)

### Order Management
- View orders (Manager + Admin)
- Add, edit, delete orders (Admin only)
- Track order status (Новый, Завершен, Отменен)

## Technology Stack

- **Backend:** Python 3.x + Flask
- **Database:** SQLite with foreign key constraints
- **Frontend:** Bootstrap 5 (CDN)
- **Icons:** Bootstrap Icons
- **Image Processing:** Pillow
- **Data Import:** openpyxl

## Brand Colors

- **Primary Accent:** #00FA9A (mint green) — main action buttons
- **Secondary:** #7FFF00 (chartreuse) — navbar, table headers
- **High Discount:** #2E8B57 (sea green) — product rows with >15% discount
- **Out of Stock:** #ADD8E6 (light blue) — product rows with 0 stock

## Database Schema

The database uses 3rd Normal Form with the following tables:
- `supplier` — Product suppliers
- `manufacturer` — Product manufacturers
- `category` — Product categories
- `pickup_point` — Order pickup locations
- `role` — User roles
- `user` — User accounts
- `product` — Product catalog
- `order` — Customer orders

All tables have proper foreign key constraints with CASCADE/RESTRICT rules.

## Notes

- Product photos are automatically resized to 300×200 pixels on upload
- The application uses Times New Roman font throughout
- All Russian text uses UTF-8 encoding
- Session secret key should be changed in production
- Passwords are stored in plain text (should use hashing in production)

## Development

To modify the application:
- **Routes:** Edit `app.py`
- **Database queries:** Edit `database.py`
- **Templates:** Edit files in `templates/`
- **Styles:** Edit `static/style.css`
- **Data import:** Edit `import_data.py`

## Troubleshooting

If the database gets corrupted or you want to reimport data:
1. Delete `shoe_store.db`
2. Restart the application — it will recreate everything

If photos are not displaying:
- Ensure photo files are in `static/images/`
- Check that filenames match the database entries
- The placeholder `picture.png` will be shown for missing photos
