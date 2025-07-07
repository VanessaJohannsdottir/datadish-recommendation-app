import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import ast
import json
import re

# Set up the database connection
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'DataScienceInstitute',
    'database': 'yelp_db'
}

# Connect using SQLAlchemy for easy UPDATE
engine = create_engine(
    f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
)


# Step 2: Clean and normalize the stringified dict
# {'dj': False, u'background_music': False, 'no_music': False, u'jukebox': True, 'live': True, 'video': False, 'karaoke': False} -> ["live", "jukebox"]
# {u'divey': False, u'hipster': False, u'casual': True, u'touristy': False, u'trendy': None, u'intimate': False, u'romantic': False, u'classy': False, u'upscale': False} -> ["casual"]
# {'dessert': True, 'latenight': False, 'lunch': True, 'dinner': True, 'brunch': None, 'breakfast': False} -> ["dessert", "lunch", "dinner"]
# {'monday': False, 'tuesday': True, 'friday': False, 'wednesday': False, 'thursday': True, 'sunday': True, 'saturday': False} -> ["tuesday", "thursday", "sunday"]
# {'dairy-free': False, 'gluten-free': True, 'vegan': False, 'kosher': False, 'halal': False, 'soy-free': False, 'vegetarian': False} -> ["gluten-free"]
def cleaner(value):
    if pd.isna(value):
        return None
    try:
        # 1. Replace Python-style values with JSON equivalents
        cleaned = value
        cleaned = re.sub(r"u'([^']*)'", r'"\1"', cleaned)      # u'string' → "string"
        cleaned = re.sub(r"'", '"', cleaned)                   # ' → "
        cleaned = cleaned.replace("False", "false")
        cleaned = cleaned.replace("True", "true")
        cleaned = cleaned.replace("None", "null")

        # 2. Try parsing as JSON
        music_dict = json.loads(cleaned)

        # 3. Extract keys where value == true
        true_keys = [k for k, v in music_dict.items() if v is True]

        return json.dumps(true_keys)  # as valid JSON string
    except Exception as e:
        print(f"Error parsing row:\n{value}\n{e}")
        return None
    
def clean_it(engine, attr):
    query = f"SELECT business_id, attribute_value FROM business_attributes_processed WHERE attribute_name = '{attr}'"
    df = pd.read_sql(query, engine)
    df['cleaned'] = df['attribute_value'].apply(cleaner)

    # Step 3: Update each cleaned value back to the DB
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    for index, row in df.iterrows():
        if row['cleaned'] is None:
            continue
        update_query = f"""
            UPDATE business_attributes_processed
            SET attribute_value = %s
            WHERE business_id = %s AND attribute_name = '{attr}'
        """
        cursor.execute(update_query, (row['cleaned'], row['business_id']))

    connection.commit()
    cursor.close()
    connection.close()
    
clean_it(engine, "Music")
clean_it(engine, "BusinessParking")
clean_it(engine, "Ambience")
clean_it(engine, "GoodForMeal")
clean_it(engine, "BestNights")
clean_it(engine, "DietaryRestrictions")
