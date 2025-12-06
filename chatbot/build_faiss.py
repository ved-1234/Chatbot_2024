import os
from tqdm import tqdm
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader

print("\n📄 Loading PDF documents...")
loader = DirectoryLoader("reqd", glob="**/*.pdf")
docs = loader.load()
print(f"Loaded {len(docs)} PDF documents.\n")

print("✂️ Splitting documents into chunks...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(docs)
print(f"Created {len(chunks)} chunks.\n")

print("🔍 Loading embedding model (nomic-embed-text)...")
embedder = OllamaEmbeddings(model="nomic-embed-text")

texts = [chunk.page_content for chunk in chunks]
metadatas = [chunk.metadata for chunk in chunks]

print("⚙️ Generating embeddings...\n")
vectors = []
batch_size = 10

for i in tqdm(range(0, len(texts), batch_size), desc="Embedding"):
    batch = texts[i:i + batch_size]
    vecs = embedder.embed_documents(batch)
    vectors.extend(vecs)

print("\nEmbedding completed!")

print("\n🗄️ Building FAISS index...")

# Convert to (text, embedding) pairs
text_embeddings = list(zip(texts, vectors))

# Build FAISS using the correct format
vectorstore = FAISS.from_embeddings(text_embeddings, embedder)

os.makedirs("faissTrial", exist_ok=True)

print("💾 Saving FAISS index...")
vectorstore.save_local("faissTrial")

print("\n✅ FAISS index saved successfully in 'faissTrial/'")
