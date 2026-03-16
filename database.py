# ─────────────────────────────────────────────
#  database.py  –  CareerMirror DB connection
# ─────────────────────────────────────────────
from flask_sqlalchemy import SQLAlchemy

# Single shared db instance imported everywhere
db = SQLAlchemy()


def init_db(app):
    """Bind the SQLAlchemy instance to the Flask app and create all tables."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        _seed_sample_data()


def _seed_sample_data():
    from models import Company

    db.session.query(Company).delete()   # clear old data

    sample = [
        Company(name="Horizon Technologies", location="Bangalore", industry="Software"),
        Company(name="NovaPharma India", location="Mumbai", industry="Healthcare"),
        Company(name="ClearSky Finance", location="Chennai", industry="FinTech"),
        Company(name="Greenleaf Media", location="Delhi", industry="Media"),
        Company(name="Apex Logistics", location="Pune", industry="Logistics"),
        Company(name="ZenCode Labs", location="Hyderabad", industry="Product"),
        Company(name="NetoAI", location="Chennai", industry="Product"),
        Company(name="Cognizant", location="Chennai", industry="Service"),
        Company(name="TATA Consultancy Service", location="Chennai", industry="Service"),
        Company(name="ZOHO", location="Chennai", industry="Product"),
        Company(name="Hitachi", location="Chennai", industry="Service"),
    ]

    db.session.bulk_save_objects(sample)
    db.session.commit()
    print("✅  Sample companies seeded.")
