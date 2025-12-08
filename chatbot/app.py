import json
import time
import os
from random import randint
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from huggingface_hub import snapshot_download

# -------------------------------------------------
# LOAD ENV
# -------------------------------------------------
load_dotenv()

# -------------------------------------------------
# APP SETUP
# -------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")  # ✅ REQUIRED ON RENDER

OTP_EXPIRY_SECONDS = 120  # ✅ 2 minutes

# -------------------------------------------------
# ✅ MAILGUN CONFIG (SMTP)
# -------------------------------------------------
app.config.update(
    MAIL_SERVER="smtp.mailgun.org",
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=f"postmaster@{os.getenv('MAILGUN_DOMAIN')}",
    MAIL_PASSWORD=os.getenv("MAILGUN_API_KEY"),
    MAIL_DEFAULT_SENDER=os.getenv("MAILGUN_FROM"),
    MAIL_TIMEOUT=10  # ✅ PREVENT HANG / WORKER KILL
)

mail = Mail(app)

# -------------------------------------------------
# ROUTES
# -------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
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
# ✅ SEND OTP (MAILGUN SAFE)
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
        session.pop("otp", None)
        session.pop("otp_time", None)
        return redirect(url_for("chat"))

    return render_template("verify.html", email=session.get("email"), msg="Invalid OTP")


@app.route("/chat")
def chat():
    return render_template("chat.html")

# -------------------------------------------------
# ✅ RAG SETUP
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


# -------------------------------------------------
# RUN
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
