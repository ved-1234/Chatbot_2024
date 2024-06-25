import sqlite3
import numpy as np
import ast

# Connect to the SQLite database
conn = sqlite3.connect('embeddings.db')
cursor = conn.cursor()

# Create the table with an auto-incrementing primary key
cursor.execute('''
    CREATE TABLE IF NOT EXISTS embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        embedding BLOB
    )
''')

# Load the embeddings from the file
with open("embeddings.txt", "r") as f:
    embeddings = [line.strip() for line in f.readlines()]

# Convert the embeddings to a list of NumPy arrays
embeddings_array = [np.array(ast.literal_eval(embedding), dtype=np.float32) for embedding in embeddings]

# Insert the embeddings into the database
for embedding in embeddings_array:
    # Debug: Print the shape of the embedding before storage
    print(f"Storing embedding with shape: {embedding.shape}")
    cursor.execute('''
        INSERT INTO embeddings (embedding) VALUES (?)
    ''', (sqlite3.Binary(embedding.tobytes()),))

# Commit the changes
conn.commit()

cursor.execute('SELECT * FROM embeddings')

# Fetch all the rows
rows = cursor.fetchall()

# Print the table contents with shapes
for row in rows:
    embedding = np.frombuffer(row[1], dtype=np.float32)
    print(f"ID: {row[0]}, Embedding shape after retrieval: {embedding.shape}")

# Close the connection
conn.close()
