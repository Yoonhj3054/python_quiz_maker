import json
import random
import re
import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, session, redirect

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Load questions safely and clean tags
try:
    with open('data/questions.json', 'r', encoding='utf-8') as f:
        raw_questions = json.load(f)
        
    ALL_QUESTIONS = []
    Q_DICT = {}
    for q in raw_questions:
        clean_opts = []
        for opt in q['options']:
            # Remove [xxx 관련] or [✅ 정답]
            opt = re.sub(r'\[.*?\]\s*', '', opt)
            # Remove (variation-xxxx) or (ans-xxxx)
            opt = re.sub(r'\((variation|ans)-\d+\)', '', opt).strip()
            clean_opts.append(opt)
        q['options'] = clean_opts
        ALL_QUESTIONS.append(q)
        Q_DICT[q['id']] = q
except Exception as e:
    ALL_QUESTIONS = []
    Q_DICT = {}
    print(f"Failed to load questions: {e}")

Q_BY_DIFF = {
    '초급': [q for q in ALL_QUESTIONS if q['difficulty'] == '초급'],
    '중급': [q for q in ALL_QUESTIONS if q['difficulty'] == '중급'],
    '고급': [q for q in ALL_QUESTIONS if q['difficulty'] == '고급'],
    '최상': [q for q in ALL_QUESTIONS if q['difficulty'] == '최상']
}

def get_random_question_by_level(level, recent_topics=None):
    if recent_topics is None:
        recent_topics = []
        
    # Determine weights for [초급, 중급, 고급, 최상]
    if level == 1:
        weights = [80, 20, 0, 0]
    elif level == 2:
        weights = [50, 50, 0, 0]
    elif level == 3:
        weights = [20, 60, 20, 0]
    elif level == 4:
        weights = [10, 40, 50, 0]
    elif level <= 6:
        weights = [0, 20, 60, 20]
    elif level <= 8:
        weights = [0, 10, 40, 50]
    else:
        weights = [0, 0, 20, 80]
        
    diffs = ['초급', '중급', '고급', '최상']
    chosen_diff = random.choices(diffs, weights=weights, k=1)[0]
    
    pool = Q_BY_DIFF.get(chosen_diff, ALL_QUESTIONS)
    
    # Filter out recently seen topics to force variety
    filtered_pool = [q for q in pool if q['topic'] not in recent_topics]
    
    # If filtered is empty, fallback to full pool
    if not filtered_pool:
        filtered_pool = pool
        
    return random.choice(filtered_pool)

DB_PATH = 'data/db.json'

def get_db():
    if not os.path.exists(DB_PATH):
        return {'users': {}, 'user_history': {}, 'ranking_board': []}
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {'users': {}, 'user_history': {}, 'ranking_board': []}

def save_db(db):
    os.makedirs('data', exist_ok=True)
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html', username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        action = request.form.get('action')
        
        if not user_id or not password:
            return render_template('auth.html', error='아이디와 비밀번호를 모두 입력해주세요.', is_login=(action=='login'))

        db = get_db()

        if action == 'signup':
            if len(password) < 8:
                return render_template('auth.html', error='비밀번호는 8자리 이상이어야 합니다.', is_login=False)
            if user_id in db['users']:
                return render_template('auth.html', error='이미 존재하는 아이디입니다.', is_login=False)
            db['users'][user_id] = password
            if user_id not in db['user_history']:
                db['user_history'][user_id] = []
            save_db(db)
            session['username'] = user_id
            return redirect('/')
        else: # login
            if user_id not in db['users']:
                return render_template('auth.html', error='없는 아이디입니다.', is_login=True)
            if db['users'][user_id] != password:
                return render_template('auth.html', error='비밀번호가 틀렸습니다.', is_login=True)
                
            session['username'] = user_id
            return redirect('/')
            
    return render_template('auth.html', is_login=True)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/quiz_config', methods=['GET', 'POST'])
@login_required
def quiz_config():
    if request.method == 'POST':
        diff = request.form.get('difficulty')
        count = int(request.form.get('count', 10))
        
        filtered = [q for q in ALL_QUESTIONS if q['difficulty'] == diff]
        random.shuffle(filtered)
        selected_ids = [q['id'] for q in filtered[:count]]
        
        session['active_q_ids'] = selected_ids
        session['mode'] = 'quiz'
        session['answers'] = []
        session['current_idx'] = 0
        session['results_saved'] = False
        return redirect('/active')
        
    return render_template('quiz_config.html')

