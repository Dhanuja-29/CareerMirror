# CareerMirror — Flask + PostgreSQL Career Review Platform

A full-stack Glassdoor-style platform built with Flask, SQLAlchemy, and PostgreSQL.

---

## 📁 Project Structure

```
careermirror/
├── app.py              ← Flask routes (Home, Register, Login, Reviews, Admin, API)
├── database.py         ← DB connection, init_db(), seed data
├── models.py           ← SQLAlchemy ORM: User, Company, Review
├── requirements.txt    ← Python dependencies
├── .env                ← Environment variables (DB URL, secret key)
│
├── templates/
│   ├── base.html       ← Nav, flash messages, footer
│   ├── home.html       ← Landing page + company search
│   ├── register.html   ← Registration form
│   ├── login.html      ← Login form
│   ├── company.html    ← Company profile + reviews
│   ├── add_review.html ← Review submission form
│   └── admin.html      ← Admin moderation panel
│
└── static/
    ├── css/style.css   ← Full responsive stylesheet
    └── js/main.js      ← Scroll reveal, nav effects
```

---

## ⚙️ Setup Instructions

### 1. Create & activate a virtual environment

```bash
python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create the PostgreSQL database

```sql
-- In psql or pgAdmin:
CREATE DATABASE careermirror_db;
```

### 4. Configure environment variables

Edit `.env`:

```env
DATABASE_URL=postgresql://YOUR_USER:YOUR_PASSWORD@localhost/careermirror_db
SECRET_KEY=change-this-to-a-random-string
FLASK_ENV=development
FLASK_DEBUG=1
```

### 5. Run the app

```bash
python app.py
```

Flask will:
- Connect to PostgreSQL
- Auto-create all tables (users, companies, reviews)
- Seed 6 sample companies
- Start at http://127.0.0.1:5000

---

## 🔑 Making Yourself Admin

After registering an account, run in `psql` or a DB client:

```sql
UPDATE users SET is_admin = TRUE WHERE email = 'your@email.com';
```

Then visit `/admin` to approve or delete reviews.

---

## 🌐 Routes Summary

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home page with company listing + search |
| `/register` | GET, POST | Create account |
| `/login` | GET, POST | Log in |
| `/logout` | GET | Log out |
| `/company/<id>` | GET | Company profile + approved reviews |
| `/add_review/<id>` | GET, POST | Submit a review (login required) |
| `/admin` | GET | Admin panel – pending + approved reviews |
| `/admin/approve/<id>` | GET | Approve a review (admin only) |
| `/admin/delete/<id>` | GET | Delete a review (admin only) |
| `/api/companies` | GET | JSON API for company search |

---

## 🗄️ Database Schema

```
users      → id, name, email, password (bcrypt), is_admin, created_at
companies  → id, name, location, industry
reviews    → id, review_text, rating, role, approved, created_at,
             user_id (FK→users), company_id (FK→companies)
```

---

## 🚀 Future Improvements

- AI sentiment analysis on review text
- Company ranking leaderboard
- Job listings per company
- Resume upload
- Rating trend graphs
- Email notifications
