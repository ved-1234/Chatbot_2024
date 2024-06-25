import sqlite3
import numpy as np
import ast

# Connect to the SQLite database
conn = sqlite3.connect('embeddings.db')
cursor = conn.cursor()

# Create a table to store the embeddings



# Load the embeddings from the file
with open("embeddings.txt", "r") as f:
    embeddings = [line.strip() for line in f.readlines()]

# Convert the embeddings to a list of NumPy arrays
embeddings_array = [np.array(ast.literal_eval(embedding)) for embedding in embeddings]

# Insert the embeddings into the database
for i, embedding in enumerate(embeddings_array):
    cursor.execute('''
        INSERT INTO embeddings (id, embedding) VALUES (?,?)
    ''', (i, sqlite3.Binary(embedding.tobytes())))

# Commit the changes
conn.commit()
cursor.execute('SELECT * FROM embeddings')

# Fetch all the rows
rows = cursor.fetchall()

# Print the table contents
for row in rows:
    print(row)


# Close the connection
conn.close()
