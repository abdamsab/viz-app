from faker import Faker
from pymongo import MongoClient, errors
from random import randint, choice
import random
from datetime import datetime

fake = Faker()

def generate_sales_data(num_entries):
    data = []
    for _ in range(num_entries):
        transaction_id = fake.uuid4()
        date = fake.date_time_between(start_date='-1y', end_date='now')
        customer_id = fake.uuid4()
        items = []
        num_items = randint(1, 5)  # Random number of items per transaction
        for _ in range(num_items):
            item_id = fake.uuid4()
            quantity = randint(1, 10)
            price = round(random.uniform(1.0, 100.0), 2)
            items.append({
                "item_id": str(item_id),
                "quantity": quantity,
                "price": price
            })
        total_amount = sum(item['quantity'] * item['price'] for item in items)
        payment_method = choice(['credit card', 'cash', 'paypal'])
        location = fake.city()
        
        entry = {
            "transaction_id": str(transaction_id),
            "date": date,
            "customer_id": str(customer_id),
            "items": items,
            "total_amount": total_amount,
            "payment_method": payment_method,
            "location": location
        }
        
        data.append(entry)
    
    return data

def insert_sales_data(uri, database_name, collection_name, num_entries=500):
    client = None
    try:
        # MongoDB Connection to local instance
        client = MongoClient(uri)
        db = client[database_name]
        collection = db[collection_name]

        # Generate random sales entries
        sales_data = generate_sales_data(num_entries)

        # Insert generated data into MongoDB collection
        result = collection.insert_many(sales_data)
        print(f"Inserted {len(result.inserted_ids)} documents into the collection.")

    except errors.ConnectionFailure as e:
        print(f"Connection to MongoDB failed: {e}")
    except errors.OperationFailure as e:
        print(f"Error performing operation on MongoDB: {e}")
    except errors.InvalidURI as e:
        print(f"Invalid MongoDB URI: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if client:
            client.close()  # Close MongoDB connection

# Example usage
if __name__ == "__main__":
    uri = "mongodb://localhost:27017/"  # Local MongoDB URI
    database_name = "viz-app"
    collection_name = "sales"
    
    insert_sales_data(uri, database_name, collection_name)
