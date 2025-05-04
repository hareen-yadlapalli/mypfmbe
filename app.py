# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)
CORS(app)

# Configure PostgreSQL URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/mypfm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ----------------------
# Models
# ----------------------

class Member(db.Model):
    __tablename__ = 'members'
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob  = db.Column(db.Date, nullable=True)

class Property(db.Model):
    __tablename__ = 'properties'
    id      = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=False)
    suburb  = db.Column(db.String(100), nullable=False)
    purpose = db.Column(db.String(100), nullable=False)

class Account(db.Model):
    __tablename__ = 'accounts'
    id           = db.Column(db.Integer, primary_key=True)
    type         = db.Column(db.String(50))
    bsb          = db.Column(db.String(20))
    accountno    = db.Column(db.String(20))
    provider     = db.Column(db.String(100))
    productname  = db.Column(db.String(100))
    balance      = db.Column(db.Numeric(15, 2))
    interestrate = db.Column(db.Numeric(5, 2))
    emi          = db.Column(db.Numeric(15, 2))

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id              = db.Column(db.Integer, primary_key=True)
    billid          = db.Column(db.Integer)
    purchaseid      = db.Column(db.Integer)
    category        = db.Column(db.String(50))
    subcategory1    = db.Column(db.String(50))
    subcategory2    = db.Column(db.String(50))
    subcategory3    = db.Column(db.String(50))
    provider        = db.Column(db.String(100))
    amount          = db.Column(db.Numeric(15, 2))
    transactiondate = db.Column(db.Date)
    accountid       = db.Column(db.Integer)
    propertyid      = db.Column(db.Integer)

class Purchase(db.Model):
    __tablename__ = 'purchases'
    id            = db.Column(db.Integer, primary_key=True)
    transactionid = db.Column(db.Integer)
    memberid      = db.Column(db.Integer)
    provider      = db.Column(db.String(100))
    address       = db.Column(db.String(255))
    category      = db.Column(db.String(50))
    subcategory1  = db.Column(db.String(50))
    subcategory2  = db.Column(db.String(50))
    subcategory3  = db.Column(db.String(50))
    accountid     = db.Column(db.Integer)
    purchasedate  = db.Column(db.Date)
    amount        = db.Column(db.Numeric(15, 2))

class PurchasedItem(db.Model):
    __tablename__ = 'purchaseditems'
    id          = db.Column(db.Integer, primary_key=True)
    purchaseid  = db.Column(db.Integer)
    volunits    = db.Column(db.String(50))
    qty         = db.Column(db.Numeric(10, 2))
    price       = db.Column(db.Numeric(15, 2))
    costperunit = db.Column(db.Numeric(15, 4))

class Bill(db.Model):
    __tablename__ = 'bills'
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100))
    category     = db.Column(db.String(100))
    subcategory1 = db.Column(db.String(100))
    subcategory2 = db.Column(db.String(100))
    subcategory3 = db.Column(db.String(100))
    provider     = db.Column(db.String(100))
    frequency    = db.Column(db.String(100))
    amount       = db.Column(db.Numeric(15, 2))
    startdate    = db.Column(db.Date)
    enddate      = db.Column(db.Date)
    accountid    = db.Column(db.Integer)
    propertyid   = db.Column(db.Integer)

class Category(db.Model):
    __tablename__ = 'categories'
    id           = db.Column(db.Integer, primary_key=True)
    category     = db.Column(db.String(100))
    subcategory1 = db.Column(db.String(100))
    subcategory2 = db.Column(db.String(100))
    subcategory3 = db.Column(db.String(100))

# ----------------------
# Helpers
# ----------------------

# Convert model instance to dict, format dates as 'YYYY-MM-DD'
def to_dict(self):
    result = {}
    for col in self.__table__.columns:
        val = getattr(self, col.name)
        if isinstance(val, date):
            result[col.name] = val.isoformat()
        else:
            result[col.name] = val
    return result

for cls in (Member, Property, Account, Transaction,
            Purchase, PurchasedItem, Bill, Category):
    cls.to_dict = to_dict

# Parse optional date strings to Python date
def parse_date(date_str):
    if date_str:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    return None

# ----------------------
# CRUD Endpoints
# ----------------------

## Members
@app.route('/api/members', methods=['GET'])
def get_members():
    return jsonify([m.to_dict() for m in Member.query.all()])

@app.route('/api/members/<int:id>', methods=['GET'])
def get_member(id):
    m = Member.query.get(id)
    return (jsonify(m.to_dict()), 200) if m else (jsonify({'msg':'Not found'}), 404)

@app.route('/api/members', methods=['POST'])
def create_member():
    data = request.get_json()
    dob = parse_date(data.get('dob'))
    m = Member(name=data['name'], dob=dob)
    db.session.add(m)
    db.session.commit()
    return jsonify(m.to_dict()), 201

@app.route('/api/members/<int:id>', methods=['PUT'])
def update_member(id):
    data = request.get_json()
    m = Member.query.get(id)
    if not m:
        return jsonify({'msg':'Not found'}), 404
    m.name = data['name']
    m.dob  = parse_date(data.get('dob'))
    db.session.commit()
    return jsonify(m.to_dict())

