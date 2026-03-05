from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
client=MongoClient("mongodb://localhost:27017/")
db=client["elabour"]
coll=db["users"]

app = Flask(__name__)

# Temporary storage (acts like database)
users = []

@app.route("/")
def home():
    return render_template("new_user.html")


@app.route("/newuser")
def newuser():
    return render_template("new_user.html")


@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    

    username = request.form.get("username")
    mobile = request.form.get("mobile")

    user = {
        "username": username,
        "mobile": mobile
    }

    users.append(user)
    coll.insert_one(user)

    print("Saved Users:", users)   # shows saved data in terminal

    return  render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)