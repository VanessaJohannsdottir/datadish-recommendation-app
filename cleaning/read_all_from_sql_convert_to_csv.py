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


###### EXPORT business
file_path = f'../data/business.csv'

query = f"""
select * from business_processed
"""
df = pd.read_sql(query, conn)

df.to_csv(file_path, index=False, encoding='utf-8')


###### EXPORT business_categories
file_path = f'../data/business_categories.csv'

query = f"""
select * from business_categories_processed
"""
df = pd.read_sql(query, conn)

df.to_csv(file_path, index=False, encoding='utf-8')


###### EXPORT business_attributes
file_path = f'../data/business_attributes.csv'

query = f"""
select * from business_attributes_processed
"""
df = pd.read_sql(query, conn)

df.to_csv(file_path, index=False, encoding='utf-8')


###### EXPORT business_hours
file_path = f'../data/business_hours.csv'

query = f"""
select * from business_hours_processed
"""
df = pd.read_sql(query, conn)

df.to_csv(file_path, index=False, encoding='utf-8')

# Close the connection
conn.close()