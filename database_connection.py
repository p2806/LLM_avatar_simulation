
""" Database.py 

Database class to allow easy interactions with the database.

"""


from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import certifi
import os

def dbconnection():
   
    load_dotenv()   
    Mongo_URI = os.getenv("MONGO_KEY")
    DBNAME = os.getenv("DBNAME")
    COLLECTION = os.getenv("COLLECTION")
   
    client = MongoClient(Mongo_URI, tlsCAFile=certifi.where())
    db = client[DBNAME]
    users_collection = db[COLLECTION]
    return users_collection

def verify_user(username, password):
    user = dbconnection().find_one({"username": username})

    if user:
        user_id = user["_id"]
        return user_id
    else:
        return 0
def create_user(username,password):
    user = dbconnection().find_one({"username": username})
    if user:
        return "Member already exists"
    else:
        user_data = {
            "username": username,
            "password": password
        }
        return dbconnection().insert_one(user_data)
def add_field_to_user(user_id, new_field):
    try:
        
        collection = dbconnection()
        # Update the user document by adding a new field
        result = collection.update_one(
            {"_id": ObjectId(user_id)}, 
            {"$set": {"liked": new_field}}
        )
    
        # Check if the update was successful
        if result.matched_count > 0:
            return "Field added successfully."
        else:
            return "User not found."

    except Exception as e:
        print("Error:", e)

def add_conversation_feedback(user_id, conversation, feedback):
    try:
       
        collection = dbconnection()
        # Create a new conversation entry
        new_entry = {"conversation": conversation, "feedback": feedback}

        # Update the user's document by appending to the 'conversations' list
        result = collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"conversations": new_entry}}
        )

        # Check if the update was successful
        if result.matched_count > 0:
            print("Conversation and feedback added successfully.")
        else:
            print("User not found.")

    except Exception as e:
        print("Error:", e)

def get_conversation_feedback(user_id):
       
    collection = dbconnection()
# Query to retrieve the conversations and feedback for the specific user
    if user_id!=123:
        user_data = collection.find_one({"_id": ObjectId(user_id)}, {"_id": 0, "conversations": 1})
        conversations = user_data.get("conversations", []) if user_data else []
    else:
        conversations = []
    return conversations



