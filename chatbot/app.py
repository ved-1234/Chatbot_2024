import json
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_mail import Mail, Message
from random import randint
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from huggingface_hub import snapshot_download


load_dotenv()
app = Flask(__name__)

# -------------------------------------
# Email + Flask Config
# -------------------------------------
with open('config.json', 'r') as f:
    params = json.load(f)['params']

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# -------------------------------------
# ROUTES
# -------------------------------------

@app.route("/")
def home():
    return render_template('home.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        return redirect(url_for('home'))
    return render_template('register.html', msg="")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for('email'))
    return render_template('login.html', msg="")


@app.route("/email")
def email():
    return render_template('email.html', msg="")


@app.route('/verify', methods=["POST"])
def verify():
    gmail = request.form['email']
    otp = randint(1000, 9999)
    session['otp'] = otp
    msg = Message('OTP', sender=app.config['MAIL_USERNAME'], recipients=[gmail])
    msg.body = str(otp)
    mail.send(msg)
    return render_template("verify.html", email=gmail)


@app.route('/validate', methods=["POST"])
def validate():
    userotp = request.form['otp']
    if session.get('otp') == int(userotp):
        session.pop('otp', None)
        return redirect(url_for('chat'))
    return render_template('email.html', msg='Not verified! Please try again.')



@app.route('/chat')
def chat():
    return render_template('chat.html')

# -------------------------------------
# RAG SETUP  
# (FAISS + manual context injection to avoid LangChain bugs)
# -------------------------------------

groq_api_key = os.environ['GROQ_API_KEY']
embeddings = OllamaEmbeddings(model='nomic-embed-text')

# Load your FAISS index
# -------------------------------------
# Download FAISS index from Hugging Face
# -------------------------------------

FAISS_REPO_ID = "ved123456/faiss-chatbot-model"  # ✅ CHANGE THIS

faiss_path = snapshot_download(
    repo_id=FAISS_REPO_ID,
    repo_type="model",   # or "dataset" depending on how you uploaded
    local_dir="faiss_downloaded",
    local_dir_use_symlinks=False
)

# Load FAISS from downloaded directory
db = FAISS.load_local(
    faiss_path,
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = db.as_retriever()


retriever = db.as_retriever()

# ---- FIXED WORKING PROMPT ----
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
Answer the question using ONLY the context below.
If the answer is not in the context, reply exactly:
"I cannot find that information in the documents."

<context>
{context}
</context>

Question: {question}
"""
)

# LLM
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model='llama-3.1-8b-instant'
)

# ---- WORKING RAG FUNCTION ----
def rag_answer(question):
    # Step 1: retrieve docs from FAISS
    docs = retriever.get_relevant_documents(question)

    # Step 2: join text
    context_text = "\n\n".join([doc.page_content for doc in docs if doc.page_content.strip()])

    # Step 3: format prompt
    final_prompt = prompt.format(
        context=context_text,
        question=question
    )

    # Step 4: ask LLM
    response = llm.invoke(final_prompt)

    return response.content, docs


# -------------------------------------
# ASK ENDPOINT
# -------------------------------------
@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.json.get('msg')

    if not question:
        return jsonify({'error': 'No question provided'}), 400

    answer, docs = rag_answer(question)

    print("\n--------------------")
    print("🔍 RETRIEVED DOCUMENTS:")
    for doc in docs:
        print(doc.page_content[:300])
        print("--------------------")
    print("--------------------\n")

    return jsonify({
        "answer": answer,
        "context": [doc.page_content[:200] for doc in docs]
    })


if __name__ == '__main__':
    app.run(debug=True, port=8000)
