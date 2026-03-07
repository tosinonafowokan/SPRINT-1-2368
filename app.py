from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database connection
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Lawve.091197@localhost/vip_event_manager"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Example model
class Member(db.Model):
    __tablename__ = "members"

    member_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    membership_level = db.Column(db.String(20))


# Test route
@app.route("/")
def home():
    return jsonify({"message": "VIP Event Manager API is running"})


# Get members route
@app.route("/members")
def get_members():
    members = Member.query.all()
    result = []
    for m in members:
        result.append({
            "id": m.member_id,
            "first_name": m.first_name,
            "last_name": m.last_name,
            "membership_level": m.membership_level
        })
    
    return jsonify(result)
    
    
if __name__ == "__main__":
        app.run(debug=True)