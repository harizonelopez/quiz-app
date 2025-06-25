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
    # Shuffle the questions
    shuffled_questions = random.sample(questions, len(questions))
    randomized_quiz = []
    # Randomize the options for each question
    for q in shuffled_questions:
        options = q['choices'][:]
        random.shuffle(options)
        randomized_quiz.append({
            'question': q['question'],
            'answer': q['answer'],
            'choices': options,
            'stage': q.get('stage', 1)  # Default stage to 1 if not specified
        })

    session['quiz'] = randomized_quiz

    return redirect(url_for('main.quiz'))


# This route handles the quiz logic
@main.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'username' not in session or 'score' not in session or 'quiz' not in session:
        flash("Please start the quiz first.", "warning")
        return redirect(url_for('main.index'))

    index = session['question_index']
    quiz = session['quiz']

    if index >= len(quiz):
        return redirect(url_for('main.result'))

    question = quiz[index]
    feedback = session.pop('feedback', None)

    if request.method == 'POST':
        selected = request.form.get('answer')
        if selected == question['answer']:
            session['score'] += 1
            session['feedback'] = 'Correct!'
        else:
            session['feedback'] = 'Wrong!'

        session['question_index'] += 1
        return redirect(url_for('main.quiz'))
    
    return render_template('quiz.html', question=question, index=index + 1,
                           total=len(quiz), stage=question['stage'], feedback=feedback)


# This route handles the answer submission to only 'POST' endpoint
@main.route('/quiz', methods=['POST'])
def submit_answer():
    if 'quiz' not in session:
        return redirect(url_for('main.index'))
    
    selected = request.form.get('answer')
    index = session['question_index']
    quiz = session['quiz']
    
    correct_answer = quiz[index]['correct']
    if selected == correct_answer:
        session['score'] += 1

    session['question_index'] += 1

    return redirect(url_for('main.quiz'))


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
from flask import session

@main.route('/leaderboard')
def show_leaderboard():
    leaderboard = load_leaderboard()
    sorted_board = sorted(leaderboard, key=lambda x: x['score'], reverse=True)

    username = session.get('username')  # from quiz session
    top_n = 10
    top_board = sorted_board[:top_n]

    # Find current user's full rank and data
    user_entry = next((e for e in sorted_board if e['name'] == username), None)
    user_rank = sorted_board.index(user_entry) + 1 if user_entry else None

    # Show user if not in top 10 already
    show_user_entry = user_entry and user_entry not in top_board

    usernames = [entry['name'] for entry in top_board]
    scores = [entry['score'] for entry in top_board]

    return render_template(
        'leaderboard.html',
        leaderboard=top_board,
        usernames=usernames,
        scores=scores,
        current_user=username,
        user_entry=user_entry,
        user_rank=user_rank,
        show_user_entry=show_user_entry
    )
    
