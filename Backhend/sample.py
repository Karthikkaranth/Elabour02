from pymongo import MongoClient 
client = MongoClient("mongodb://localhost:27017/")
db = client["BBHC"]
coll=db["class"]
coll.insert_one({"name":"karthik","age":21,"city":"Byndoor"})
coll.insert_one({"college":"BBHC Kundapura","course":"BCA","year":2024})
print("Data inserted successfully")