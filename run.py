import sqlalchemy as db
import pandas as pd
import toml
from dotenv import load_dotenv 
import subprocess
import os

if __name__=="__main__":
    
    config = toml.load('config.toml')
    
    # Database connection parameters
    host = config['db']['host']
    port = config['db']['port']
    database = config['db']['database']
    schema = config['db']['schema']

    # get private parameters
    load_dotenv()
    user=os.getenv('DATABASE_USER')
    password=os.getenv('DATABASE_PASSWORD')

    # Connect to the database
    engine = db.create_engine(f'mysql+mysqlconnector://{user}:{password}@{database}.{host}:{port}/{schema}')

    # SQL query to fetch top 10 customers with highest sales
    sql = """
    SELECT CustomerID, SUM(Sales) AS TotalSales
    FROM orders
    GROUP BY CustomerID
    ORDER BY SUM(Sales) DESC
    LIMIT 10
    """
    # Query the database
    df = pd.read_sql(sql,con=engine)
    df.to_json('top_10_customers.json')

    # get s3 bucket info
    bucket=config['s3']['bucket']
    folder=config['s3']['folder']

    # copy json file to S3
    subprocess.call(['aws','s3','cp','top_10_customers.json', f's3://{bucket}/{folder}/top_10_customers.json'])
    
