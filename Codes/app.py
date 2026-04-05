from flask import Flask, render_template, request, jsonify, redirect
from pymongo import MongoClient
from datetime import datetime
import re
from bson import ObjectId

# ---------------- DATABASE CONNECTION ----------------
client = MongoClient("mongodb://localhost:27017/")
db = client["Elabour"]

u_coll = db["users"]     # Customers
w_coll = db["workers"]   # Workers

# ---------------- FLASK APP ----------------
app = Flask(__name__)

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("auth/index.html")

# ---------------- CUSTOMER REGISTER PAGE ----------------
@app.route("/newuser")
def newuser():
    return render_template("signup/new_user.html")

# ---------------- LOGIN PAGE ----------------
@app.route("/index")
def index():
    return render_template("auth/index.html")

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

    # Username validation
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]+$', username):
        return "Username must contain letters and numbers", 400

    # Mobile validation
    if not mobile.isdigit() or len(mobile) != 10:
        return "Invalid mobile number", 400

    # Duplicate check
    if u_coll.find_one({"username": username}):
        return "Username already exists", 400

    user = {
        "username": username,
        "mobile": mobile,
        "created_at": datetime.now()
    }

    u_coll.insert_one(user)
    return redirect("/")


# ---------------- WORKER REGISTER PAGE ----------------
@app.route("/labour")
def register_labour():
    return render_template("signup/register_labour.html")

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

    name = name.strip()
    mobile = mobile.strip()

    # Validation
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]+$', name):
        return "error"

    if not mobile.isdigit() or len(mobile) != 10:
        return "error"

    if w_coll.find_one({"name": name}):
        return "exists"

    worker = {
        "name": name,
        "mobile": mobile,
        "skill": skill,
        "created_at": datetime.now()
    }

    w_coll.insert_one(worker)

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

    if not username or not password or not role:
        return jsonify({"status": "error"})

    if role == "customer":
        user = u_coll.find_one({
            "username": username,
            "mobile": password
        })

    elif role == "worker":
        user = w_coll.find_one({
            "name": username,
            "mobile": password
        })

    else:
        return jsonify({"status": "error"})

    if not user:
        return jsonify({"status": "error"})

    return jsonify({"status": "otp_required"})


# ---------------- OTP VERIFY ----------------
@app.route("/verify_otp", methods=["POST"])
def verify_otp():

    data = request.get_json()
    otp = data.get("otp")

    if otp == "correct_otp":
        return jsonify({
            "status": "success",
            "redirect": "/customer"
        })
    else:
        return jsonify({"status": "error"})


# =========================================================
# 👨‍💼 ADMIN SECTION
# =========================================================

# ADMIN PAGE
@app.route("/admin")
def admin():
    return render_template("admin/admin_panel.html")


# GET USERS
@app.route("/admin/get_users")
def get_users():

    workers_data = []
    customers_data = []

    # WORKERS
    for w in w_coll.find():
        workers_data.append({
            "id": str(w["_id"]),
            "name": w.get("name", ""),
            "phone": w.get("mobile", "")
        })

    # CUSTOMERS
    for c in u_coll.find():
        customers_data.append({
            "id": str(c["_id"]),
            "name": c.get("username", ""),
            "phone": c.get("mobile", "")
        })

    return jsonify({
        "workers": workers_data,
        "customers": customers_data
    })


# DELETE USER
@app.route("/admin/delete_user", methods=["POST"])
def delete_user():

    data = request.get_json()
    user_id = data.get("id")
    role = data.get("role")

    if role == "worker":
        w_coll.delete_one({"_id": ObjectId(user_id)})
    else:
        u_coll.delete_one({"_id": ObjectId(user_id)})

    return jsonify({"status": "deleted"})


# RESET PASSWORD (mobile reset)
@app.route("/admin/reset_password", methods=["POST"])
def reset_password():

    data = request.get_json()
    user_id = data.get("id")
    role = data.get("role")

    default_password = "0000000000"

    if role == "worker":
        w_coll.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"mobile": default_password}}
        )
    else:
        u_coll.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"mobile": default_password}}
        )

    return jsonify({"status": "reset"})


# =========================================================
# OTHER ROUTES (UNCHANGED)
# =========================================================

@app.route('/choose_account')
def choose_account():
    return render_template('signup/choose_account.html')

@app.route("/role")
def role():
    return render_template("role.html")

@app.route("/worker")
def worker():
    return render_template("worker/worker.html")

@app.route("/customer")
def customer():
    return render_template("user/customer.html")

@app.route("/back")
def back():
    return render_template("role.html")

@app.route("/log")
def log():
    return render_template("auth/index.html")

@app.route("/register_work")
def register_work():
    return render_template("worker/work_register.html")

@app.route("/apply_job")
def apply_job():
    return render_template("worker/applyJOB.html")

@app.route("/about")
def about():
    return render_template("about/about.html")

@app.route("/new")
def new():
    return render_template("signup/new_user.html")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)