@app.route('/api/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    m = Member.query.get(id)
    if not m:
        return jsonify({'msg':'Not found'}), 404
    db.session.delete(m)
    db.session.commit()
    return '', 204

## Properties
@app.route('/api/properties', methods=['GET'])
def get_properties():
    return jsonify([p.to_dict() for p in Property.query.all()])

@app.route('/api/properties/<int:id>', methods=['GET'])
def get_property(id):
    p = Property.query.get(id)
    return (jsonify(p.to_dict()), 200) if p else (jsonify({'msg':'Not found'}), 404)

@app.route('/api/properties', methods=['POST'])
def create_property():
    d = request.get_json()
    p = Property(address=d['address'], suburb=d['suburb'], purpose=d['purpose'])
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201

@app.route('/api/properties/<int:id>', methods=['PUT'])
def update_property(id):
    d = request.get_json()
    p = Property.query.get(id)
    if not p:
        return jsonify({'msg':'Not found'}), 404
    p.address = d['address']
    p.suburb  = d['suburb']
    p.purpose = d['purpose']
    db.session.commit()
    return jsonify(p.to_dict())

@app.route('/api/properties/<int:id>', methods=['DELETE'])
def delete_property(id):
    p = Property.query.get(id)
    if not p:
        return jsonify({'msg':'Not found'}), 404
    db.session.delete(p)
    db.session.commit()
    return '', 204

## Accounts
@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    return jsonify([a.to_dict() for a in Account.query.all()])

@app.route('/api/accounts/<int:id>', methods=['GET'])
def get_account(id):
    a = Account.query.get(id)
    return (jsonify(a.to_dict()), 200) if a else (jsonify({'msg':'Not found'}), 404)

@app.route('/api/accounts', methods=['POST'])
def create_account():
    d = request.get_json()
    a = Account(**{k: d.get(k) for k in ('type','bsb','accountno','provider','productname','balance','interestrate','emi')})
    db.session.add(a)
    db.session.commit()
    return jsonify(a.to_dict()), 201

@app.route('/api/accounts/<int:id>', methods=['PUT'])
def update_account(id):
    d = request.get_json()
    a = Account.query.get(id)
    if not a:
        return jsonify({'msg':'Not found'}), 404
    for k in ('type','bsb','accountno','provider','productname','balance','interestrate','emi'):
        setattr(a, k, d.get(k))
    db.session.commit()
    return jsonify(a.to_dict())

@app.route('/api/accounts/<int:id>', methods=['DELETE'])
def delete_account(id):
    a = Account.query.get(id)
    if not a:
        return jsonify({'msg':'Not found'}), 404
    db.session.delete(a)
    db.session.commit()
    return '', 204

## Transactions
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    return jsonify([t.to_dict() for t in Transaction.query.all()])

@app.route('/api/transactions/<int:id>', methods=['GET'])
def get_transaction(id):
    t = Transaction.query.get(id)
    return (jsonify(t.to_dict()), 200) if t else (jsonify({'msg':'Not found'}), 404)

@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    d = request.get_json()
    td = parse_date(d.get('transactiondate'))
    t = Transaction(**{k: d.get(k) for k in ('billid','purchaseid','category','subcategory1','subcategory2','subcategory3','provider','amount','accountid','propertyid')},
                    transactiondate=td)
    db.session.add(t)
    db.session.commit()
    return jsonify(t.to_dict()), 201

@app.route('/api/transactions/<int:id>', methods=['PUT'])
def update_transaction(id):
    d =request.get_json()
    t = Transaction.query.get(id)
    if not t:
        return jsonify({'msg':'Not found'}), 404
    t.transactiondate = parse_date(d.get('transactiondate'))
    for k in ('billid','purchaseid','category','subcategory1','subcategory2','subcategory3','provider','amount','accountid','propertyid'):
        setattr(t, k, d.get(k))
    db.session.commit()
    return jsonify(t.to_dict())

@app.route('/api/transactions/<int:id>', methods=['DELETE'])
def delete_transaction(id):
    t = Transaction.query.get(id)
    if not t:
        return jsonify({'msg':'Not found'}), 404
    db.session.delete(t)
    db.session.commit()
    return '', 204

## Purchases
@app.route('/api/purchases', methods=['GET'])
def get_purchases():
    return jsonify([p.to_dict() for p in Purchase.query.all()])

@app.route('/api/purchases/<int:id>', methods=['GET'])
def get_purchase(id):
    p = Purchase.query.get(id)
    return (jsonify(p.to_dict()), 200) if p else (jsonify({'msg':'Not found'}), 404)

@app.route('/api/purchases', methods=['POST'])
def create_purchase():
    d = request.get_json()
    pd = parse_date(d.get('purchasedate'))
    p = Purchase(**{k: d.get(k) for k in ('transactionid','memberid','provider','address','category','subcategory1','subcategory2','subcategory3','accountid','amount')},
                 purchasedate=pd)
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201
@app.route('/api/purchases/<int:id>', methods=['PUT'])
def update_purchase(id):
    d = request.get_json()
    p = Purchase.query.get(id)
    if not p:
        return jsonify({'msg':'Not found'}), 404
    p.purchasedate = parse_date(d.get('purchasedate'))
    for k in ('transactionid','memberid','provider','address','category','subcategory1','subcategory2','subcategory3','accountid','amount'):
        setattr(p, k, d.get(k))
    db.session.commit()
    return jsonify(p.to_dict())

@app.route('/api/purchases/<int:id>', methods=['DELETE'])
def delete_purchase(id):
    p = Purchase.query.get(id)
    if not p:
        return jsonify({'msg':'Not found'}), 404
    db.session.delete(p)
    db.session.commit()
    return '', 204

## Purchased Items
@app.route('/api/purchaseditems', methods=['GET'])
def get_purchased_items():
    return jsonify([pi.to_dict() for pi in PurchasedItem.query.all()])

@app.route('/api/purchaseditems/<int:id>', methods=['GET'])
def get_purchased_item(id):
    pi = PurchasedItem.query.get(id)
    return (jsonify(pi.to_dict()), 200) if pi else (jsonify({'msg':'Not found'}), 404)

@app.route('/api/purchaseditems', methods=['POST'])
def create_purchased_item():
    d = request.get_json()
    pi = PurchasedItem(**{k: d.get(k) for k in ('purchaseid','volunits','qty','price','costperunit')})
    db.session.add(pi)
    db.session.commit()
    return jsonify(pi.to_dict()), 201

@app.route('/api/purchaseditems/<int:id>', methods=['PUT'])
def update_purchased_item(id):
    d = request.get_json()
    pi = PurchasedItem.query.get(id)
    if not pi:
        return jsonify({'msg':'Not found'}), 404
    for k in ('purchaseid','volunits','qty','price','costperunit'):
        setattr(pi, k, d.get(k))
    db.session.commit()
    return jsonify(pi.to_dict())

@app.route('/api/purchaseditems/<int:id>', methods=['DELETE'])
def delete_purchased_item(id):
    pi = PurchasedItem.query.get(id)
    if not pi:
        return jsonify({'msg':'Not found'}), 404
    db.session.delete(pi)
    db.session.commit()
    return '', 204

## Bills
@app.route('/api/bills', methods=['GET'])
def get_bills():
    return jsonify([b.to_dict() for b in Bill.query.all()])

@app.route('/api/bills/<int:id>', methods=['GET'])
def get_bill(id):
    b = Bill.query.get(id)
    return (jsonify(b.to_dict()), 200) if b else (jsonify({'msg':'Not found'}), 404)

@app.route('/api/bills', methods=['POST'])
def create_bill():
    d = request.get_json()
    sd = parse_date(d.get('startdate'))
    ed = parse_date(d.get('enddate'))
    b = Bill(**{k: d.get(k) for k in ('name','category','subcategory1','subcategory2','subcategory3','provider','frequency','amount','accountid','propertyid')},
             startdate=sd, enddate=ed)
    db.session.add(b)
    db.session.commit()
    return jsonify(b.to_dict()), 201

@app.route('/api/bills/<int:id>', methods=['PUT'])
def update_bill(id):
    d = request.get_json()
    b = Bill.query.get(id)
    if not b:
        return jsonify({'msg':'Not found'}), 404
    b.startdate = parse_date(d.get('startdate'))
    b.enddate   = parse_date(d.get('enddate'))
    for k in ('name','category','subcategory1','subcategory2','subcategory3','provider','frequency','amount','accountid','propertyid'):
        setattr(b, k, d.get(k))
    db.session.commit()
    return jsonify(b.to_dict())

@app.route('/api/bills/<int:id>', methods=['DELETE'])
def delete_bill(id):
    b = Bill.query.get(id)
    if not b:
        return jsonify({'msg':'Not found'}), 404
    db.session.delete(b)
    db.session.commit()
    return '', 204

## Categories
@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify([c.to_dict() for c in Category.query.all()])

@app.route('/api/categories/<int:id>', methods=['GET'])
def get_category(id):
    c = Category.query.get(id)
    return (jsonify(c.to_dict()), 200) if c else (jsonify({'msg':'Not found'}), 404)

@app.route('/api/categories', methods=['POST'])
def create_category():
    d = request.get_json()
    c = Category(**{k: d.get(k) for k in ('category','subcategory1','subcategory2','subcategory3')})
    db.session.add(c)
    db.session.commit()
    return jsonify(c.to_dict()), 201

@app.route('/api/categories/<int:id>', methods=['PUT'])
def update_category(id):
    d = request.get_json()
    c = Category.query.get(id)
    if not c:
        return jsonify({'msg':'Not found'}), 404
    for k in ('category','subcategory1','subcategory2','subcategory3'):
        setattr(c, k, d.get(k))
    db.session.commit()
    return jsonify(c.to_dict())

@app.route('/api/categories/<int:id>', methods=['DELETE'])
def delete_category(id):
    c = Category.query.get(id)
    if not c:
        return jsonify({'msg':'Not found'}), 404
    db.session.delete(c)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
