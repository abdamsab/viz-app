from faker import Faker
from random import randint, choice
import random
from datetime import datetime
import json

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
            item_name = choice(['Laptop', 'Smartphone', 'Tablet', 'Headphones'])
            quantity = randint(1, 10)
            price = round(random.uniform(1.0, 100.0), 2)
            items.append({
                "item_id": str(item_id),
                "item_name": item_name,
                "quantity": quantity,
                "price": price
            })
        total_amount = sum(item['quantity'] * item['price'] for item in items)
        payment_method = choice(['credit card', 'cash', 'paypal'])
        location = fake.city()
        
        entry = {
            "transaction_id": str(transaction_id),
            "date": date.isoformat(),
            "customer_id": str(customer_id),
            "items": items,
            "total_amount": total_amount,
            "payment_method": payment_method,
            "location": location
        }
        
        data.append(entry)
    
    return data

def save_sales_data_to_json(data, filename="sales_data.json"):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4, default=str)
        print(f"Sales data saved to {filename}")
    except Exception as e:
        print(f"An error occurred while saving data to JSON: {e}")

# Example usage
if __name__ == "__main__":
    num_entries = 500
    sales_data = generate_sales_data(num_entries)
    save_sales_data_to_json(sales_data)
