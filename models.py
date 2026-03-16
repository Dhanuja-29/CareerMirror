# ─────────────────────────────────────────────
#  models.py  –  CareerMirror ORM models
# ─────────────────────────────────────────────
from database import db
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    """Registered employee / job-seeker accounts."""
    __tablename__ = "users"

    id         = db.Column(db.Integer,     primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(150), unique=True, nullable=False)
    password   = db.Column(db.String(255), nullable=False)   # bcrypt hash
    is_admin   = db.Column(db.Boolean,     default=False)
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)

    # One user → many reviews
    reviews = db.relationship("Review", backref="author", lazy=True,
                              cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"


class Company(db.Model):
    """Company listed on the platform."""
    __tablename__ = "companies"

    id       = db.Column(db.Integer,     primary_key=True)
    name     = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(100))
    industry = db.Column(db.String(100))

    # One company → many reviews
    reviews = db.relationship("Review", backref="company", lazy=True,
                              cascade="all, delete-orphan")

    @property
    def avg_rating(self):
        approved = [r for r in self.reviews if r.approved]
        if not approved:
            return None
        return round(sum(r.rating for r in approved) / len(approved), 1)

    @property
    def review_count(self):
        return len([r for r in self.reviews if r.approved])

    def __repr__(self):
        return f"<Company {self.name}>"


class Review(db.Model):
    """Employee review for a company."""
    __tablename__ = "reviews"

    id          = db.Column(db.Integer, primary_key=True)
    review_text = db.Column(db.Text,    nullable=False)
    rating      = db.Column(db.Integer, nullable=False)          # 1–5
    role        = db.Column(db.String(100))                      # e.g. "Senior Engineer"
    approved    = db.Column(db.Boolean, default=False)           # admin must approve
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"),    nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)

    def __repr__(self):
        return f"<Review {self.id} rating={self.rating}>"
