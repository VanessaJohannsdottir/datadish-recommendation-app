import pandas as pd
import mysql.connector
import os

# Set up the database connection
conn = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='DataScienceInstitute',
    database='yelp_db'
)


file_path = f'../data/reviews.csv'

query = f"""
select * from review_processed
"""
df = pd.read_sql(query, conn)

df.to_csv(file_path, index=False, encoding='utf-8')

# Close the connection
conn.close()