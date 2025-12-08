Installation and Setup
Clone the Repository

git clone https://github.com/ved-1234/Chatbot_2024.git

cd Chatbot_2024

cd chatbot 

Create Virtual Environment

python -m venv venv

source venv/bin/activate   # On Windows: venv\Scripts\activate

Install Dependencies

pip install -r requirements.txt

Environment Variables (.env)

Create a .env file and add:

SECRET_KEY=your_secret_key

GROQ_API_KEY=your_groq_api_key

#MailGun service

MAILGUN_API_KEY=your_mailgun_api_key

MAILGUN_DOMAIN=your_mailgun_domain

MAILGUN_FROM=Your Name <mailgun@yourdomain>

Run the Application

python app.py


The app will run on:

http://localhost:10000