@app.route('/test_config', methods=['GET', 'POST'])
@login_required
def test_config():
    if request.method == 'POST':
        level = request.form.get('level')
        
        distribution = {'초급': 0, '중급': 0, '고급': 0, '최상': 0}
        time_limit = 20
        
        if level == '초급':
            distribution = {'초급': 10, '중급': 5, '고급': 3, '최상': 2}
            time_limit = 20
        elif level == '중급':
            distribution = {'초급': 5, '중급': 8, '고급': 5, '최상': 2}
            time_limit = 30
        else:
            distribution = {'초급': 2, '중급': 5, '고급': 8, '최상': 5}
            time_limit = 40
            
        test_q_ids = []
        for diff, count in distribution.items():
            filtered = [q for q in ALL_QUESTIONS if q['difficulty'] == diff]
            random.shuffle(filtered)
            test_q_ids.extend([q['id'] for q in filtered[:count]])
            
        random.shuffle(test_q_ids)
        
        session['active_q_ids'] = test_q_ids
        session['mode'] = 'test'
        session['answers'] = []
        session['current_idx'] = 0
        session['time_limit'] = time_limit
        session['start_time_set'] = True 
        session['results_saved'] = False
        return redirect('/active')
        
    return render_template('test_config.html')

@app.route('/active', methods=['GET', 'POST'])
@login_required
def active():
    if 'active_q_ids' not in session:
        return redirect('/')
        
    q_ids = session['active_q_ids']
    idx = session.get('current_idx', 0)
    
    if request.method == 'POST':
        if request.form.get('time_up') == 'true':
            return redirect('/results')

        selected_option = request.form.get('option')
        
        if selected_option is not None:
            selected_option = int(selected_option)
            current_q = Q_DICT.get(q_ids[idx])
            is_correct = (selected_option == current_q['correctAnswer'])
            
            ans = session.get('answers', [])
            ans.append({
                'q_id': current_q['id'],
                'selectedOption': selected_option,
                'isCorrect': is_correct
            })
            session['answers'] = ans
            session['current_idx'] = idx + 1
            
            if session['current_idx'] >= len(q_ids):
                return redirect('/results')
                
        return redirect('/active')
        
    if idx >= len(q_ids):
        return redirect('/results')
        
    current_q = Q_DICT.get(q_ids[idx])
    return render_template('active.html', 
                          q=current_q, 
                          idx=idx, 
                          total=len(q_ids),
                          mode=session.get('mode'),
                          time_limit=session.get('time_limit') if session.get('start_time_set') else None)

@app.route('/retry_similar', methods=['POST'])
@login_required
def retry_similar():
    incorrect_q_ids = [a['q_id'] for a in session.get('answers', []) if not a['isCorrect']]
    new_q_ids = []
    
    for q_id in incorrect_q_ids:
        inc_q = Q_DICT.get(q_id)
        matches = [q for q in ALL_QUESTIONS if q['topic'] == inc_q['topic'] and q['difficulty'] == inc_q['difficulty'] and q['id'] != inc_q['id'] and q['id'] not in new_q_ids]
        if matches:
            new_q_ids.append(random.choice(matches)['id'])
        else:
            new_q_ids.append(inc_q['id'])
            
    session['active_q_ids'] = new_q_ids
    session['mode'] = 'quiz'
    session['answers'] = []
    session['current_idx'] = 0
    session['results_saved'] = False
    return redirect('/active')

