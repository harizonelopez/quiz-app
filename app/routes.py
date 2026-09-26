from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .quiz_data import questions
import random
import sqlite3

main = Blueprint('main', __name__)

DATABASE = 'quiz.db'


# --------------- Database Helpers --------------- #
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the leaderboard table if it doesn't exist."""
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                percentage REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()


# Initialize database when the module loads
init_db()


# --------------- Home --------------- #
@main.route('/')
def index():
    session.clear()
    return render_template('index.html')


# --------------- Start Quiz --------------- #
@main.route('/start-quiz', methods=['POST'])
def start_quiz():
    username = request.form.get('username', '').strip()
    if not username or len(username) < 3:
        flash('Please enter a valid name (minimum 3 characters).', 'error')
        return redirect(url_for('main.index'))

    session['username'] = username
    session['score'] = 0
    session['question_index'] = 0

    # Shuffle questions + randomize choices
    shuffled_questions = random.sample(questions, len(questions))
    randomized_quiz = []
    for q in shuffled_questions:
        options = q['choices'][:]
        random.shuffle(options)
        randomized_quiz.append({
            'question': q['question'],
            'answer': q['answer'],
            'choices': options,
            'stage': q.get('stage', 1)
        })

    session['quiz'] = randomized_quiz
    return redirect(url_for('main.quiz'))


# --------------- Quiz Logic --------------- #
@main.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'username' not in session or 'quiz' not in session:
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

    return render_template(
        'quiz.html',
        question=question,
        index=index + 1,
        total=len(quiz),
        stage=question['stage'],
        feedback=feedback
    )


# --------------- Result + Save Score --------------- #
@main.route('/result')
def result():
    score = session.get('score', 0)
    total = len(session.get('quiz', []))
    username = session.get('username', 'Anonymous')
    percentage = round((score / total) * 100, 1) if total > 0 else 0

    with get_db() as conn:
        # Keep only the best score for each user
        conn.execute('DELETE FROM leaderboard WHERE name = ?', (username,))
        conn.execute('''
            INSERT INTO leaderboard (name, score, total, percentage)
            VALUES (?, ?, ?, ?)
        ''', (username, score, total, percentage))
        conn.commit()

    return render_template(
        'result.html',
        score=score,
        percent=percentage,
        total=total,
        username=username
    )


# --------------- Leaderboard --------------- #
@main.route('/leaderboard')
def show_leaderboard():
    with get_db() as conn:
        rows = conn.execute('''
            SELECT name, score, total, percentage, created_at
            FROM leaderboard
            ORDER BY score DESC, percentage DESC
            LIMIT 10
        ''').fetchall()

        # Convert to normal dictionaries
        top_board = [dict(row) for row in rows]

        # Prepare data for Chart.js
        usernames = [entry['name'] for entry in top_board]
        scores = [entry['score'] for entry in top_board]

        username = session.get('username')
        user_entry = None
        user_rank = None
        show_user_entry = False

        if username:
            row = conn.execute('''
                SELECT name, score, total, percentage
                FROM leaderboard
                WHERE name = ?
            ''', (username,)).fetchone()

            if row:
                user_entry = dict(row)

                rank_row = conn.execute('''
                    SELECT COUNT(*) + 1 as rank
                    FROM leaderboard
                    WHERE score > ? OR (score = ? AND percentage > ?)
                ''', (user_entry['score'], user_entry['score'], user_entry['percentage'])).fetchone()

                user_rank = rank_row['rank']

                # Show extra row only if user is not already in top 10
                show_user_entry = user_entry not in top_board

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


# --------------- Retake --------------- #
@main.route('/retake')
def retake_quiz():
    if 'username' in session:
        session['score'] = 0
        session['question_index'] = 0
        session.pop('feedback', None)

        shuffled = random.sample(questions, len(questions))
        randomized = []
        for q in shuffled:
            options = q['choices'][:]
            random.shuffle(options)
            randomized.append({
                'question': q['question'],
                'answer': q['answer'],
                'choices': options,
                'stage': q.get('stage', 1)
            })
        session['quiz'] = randomized

    return redirect(url_for('main.quiz'))