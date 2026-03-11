from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

# --- DATABASE SETUP ---
# Connect to local MongoDB instance
client = MongoClient("mongodb://localhost:27017/")
db = client["elabour02"]  # Select Database
coll = db["users01"]      # Select Collection

app = Flask(__name__)

# Temporary in-memory list (clears when server restarts)
users = []

# --- NAVIGATION ROUTES ---

@app.route("/")
def home():
    """Initial landing page (Register)"""
    return render_template("register.html")

@app.route("/newuser")
def newuser():
    """Form to create a new user profile"""
    return render_template("new_user.html")

@app.route("/index")
def index():
    """General index/home page after login"""
    return render_template("index.html")

# --- AUTHENTICATION LOGIC ---

@app.route("/register", methods=["POST","GET"])
def register():
    """Handles User Registration: Saves data to both list and MongoDB"""
    if request.method == "GET":
        return render_template("register.html")

    # Get data from the HTML form
    username = request.form.get("username")
    mobile = request.form.get("mobile")

    user = {
        "username": username,
        "mobile": mobile
    }

    # Store in list and MongoDB
    users.append(user)
    coll.insert_one(user)

    print("Saved Users:", users)
    return render_template("register.html")

@app.route("/login", methods=["POST"])
def login():
    """Checks credentials against MongoDB and returns JSON response"""
    username = request.form.get("username").strip()
    mobile = request.form.get("mobile").strip()

    # Search MongoDB for matching user
    user = coll.find_one({"username": username, "mobile": mobile})

    if user:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error"})

# --- ROLE & DASHBOARD ROUTES ---

@app.route("/role")
def role():
    """Page to select user role (Worker/Customer/Admin)"""
    return render_template("role.html")

@app.route("/worker")
def worker():
    """Dashboard for Worker users"""
    return render_template("worker.html")

@app.route("/customer")
def customer():
    """Dashboard for Customer users"""
    return render_template("customer.html")

@app.route("/admin")
def admin():
    """Admin control panel (Work in progress)"""
    return render_template("work_in_pro.html")

# --- UTILITY & CONTENT ROUTES ---

@app.route("/back")
def back():
    """Navigation helper to return to role selection"""
    return render_template("role.html")

@app.route("/log")
def log():
    """Logout functionality: redirects back to registration"""
    return render_template("register.html")

@app.route("/register_work")
def register_work():
    """Form for posting new work/jobs"""
    return render_template("work_register.html")

@app.route("/apply_job")
def apply_job():
    """Interface for workers to apply for jobs"""
    return render_template("applyJOB.html")

@app.route("/about")
def about():
    """Static page about the application"""
    return render_template("about.html")

# --- SERVER START ---
if __name__ == "__main__":
    app.run(debug=True)
