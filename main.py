from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import math

app = Flask(__name__)
app.secret_key = 'aladinh-montext'  
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

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

class Question:
    def __init__(self, prompt, options, correct_answer):
        self.prompt = prompt
        self.options = options
        self.correct_answer = correct_answer

questions = [
    Question("1. What is the capital of France?", ["Manchester", "London", "Paris", "Berlin"], 2),
    Question("2. Which programming language is this quiz written in?", ["Java", "Python", "GO", "C++"], 2),
    Question("3. What is the capital of Japan?", ["Beijing", "Seoul", "Tokyo", "Abuja"], 3),
    Question("4. Which planet is known as the Red Planet?", ["Venus", "Mars", "Jupiter", "Saturn"], 1),
    Question("5. Who wrote 'Romeo and Juliet'?", ["Charles Dickens", "William Shakespeare", "Charles Darwin", "Jane Austen"], 2),
    Question("6. What is the largest mammal on Earth?", ["Elephant", "Blue Whale", "Giraffe", "Dinosar"], 2),
    Question("7. In which year did the Titanic sink?", ["1912", "1918", "1920", "1935"], 1),
    Question("8. What is the powerhouse of the cell?", ["Nucleus", "Nucleolus", "Mitochondria", "Endoplasmic Reticulum"], 1),
    Question("9. Which programming language is often used for machine learning?", ["Java", "Python", "JavaScript", "C#"], 2),
    Question("10. What is the capital city of Kenya?", ["Kisumu", "Nakuru", "Nairobi", "Murang'a"], 3),
    Question("11. What is NOT an AI tech of Tony Stark?", ["J.A.R.V.I.S", "E.D.I.T.H", "F.R.I.D.A.Y", "Miss Minutes"], 4),
    Question("12. What is not a programming language used used for game development?", ["C++", "RUBY", "JAVA", "PHP"], 4),
    Question("13. Which of these is not a programming language?", ["C", "RAILS", "CSS", "Kotlin"], 3),
    Question("14. Which of these is used for android app development?", ["Kotlin", "HTML", "RUBY", "PHP"], 1),
    Question("15. What is an IDE?", ["Independent Dean of Environment", "Integrated Development Environment", "Internal Depart Engine", "Integer Data Entry"], 2),
    Question("16. Which of the following is not an IDE?", ["Docker", "Visual Studio Code", "Sublime", "Atom"], 1),
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
    
    if 'quiz' not in session:
        session['quiz'] = Quiz(questions)
        
    quiz = session['quiz']

    if request.method == 'POST':
        user_answer = int(request.form['answer'])
        quiz.submit_answer(user_answer)
        
        if user_answer == quiz.get_current_question().correct_answer:
            flash('Congrats, Correct answer ^.^')
        else:
            flash('Oops!! Incorrect answer, Revise well.')
            
        quiz.next_question()

        if quiz.is_finished():
            flash(f'Quiz completed, You scored {quiz.score}/{len(quiz.questions)} questions correct.')
            percent = float(quiz.score/len(quiz.questions))*100
            percentage = math.ceil(percent)
            comment1 = "Above Average, strive for the best."
            comment2 = "Below Average, Revise well."
            comment3 = "Hurray!! You are a genious, keep it up pall."
            
            if percentage == 100:
                flash(f'You have {percentage}%, {comment3}')
                
            elif percentage >= 50:
                flash(f'You have {percentage}%, {comment1}')
                
            elif percentage < 50:
                flash(f'You have {percentage}%, {comment2}')
            
            session.pop('quiz')
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

        with connect_db() as conn:
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

@app.route('/reference', methods=['GET', 'POST'])
def reference():
    if request.method == 'POST':
        return redirect(url_for('home'))
    
    return render_template('reference.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    create_table()
    app.run(debug=True)

