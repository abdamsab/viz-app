import pandas as pd
from pymongo import MongoClient

def export_collection_to_csv(uri, database_name, collection_name, csv_filename):
    # MongoDB Connection to local instance
    client = MongoClient(uri)
    db = client[database_name]
    collection = db[collection_name]

    # Fetch all data from the collection
    data = list(collection.find())

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Save DataFrame to CSV
    df.to_csv(csv_filename, index=False)

    print(f"Collection '{collection_name}' from database '{database_name}' saved to '{csv_filename}'.")

# Example usage
if __name__ == "__main__":
    uri = "mongodb://localhost:27017/"  # Local MongoDB URI
    database_name = "viz-app"
    collection_name = "sales"
    csv_filename = "sales_data.csv"

    export_collection_to_csv(uri, database_name, collection_name, csv_filename)
