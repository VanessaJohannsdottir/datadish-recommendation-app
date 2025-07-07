import json
import pymysql
from pymysql.cursors import DictCursor

# DB connection
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

# cursor.execute("DROP TABLE IF EXISTS review")
# cursor.execute("""
#     CREATE TABLE review (
#         review_id VARCHAR(22) PRIMARY KEY,
#         user_id VARCHAR(22),
#         business_id VARCHAR(22),
#         stars INT,
#         date DATE,
#         text TEXT,
#         useful INT,
#         funny INT,
#         cool INT
#     )
# """)

file_path = "yelp_academic_dataset_review.json" 

batch = []
batch_size = 20000

with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        batch.append((
            data['review_id'],
            data['user_id'],
            data['business_id'],
            data['stars'],
            data['date'],
            data['text'],
            data['useful'],
            data['funny'],
            data['cool']
        ))

        # Insert in batches for speed & efficiency
        if len(batch) >= batch_size:
            cursor.executemany("""
                INSERT INTO review (
                    review_id, user_id, business_id, stars, date, text, useful, funny, cool
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, batch)
            print(f'{len(batch)} has been inserted')
            batch = []
            

# Insert remaining
if batch:
    cursor.executemany("""
        INSERT INTO review (
            review_id, user_id, business_id, stars, date, text, useful, funny, cool
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, batch)

print("Review import completed.")
