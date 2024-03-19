import json
import boto3
import pandas as pd
import requests
import sqlalchemy as db
import toml
import os
from dotenv import load_dotenv
from datetime import date

# Define source of configurations
config = toml.load('config.toml')

# Function to query customer names from the database
def query_customer_names(customerIDs, config):
    
    # Database connection parameters
    host = config['db']['host']
    port = config['db']['port']
    database = config['db']['database']
    schema = config['db']['schema']
    
    # get private parameters
    load_dotenv()
    user = os.getenv('DATABASE_USER')
    password = os.getenv('DATABASE_PASSWORD')
    
    # Connect to the database
    engine = db.create_engine(f'mysql+mysqlconnector://{user}:{password}@{database}.{host}:{port}/{schema}')
    
    # SQL query to fetch top 10 customers with highest sales
    top_customers = ', '.join(list(map(str,customerIDs)))
    sql = """
    SELECT CustomerID, CustomerName
    FROM customers
    WHERE CustomerID IN ({})
    """.format(top_customers)
    
    # Query the database
    df = pd.read_sql(sql,con=engine)

    # Convert the df to a list of tuples
    output_lst = list(df.itertuples(index=False, name=None))
    
    return output_lst

# Lambda handler function
def lambda_handler(event, context):
    # Get the bucket and key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # get access keys
    load_dotenv()
    access_key = os.getenv('ACCESS_KEY')
    secret_key = os.getenv('SECRET_KEY')
    
    # Read the JSON file from S3
    s3_client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    response = s3_client.get_object(Bucket=bucket, Key=key)
    json_data = response['Body'].read().decode('utf-8')
    
    # Parse JSON data
    df = pd.read_json(json_data)
    customerIDs = df['CustomerID'].tolist()

    # Query customer names from the database
    customer_data = query_customer_names(customerIDs, config)

    # Prepare JSON data
    todays_date = date.today().strftime('%Y-%m-%d')
    data = []
    for customer_id, customer_name in customer_data:
        data.append({
            'id': customer_id,
            'name': customer_name,
            'date': todays_date
        })

    # Send data to API endpoint
    api_endpoint = config['api']['api_url']
    for item in data:
        response = requests.post(api_endpoint, json=item)
        if response.status_code == 201:
            print("Data sent successfully.")
        else:
            print("Failed to send data. Status code:", response.status_code)

    return {
        'statusCode': 200,
        'body': 'Function execution completed.'
    }
