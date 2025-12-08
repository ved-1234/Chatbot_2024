import json
import time
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_mail import Mail, Message
from random import randint
import os
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from huggingface_hub import snapshot_download

load_dotenv()

app = Flask(__name__)

# -------------------------------------------------
# SECURITY
# -------------------------------------------------
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")


# -------------------------------------------------
# MAIL CONFIG
# -------------------------------------------------
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_TIMEOUT=10  # ✅ PREVENT SMTP HANG
)

mail = Mail(app)

OTP_EXPIRY_SECONDS = 120  # ✅ 2 minutes

# -------------------------------------------------
# ROUTES
# -------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # later you can add DB logic here
        return redirect(url_for("login"))
    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for("email"))
    return render_template("login.html")


@app.route("/email")
def email():
    return render_template("email.html", msg="")


# -------------------------------------------------
# ✅ SEND OTP (SAFE)
# -------------------------------------------------
@app.route("/verify", methods=["POST"])
def verify():
    email = request.form["email"]

    otp = randint(1000, 9999)
    session["otp"] = otp
    session["otp_time"] = time.time()
    session["email"] = email

    msg = Message(
        subject="Your OTP Verification Code",
        sender=app.config["MAIL_USERNAME"],
        recipients=[email],
        body=f"Your OTP is {otp}. Valid for 2 minutes."
    )

    try:
        mail.send(msg)
    except Exception as e:
        print("MAIL ERROR:", e)
        return render_template("email.html", msg="Email service unavailable. Try again.")

    return render_template("verify.html", email=email)


# -------------------------------------------------
# ✅ VALIDATE OTP
# -------------------------------------------------
@app.route("/validate", methods=["POST"])
def validate():
    user_otp = request.form["otp"]

    stored_otp = session.get("otp")
    otp_time = session.get("otp_time")

    if not stored_otp or not otp_time:
        return render_template("email.html", msg="Session expired. Try again.")

    if time.time() - otp_time > OTP_EXPIRY_SECONDS:
        session.clear()
        return render_template("email.html", msg="OTP expired. Please retry.")

    if int(user_otp) == int(stored_otp):
        session.pop("otp")
        session.pop("otp_time")
        return redirect(url_for("chat"))

    return render_template("verify.html", email=session.get("email"), msg="Invalid OTP")


@app.route("/chat")
def chat():
    return render_template("chat.html")

# -------------------------------------------------
# RAG SETUP
# -------------------------------------------------
groq_api_key = os.environ["GROQ_API_KEY"]

embeddings = OllamaEmbeddings(model="nomic-embed-text")

FAISS_REPO_ID = "ved123456/faiss-chatbot-index"

faiss_path = snapshot_download(
    repo_id=FAISS_REPO_ID,
    repo_type="dataset",
    local_dir="faiss_downloaded",
    local_dir_use_symlinks=False
)

db = FAISS.load_local(
    faiss_path,
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = db.as_retriever()

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
Answer ONLY using the context below.
If not found say:
"I cannot find that information in the documents."

<context>
{context}
</context>

Question: {question}
"""
)

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model="llama-3.1-8b-instant"
)

def rag_answer(question):
    docs = retriever.get_relevant_documents(question)
    context = "\n\n".join(d.page_content for d in docs if d.page_content.strip())

    response = llm.invoke(
        prompt.format(context=context, question=question)
    )
    return response.content

# -------------------------------------------------
# CHAT API
# -------------------------------------------------
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("msg")

    if not question:
        return jsonify({"error": "Empty question"}), 400

    answer = rag_answer(question)

    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
