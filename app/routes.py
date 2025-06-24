from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .quiz_data import questions

main = Blueprint('main', __name__)

# Home route
@main.route('/')
def index():
    session.clear()
    return render_template('index.html')


# Start Quiz route
@main.route('/start-quiz', methods=['POST'])
def start_quiz():
    username = request.form.get('username').strip()
    if not username:
        flash('Please enter a valid name.', 'warning')
        # username = f"Player{len(leaderboard) + 1}"  # fallback
    session['username'] = username
    session['score'] = 0
    session['question_index'] = 0
    return redirect(url_for('main.quiz'))


# This route handles the quiz logic
@main.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'score' not in session:
        session['score'] = 0
        session['question_index'] = 0

    index = session['question_index']
    if index >= len(questions):
        return redirect(url_for('main.result'))

    question = questions[index]
    feedback = session.pop('feedback', None)  # Get and clear feedback

    if request.method == 'POST':
        selected = request.form.get('choice')
        if selected == question['answer']:
            session['score'] += 1
            session['feedback'] = 'Correct!'
        else:
            session['feedback'] = f"Wrong! The correct answer was: {question['answer']}" # To be removed later

        session['question_index'] += 1
        return redirect(url_for('main.quiz'))

    return render_template('quiz.html', question=question, index=index + 1, total=len(questions), Qst=question['Qst'], feedback=feedback)


# This route displays the result after the quiz is completed
@main.route('/result')
def result():
    username = session.get('username', 'Anonymous')
    return render_template('result.html', username=username, score=session.get('score', 0), total=len(questions))
