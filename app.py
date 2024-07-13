import os
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
import json
import plotly
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app)

# MongoDB Connection
connection_string = "mongodb://localhost:27017/"
client = MongoClient(connection_string)
db = client['viz-app']
collection = db['sales']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/salesperday')
def sales_per_day():
    try:
        # Fetch data from MongoDB
        data = list(collection.find())
        df = pd.DataFrame(data)

        # Convert date field to datetime
        df['date'] = pd.to_datetime(df['date'])

        # Example: Total sales amount per day
        sales_per_day = df.groupby(df['date'].dt.date)['total_amount'].sum().reset_index()
        sales_per_day.columns = ['date', 'total_amount']

        # Create Plotly chart
        fig = px.line(sales_per_day, x='date', y='total_amount', title='Total Sales Amount per Day')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return graphJSON

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Failed to retrieve and process data from MongoDB.'}), 500

@app.route('/soldperitem')
def sold_per_item():
    try:
        # Fetch data from MongoDB
        data = list(collection.find())
        df = pd.DataFrame(data)

        # Initialize an empty dictionary to store sold quantities per item
        items_sold = {}

        # Iterate through each row in the DataFrame
        for index, row in df.iterrows():
            items_list = row['items']
            for item in items_list:
                item_id = item['item_id']
                item_name = item['item_name']  # Assuming 'item_name' is present in each item dictionary
                quantity = item['quantity']

                # Accumulate the total sold quantity for each item
                if item_id in items_sold:
                    items_sold[item_id]['quantity'] += quantity
                else:
                    items_sold[item_id] = {
                        'item_name': item_name,
                        'quantity': quantity
                    }

       

        # Convert items_sold dictionary to a list of dictionaries
        items_sold_list = [{'item_id': k, **v} for k, v in items_sold.items()]

    

        # Create Plotly chart
        df_items_sold = pd.DataFrame(items_sold_list)
    
        df_items_sold_gp = df_items_sold.groupby('item_name')['quantity'].sum().reset_index()
        #df_items_sold_gp = pd.DataFrame(df_items_sold_gp).reset_index()
        df_items_sold_gp.columns = ['item_name', 'quantity']
        print(df_items_sold_gp)
        fig = px.bar(df_items_sold_gp, x='item_name', y='quantity', title='Total Items Sold')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return graphJSON

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Failed to retrieve and process data from MongoDB.'}), 500

@app.route('/viewdata')
def view_data():
    try:
        # Fetch all data from MongoDB collection
        data = list(collection.find())
        # Convert ObjectId to string for JSON serialization
        for entry in data:
            entry['_id'] = str(entry['_id'])
        return jsonify(data)
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Failed to retrieve and process data from MongoDB.'}), 500


@app.route('/adddata', methods=['POST'])
def add_data():
    try:
        # Get JSON data from the request
        new_data = request.json
        
        if not isinstance(new_data, list):
            return jsonify({'error': 'Input data should be a list of entries.'}), 400

        # Validate each entry in the list
        for entry in new_data:
            if not all(key in entry for key in ("transaction_id", "date", "customer_id", "items", "total_amount", "payment_method", "location")):
                return jsonify({'error': 'Each entry must contain transaction_id, date, customer_id, items, total_amount, payment_method, and location.'}), 400

        # Convert date strings to datetime objects
        for entry in new_data:
            entry["date"] = datetime.fromisoformat(entry["date"])

        # Insert the list of new data entries into the MongoDB collection
        result = collection.insert_many(new_data)
        socketio.emit('new_data')  # Notify clients of new data

        return jsonify({'status': f'{len(result.inserted_ids)} documents added successfully'}), 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Failed to add data to MongoDB.'}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True)
