from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["BBHC02"]
collection = db["class"]

@app.route("/")
def home():
    return "Flask server is running successfully"

@app.route("/register", methods=["POST"])
def register():
    try:
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

        return jsonify({"message": "Worker registered successfully!"})

    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Server error"}), 500


if __name__ == "__main__":
    app.run(debug=True)