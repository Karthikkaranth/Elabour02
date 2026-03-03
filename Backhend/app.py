from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  # allow frontend connection

# 🔗 Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["elabour"]
collection = db["workers"]

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    name = data.get("name")
    phone = data.get("phone")
    address = data.get("address")
    skills = data.get("skills")

    if not name or not phone or not address:
        return jsonify({"message": "Missing fields"}), 400

    worker = {
        "name": name,
        "phone": phone,
        "address": address,
        "skills": skills
    }

    collection.insert_one(worker)

    return jsonify({"message": "Data saved successfully!"})

if __name__ == "__main__":
    app.run(debug=True)