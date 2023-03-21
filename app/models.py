from app import db


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile_number = db.Column(db.String(20), unique=True)
    address = db.Column(db.String(200))
    email = db.Column(db.String(100), unique=True)
    instagram_handle = db.Column(db.String(100), unique=True)
    companies = db.relationship('Company', secondary='customer_companies', backref=db.backref('contacts', lazy=True))

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

class CustomerCompany(db.Model):
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), primary_key=True)
