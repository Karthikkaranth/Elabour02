from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["elabour"]
coll = db["users"]

app = Flask(__name__)

users = []

@app.route("/")
def home():
    return render_template("new_user.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        mobile = request.form.get("mobile")

        user = {
            "username": username,
            "mobile": mobile
        }

        users.append(user)
        coll.insert_one(user)

        print("Saved Users:", users)

        # redirect after signup
        return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/index")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)