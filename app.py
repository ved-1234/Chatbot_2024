import json
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_mail import Mail, Message
from random import randint
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import requests

app = Flask(__name__)

# Load email configuration from config.json
with open('config.json', 'r') as f:
    params = json.load(f)['params']

# Configure Flask app
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = params['gmail-user']
app.config['MAIL_PASSWORD'] = params['gmail-password']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

# Initialize Flask-Mail
mail = Mail(app)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        # Here you can add code to save the user's registration info to the database
        return redirect(url_for('home'))
    return render_template('register.html', msg="")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        # Here you can add code to verify the user's login info
        return redirect(url_for('email'))
    return render_template('login.html', msg="")

@app.route("/email")
def email():
    return render_template('email.html', msg="")

@app.route('/verify', methods=["POST"])
def verify():
    gmail = request.form['email']
    otp = randint(1000, 9999)  # Ensure OTP is 4 digits
    session['otp'] = otp
    msg = Message('OTP', sender=app.config['MAIL_USERNAME'], recipients=[gmail])
    msg.body = str(otp)
    mail.send(msg)
    return render_template("verify.html", email=gmail)

@app.route('/validate', methods=["POST"])
def validate():
    userotp = request.form['otp']
    otp = session.get('otp')
    if otp and otp == int(userotp):
        session.pop('otp', None)
        return redirect(url_for('chat'))
    return render_template('email.html', msg='Not verified! Please try again.')

@app.route('/chat')
def chat():
    return render_template('chat.html')

load_dotenv()
groq_api_key = os.environ['GROQ_API_KEY']

loadingDatabase = FAISS.load_local(
    'faissTrial',
    OllamaEmbeddings(model='llama3'),
    allow_dangerous_deserialization=True
)
prompt = ChatPromptTemplate.from_template("""
Answer the following question based only on the provided context. 
Please provide the most accurate response based on the question. 

<context>
{context}
</context>
Question: {input}""")

llm = ChatGroq(groq_api_key=groq_api_key, model='llama3-8b-8192')
documentchain = create_stuff_documents_chain(llm=llm, prompt=prompt)
retriever = loadingDatabase.as_retriever()
retrieverChain = create_retrieval_chain(retriever, documentchain)

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('msg')
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    response = retrieverChain.invoke({'input': question})
    answer = response.get('answer')
    return jsonify({'answer': answer})

@app.route('/get', methods=['POST'])
def get_answer():
    msg = request.form['msg']
    if not msg:
        return jsonify({'error': 'No message provided'}), 400
    ask_response = requests.post('http://localhost:8000/ask', json={'msg': msg})
    if ask_response.status_code != 200:
        return jsonify({'error': 'Error in /ask route'}), ask_response.status_code
    ask_response_data = ask_response.json()
    answer = ask_response_data.get('answer', 'No answer found')
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(debug=True, port=8000)
