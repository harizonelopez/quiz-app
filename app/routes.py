from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .quiz_data import questions
import random
import os
import json

main = Blueprint('main', __name__)

# Initialize leaderboard
LEADERBOARD_FILE = 'leaderboard.json'

# Load the leaderboard
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r') as f:
            return json.load(f)
    return []

# Save the data to the leaderboard
def save_leaderboard(data):
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(data, f, indent=4)


# Home route
@main.route('/')
def index():
    session.clear()
    return render_template('index.html')


# Start Quiz route
@main.route('/start-quiz', methods=['POST'])
def start_quiz():
    username = request.form.get('username').strip()
    if not username or len(username) < 3:
        flash('Please enter a valid name.', 'error')
        return redirect(url_for('main.index'))
    
    session['username'] = username
    session['score'] = 0
    session['question_index'] = 0

    # Shuffle questions for randomness and save for the session
    session['quiz'] = random.sample(questions, len(questions))

    return redirect(url_for('main.quiz'))


# This route handles the quiz logic
@main.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'score' not in session or 'quiz' not in session:
        return redirect(url_for('main.index'))

    index = session['question_index']
    quiz = session['quiz']

    if index >= len(quiz):
        return redirect(url_for('main.result'))

    question = quiz[index]
    feedback = session.pop('feedback', None)

    if request.method == 'POST':
        selected = request.form.get('choice')
        if selected == question['answer']:
            session['score'] += 1
            session['feedback'] = 'Correct!'
        else:
            session['feedback'] = 'Wrong!'
            # session['feedback'] = f"Wrong! The correct answer was: {question['answer']}"

        session['question_index'] += 1
        return redirect(url_for('main.quiz'))
    
    return render_template('quiz.html', question=question, index=index + 1,
                           total=len(quiz), stage=question['stage'], feedback=feedback)


# This route displays the result after the quiz is completed
@main.route('/result')
def result():
    score = session.get('score', 0)
    total = len(session.get('quiz', []))
    username = session.get('username', 'Anonymous')

    new_entry = {
        'name': username,
        'score': score,
        'total': total
    }
    # Calculate percentage
    percent = int((score / total) * 100) if total > 0 else 0

    leaderboard = load_leaderboard()

    # Remove existing entry for this username if it exists
    leaderboard = [entry for entry in leaderboard if entry['name'] != username]
    # Add the new one
    leaderboard.append(new_entry)
    # Sort by score descending
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    save_leaderboard(leaderboard)

    return render_template('result.html', score=score, percent=percent, total=total, username=username)


# This route displays the leaderboard
@main.route('/leaderboard')
def show_leaderboard():
    leaderboard = load_leaderboard()
    sorted_board = sorted(leaderboard, key=lambda x: x['score'], reverse=True)

    # Extract usernames and scores
    usernames = [entry['name'] for entry in sorted_board]
    scores = [entry['score'] for entry in sorted_board]

    return render_template('leaderboard.html', leaderboard=sorted_board, usernames=usernames, scores=scores)
    
