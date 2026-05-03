from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Lawve.091197@localhost/vip_event_manager"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


#My models
class Member(db.Model):
    __tablename__ = "members"
    member_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    details = db.Column(db.Text)
    title = db.Column(db.String(100))
    membership_level = db.Column(db.Enum('Bronze','Silver','Gold'), nullable=False)

class Event(db.Model):
    __tablename__ = "events"
    event_id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    event_description = db.Column(db.Text)
    capacity = db.Column(db.Integer, nullable=False)
    level_requirement = db.Column(db.Enum('Bronze','Silver','Gold'), nullable=False)
    event_date = db.Column(db.Date, nullable=False)

class Registration(db.Model):
    __tablename__ = "registrations"
    registration_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=False)
    registration_date = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    registration_status = db.Column(db.Enum('confirmed','waitlist','denied'), default='confirmed')
    __table_args__ = (
        db.UniqueConstraint('member_id', 'event_id', name='unique_member_event'),
    )

@app.route("/")
def home():
    return jsonify({"message": "VIP Event Manager API is running"})

@app.route("/test-db")
def test_db():
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM members LIMIT 1"))
            members = [dict(row._mapping) for row in result]
        return {"success": True, "data": members}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route("/members", methods=["GET"])
def get_members():
    members = Member.query.all()
    result = []
    for m in members:
        result.append({
            "id": m.member_id,
            "first_name": m.first_name,
            "last_name": m.last_name,
            "email": m.email,
            "membership_level": m.membership_level
        })
    return jsonify(result)

@app.route("/members", methods=["POST"])
def add_member():
    data = request.json
    try:
        new_member = Member(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data.get('email'),
            details=data.get('details'),
            title=data.get('title'),
            membership_level=data['membership_level']
        )
        db.session.add(new_member)
        db.session.commit()
        return jsonify({"success": True, "member_id": new_member.member_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})

@app.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    data = request.json
    member = Member.query.get(id)

    if not member:
        return jsonify({"success": False, "error": "Member not found"})

    member.first_name = data.get("first_name", member.first_name)
    member.last_name = data.get("last_name", member.last_name)
    member.email = data.get("email", member.email)
    member.membership_level = data.get("membership_level", member.membership_level)

    db.session.commit()

    return jsonify({"success": True, "message": "Member updated"})

@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
    member = Member.query.get(id)

    if not member:
        return jsonify({"success": False, "error": "Member not found"})

    db.session.delete(member)
    db.session.commit()

    return jsonify({"success": True, "message": "Member deleted"})
    
@app.route("/events", methods=["GET"])
def get_events():
    events = Event.query.all()
    result = []
    for e in events:
        result.append({
            "id": e.event_id,
            "name": e.event_name,
            "capacity": e.capacity,
            "level_requirement": e.level_requirement,
            "date": str(e.event_date)
        })
    return jsonify(result)

@app.route("/events", methods=["POST"])
def add_event():
    data = request.json
    try:
        existing_event = Event.query.filter_by(event_date=datetime.strptime(data['event_date'], "%Y-%m-%d").date()).first()
        if existing_event:
            return jsonify({"success": False, "error": "An event already exists on this date."})
        new_event = Event(
            event_name=data['event_name'],
            event_description=data.get('event_description'),
            capacity=data['capacity'],
            level_requirement=data['level_requirement'],
            event_date=datetime.strptime(data['event_date'], "%Y-%m-%d")
        )
        db.session.add(new_event)
        db.session.commit()
        return jsonify({"success": True, "event_id": new_event.event_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})

@app.route("/registrations", methods=["POST"])
def add_registration():
    data = request.json
    try:
        member = Member.query.get(data['member_id'])
        event = Event.query.get(data['event_id'])
        if not member or not event:
            return jsonify({"success": False, "error": "Member or Event not found"})
        levels = {'Bronze': 1, 'Silver': 2, 'Gold': 3}
        if levels[member.membership_level] < levels[event.level_requirement]:
            return jsonify({"success": False, "error": "Member level does not meet event requirement."})
        current_count = Registration.query.filter_by(event_id=event.event_id).count()
        if current_count >= event.capacity:
            return jsonify({"success": False, "error": "Event has reached maximum capacity."})
        existing = Registration.query.filter_by(member_id=member.member_id, event_id=event.event_id).first()
        if existing:
            return jsonify({"success": False, "error": "Member is already registered for this event."})
        new_reg = Registration(member_id=member.member_id, event_id=event.event_id)
        db.session.add(new_reg)
        db.session.commit()
        return jsonify({"success": True, "registration_id": new_reg.registration_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})

@app.route("/registrations", methods=["GET"])
def get_registrations():
    regs = Registration.query.all()
    return jsonify([
        {"id": r.registration_id, "member_id": r.member_id, "event_id": r.event_id} for r in regs
    ])

@app.route("/events/<int:id>/members", methods=["GET"])
def get_event_members(id):
    regs = Registration.query.filter_by(event_id=id).all()

    result = []
    for r in regs:
        member = Member.query.get(r.member_id)
        result.append({"name": f"{member.first_name} {member.last_name}", "membership_level": member.membership_level})
    return jsonify(result)

@app.route("/registrations/<int:id>", methods=["DELETE"])
def delete_registration(id):
    reg = Registration.query.get(id)

    if not reg:
        return jsonify({"success": False, "error": "Registration not found"})

    db.session.delete(reg)
    db.session.commit()

    return jsonify({"success": True})

@app.route("/events/level/<level>", methods=["GET"])
def get_events_by_level(level):
    events = Event.query.filter_by(level_requirement=level).all()

    return jsonify([
        {"id": e.event_id, "name": e.event_name}
        for e in events
    ])

@app.route("/members/level/<level>", methods=["GET"])
def get_members_by_level(level):
    members = Member.query.filter_by(membership_level=level).all()

    return jsonify([
        {"id": m.member_id, "name": m.first_name}
        for m in members
    ])

if __name__ == "__main__":
    app.run(debug=True)