from flask import Flask, render_template, request, jsonify, redirect
from pymongo import MongoClient
from datetime import datetime
import re
from bson import ObjectId

# ---------------- DATABASE ----------------
client = MongoClient("mongodb://localhost:27017/")
db = client["Elabour"]

u_coll = db["users"]
w_coll = db["workers"]
login_users = db["admin01"]

app = Flask(__name__)

# ---------------- ADMIN USERS ----------------
login_users.update_one({"username": "admin"}, {"$set": {"password": "admin123"}}, upsert=True)
login_users.update_one({"username": "admin2"}, {"$set": {"password": "admin456"}}, upsert=True)
login_users.update_one({"username": "admin3"}, {"$set": {"password": "admin457"}}, upsert=True)

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("auth/index.html")

@app.route("/index")
def index():
    return render_template("auth/index.html")

# =========================================================
# ✅ NAVIGATION ROUTES (🔥 RESTORED)
# =========================================================
@app.route("/newuser")
def newuser():
    return render_template("signup/new_user.html")

@app.route("/labour")
def labour():
    return render_template("signup/register_labour.html")

@app.route("/choose_account")
def choose_account():
    return render_template("signup/choose_account.html")

@app.route("/role")
def role():
    return render_template("role.html")

@app.route("/back")
def back():
    return render_template("role.html")

@app.route("/log")
def log():
    return render_template("auth/index.html")

# DASHBOARDS
@app.route("/customer")
def customer():
    return render_template("user/customer.html")

@app.route("/worker")
def worker():
    return render_template("worker/worker.html")

# =========================================================
# 🔥 CUSTOMER REGISTER
# =========================================================
@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    mobile = request.form.get("mobile")

    if not username or not mobile:
        return "Missing data", 400

    username = username.strip()
    mobile = mobile.strip()

    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]+$', username):
        return "Invalid username", 400

    if not mobile.isdigit() or len(mobile) != 10:
        return "Invalid mobile", 400

    if u_coll.find_one({"username": username}):
        return "Username exists", 400

    u_coll.insert_one({
        "username": username,
        "mobile": mobile,
        "created_at": datetime.now()
    })

    return redirect("/")

# =========================================================
# 🔥 WORKER REGISTER
# =========================================================
@app.route("/register_worker", methods=["POST"])
def register_worker():

    name = request.form.get("name")
    mobile = request.form.get("mobile")
    skill = request.form.get("skill")

    if not name or not mobile or not skill:
        return "error"

    if not mobile.isdigit() or len(mobile) != 10:
        return "error"

    if w_coll.find_one({"name": name}):
        return "exists"

    w_coll.insert_one({
        "name": name,
        "mobile": mobile,
        "skill": skill,
        "created_at": datetime.now()
    })

    return "success"

# =========================================================
# 🔐 LOGIN
# =========================================================
@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    role = data.get("role")

    if role == "admin":
        admin = login_users.find_one({"username": username, "password": password})
        if not admin:
            return jsonify({"status": "error"})
        return jsonify({"status": "success", "redirect": "/admin"})

    elif role == "customer":
        user = u_coll.find_one({"username": username, "mobile": password})

    elif role == "worker":
        user = w_coll.find_one({"name": username, "mobile": password})

    else:
        return jsonify({"status": "error"})

    if not user:
        return jsonify({"status": "error"})

    return jsonify({"status": "otp_required"})

# OTP
@app.route("/verify_otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    if data.get("otp") == "correct_otp":
        return jsonify({"status": "success", "redirect": "/customer"})
    return jsonify({"status": "error"})

# =========================================================
# 👨‍💼 ADMIN SECTION (UNCHANGED)
# =========================================================
@app.route("/admin")
def admin():
    return render_template("admin/admin_panel.html")

@app.route("/admin/get_users")
def get_users():
    workers = []
    customers = []

    for w in w_coll.find():
        workers.append({
            "id": str(w["_id"]),
            "name": w.get("name"),
            "phone": w.get("mobile")
        })

    for c in u_coll.find():
        customers.append({
            "id": str(c["_id"]),
            "name": c.get("username"),
            "phone": c.get("mobile")
        })

    return jsonify({"workers": workers, "customers": customers})

@app.route("/admin/delete_user", methods=["POST"])
def delete_user():
    data = request.get_json()

    if data["role"] == "worker":
        w_coll.delete_one({"_id": ObjectId(data["id"])})
    else:
        u_coll.delete_one({"_id": ObjectId(data["id"])})

    return jsonify({"msg": "Deleted Successfully"})

@app.route("/admin/update_user", methods=["POST"])
def update_user():
    data = request.get_json()

    if data["role"] == "worker":
        w_coll.update_one(
            {"_id": ObjectId(data["id"])},
            {"$set": {"name": data["name"], "mobile": data["phone"]}}
        )
    else:
        u_coll.update_one(
            {"_id": ObjectId(data["id"])},
            {"$set": {"username": data["name"], "mobile": data["phone"]}}
        )

    return jsonify({"msg": "Updated Successfully"})

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)