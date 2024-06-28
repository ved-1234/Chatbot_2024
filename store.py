import sqlite3

def load_embeddings(file_path):
    """
    Loads embeddings from a file.
    
    Args:
    file_path (str): The path to the file containing embeddings.
    
    Returns:
    list: A list of embeddings, where each embedding is a list of floats.
    """
    embeddings = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            emb = [float(x) for x in line.strip().split(',')]
            embeddings.append(emb)
    return embeddings

def create_database(db_file):
    """
    Creates an SQLite database file and initializes the table for embeddings.
    
    Args:
    db_file (str): The path to the SQLite database file.
    """
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    
    # Create table
    c.execute('''CREATE TABLE embeddings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 embedding TEXT)''')
    
    conn.commit()
    conn.close()

def insert_embeddings(embeddings, db_file):
    """
    Inserts embeddings into the SQLite database.
    
    Args:
    embeddings (list): A list of embeddings, where each embedding is a list of floats.
    db_file (str): The path to the SQLite database file.
    """
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    
    for emb in embeddings:
        emb_str = ','.join(map(str, emb))
        c.execute("INSERT INTO embeddings (embedding) VALUES (?)", (emb_str,))
    
    conn.commit()
    conn.close()

def main():
    """
    Main function to load embeddings from file and store them in an SQLite database.
    """
    file_path = 'embedding.txt'  # Path to your embeddings file
    db_file = 'embeddings.db'    # SQLite database file
    
    # Load embeddings from file
    embeddings = load_embeddings(file_path)
    
    # Create SQLite database and table
    create_database(db_file)
    
    # Insert embeddings into SQLite database
    insert_embeddings(embeddings, db_file)
    
    print(f'Embeddings loaded and stored in SQLite database "{db_file}".')

if __name__ == "__main__":
    main()
