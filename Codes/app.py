from flask import Flask, render_template, request, jsonify, redirect, session
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
posts_coll = db["posts"]
worker_collection = db["workerreg"]
requests_collection = db["requests"]
history_collection = db["history"]
app = Flask(__name__)

# 🔐 SECRET KEY
app.secret_key = "elabour_karthik_project_key"

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

# ---------------- NAVIGATION ----------------
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

#BACK TO WORKER
#BACK TO WORKER
@app.route("/back1")
def backtoworker():
    if "user" not in session:
        return redirect("/")
        
    return render_template("worker/worker.html", username=session.get("worker_name"))


#BACK TO CUSTOMER
@app.route("/back2")
def backtouser():
    if "user" not in session:
        return redirect("/")
        
    return render_template("user/customer.html", username=session.get("customer_name"))
@app.route("/log")
def log():
    return render_template("auth/index.html")

# ---------------- DASHBOARDS ----------------
@app.route("/customer")
def customer():
    if "user" not in session:
        return redirect("/")
    
    return render_template("user/customer.html", username=session.get("customer_name"))
@app.route("/worker")
def worker():
    if "user" not in session:
        return redirect("/")
        
    return render_template("worker/worker.html", username=session.get("worker_name"))
# ---------------- CUSTOMER REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    mobile = request.form.get("mobile")

    if not username or not mobile:
        return "Missing data", 400

    if u_coll.find_one({"username": username}):
        return "Username exists", 400

    u_coll.insert_one({
        "username": username,
        "mobile": mobile,
        "created_at": datetime.now()
    })

    return redirect("/")

# ---------------- WORKER REGISTER ----------------
@app.route("/register_worker", methods=["POST"])
def register_worker():

    name = request.form.get("name")
    mobile = request.form.get("mobile")

    if not name or not mobile:
        return "error"

    if w_coll.find_one({"name": name}):
        return "exists"

    w_coll.insert_one({
        "name": name,
        "mobile": mobile,
        "created_at": datetime.now()
    })

    return "success"

# ---------------- LOGIN ----------------
# ---------------- LOGIN ----------------
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

        session["user"] = username
        session["role"] = "admin"

        return jsonify({"status": "success", "redirect": "/admin"})

    elif role == "customer":
        user = u_coll.find_one({"username": username, "mobile": password})

    elif role == "worker":
        user = w_coll.find_one({"name": username, "mobile": password})

    else:
        return jsonify({"status": "error"})

    if not user:
        return jsonify({"status": "error"})

    # 🔥 ADD THIS ONLY
    session["user"] = username
    session["role"] = role

    if role == "customer":
        session["customer_name"] = user.get("username")
    elif role == "worker":
        session["worker_name"] = user.get("name")

    return jsonify({"status": "otp_required"})
# ---------------- OTP ----------------
@app.route("/verify_otp", methods=["POST"])
def verify_otp():
    data = request.get_json()

    if data.get("otp") == "correct_otp":

        if session.get("role") == "customer":
            return jsonify({"status": "success", "redirect": "/customer"})
        elif session.get("role") == "worker":
            return jsonify({"status": "success", "redirect": "/worker"})
        else:
            return jsonify({"status": "success", "redirect": "/"})

    return jsonify({"status": "error"})

# =========================================================
# 🔥 POST WORK SAVE TO MONGODB
# =========================================================
@app.route("/post_work", methods=["POST"])
def save_work():

    if "user" not in session:
        return jsonify({"status": "error", "message": "Login required"})

    data = request.get_json()

    post_data = {
        "username": session["user"],
        "role": session["role"],

        "name": data.get("name"),
        "phone": data.get("phone"),
        "address": data.get("address"),
        "location": data.get("location"),
        "date": data.get("date"),

        # 🔥 NEW FIELDS ADDED
        "description": data.get("description"),
        "salary_min": data.get("salary_min"),
        "salary_max": data.get("salary_max"),

        "skills": data.get("skills"),
        "start_time": data.get("start_time"),
        "end_time": data.get("end_time"),

        "created_at": datetime.now()
    }

    posts_coll.insert_one(post_data)

    return jsonify({"status": "success"})
# =========================================================
# 🔥 SHOW ONLY USER POSTS
# =========================================================
@app.route("/my_posts")
def my_posts():

    if "user" not in session:
        return jsonify([])

    posts = list(posts_coll.find({"username": session["user"]}))

    for p in posts:
        p["_id"] = str(p["_id"])

    return jsonify(posts)



# =========================================================
# 🔥 UPDATE POST
# =========================================================
@app.route("/update_post/<id>", methods=["POST"])
def update_post(id):

    if "user" not in session:
        return jsonify({"status": "error", "message": "Login required"})

    data = request.get_json()

    posts_coll.update_one(
        {"_id": ObjectId(id), "username": session["user"]},
        {"$set": {
    "name": data.get("name"),
    "phone": data.get("phone"),
    "location": data.get("location"),
    "address": data.get("address"),
    "date": data.get("date"),

    "description": data.get("description"),

    "salary_min": data.get("salary_min"),
    "salary_max": data.get("salary_max"),

    "start_time": data.get("start_time"),
    "end_time": data.get("end_time"),

    "skills": data.get("skills")
}}
    )

    return jsonify({"status": "success"})

# =========================================================
# 🔥 ADMIN APIs (NEW)
# =========================================================

