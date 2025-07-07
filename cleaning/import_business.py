import json
import pymysql
from pymysql.cursors import DictCursor

# === DB CONFIGURATION ===
conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='DataScienceInstitute',
    database='yelp_db',
    charset='utf8mb4',
    cursorclass=DictCursor,
    autocommit=True
)

cursor = conn.cursor()

# === HELPER FUNCTION ===
def flatten_attributes(business_id, attributes):
    flat_attrs = []
    for key, value in attributes.items():
        if isinstance(value, dict):
            for subkey, subval in value.items():
                flat_attrs.append((business_id, f"{key}:{subkey}", str(subval)))
        else:
            flat_attrs.append((business_id, key, str(value)))
    return flat_attrs

# === MAIN INSERTION FUNCTION ===
def insert_businesses(filepath, batch_size=5000):
    with open(filepath, 'r', encoding='utf-8') as f:
        business_batch = []
        attr_batch = []
        cat_batch = []
        hours_batch = []
        count = 0

        for line in f:
            data = json.loads(line)
            business_id = data.get('business_id')

            # --- Prepare business row ---
            business_batch.append((
                business_id,
                data.get('name'),
                data.get('address'),
                data.get('city'),
                data.get('state'),
                data.get('postal_code'),
                data.get('latitude'),
                data.get('longitude'),
                data.get('stars'),
                data.get('review_count'),
                data.get('is_open')
            ))

            # --- Flatten attributes ---
            if 'attributes' in data and isinstance(data['attributes'], dict):
                attr_batch.extend(flatten_attributes(business_id, data['attributes']))

            # --- Categories ---
            if 'categories' in data and isinstance(data['categories'], list):
                for category in data['categories']:
                    cat_batch.append((business_id, category))
            elif isinstance(data.get('categories'), str):
                for category in data['categories'].split(','): # "categories":"Doctors, Traditional Chinese Medicine, Naturopathic\/Holistic, Acupuncture, Health & Medical, Nutritionists" 0> ["Doctors","Traditional Chinese Medicine"," Naturopathic\/Holistic"]
                    cat_batch.append((business_id, category.strip()))

            # --- Business hours ---
            if 'hours' in data and isinstance(data['hours'], dict):
                for day, hour in data['hours'].items():
                    hours_batch.append((business_id, day, hour))

            count += 1

            # === Insert batch ===
            if count % batch_size == 0:
                insert_all(business_batch, attr_batch, cat_batch, hours_batch)
                business_batch.clear()
                attr_batch.clear()
                cat_batch.clear()
                hours_batch.clear()
                print(f"{count} records processed...")

        # === Final Insert ===
        if business_batch:
            insert_all(business_batch, attr_batch, cat_batch, hours_batch)
            print(f"Finished inserting {count} records.")

# === BATCH INSERT FUNCTION ===
def insert_all(businesses, attributes, categories, hours):
    try:
        # Insert into business
        cursor.executemany("""
            INSERT IGNORE INTO business 
            (business_id, name, address, city, state, postal_code, latitude, longitude, stars, review_count, is_open)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, businesses)

        # Insert into attributes
        if attributes:
            cursor.executemany("""
                INSERT IGNORE INTO business_attributes (business_id, attribute_name, attribute_value)
                VALUES (%s, %s, %s)
            """, attributes)

        # Insert into categories
        if categories:
            cursor.executemany("""
                INSERT IGNORE INTO business_categories (business_id, category)
                VALUES (%s, %s)
            """, categories)

        # Insert into hours
        if hours:
            cursor.executemany("""
                INSERT IGNORE INTO business_hours (business_id, day_of_week, hours)
                VALUES (%s, %s, %s)
            """, hours)

    except Exception as e:
        print("Error inserting batch:", e)




insert_businesses('yelp_academic_dataset_business.json')
cursor.close()
conn.close()
