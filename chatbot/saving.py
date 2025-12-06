from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import TextLoader
loader=TextLoader('data.txt',encoding='utf-8')
txtLoaderDocument=loader.load()
textSplitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
documents=textSplitter.split_documents(txtLoaderDocument)
vectorDatabase=FAISS.from_documents(documents=documents[:5],embedding=OllamaEmbeddings(model='llama3'))
vectorDatabase.save_local('faissTrial')