@app.route("/admin/get_users")
def admin_get_users():

    workers = list(w_coll.find())
    customers = list(u_coll.find())

    for w in workers:
        w["id"] = str(w["_id"])

    for c in customers:
        c["id"] = str(c["_id"])

    return jsonify({
        "workers": [{"id": w["id"], "name": w["name"], "phone": w["mobile"]} for w in workers],
        "customers": [{"id": c["id"], "name": c["username"], "phone": c["mobile"]} for c in customers]
    })


@app.route("/admin/get_posts/<username>")
def admin_get_posts(username):

    posts = list(posts_coll.find({"username": username}))

    for p in posts:
        p["_id"] = str(p["_id"])

    return jsonify(posts)


@app.route("/admin/delete_post", methods=["POST"])
def admin_delete_post():

    data = request.get_json()
    posts_coll.delete_one({"_id": ObjectId(data.get("id"))})

    return jsonify({"msg": "Post removed"})


@app.route("/admin/delete_user", methods=["POST"])
def admin_delete_user():

    data = request.get_json()

    if data.get("role") == "worker":
        w_coll.delete_one({"_id": ObjectId(data.get("id"))})
    else:
        u_coll.delete_one({"_id": ObjectId(data.get("id"))})

    return jsonify({"msg": "User deleted"})


@app.route("/admin/update_user", methods=["POST"])
def admin_update_user():

    data = request.get_json()

    if data.get("role") == "worker":
        w_coll.update_one(
            {"_id": ObjectId(data.get("id"))},
            {"$set": {"name": data.get("name"), "mobile": data.get("phone")}}
        )
    else:
        u_coll.update_one(
            {"_id": ObjectId(data.get("id"))},
            {"$set": {"username": data.get("name"), "mobile": data.get("phone")}}
        )

    return jsonify({"msg": "User updated"})

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    return render_template("admin/admin_panel.html")

# ---------------- CUSTOMER PAGE ----------------
@app.route('/cus')
def contractor():
    if "user" not in session:
        return redirect("/")
        
    return render_template('user/customer.html', username=session.get("customer_name"))
# ---------------- POST PAGE ----------------
@app.route('/post')
def post_page():
    return render_template('user/post.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

# =========================================================
# 🔥 GET ALL JOBS FOR WORKER
# =========================================================
@app.route("/get_all_jobs")
def get_all_jobs():

    jobs = list(posts_coll.find())

    for j in jobs:
        j["_id"] = str(j["_id"])

    return jsonify(jobs)

#about for worker
@app.route("/aboutw")
def aboutw():
    return render_template("about/about.html")

@app.route("/aboutu")
def aboutu():
    return render_template("about/aboutuser.html")


@app.route("/reg")
def reg():
    return render_template("worker/regworker.html")


@app.route("/reg_worker", methods=["POST"])
def reg_worker():
    data = request.get_json()

    worker = {
    "username": session.get("user"),   # 🔥 ADD THIS
    "name": data.get("name"),
    "phone": data.get("phone"),
    "address": data.get("address"),
    "experience": data.get("experience"),
    "bio": data.get("bio"),
    "skills": data.get("skills"),
    "status": "pending"
}
    requests_collection.insert_one(worker)

    return jsonify({"status": "success"})
    

@app.route("/worker_status")
def worker_status():

    if "user" not in session:
        return jsonify([])

    user = session["user"]

    # get pending + history both
    pending = list(requests_collection.find({"username": user}))
    history = list(history_collection.find({"username": user}))

    all_data = pending + history

    for d in all_data:
        d["_id"] = str(d["_id"])

    return jsonify(all_data)

@app.route("/get_requests")

def get_requests():
    data = list(requests_collection.find({}, {"_id": 1, "name": 1, "phone": 1, "skills": 1, "status": 1}))
    
    for d in data:
        d["_id"] = str(d["_id"])
    
    return jsonify(data)


@app.route("/get_request/<id>")
def get_request(id):
    from bson import ObjectId
    r = requests_collection.find_one({"_id": ObjectId(id)})
    r["_id"] = str(r["_id"])
    return jsonify(r)

#accept or reject worker request
@app.route("/update_request/<id>", methods=["POST"])
def update_request(id):
    from bson import ObjectId

    try:
        data = request.get_json()
        status = data.get("status")

        req = requests_collection.find_one({"_id": ObjectId(id)})

        if not req:
            return jsonify({"status": "error", "message": "Request not found"})

        # update status
        req["status"] = status

        # move to history
        history_collection.insert_one(req)

        # delete from requests
        requests_collection.delete_one({"_id": ObjectId(id)})

        return jsonify({"status": "success"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

#history page
@app.route("/get_history")
def get_history():
    data = list(history_collection.find({}, {"_id": 0}))
    return jsonify(data)


@app.route('/delete_post/<id>', methods=['DELETE'])
def delete_post(id):

    if "user" not in session:
        return jsonify({"message":"Login required"}), 401

    result = posts_coll.delete_one({
        "_id": ObjectId(id),
        "username": session["user"]
    })

    if result.deleted_count > 0:
        return jsonify({"message":"Post deleted successfully"})
    else:
        return jsonify({"message":"Post not found"}), 404
    ...

@app.route("/get_post/<id>")
def get_post(id):

    try:
        post = posts_coll.find_one({
            "_id": ObjectId(id)
        })

        if not post:
            return jsonify({
                "status": "error",
                "message": "Post not found"
            }), 404

        post["_id"] = str(post["_id"])
        print(post)
        return jsonify(post)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)