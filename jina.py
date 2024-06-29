from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import faiss
import numpy as np


# Initialize the model
model = SentenceTransformer(
    "jinaai/jina-embeddings-v2-base-en",  # switch to en/zh for English or Chinese
    trust_remote_code=True
)

# Set the maximum sequence length
model.max_seq_length = 1024

# Function to read contents from a .txt file
def read_txt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return [line.strip() for line in lines if line.strip()]

# Path to your .txt file
file_path = 'data.txt'

# Read file and get lines
lines = read_txt_file(file_path)

# Encode lines into embeddings
embeddings = model.encode(lines)

# # Example to print embeddings and cosine similarity between first two lines
# if len(embeddings) > 1:
#     print(cos_sim(embeddings[0], embeddings[1]))

# Print all embeddings
print(embeddings)
embeddings_np = np.array(embeddings)

# Dimensions of the embeddings
d = embeddings_np.shape[1]

# Create a FAISS index
index = faiss.IndexFlatL2(d)  # L2 distance is the most common distance metric

# Add embeddings to the index
index.add(embeddings_np)


# Optionally, save the index to disk for future use
faiss.write_index(index, 'embeddings_index.faiss')

# print(f"Stored {index.ntotal} vectors in the FAISS index.")
# print(faiss.index[0])
first_embedding = index.reconstruct(0)
print("First embedding:", first_embedding)

