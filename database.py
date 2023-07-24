import requests
import xml.etree.ElementTree as ET
import psycopg2

def get_feed_data(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.content
    else:
        return None

# Database connection credentials
db_host = 'localhost'
db_name = 'lab'
db_user = 'postgres'
db_password = '1610'

# Establishing connection
conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)
cursor = conn.cursor()

# Creating the table
create_table_query = '''
    CREATE TABLE IF NOT EXISTS feed_data (
        id SERIAL PRIMARY KEY,
        title TEXT,
        link TEXT,
        description TEXT,
        pub_date TIMESTAMP
    )
'''
cursor.execute(create_table_query)
conn.commit()

# Extracting data
feed_url = "https://feeds.bbci.co.uk/news/rss.xml"  
feed_data = get_feed_data(feed_url)

if feed_data:
    root = ET.fromstring(feed_data)
    
    # Iterate over items and insert data into the table
    for item in root.findall('.//item'):
        title = item.find('title').text
        link = item.find('link').text
        description = item.find('description').text
        pub_date = item.find('pubDate').text
        
        # Inserting data into the table
        insert_query = '''
            INSERT INTO feed_data (title, link, description, pub_date)
            VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(insert_query, (title, link, description, pub_date))
        conn.commit()

    print("Feed data stored in PostgreSQL successfully.")
else:
    print("Failed to retrieve feed data.")

# Closing the database connection
cursor.close()
conn.close()
