import sqlite3
import numpy as np
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Function to convert a query to an embedding using a pre-trained model
def query_to_embedding(query, model):
    return model.encode([query])[0]  # Ensure it returns a vector for a single query

# Function to retrieve all embeddings and their similarities to a query
def retrieve_all_similarities(query, model, db_path='embeddings.db'):
    # Convert the query to an embedding
    query_embedding = query_to_embedding(query, model)
    original_dimension = query_embedding.shape[0]  # Get the original dimension
    
    # Debug: Print the shape of the query embedding
    print("Query embedding shape:", query_embedding.shape)
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fetch all embeddings from the database
    cursor.execute('SELECT id, embedding FROM embeddings')
    rows = cursor.fetchall()
    
    # Extract embeddings and ensure they are NumPy arrays
    embeddings = []
    ids = []
    for row in rows:
        embedding_id = row[0]
        embedding_str = row[1]
        
        # Convert embedding string to numpy array
        embedding = np.array([float(x) for x in embedding_str.split(',')])
        
        # Debug: Print detailed information about each embedding
        print(f"Embedding ID {embedding_id} shape:", embedding.shape)
        
        # Store embeddings and IDs
        embeddings.append(embedding)
        ids.append(embedding_id)
    
    # Convert embeddings list to numpy array and ensure they have uniform shape using PCA
    embeddings = np.array(embeddings)
    if embeddings.shape[1] != original_dimension:
        print(f"Reducing dimensionality of embeddings from {embeddings.shape[1]} to {original_dimension}")
        pca = PCA(n_components=original_dimension)
        embeddings = pca.fit_transform(embeddings)
    
    # Calculate similarity for each embedding
    similarities = []
    for i, embedding in enumerate(embeddings):
        similarity = cosine_similarity(query_embedding.reshape(1, -1), embedding.reshape(1, -1))
        similarities.append((ids[i], similarity[0][0]))  # Store ID and similarity
    
    # Sort by similarity in descending order
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return similarities

# Load the pre-trained model (e.g., Sentence-BERT)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Example usage
user_query = "how many members are there in comps faculty?"
similarities = retrieve_all_similarities(user_query, model)

print("User Query:", user_query)
print("Similarities:")
for idx, similarity in similarities[:10]:  # Print top 10 similarities
    print(f"Embedding ID: {idx}, Similarity: {similarity:.4f}")

