from flask import Flask, render_template, request, jsonify
from transformers import pipeline
import sqlite3
import pickle
from langchain.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Initialize the QA pipeline
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

app = Flask(__name__)

# Function to load the FAISS vector store from the SQLite database
def load_faiss_store():
    conn = sqlite3.connect('embeddings.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, doc_content, embedding_blob FROM embeddings")
    rows = cursor.fetchall()
    conn.close()
    
    # Load embeddings into FAISS vector store
    docs = []
    embeddings = []
    for row in rows:
        doc_id, doc_content, embedding_blob = row
        embedding = pickle.loads(embedding_blob)
        docs.append(doc_content)
        embeddings.append(embedding)

    embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    vector_store = FAISS.from_embeddings(embeddings, embedding_model)
    return vector_store

# Load the FAISS store
vector_store = load_faiss_store()
retriever = vector_store.as_retriever()

# Function to answer a query using the QA pipeline and the retriever
def answer_query(query):
    relevant_docs = retriever.get_relevant_documents(query)
    context = " ".join(doc.page_content for doc in relevant_docs)
    result = qa_pipeline(question=query, context=context)
    return result['answer']

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["POST"])
def chat():
    msg = request.form["msg"]
    response = get_chat_response(msg)
    return jsonify(response)

def get_chat_response(text):
    return answer_query(text)

if __name__ == '__main__':
    app.run()
