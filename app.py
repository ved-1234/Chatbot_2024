import chromadb.utils.embedding_functions as embedding_functions

ollama_ef = embedding_functions.OllamaEmbeddingFunction(
    url="http://localhost:11434/api/embeddings",
    model_name="llama3"
)
texts_to_embed = [
    "This is my first text to embed",
    "This is my second document"
]

try:
    embeddings = ollama_ef(texts_to_embed)
    print("Embeddings:", embeddings)
except Exception as e:
    print("Error generating embeddings:", e)
