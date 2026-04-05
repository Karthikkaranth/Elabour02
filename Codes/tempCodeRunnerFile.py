
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["Elabour"]
u_coll = db["users"]
w_coll = db["workers"]   
u_coll.insert_one({"username": "testuser", "mobile": "1234567890"})
w_coll.insert_one({"username": "testuser", "mobile": "1234567890"})
app = Flask(__name__)

users = []  

@app.route("/")
def home():
    return render_template("auth/index.html")

#for going to chosse_user page
@app.route('/choose_account')
def choose_account():
    return render_template('signup/choose_account.html')


@app.route("/newuser")
def newuser():
    return render_template("signup/new_user.html")

@app.route("/index")
def index():
    return render_template("auth/index.html")

"""@app.route("/reg", methods=["POST","GET"])
def register():

    if request.method == "GET":
        return render_template("auth/register.html")

    username = request.form.get("username")
    mobile = request.form.get("mobile")

    user = {
        "username": username,
        "mobile": mobile
    }

    users.append(user)
    u_coll.insert_one(user)

    print("Saved Users:", users)
    return render_template("auth/register.html")"""
@app.route("/l")
def reg():
    return render_template("auth/register.html")

# LOGIN CHECK
@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username").strip()
    mobile = request.form.get("mobile").strip()

    print("Username:", username)
    print("Mobile:", mobile)

    user = u_coll.find_one({"username": username, "mobile": mobile})

    print("User found:", user)

    if user:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error"})

#for role.html
@app.route("/role")
def role():
    return render_template("role.html")

# Main role selection page


# Worker page
@app.route("/worker")
def worker():
    return render_template("worker/worker.html")


# Customer page
@app.route("/customer")
def customer():
    return render_template("user/customer.html")


# Admin page
@app.route("/admin")
def admin():
    return render_template("worker/work_in_pro.html")


@app.route("/back")
def back():
    return render_template("role.html")

#worker.html logut
@app.route("/log")
def log():
    return render_template("auth/index.html")

# Register Work Page
@app.route("/register_work")
def register_work():
    return render_template("worker/work_register.html")

@app.route("/apply_job")
def apply_job():
    return render_template("worker/applyJOB.html")

@app.route("/about")
def about():
    return render_template("about/about.html")

#new user 
@app.route("/new")
def new():
    return render_template("signup/new_user.html")

@app.route("/labour")
def register_labour():
    return render_template("signup/register_labour.html")


if __name__ == "__main__":
    app.run(debug=True,use_reloader=False)
# debug=True enables developer mode (if it is flase auto reload is disabled and you need to restart the server manually after code changes)
# use_reloader=False prevents Flask from running the app twice (avoids socket errors on Windows)
