from pymongo import MongoClient

# Connect to MongoDB locally
client = MongoClient('mongodb://localhost:27017/')

# Create or switch to a database
mydatabase = client['mydatabase']

# Create or access a collection
mycollection = mydatabase['mycollection']

# Example document to insert into the collection
document = {
    "name": "Alice",
    "age": 28,
    "city": "New York"
}

# Insert document into the collection
result = mycollection.insert_one(document)
print(f"Inserted document with ID: {result.inserted_id}")
