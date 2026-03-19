from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os, uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_FILE = "db.json"
API_KEY = "secret123"  # możesz zmienić później


# ---------- DB ----------

def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}}
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------- AUTH ----------

def check_key(req):
    return req.headers.get("x-api-key") == API_KEY


# ---------- ROUTES ----------

@app.route("/")
def home():
    return {"status": "API działa 💪"}


@app.route("/create-user", methods=["POST"])
def create_user():
    if not check_key(request):
        return {"error": "unauthorized"}, 403

    db = load_db()
    user_id = str(uuid.uuid4())

    db["users"][user_id] = {
        "name": request.json.get("name", "User"),
        "exercises": {}
    }

    save_db(db)
    return {"user_id": user_id}


@app.route("/add-exercise", methods=["POST"])
def add_exercise():
    if not check_key(request):
        return {"error": "unauthorized"}, 403

    db = load_db()
    user_id = request.json.get("user_id")
    name = request.json.get("name")

    if user_id not in db["users"]:
        return {"error": "user not found"}, 404

    db["users"][user_id]["exercises"][name] = {
        "daily": 0,
        "total": 0,
        "history": {}
    }

    save_db(db)
    return {"status": "ok"}


@app.route("/add-reps", methods=["POST"])
def add_reps():
    if not check_key(request):
        return {"error": "unauthorized"}, 403

    db = load_db()
    user_id = request.json.get("user_id")
    ex = request.json.get("exercise")
    reps = request.json.get("reps", 0)

    today = datetime.now().strftime("%Y-%m-%d")

    user = db["users"].get(user_id)
    if not user:
        return {"error": "user not found"}, 404

    if ex not in user["exercises"]:
        return {"error": "exercise not found"}, 404

    e = user["exercises"][ex]
    e["daily"] += reps
    e["total"] += reps
    e["history"][today] = e["history"].get(today, 0) + reps

    save_db(db)
    return {"status": "ok"}


@app.route("/get-user", methods=["GET"])
def get_user():
    if not check_key(request):
        return {"error": "unauthorized"}, 403

    db = load_db()
    user_id = request.args.get("user_id")

    user = db["users"].get(user_id)
    if not user:
        return {"error": "not found"}, 404

    return jsonify(user)


# ---------- RUN ----------

if __name__ == "__main__":
    app.run()
