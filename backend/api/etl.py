import os
import psycopg2
import requests

# Config
base_url = "https://api.kierratys.info/collectionspots/"
api_key = env_var_value = os.getenv("KIERRATYS_API_KEY")

try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="foobar",
        host="localhost",
        port="5434",
    )
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS recycler.collection_spots")

    c.execute(
        """CREATE TABLE IF NOT EXISTS recycler.collection_spots
                (id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                name TEXT,
                address TEXT)"""
    )

    # Clear the table
    c.execute("DELETE FROM recycler.collection_spots")

    # Initialize total_items
    total_items = None

    # Get the details of the first page and set total_items
    url = f"{base_url}?api_key={api_key}&format=json&limit=1000&offset=0"
    response = requests.get(url)
    data = response.json()
    total_items = data["count"]

    # Iterate through all pages and save the data to the database
    limit = 1000
    offset = 0
    total_pages = int(total_items / limit + 1)

    while offset < total_items:
        url = f"{base_url}?api_key={api_key}&format=json&limit={limit}&offset={offset}"

        page = int(offset / limit + 1)

        print("Loading page " + str(page) + " of " + total_pages)

        response = requests.get(url)
        data = response.json()

        # Iterate through the search results and save them to the database
        for item in data["results"]:
            name = item["name"]
            address = item["address"]
            c.execute(
                "INSERT INTO recycler.collection_spots (name, address) VALUES (%s, %s)",
                (name, address),
            )

        # Update the offset for the next page
        offset += limit

    conn.commit()
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Save the changes and close the database connection
    if conn:
        conn.close()