@app.route('/results')
@login_required
def results():
    answers = session.get('answers', [])
    mode = session.get('mode', 'quiz')
    total = len(session.get('active_q_ids', []))
    
    correct_count = sum(1 for a in answers if a['isCorrect'])
    score = round((correct_count / total) * 100) if total > 0 else 0
    
    incorrect = []
    for a in answers:
        if not a['isCorrect']:
            q_info = Q_DICT.get(a['q_id'])
            incorrect.append({
                'question': q_info,
                'selectedOption': a['selectedOption']
            })
    
    report = {}
    for a in answers:
        topic = Q_DICT.get(a['q_id'])['topic']
        if topic not in report:
            report[topic] = {'total': 0, 'incorrect': 0}
        report[topic]['total'] += 1
        if not a['isCorrect']:
            report[topic]['incorrect'] += 1
            
    weakness = []
    for topic, data in report.items():
        if data['incorrect'] > 0:
            weakness.append({
                'topic': topic,
                'errorRate': round((data['incorrect'] / data['total']) * 100),
                'incorrect': data['incorrect'],
                'total': data['total']
            })
    weakness.sort(key=lambda x: x['errorRate'], reverse=True)
    
    # Save to history
    username = session.get('username')
    if username and not session.get('results_saved'):
        db = get_db()
        if username not in db['user_history']:
            db['user_history'][username] = []
        db['user_history'][username].append({
            'mode': mode,
            'score': score,
            'total': total,
            'correct': correct_count,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        save_db(db)
        session['results_saved'] = True
    
    return render_template('results.html', score=score, total=total, correct=correct_count, incorrect=incorrect, weakness=weakness, mode=mode)

@app.route('/profile')
@login_required
def profile():
    db = get_db()
    history = db['user_history'].get(session.get('username'), [])
    return render_template('profile.html', history=list(reversed(history)))

@app.route('/game')
@login_required
def game():
    # Sort ranking board
    db = get_db()
    ranked = sorted(db['ranking_board'], key=lambda x: x['score'], reverse=True)
    return render_template('game.html', ranking=ranked)

@app.route('/game_start')
@login_required
def game_start():
    # Initialize game state
    session['g_hp'] = 3
    session['g_score'] = 0
    session['g_exp'] = 0
    session['g_level'] = 1
    session['g_combo'] = 0
    session['g_achievements'] = []
    session['g_recent_topics'] = []
    
    # Pick first random question based on Level 1
    session['g_current_q_id'] = get_random_question_by_level(1, [])['id']
    
    return redirect('/game_active')

@app.route('/game_active', methods=['GET', 'POST'])
@login_required
def game_active():
    if 'g_hp' not in session or session['g_hp'] <= 0:
        return redirect('/game')
        
    q_id = session.get('g_current_q_id')
    current_q = Q_DICT.get(q_id)
    
    # Bug Fix: If the cookie holds an old/deleted question ID, pick a new one
    if current_q is None:
        current_q = get_random_question_by_level(session.get('g_level', 1), session.get('g_recent_topics', []))
        session['g_current_q_id'] = current_q['id']
    
    message = None
    msg_type = None
    level_up = False
    new_achievements = []

    if request.method == 'POST':
        selected_option = request.form.get('option')
        if selected_option is not None:
            selected_option = int(selected_option)
            is_correct = (selected_option == current_q['correctAnswer'])
            
            if is_correct:
                session['g_combo'] += 1
                combo_bonus = session['g_combo'] * 2
                session['g_score'] += (10 + combo_bonus)
                session['g_exp'] += 20
                
                message = f"정답입니다! 콤보 x{session['g_combo']} (+{10+combo_bonus}점)"
                msg_type = "success"
                
                # Check level up
                if session['g_exp'] >= session['g_level'] * 100:
                    session['g_level'] += 1
                    session['g_exp'] = 0
                    level_up = True
                    message += f" 🆙 레벨업! (Lv.{session['g_level']})"
                
                # Check achievements
                achs = set(session['g_achievements'])
                if session['g_combo'] >= 3 and "콤보 초보자" not in achs:
                    achs.add("콤보 초보자")
                    new_achievements.append("콤보 초보자")
                if session['g_combo'] >= 10 and "콤보 마스터" not in achs:
                    achs.add("콤보 마스터")
                    new_achievements.append("콤보 마스터")
                if session['g_level'] >= 5 and "Python 견습생" not in achs:
                    achs.add("Python 견습생")
                    new_achievements.append("Python 견습생")
                if session['g_level'] >= 10 and "Python 마스터" not in achs:
                    achs.add("Python 마스터")
                    new_achievements.append("Python 마스터")
                session['g_achievements'] = list(achs)
                
            else:
                session['g_hp'] -= 1
                session['g_combo'] = 0
                message = f"오답입니다! 목숨이 1 깎였습니다. (정답: {current_q['options'][current_q['correctAnswer']]})"
                msg_type = "error"
                
                if session['g_hp'] <= 0:
                    # Game Over -> register ranking
                    db = get_db()
                    db['ranking_board'].append({
                        'name': session['username'],
                        'score': session['g_score'],
                        'level': session['g_level']
                    })
                    save_db(db)
                    return redirect('/game_over')
            
            # Next question
            recents = session.get('g_recent_topics', [])
            recents.append(current_q['topic'])
            if len(recents) > 3:
                recents.pop(0)
            session['g_recent_topics'] = recents
            
            next_q = get_random_question_by_level(session['g_level'], recents)
            session['g_current_q_id'] = next_q['id']
            current_q = next_q
            
    return render_template('game_active.html', 
                          q=current_q, 
                          hp=session['g_hp'],
                          score=session['g_score'],
                          exp=session['g_exp'],
                          level=session['g_level'],
                          combo=session['g_combo'],
                          max_exp=session['g_level'] * 100,
                          message=message,
                          msg_type=msg_type,
                          level_up=level_up,
                          new_achievements=new_achievements)

@app.route('/game_over')
@login_required
def game_over():
    return render_template('game_over.html',
                           score=session.get('g_score', 0),
                           level=session.get('g_level', 1),
                           achievements=session.get('g_achievements', []))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
