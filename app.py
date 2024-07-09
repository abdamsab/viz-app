import os
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
import json
import plotly

app = Flask(__name__)

# MongoDB Connection
client = MongoClient('mongodb://localhost:27017/')
db = client['viz-app']  # Replace with your actual database name
collection = db['sales']  # Replace with your collection name

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/salesperday')
def sales_per_day():
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
    
    # Customize Plotly figure for interactivity
    fig.update_layout(
        hovermode='x',  # Enable hover information
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label='1m', step='month', stepmode='backward'),
                    dict(count=6, label='6m', step='month', stepmode='backward'),
                    dict(count=1, label='YTD', step='year', stepmode='todate'),
                    dict(count=1, label='1y', step='year', stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(visible=True),  # Enable range slider
            type='date'  # Set x-axis type to date for better date handling
        ),
        autosize=True,  # Enable responsive layout
        margin=dict(autoexpand=True),  # Expand margin for better view
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/#')
def sold_peritem():
    # Fetch data from MongoDB
    data = list(collection.find())
    df = pd.DataFrame(data)
    print(df)
    
    # Check if 'item' column exists in the dataframe
    if 'item' not in df.columns:
        return jsonify({'error': 'Field "item" not found in data'}), 400

    # Example: Total quantity of each item sold
    items_sold = df.groupby('items')['quantity'].sum().reset_index()
    items_sold.columns = ['item', 'total_quantity']

    # Create Plotly chart
    fig = px.bar(items_sold, x='item', y='total_quantity', title='Total Quantity Sold per Item')

    # Customize Plotly figure for interactivity
    fig.update_layout(
        hovermode='x',  # Enable hover information
        autosize=True,  # Enable responsive layout
        margin=dict(autoexpand=True),  # Expand margin for better view
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


@app.route('/soldperitem')
def sold_per_item():
    try:
        # Fetch data from MongoDB
        data = list(collection.find())

        # Convert to DataFrame
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
        fig = px.bar(df_items_sold, x='item_name', y='quantity', title='Total Items Sold')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return graphJSON

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Failed to retrieve and process data from MongoDB.'}), 500


@app.route('/allsales')
def all_sales():
    # Fetch data from MongoDB
    data = list(collection.find())
    df = pd.DataFrame(data)

    # Convert ObjectId to string
    df['_id'] = df['_id'].astype(str)

    # Convert DataFrame to JSON
    sales_data = df.to_dict(orient='records')
    return jsonify(sales_data)

@app.route('/addsale', methods=['POST'])
def add_sale():
    data = request.get_json()
    
    # Validate data
    required_fields = ['date', 'item', 'quantity', 'total_amount']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    # Insert data into MongoDB
    collection.insert_one(data)
    return jsonify({'message': 'Sale added successfully!'}), 201

if __name__ == '__main__':
    app.run(debug=True)
