
# from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings import OllamaEmbeddings
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.chains  import create_retrieval_chain
# from langchain.prompts import ChatPromptTemplate
# from flask import Flask, request, jsonify
# from langchain_groq import ChatGroq
# import os
# from flask import Flask, render_template, request, jsonify
# import requests
# from dotenv import load_dotenv
# load_dotenv()
# groq_api_key=os.environ['GROQ_API_KEY']
# app = Flask(__name__)
# loadingDatabase=FAISS.load_local(
#     'faissTrial',
#     OllamaEmbeddings(model='llama3'),
#     allow_dangerous_deserialization=True
# )
# prompt = ChatPromptTemplate.from_template("""
# Answer the following question based only on the provided context. 
# please provide the most accurate response based on the question. 

# <context>
# {context}
# </context>
# Question: {input}""")

# llm=ChatGroq(groq_api_key=groq_api_key,model='llama3-8b-8192')
# documentchain=create_stuff_documents_chain(llm=llm,prompt=prompt)
# retriever=loadingDatabase.as_retriever()
# retrieverChain=create_retrieval_chain(retriever,documentchain)

# from flask import Flask, render_template, request, jsonify
# import requests

# app = Flask(__name__)

# @app.route('/')
# def home():
#     return render_template('chat.html')

# @app.route('/ask', methods=['POST'])
# def ask_question():
#     data = request.json
#     question = data.get('msg')
#     if not question:
#         return jsonify({'error': 'No question provided'}), 400
    
#     response = retrieverChain.invoke({'input': question})
#     answer = response.get('answer')
    
#     return jsonify({'answer': answer})


# @app.route('/get', methods=['GET','POST'])
# def get_answer():
#     msg = request.form['msg']
#     if not msg:
#         return jsonify({'error': 'No message provided'}), 400
    
#     ask_response = requests.post('http://localhost:8000/ask', json={'msg': msg})
    
#     if ask_response.status_code != 200:
#         return jsonify({'error': 'Error in /ask route'}), ask_response.status_code
    
#     ask_response_data = ask_response.json()
#     answer = ask_response_data.get('answer', 'No answer found')
    
#     return jsonify({'answer': answer})

# if __name__ == '__main__':
#     app.run(debug=True,port=8000)