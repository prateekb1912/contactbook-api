from flask import jsonify, request
from sqlalchemy.exc import IntegrityError

from app import db
from app.main import bp
from app.models import Company, Contact


@bp.route('/contacts', methods=['POST'])
def create_contact():
    data = request.get_json()

    # Validate input
    if not data:
        return jsonify({'message': 'No input data provided'}), 400
    if not any([data.get('mobile_number'), data.get('email'), data.get('instagram_handle')]):
        return jsonify({'message': 'At least one of mobile_number, email, or instagram_handle must be provided'}), 400

    # Create contact
    contact = Contact(name=data.get('name'),
                      mobile_number=data.get('mobile_number'),
                      address=data.get('address'),
                      email=data.get('email'),
                      instagram_handle=data.get('instagram_handle'))

    # Add companies
    if data.get('companies'):
        for company_name in data.get('companies'):
            company = Company.query.filter_by(name=company_name).first()
            if not company:
                company = Company(name=company_name)
            contact.companies.append(company)

    # Save to database
    try:
        db.session.add(contact)
        db.session.commit()
        return jsonify({'message': 'Contact created successfully'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Contact already exists'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@bp.route('/contacts', methods=['GET'])
def get_contact():
    mobile_number = request.args.get('mobile_number')
    email = request.args.get('email')
    instagram_handle = request.args.get('instagram_handle')

    if not any([mobile_number, email, instagram_handle]):
        return jsonify({'message': 'At least one of mobile_number, email, or instagram_handle must be provided'}), 400

    contact = Contact.query.filter((Contact.mobile_number == mobile_number) |
                                    (Contact.email == email) |
                                    (Contact.instagram_handle == instagram_handle)).first()

    if not contact:
        return jsonify({'message': 'Contact not found'}), 404

    return jsonify(contact.serialize()), 200


@bp.route('/contacts/companies/<company_name>', methods=['GET'])
def get_contacts_by_company(company_name):
    company = Company.query.filter_by(name=company_name).first()

    if not company:
        return jsonify({'message': f'Company with name "{company_name}" not found'}), 404

    contacts = company.contacts.all()

    return jsonify([contact.serialize() for contact in contacts]), 200


@bp.route('/contacts', methods=['PUT'])
def update_contact():
    mobile_number = request.json.get('mobile_number')
    email = request.json.get('email')
    instagram_handle = request.json.get('instagram_handle')

    if not any([mobile_number, email, instagram_handle]):
        return jsonify({'message': 'At least one of mobile_number, email, or instagram_handle must be provided'}), 400

    contact = Contact.query.filter((Contact.mobile_number == mobile_number) |
                                    (Contact.email == email) |
                                    (Contact.instagram_handle == instagram_handle)).first()

    if not contact:
        return jsonify({'message': 'Contact not found'}), 404

    if 'name' in request.json:
        contact.name = request.json['name']
    if 'address' in request.json:
        contact.address = request.json['address']
    if 'companies' in request.json:
        companies = []
        for company_name in request.json['companies']:
            company = Company.query.filter_by(name=company_name).first()
            if not company:
                return jsonify({'message': f'Company with name "{company_name}" not found'}), 400
            companies.append(company)
        contact.companies = companies

    db.session.commit()

    return jsonify(contact.serialize()), 200
