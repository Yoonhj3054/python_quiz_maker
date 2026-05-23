import json
import random
import re
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

# Mock DB (In-memory for prototype)
users = {}
user_history = {}

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

        if action == 'signup':
            if len(password) < 8:
                return render_template('auth.html', error='비밀번호는 8자리 이상이어야 합니다.', is_login=False)
            if user_id in users:
                return render_template('auth.html', error='이미 존재하는 아이디입니다.', is_login=False)
            users[user_id] = password
            session['username'] = user_id
            return redirect('/')
        else: # login
            if user_id not in users:
                return render_template('auth.html', error='없는 아이디입니다.', is_login=True)
            if users[user_id] != password:
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
        if username not in user_history:
            user_history[username] = []
        user_history[username].append({
            'mode': mode,
            'score': score,
            'total': total,
            'correct': correct_count,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        session['results_saved'] = True
    
    return render_template('results.html', score=score, total=total, correct=correct_count, incorrect=incorrect, weakness=weakness, mode=mode)

@app.route('/profile')
@login_required
def profile():
    history = user_history.get(session.get('username'), [])
    return render_template('profile.html', history=history)

@app.route('/game')
@login_required
def game():
    return render_template('game.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
