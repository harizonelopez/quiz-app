
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = 'aladinh-montext'  

DATABASE = 'users.db'

def connect_db():
    return sqlite3.connect(DATABASE)

def create_table():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

class Question:
    def __init__(self, prompt, options, correct_answer):
        self.prompt = prompt
        self.options = options
        self.correct_answer = correct_answer

questions = [
    Question("What is the capital of France?", ["London", "Paris", "Berlin"], 1),
    Question("Which programming language is this quiz written in?", ["Java", "Python", "C++"], 1),
    Question("What is the capital of Japan?", ["Beijing", "Seoul", "Tokyo"], 2),
    Question("Which planet is known as the Red Planet?", ["Venus", "Mars", "Jupiter"], 1),
    Question("Who wrote 'Romeo and Juliet'?", ["Charles Dickens", "William Shakespeare", "Jane Austen"], 1),
    Question("What is the largest mammal on Earth?", ["Elephant", "Blue Whale", "Giraffe"], 2),
    Question("In which year did the Titanic sink?", ["1912", "1920", "1935"], 1),
    Question("What is the powerhouse of the cell?", ["Nucleus", "Mitochondria", "Endoplasmic Reticulum"], 1),
    Question("Which programming language is often used for machine learning?", ["Java", "Python", "C#"], 2),
    Question("What is the capital of Kenya?", ["Kisumu", "Eldoret", "Nairobi"], 2),

]

# Initialize Quiz
quiz = Quiz(questions)

]

class Quiz:
    def __init__(self, questions):
        self.questions = questions
        self.current_question_index = 0
        self.score = 0

    def get_current_question(self):
        return self.questions[self.current_question_index]

    def submit_answer(self, user_answer):
        correct_answer = self.get_current_question().correct_answer
        if user_answer == correct_answer:
            self.score += 1

    def next_question(self):
        self.current_question_index += 1

    def is_finished(self):
        return self.current_question_index == len(self.questions)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'username' not in session:
        flash('Please login to take the quiz.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_answer = int(request.form['answer'])

        if user_answer == quiz.get_current_question().correct_answer:
            flash('Congrats, Correct answer!')
        else:
            flash('Oops, Incorrect answer! Try again')

            quiz.next_question()

        if quiz.is_finished():
            flash(f'Quiz completed! You scored {quiz.score}/{len(quiz.questions)}.')
            return redirect(url_for('home'))

    return render_template('quiz.html', quiz=quiz)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect_db()
        c = conn.cursor()

        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        existing_user = c.fetchone()

        if existing_user:
            flash('Username already taken. Please choose another.')
        else:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            flash('Account created successfully. Please login.')
            return redirect(url_for('login'))

        conn.close()

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect_db()
        c = conn.cursor()

        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()

        if user and check_password_hash(user[2], password):
            session['username'] = username
            flash('Login successful!')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.')

        conn.close()

    return render_template('login.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        return redirect(url_for('home'))
    
    return render_template('contacts.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    create_table()
    app.run(debug=True)
