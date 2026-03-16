# ─────────────────────────────────────────────
#  app.py  –  CareerMirror Flask Application
# ─────────────────────────────────────────────
import os
from flask import (Flask, render_template, request,
                   redirect, url_for, flash, jsonify)
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

load_dotenv()                           # read .env

from database import db, init_db
from models   import User, Company, Review

# ── App setup ────────────────────────────────
app = Flask(__name__)
app.config["SECRET_KEY"]              = os.getenv("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost/careermirror_db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

bcrypt       = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view      = "login"
login_manager.login_message   = "Please log in to continue."
login_manager.login_message_category = "info"

init_db(app)                            # create tables + seed


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ── HOME ─────────────────────────────────────
@app.route("/")
def home():
    q         = request.args.get("q", "").strip()
    industry  = request.args.get("industry", "").strip()
    companies = Company.query

    if q:
        companies = companies.filter(
            Company.name.ilike(f"%{q}%") |
            Company.location.ilike(f"%{q}%")
        )
    if industry:
        companies = companies.filter(Company.industry.ilike(f"%{industry}%"))

    companies  = companies.all()
    industries = db.session.query(Company.industry).distinct().all()
    industries = sorted([i[0] for i in industries if i[0]])

    return render_template("home.html",
                           companies=companies,
                           industries=industries,
                           q=q,
                           selected_industry=industry)


# ── REGISTER ─────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        name     = request.form["name"].strip()
        email    = request.form["email"].strip().lower()
        password = request.form["password"]

        if not name or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
            return redirect(url_for("register"))

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(name=name, email=email, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash("Account created! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# ── LOGIN ─────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        email    = request.form["email"].strip().lower()
        password = request.form["password"]
        user     = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=True)
            flash(f"Welcome back, {user.name}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("home"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


# ── LOGOUT ────────────────────────────────────
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


# ── COMPANY PROFILE ───────────────────────────
@app.route("/company/<int:company_id>")
def company_profile(company_id):
    company = Company.query.get_or_404(company_id)
    reviews = (Review.query
               .filter_by(company_id=company_id, approved=True)
               .order_by(Review.created_at.desc())
               .all())
    return render_template("company.html", company=company, reviews=reviews)


# ── ADD REVIEW ────────────────────────────────
@app.route("/add_review/<int:company_id>", methods=["GET", "POST"])
@login_required
def add_review(company_id):
    company = Company.query.get_or_404(company_id)

    if request.method == "POST":
        review_text = request.form["review_text"].strip()
        rating      = request.form.get("rating", type=int)
        role        = request.form.get("role", "").strip()

        if not review_text or not rating or rating not in range(1, 6):
            flash("Please provide a review and a valid rating (1–5).", "error")
            return redirect(url_for("add_review", company_id=company_id))

        review = Review(
            review_text=review_text,
            rating=rating,
            role=role or None,
            company_id=company_id,
            user_id=current_user.id,
            approved=False          # awaits admin approval
        )
        db.session.add(review)
        db.session.commit()
        flash("Your review has been submitted and is pending approval.", "success")
        return redirect(url_for("company_profile", company_id=company_id))

    return render_template("add_review.html", company=company)


# ── ADMIN – PENDING REVIEWS ───────────────────
@app.route("/admin")
@login_required
def admin():
    if not current_user.is_admin:
        flash("Admin access required.", "error")
        return redirect(url_for("home"))

    pending  = Review.query.filter_by(approved=False).order_by(Review.created_at.desc()).all()
    approved = Review.query.filter_by(approved=True).order_by(Review.created_at.desc()).all()
    return render_template("admin.html", pending=pending, approved=approved)


@app.route("/admin/approve/<int:review_id>")
@login_required
def approve_review(review_id):
    if not current_user.is_admin:
        flash("Admin access required.", "error")
        return redirect(url_for("home"))
    review = Review.query.get_or_404(review_id)
    review.approved = True
    db.session.commit()
    flash("Review approved.", "success")
    return redirect(url_for("admin"))


@app.route("/admin/delete/<int:review_id>")
@login_required
def delete_review(review_id):
    if not current_user.is_admin:
        flash("Admin access required.", "error")
        return redirect(url_for("home"))
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash("Review deleted.", "success")
    return redirect(url_for("admin"))


# ── API – SEARCH (JSON, used by fetch in JS) ──
@app.route("/api/companies")
def api_companies():
    q        = request.args.get("q", "").strip()
    industry = request.args.get("industry", "").strip()
    qs = Company.query
    if q:
        qs = qs.filter(
            Company.name.ilike(f"%{q}%") |
            Company.location.ilike(f"%{q}%")
        )
    if industry:
        qs = qs.filter(Company.industry.ilike(f"%{industry}%"))

    results = [
        {
            "id":       c.id,
            "name":     c.name,
            "location": c.location,
            "industry": c.industry,
            "rating":   c.avg_rating,
            "reviews":  c.review_count,
        }
        for c in qs.all()
    ]
    return jsonify(results)


# ── RUN ───────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
