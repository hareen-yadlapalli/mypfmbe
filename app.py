from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)  # This will allow all domains, you can restrict this to specific domains if needed


# Set the PostgreSQL URI (replace with your own credentials)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/mypfm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Models (tables)
class Member(db.Model):
    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    dob = db.Column(db.Date)

    def __repr__(self):
        return f'<Member {self.name}>'

class Property(db.Model):
    __tablename__ = 'properties'

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255))
    suburb = db.Column(db.String(100))
    purpose = db.Column(db.String(100))

class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    bsb = db.Column(db.String(20))
    accountno = db.Column(db.String(20))
    provider = db.Column(db.String(100))
    productname = db.Column(db.String(100))
    balance = db.Column(db.Numeric(15, 2))
    interestrate = db.Column(db.Numeric(5, 2))
    emi = db.Column(db.Numeric(15, 2))

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    billid = db.Column(db.Integer)
    purchaseid = db.Column(db.Integer)
    category = db.Column(db.String(50))
    subcategory1 = db.Column(db.String(50))
    subcategory2 = db.Column(db.String(50))
    subcategory3 = db.Column(db.String(50))
    provider = db.Column(db.String(100))
    amount = db.Column(db.Numeric(15, 2))
    transactiondate = db.Column(db.Date)
    accountid = db.Column(db.Integer)
    propertyid = db.Column(db.Integer)

class Purchase(db.Model):
    __tablename__ = 'purchases'

    id = db.Column(db.Integer, primary_key=True)
    transactionid = db.Column(db.Integer)
    memberid = db.Column(db.Integer)
    provider = db.Column(db.String(100))
    address = db.Column(db.String(255))
    category = db.Column(db.String(50))
    subcategory1 = db.Column(db.String(50))
    subcategory2 = db.Column(db.String(50))
    subcategory3 = db.Column(db.String(50))
    accountid = db.Column(db.Integer)
    purchasedate = db.Column(db.Date)
    amount = db.Column(db.Numeric(15, 2))

class PurchasedItem(db.Model):
    __tablename__ = 'purchaseditems'

    id = db.Column(db.Integer, primary_key=True)
    purchaseid = db.Column(db.Integer)
    volunits = db.Column(db.String(50))
    qty = db.Column(db.Numeric(10, 2))
    price = db.Column(db.Numeric(15, 2))
    costperunit = db.Column(db.Numeric(15, 4))

class Bill(db.Model):
    __tablename__ = 'bills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(db.String(100))
    subcategory1 = db.Column(db.String(100))
    subcategory2 = db.Column(db.String(100))
    subcategory3 = db.Column(db.String(100))
    provider = db.Column(db.String(100))
    frequency = db.Column(db.String(100))
    amount = db.Column(db.Numeric(15, 2))
    startdate = db.Column(db.Date)
    enddate = db.Column(db.Date)
    accountid = db.Column(db.Integer)
    propertyid = db.Column(db.Integer)

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100))
    subcategory1 = db.Column(db.String(100))
    subcategory2 = db.Column(db.String(100))
    subcategory3 = db.Column(db.String(100))

# Helper function to return model data as dictionary (for easy JSON conversion)
def to_dict(self):
    return {column.name: getattr(self, column.name) for column in self.__table__.columns}

# Add `to_dict` method to all models
Member.to_dict = to_dict
Property.to_dict = to_dict
Account.to_dict = to_dict
Transaction.to_dict = to_dict
Purchase.to_dict = to_dict
PurchasedItem.to_dict = to_dict
Bill.to_dict = to_dict
Category.to_dict = to_dict

# API Routes for CRUD Operations

# Get all members
@app.route('/api/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return jsonify([member.to_dict() for member in members])

# Get member by ID
@app.route('/api/members/<int:id>', methods=['GET'])
def get_member(id):
    member = Member.query.get(id)
    if member:
        return jsonify(member.to_dict())
    return jsonify({'message': 'Member not found'}), 404

# POST new member
@app.route('/api/members', methods=['POST'])
def create_member():
    data = request.get_json()
    new_member = Member(name=data['name'], dob=data['dob'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify(new_member.to_dict()), 201

# PUT (Replace) member
@app.route('/api/members/<int:id>', methods=['PUT'])
def update_member(id):
    data = request.get_json()
    member = Member.query.get(id)
    if member:
        member.name = data['name']
        member.dob = data['dob']
        db.session.commit()
        return jsonify(member.to_dict())
    return jsonify({'message': 'Member not found'}), 404

# DELETE member
@app.route('/api/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get(id)
    if member:
        db.session.delete(member)
        db.session.commit()
        return '', 204
    return jsonify({'message': 'Member not found'}), 404

# Repeat the same pattern for Properties, Accounts, Transactions, Purchases, PurchasedItems, Bills, and Categories

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
