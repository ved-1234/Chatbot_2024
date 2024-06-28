from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import numpy as np
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

app = FastAPI()

# Load the pre-trained model (e.g., Sentence-BERT)
model = SentenceTransformer('all-MiniLM-L6-v2')

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

# Define the request and response models for FastAPI
class QueryRequest(BaseModel):
    query: str

class GeneratedResponse(BaseModel):
    generated_response: str

# Define the LLM model (for example, using OpenAI's GPT-3 API)
class LLMModel:
    def generate(self, prompt):
        # Implement the LLM model's generate function
        # For example, you can use OpenAI's GPT-3 API like this:
        # response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=150)
        # return response.choices[0].text.strip()
        
        # For demonstration purposes, we'll return a simple echo response
        return f"Generated response based on prompt: {prompt}"

llm_model = LLMModel()

# Function to send response and query to LLM model for generating
def generate_response(query, embeddings, llm_model):
    # Combine query and retrieved documents to generate a response
    prompt = f"Query: {query}\nResponse:\nEmbeddings: {embeddings}"
    
    # Generate the response using the LLM model
    generated_response = llm_model.generate(prompt)
    return generated_response

@app.post("/generate_response", response_model=GeneratedResponse)
async def generate_response_endpoint(request: QueryRequest):
    query = request.query
    
    # Retrieve all embeddings and their similarities to the query
    similarities = retrieve_all_similarities(query, model)
    
    if not similarities:
        raise HTTPException(status_code=404, detail="No embeddings found")
    
    # Get the top similarity embedding ID and similarity score
    top_similarity_id, top_similarity_score = similarities[0]
    
    # For demonstration, assume the top retrieved embedding is available directly
    # Ideally, you should retrieve the embedding from the database
    top_retrieved_embedding = [embedding for embedding_id, embedding in similarities if embedding_id == top_similarity_id][0]
    
    # Generate a response using the LLM model
    generated_response = generate_response(query, [top_retrieved_embedding], llm_model)
    
    return GeneratedResponse(generated_response=generated_response)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)

