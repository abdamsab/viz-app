import os
from flask import Flask, render_template, jsonify
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
def data():
    # Fetch data from MongoDB
    data = list(collection.find())
    df = pd.DataFrame(data)
    
    # Convert date field to datetime
    df['date'] = pd.to_datetime(df['date'])

    # Example: Total sales amount per day
    sales_per_day = df.groupby(df['date'].dt.date)['total_amount'].sum().reset_index()
    sales_per_day.columns = ['date', 'total_amount']

    # Create Plotly chart with interactive features
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

if __name__ == '__main__':
    app.run(debug=True)
