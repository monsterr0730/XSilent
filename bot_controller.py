import os
import time
import uuid
import hashlib
import threading
from datetime import datetime
from flask import Flask, request, jsonify, session, redirect, url_for
import pymongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "primexarmy_secret_key_2024"

# ========================================
# 🔥 CONFIGURATION - SIRF NAAM CHANGE KARO
# ========================================
PANEL_NAME = "XSILENT"  # 👈 Yahan apna naam dalo

SITE_NAME = XSILENT.upper()
OWNER_USERNAME = XSILENT.lower()
OWNER_PASSWORD = f"{TSILENT}@2024"
SITE_URL = os.getenv("SITE_URL", f"https://{XSILENT.lower()}.up.railway.app")

# Attack settings
DEFAULT_DURATION = 300  # 5 minutes (300 seconds)
MAX_DURATION = 300

# MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://mohitrao83076_db_user:xX0q1PRY7l0Nfks6@monster.ydmmckl.mongodb.net/?retryWrites=true&w=majority")
# ========================================

ATTACK_METHODS = ["UDP", "TCP", "HTTP", "SYN", "ICMP"]

PLANS = {
    "free": {"name": "FREE", "daily_limit": 10, "max_duration": 300},
    "basic": {"name": "BASIC", "daily_limit": 50, "max_duration": 300},
    "premium": {"name": "PREMIUM", "daily_limit": 200, "max_duration": 300},
    "vip": {"name": "VIP", "daily_limit": 999, "max_duration": 300}
}

# MongoDB Connection
mongo_client = None
db = None
users_col = None
attacks_col = None
mongo_connected = False

for attempt in range(3):
    try:
        mongo_client = pymongo.MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        mongo_client.admin.command('ping')
        db = mongo_client[PANEL_NAME.lower()]
        users_col = db['users']
        attacks_col = db['attacks']
        mongo_connected = True
        print(f"✅ MongoDB connected")
        break
    except Exception as e:
        print(f"⚠️ MongoDB attempt {attempt + 1} failed")
        mongo_connected = False
        time.sleep(2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user():
    if 'user_id' in session:
        if session.get('is_owner'):
            return {"username": OWNER_USERNAME, "is_owner": True, "plan": "vip", "_id": "owner"}
        if mongo_connected and users_col:
            try:
                return users_col.find_one({"_id": ObjectId(session['user_id'])})
            except:
                return None
    return None

def attack_monitor():
    while True:
        try:
            if mongo_connected and attacks_col:
                pending = list(attacks_col.find({"status": "pending"}).limit(5))
                for attack in pending:
                    duration = attack.get('duration', DEFAULT_DURATION)
                    attacks_col.update_one({"_id": attack["_id"]}, {"$set": {"status": "running"}})
                    
                    def complete_attack(aid, dur):
                        time.sleep(dur)
                        if mongo_connected and attacks_col:
                            attacks_col.update_one({"_id": aid}, {"$set": {"status": "completed"}})
                    
                    threading.Thread(target=complete_attack, args=(attack["_id"], duration), daemon=True).start()
            time.sleep(2)
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(5)

# ========================================
# 🟢 USER PANEL - Sirf user apna history dekhega
# ========================================

@app.route('/')
def index():
    user = get_user()
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{SITE_NAME} - Premium Panel</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: Arial; background: linear-gradient(135deg, #0a0a0f, #1a1a2e); color: white; }}
            .navbar {{ background: rgba(10,10,15,0.95); padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; }}
            .logo {{ font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #a855f7, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .nav-links a {{ color: white; text-decoration: none; margin-left: 25px; }}
            .hero {{ text-align: center; padding: 100px 20px; }}
            h1 {{ font-size: 56px; margin-bottom: 20px; background: linear-gradient(135deg, #fff, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .btn {{ background: linear-gradient(135deg, #a855f7, #7c3aed); padding: 14px 35px; color: white; text-decoration: none; border-radius: 50px; display: inline-block; margin: 10px; }}
            .features {{ display: flex; justify-content: center; gap: 30px; padding: 60px; flex-wrap: wrap; }}
            .feature {{ background: rgba(255,255,255,0.05); padding: 30px; border-radius: 20px; width: 250px; text-align: center; }}
            footer {{ text-align: center; padding: 30px; background: rgba(0,0,0,0.5); }}
        </style>
    </head>
    <body>
        <div class="navbar">
            <div class="logo">🔥 {SITE_NAME}</div>
            <div class="nav-links">
                <a href="/">Home</a>
                <a href="/pricing">Pricing</a>
                {f'<a href="/dashboard">Dashboard</a><a href="/logout">Logout</a>' if user else '<a href="/login">Login</a><a href="/register">Register</a>'}
            </div>
        </div>
        <div class="hero">
            <h1>{SITE_NAME}</h1>
            <p>Premium IP Stress Testing Panel | 300 Seconds Attack Power</p>
            <a href="/register" class="btn">Get Started Free</a>
        </div>
        <div class="features">
            <div class="feature"><h3>⚡ 300 Sec Attack</h3><p>Full power</p></div>
            <div class="feature"><h3>🔒 Secure</h3><p>No logs</p></div>
            <div class="feature"><h3>📊 Live Stats</h3><p>Real-time</p></div>
        </div>
        <footer><p>&copy; 2024 {SITE_NAME}</p></footer>
    </body>
    </html>
    """

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == OWNER_USERNAME and password == OWNER_PASSWORD:
            session.clear()
            session['user_id'] = "owner"
            session['username'] = OWNER_USERNAME
            session['is_owner'] = True
            return '<script>alert("Welcome Owner!"); window.location.href="/owner-panel";</script>'
        
        if mongo_connected and users_col:
            try:
                user = users_col.find_one({"username": username})
                if user and user.get('password') == hash_password(password):
                    session.clear()
                    session['user_id'] = str(user['_id'])
                    session['username'] = user['username']
                    session['is_owner'] = False
                    return '<script>alert("Login successful!"); window.location.href="/dashboard";</script>'
            except:
                pass
        return '<script>alert("Invalid credentials!"); window.location.href="/login";</script>'
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - {SITE_NAME}</title>
        <style>
            body {{ font-family: Arial; background: linear-gradient(135deg, #0a0a0f, #1a1a2e); color: white; min-height: 100vh; display: flex; justify-content: center; align-items: center; }}
            .card {{ background: rgba(255,255,255,0.05); padding: 40px; border-radius: 20px; width: 350px; text-align: center; }}
            input {{ width: 100%; padding: 12px; margin: 10px 0; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; color: white; }}
            button {{ width: 100%; padding: 12px; background: #a855f7; border: none; border-radius: 8px; color: white; cursor: pointer; }}
            a {{ color: #a855f7; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Welcome Back!</h2>
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <p style="margin-top: 20px;">New user? <a href="/register">Register</a></p>
        </div>
    </body>
    </html>
    """

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        if not all([username, email, password]):
            return '<script>alert("All fields required!"); window.location.href="/register";</script>'
        if username == OWNER_USERNAME:
            return '<script>alert("Username not available!"); window.location.href="/register";</script>'
        if password != confirm:
            return '<script>alert("Passwords do not match!"); window.location.href="/register";</script>'
        if len(password) < 6:
            return '<script>alert("Password must be 6+ characters!"); window.location.href="/register";</script>'
        
        if not mongo_connected or not users_col:
            return '<script>alert("Database error! Try again."); window.location.href="/register";</script>'
        
        try:
            if users_col.find_one({"username": username}):
                return '<script>alert("Username already exists!"); window.location.href="/register";</script>'
            
            user_data = {
                "username": username,
                "email": email,
                "password": hash_password(password),
                "plan": "free",
                "expiry": time.time() + (7 * 86400),
                "created_at": time.time(),
                "total_attacks": 0
            }
            result = users_col.insert_one(user_data)
            session.clear()
            session['user_id'] = str(result.inserted_id)
            session['username'] = username
            session['is_owner'] = False
            return '<script>alert("Registration successful! Free trial activated."); window.location.href="/dashboard";</script>'
        except Exception as e:
            return '<script>alert("Registration failed! Try again."); window.location.href="/register";</script>'
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register - {SITE_NAME}</title>
        <style>
            body {{ font-family: Arial; background: linear-gradient(135deg, #0a0a0f, #1a1a2e); color: white; min-height: 100vh; display: flex; justify-content: center; align-items: center; }}
            .card {{ background: rgba(255,255,255,0.05); padding: 40px; border-radius: 20px; width: 350px; text-align: center; }}
            input {{ width: 100%; padding: 12px; margin: 10px 0; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; color: white; }}
            button {{ width: 100%; padding: 12px; background: #a855f7; border: none; border-radius: 8px; color: white; cursor: pointer; }}
            a {{ color: #a855f7; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Create Account</h2>
            <p>7 days free trial | 300 sec attack</p>
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="email" name="email" placeholder="Email" required>
                <input type="password" name="password" placeholder="Password" required>
                <input type="password" name="confirm_password" placeholder="Confirm Password" required>
                <button type="submit">Register</button>
            </form>
            <p style="margin-top: 20px;">Have account? <a href="/login">Login</a></p>
        </div>
    </body>
    </html>
    """

# ========================================
# 🟢 USER DASHBOARD - Sirf apna history
# ========================================

@app.route('/dashboard')
def dashboard():
    user = get_user()
    if not user or user.get('is_owner'):
        return redirect('/login')
    
    plan_name = user.get('plan', 'free')
    plan = PLANS.get(plan_name, PLANS['free'])
    today = datetime.now().strftime('%Y-%m-%d')
    
    # User ki apni attacks count
    if mongo_connected and attacks_col:
        today_attacks = attacks_col.count_documents({"user_id": user['_id'], "date": today})
        total_attacks = attacks_col.count_documents({"user_id": user['_id']})
    else:
        today_attacks = total_attacks = 0
    
    # User ka apna history
    recent_html = ""
    if mongo_connected and attacks_col:
        recent = list(attacks_col.find({"user_id": user['_id']}).sort("created_at", -1).limit(10))
        for a in recent:
            recent_html += f"""
            <tr>
                <td>{a.get('target', 'N/A')}</td>
                <td>{a.get('port', 'N/A')}</td>
                <td>{a.get('method', 'N/A')}</td>
                <td>{a.get('duration', 'N/A')}s</td>
                <td>{a.get('status', 'N/A')}</td>
            </tr>
            """
    
    methods_html = "".join([f'<option value="{m}">{m}</option>' for m in ATTACK_METHODS])
    days_left = max(0, int((user.get('expiry', 0) - time.time())/86400))
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>User Dashboard - {SITE_NAME}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: Arial; background: #0a0a0f; color: white; }}
            .sidebar {{ position: fixed; left: 0; top: 0; width: 220px; height: 100%; background: rgba(10,10,15,0.95); padding: 30px 20px; }}
            .logo {{ font-size: 20px; font-weight: bold; color: #a855f7; margin-bottom: 40px; text-align: center; }}
            .nav-item {{ display: block; padding: 10px 15px; margin: 5px 0; border-radius: 10px; color: white; text-decoration: none; }}
            .nav-item:hover {{ background: rgba(168,85,247,0.2); color: #a855f7; }}
            .main {{ margin-left: 220px; padding: 30px; }}
            .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }}
            .stat-card {{ background: rgba(255,255,255,0.05); border-radius: 15px; padding: 20px; text-align: center; }}
            .stat-number {{ font-size: 32px; font-weight: bold; color: #a855f7; }}
            .attack-card {{ background: rgba(255,255,255,0.05); border-radius: 20px; padding: 30px; margin-bottom: 30px; }}
            .form-group {{ margin-bottom: 15px; }}
            .form-group label {{ display: block; margin-bottom: 5px; color: #888; }}
            .form-group input, .form-group select {{ width: 100%; padding: 12px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: white; }}
            .launch-btn {{ background: linear-gradient(135deg, #ef4444, #dc2626); color: white; border: none; padding: 14px; border-radius: 10px; font-weight: bold; cursor: pointer; width: 100%; }}
            .recent-card {{ background: rgba(255,255,255,0.05); border-radius: 20px; padding: 30px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); }}
            @media (max-width: 768px) {{ .sidebar {{ display: none; }} .main {{ margin-left: 0; }} }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div class="logo">🔥 {SITE_NAME}</div>
            <a href="/dashboard" class="nav-item active">📊 Dashboard</a>
            <a href="/history" class="nav-item">📜 My History</a>
            <a href="/pricing" class="nav-item">💎 Upgrade</a>
            <a href="/logout" class="nav-item">🚪 Logout</a>
        </div>
        
        <div class="main">
            <h2>Welcome, {user['username']}!</h2>
            <p style="margin-bottom: 20px;">Plan: {plan['name']} | Days Left: {days_left} | Max Attack: 300 seconds</p>
            
            <div class="stats">
                <div class="stat-card"><h3>Today</h3><div class="stat-number">{today_attacks}</div><small>Limit: {plan['daily_limit']}</small></div>
                <div class="stat-card"><h3>Total Attacks</h3><div class="stat-number">{total_attacks}</div></div>
                <div class="stat-card"><h3>Max Duration</h3><div class="stat-number">300s</div></div>
            </div>
            
            <div class="attack-card">
                <h3>Launch Attack (300 Seconds Max)</h3>
                <form id="attackForm">
                    <div class="form-group"><label>Target IP</label><input type="text" id="target" placeholder="1.1.1.1" required></div>
                    <div class="form-group"><label>Port</label><input type="number" id="port" placeholder="80" required></div>
                    <div class="form-group"><label>Method</label><select id="method">{methods_html}</select></div>
                    <div class="form-group"><label>Duration (seconds)</label><input type="number" id="duration" min="10" max="300" value="300" required></div>
                    <button type="submit" class="launch-btn">🚀 LAUNCH ATTACK (300s)</button>
                </form>
            </div>
            
            <div class="recent-card">
                <h3>My Recent Attacks</h3>
                <table>
                    <thead><tr><th>Target</th><th>Port</th><th>Method</th><th>Duration</th><th>Status</th></tr></thead>
                    <tbody>{recent_html if recent_html else '<tr><td colspan="5" style="text-align:center">No attacks yet</td></tr>'}</tbody>
                </table>
            </div>
        </div>
        
        <script>
            document.getElementById('attackForm').onsubmit = async function(e) {{
                e.preventDefault();
                let target = document.getElementById('target').value;
                let port = document.getElementById('port').value;
                let method = document.getElementById('method').value;
                let duration = document.getElementById('duration').value;
                
                let res = await fetch('/launch-attack', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                    body: `target=${{target}}&port=${{port}}&method=${{method}}&duration=${{duration}}`
                }});
                let data = await res.json();
                if(data.success) {{
                    alert('✅ Attack launched for ' + duration + ' seconds!');
                    location.reload();
                }} else {{
                    alert('❌ Error: ' + data.error);
                }}
            }};
        </script>
    </body>
    </html>
    """

@app.route('/history')
def history():
    user = get_user()
    if not user or user.get('is_owner'):
        return redirect('/login')
    
    attacks_html = ""
    if mongo_connected and attacks_col:
        attacks = list(attacks_col.find({"user_id": user['_id']}).sort("created_at", -1).limit(50))
        for a in attacks:
            attacks_html += f"""
            <tr>
                <td>{a.get('target', 'N/A')}</td>
                <td>{a.get('port', 'N/A')}</td>
                <td>{a.get('method', 'N/A')}</td>
                <td>{a.get('duration', 'N/A')}s</td>
                <td>{a.get('status', 'N/A')}</td>
                <td>{datetime.fromtimestamp(a.get('created_at', time.time())).strftime('%Y-%m-%d %H:%M:%S') if a.get('created_at') else 'N/A'}</td>
            </tr>
            """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>My History - {SITE_NAME}</title>
        <style>
            body {{ font-family: Arial; background: #0a0a0f; color: white; padding: 20px; }}
            .sidebar {{ position: fixed; left: 0; top: 0; width: 220px; height: 100%; background: rgba(10,10,15,0.95); padding: 30px 20px; }}
            .logo {{ font-size: 20px; font-weight: bold; color: #a855f7; margin-bottom: 40px; text-align: center; }}
            .nav-item {{ display: block; padding: 10px 15px; margin: 5px 0; border-radius: 10px; color: white; text-decoration: none; }}
            .nav-item:hover {{ background: rgba(168,85,247,0.2); color: #a855f7; }}
            .main {{ margin-left: 220px; padding: 30px; }}
            table {{ width: 100%; border-collapse: collapse; background: rgba(255,255,255,0.05); border-radius: 10px; overflow: hidden; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }}
            th {{ background: rgba(168,85,247,0.2); }}
            .btn {{ background: #a855f7; padding: 10px 20px; color: white; text-decoration: none; border-radius: 8px; display: inline-block; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div class="logo">🔥 {SITE_NAME}</div>
            <a href="/dashboard" class="nav-item">Dashboard</a>
            <a href="/history" class="nav-item active">My History</a>
            <a href="/logout" class="nav-item">Logout</a>
        </div>
        <div class="main">
            <a href="/dashboard" class="btn">← Back</a>
            <h2>My Attack History (Last 50)</h2>
            <table>
                <thead><tr><th>Target</th><th>Port</th><th>Method</th><th>Duration</th><th>Status</th><th>Date</th></tr></thead>
                <tbody>{attacks_html if attacks_html else '<tr><td colspan="6" style="text-align:center">No attacks yet</td></tr>'}</tbody>
            </table>
        </div>
    </body>
    </html>
    """

@app.route('/launch-attack', methods=['POST'])
def launch_attack():
    user = get_user()
    if not user or user.get('is_owner'):
        return jsonify({"success": False, "error": "Please login"})
    
    plan_name = user.get('plan', 'free')
    plan = PLANS.get(plan_name, PLANS['free'])
    
    target = request.form.get('target')
    port = request.form.get('port')
    method = request.form.get('method')
    duration = request.form.get('duration')
    
    if not all([target, port, method, duration]):
        return jsonify({"success": False, "error": "All fields required"})
    
    try:
        duration = int(duration)
        if duration < 10:
            return jsonify({"success": False, "error": "Minimum 10 seconds"})
        if duration > 300:
            return jsonify({"success": False, "error": "Maximum 300 seconds"})
        if duration > plan['max_duration']:
            return jsonify({"success": False, "error": f"Your plan max {plan['max_duration']} seconds"})
    except:
        return jsonify({"success": False, "error": "Invalid duration"})
    
    try:
        port = int(port)
        if port < 1 or port > 65535:
            return jsonify({"success": False, "error": "Invalid port"})
    except:
        return jsonify({"success": False, "error": "Invalid port"})
    
    # Check daily limit
    today = datetime.now().strftime('%Y-%m-%d')
    if mongo_connected and attacks_col:
        today_count = attacks_col.count_documents({"user_id": user['_id'], "date": today})
        if today_count >= plan['daily_limit']:
            return jsonify({"success": False, "error": f"Daily limit reached! Max {plan['daily_limit']} attacks"})
    
    if mongo_connected and attacks_col:
        attack_data = {
            "user_id": user['_id'],
            "username": user['username'],
            "target": target,
            "port": port,
            "method": method,
            "duration": duration,
            "status": "pending",
            "date": today,
            "created_at": time.time()
        }
        attacks_col.insert_one(attack_data)
        
        # Update user attack count
        users_col.update_one({"_id": user['_id']}, {"$inc": {"total_attacks": 1}})
    
    return jsonify({"success": True})

@app.route('/pricing')
def pricing():
    user = get_user()
    plans_html = ""
    for key, plan in PLANS.items():
        price = 0 if key == 'free' else 10 if key == 'basic' else 25 if key == 'premium' else 50
        plans_html += f"""
        <div style="background: rgba(255,255,255,0.05); padding: 25px; margin: 15px; display: inline-block; width: 200px; border-radius: 15px; text-align: center;">
            <h3>{plan['name']}</h3>
            <p style="font-size: 28px; color: #a855f7;">${price}</p>
            <p>/month</p>
            <p>✅ {plan['daily_limit']} attacks/day</p>
            <p>✅ {plan['max_duration']}s max</p>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pricing - {SITE_NAME}</title>
        <style>
            body {{ font-family: Arial; background: linear-gradient(135deg, #0a0a0f, #1a1a2e); color: white; text-align: center; padding: 50px; }}
            .navbar {{ background: rgba(10,10,15,0.95); padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; position: fixed; top: 0; left: 0; right: 0; }}
            .logo {{ font-size: 24px; font-weight: bold; color: #a855f7; }}
            .nav-links a {{ color: white; text-decoration: none; margin-left: 20px; }}
            .container {{ margin-top: 100px; }}
            .plans {{ display: flex; justify-content: center; flex-wrap: wrap; }}
        </style>
    </head>
    <body>
        <div class="navbar">
            <div class="logo">🔥 {SITE_NAME}</div>
            <div class="nav-links">
                <a href="/">Home</a>
                <a href="/pricing">Pricing</a>
                {f'<a href="/dashboard">Dashboard</a><a href="/logout">Logout</a>' if user else '<a href="/login">Login</a><a href="/register">Register</a>'}
            </div>
        </div>
        <div class="container">
            <h1>Choose Your Plan</h1>
            <p>All plans: 300 seconds max attack duration</p>
            <div class="plans">{plans_html}</div>
        </div>
    </body>
    </html>
    """

# ========================================
# 🔴 OWNER PANEL - Sab kuch dikhega (Alag System)
# ========================================

@app.route('/owner-panel')
def owner_panel():
    user = get_user()
    if not user or not user.get('is_owner'):
        return redirect('/login')
    
    # Owner ko sab stats dikhenge
    if mongo_connected and attacks_col:
        total_users = users_col.count_documents({}) if users_col else 0
        total_attacks = attacks_col.count_documents({})
        today_attacks = attacks_col.count_documents({"date": datetime.now().strftime('%Y-%m-%d')})
        running_attacks = attacks_col.count_documents({"status": "running"})
    else:
        total_users = total_attacks = today_attacks = running_attacks = 0
    
    # All users list
    users_html = ""
    if mongo_connected and users_col:
        all_users = list(users_col.find().sort("created_at", -1))
        for u in all_users:
            days_left = max(0, int((u.get('expiry', 0) - time.time())/86400))
            users_html += f"""
            <tr>
                <td>{u.get('username', 'N/A')}</td>
                <td>{u.get('email', 'N/A')}</td>
                <td>{u.get('plan', 'free').upper()}</td>
                <td>{days_left} days</td>
                <td>{u.get('total_attacks', 0)}</td>
                <td>
                    <select id="plan_{u['_id']}" onchange="upgradeUser('{u['_id']}', this.value)">
                        <option value="free" {'selected' if u.get('plan')=='free' else ''}>FREE</option>
                        <option value="basic" {'selected' if u.get('plan')=='basic' else ''}>BASIC</option>
                        <option value="premium" {'selected' if u.get('plan')=='premium' else ''}>PREMIUM</option>
                        <option value="vip" {'selected' if u.get('plan')=='vip' else ''}>VIP</option>
                    </select>
                </td>
            </tr>
            """
    
    # All attacks history
    attacks_html = ""
    if mongo_connected and attacks_col:
        all_attacks = list(attacks_col.find().sort("created_at", -1).limit(30))
        for a in all_attacks:
            attacks_html += f"""
            <tr>
                <td>{a.get('username', 'N/A')}</td>
                <td>{a.get('target', 'N/A')}</td>
                <td>{a.get('port', 'N/A')}</td>
                <td>{a.get('method', 'N/A')}</td>
                <td>{a.get('duration', 'N/A')}s</td>
                <td>{a.get('status', 'N/A')}</td>
                <td>{datetime.fromtimestamp(a.get('created_at', time.time())).strftime('%Y-%m-%d %H:%M:%S') if a.get('created_at') else 'N/A'}</td>
            </tr>
            """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Owner Panel - {SITE_NAME}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: Arial; background: #0a0a0f; color: white; }}
            .sidebar {{ position: fixed; left: 0; top: 0; width: 260px; height: 100%; background: rgba(10,10,15,0.95); border-right: 1px solid rgba(255,255,255,0.1); padding: 30px 20px; overflow-y: auto; }}
            .logo {{ font-size: 20px; font-weight: bold; color: #a855f7; margin-bottom: 40px; text-align: center; }}
            .nav-item {{ display: block; padding: 10px 15px; margin: 5px 0; border-radius: 10px; color: white; text-decoration: none; }}
            .nav-item:hover, .nav-item.active {{ background: rgba(168,85,247,0.2); color: #a855f7; }}
            .main {{ margin-left: 260px; padding: 30px; }}
            .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }}
            .stat-card {{ background: rgba(255,255,255,0.05); border-radius: 15px; padding: 20px; text-align: center; }}
            .stat-number {{ font-size: 32px; font-weight: bold; color: #a855f7; }}
            table {{ width: 100%; border-collapse: collapse; background: rgba(255,255,255,0.05); border-radius: 10px; overflow: hidden; margin-top: 20px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }}
            th {{ background: rgba(168,85,247,0.2); }}
            select {{ background: rgba(255,255,255,0.1); color: white; padding: 5px 10px; border-radius: 5px; border: 1px solid #a855f7; cursor: pointer; }}
            .section {{ margin-bottom: 40px; }}
            h2 {{ color: #a855f7; margin-bottom: 20px; }}
            .success {{ background: #10b981; padding: 10px; border-radius: 5px; margin: 10px 0; display: none; position: fixed; top: 20px; right: 20px; z-index: 999; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div class="logo">👑 {SITE_NAME} OWNER</div>
            <a href="/owner-panel" class="nav-item active">📊 Overview</a>
            <a href="/owner-users" class="nav-item">👥 Users</a>
            <a href="/owner-attacks" class="nav-item">⚔️ All Attacks</a>
            <a href="/dashboard" class="nav-item">🟢 User Mode</a>
            <a href="/logout" class="nav-item">🚪 Logout</a>
        </div>
        
        <div class="main">
            <div id="successMsg" class="success"></div>
            
            <h1>👑 Owner Control Panel</h1>
            <p>Welcome, {OWNER_USERNAME} | Total Control Mode</p>
            
            <div class="stats">
                <div class="stat-card"><h3>Total Users</h3><div class="stat-number">{total_users}</div></div>
                <div class="stat-card"><h3>Total Attacks</h3><div class="stat-number">{total_attacks}</div></div>
                <div class="stat-card"><h3>Today</h3><div class="stat-number">{today_attacks}</div></div>
                <div class="stat-card"><h3>Running</h3><div class="stat-number">{running_attacks}</div></div>
            </div>
            
            <div class="section">
                <h2>👥 All Users ({total_users})</h2>
                <table>
                    <thead><tr><th>Username</th><th>Email</th><th>Plan</th><th>Days Left</th><th>Total Attacks</th><th>Upgrade</th></tr></thead>
                    <tbody>{users_html if users_html else '<tr><td colspan="6" style="text-align:center">No users yet</td></tr>'}</tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>⚔️ Recent Attacks (Last 30)</h2>
                <table>
                    <thead><tr><th>User</th><th>Target</th><th>Port</th><th>Method</th><th>Duration</th><th>Status</th><th>Time</th></tr></thead>
                    <tbody>{attacks_html if attacks_html else '<tr><td colspan="7" style="text-align:center">No attacks yet</td></tr>'}</tbody>
                </table>
            </div>
        </div>
        
        <script>
            async function upgradeUser(userId, plan) {{
                let res = await fetch('/owner/upgrade-user', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{user_id: userId, plan: plan}})
                }});
                let data = await res.json();
                if(data.success) {{
                    document.getElementById('successMsg').innerHTML = '✅ User upgraded to ' + plan.toUpperCase();
                    document.getElementById('successMsg').style.display = 'block';
                    setTimeout(() => location.reload(), 1500);
                }} else {{
                    alert('Error: ' + data.error);
                }}
            }}
        </script>
    </body>
    </html>
    """

@app.route('/owner-users')
def owner_users():
    user = get_user()
    if not user or not user.get('is_owner'):
        return redirect('/login')
    
    users_html = ""
    if mongo_connected and users_col:
        all_users = list(users_col.find().sort("created_at", -1))
        for u in all_users:
            days_left = max(0, int((u.get('expiry', 0) - time.time())/86400))
            users_html += f"""
            <tr>
                <td>{u.get('username', 'N/A')}</td>
                <td>{u.get('email', 'N/A')}</td>
                <td>{u.get('plan', 'free').upper()}</td>
                <td>{days_left} days</td>
                <td>{u.get('total_attacks', 0)}</td>
                <td>
                    <select id="plan_{u['_id']}" onchange="upgradeUser('{u['_id']}', this.value)">
                        <option value="free" {'selected' if u.get('plan')=='free' else ''}>FREE</option>
                        <option value="basic" {'selected' if u.get('plan')=='basic' else ''}>BASIC</option>
                        <option value="premium" {'selected' if u.get('plan')=='premium' else ''}>PREMIUM</option>
                        <option value="vip" {'selected' if u.get('plan')=='vip' else ''}>VIP</option>
                    </select>
                </td>
            </tr>
            """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Users - {SITE_NAME} Owner</title>
        <style>
            body {{ font-family: Arial; background: #0a0a0f; color: white; padding: 20px; }}
            .sidebar {{ position: fixed; left: 0; top: 0; width: 260px; height: 100%; background: rgba(10,10,15,0.95); padding: 30px 20px; }}
            .logo {{ font-size: 20px; font-weight: bold; color: #a855f7; margin-bottom: 40px; text-align: center; }}
            .nav-item {{ display: block; padding: 10px 15px; margin: 5px 0; border-radius: 10px; color: white; text-decoration: none; }}
            .nav-item:hover {{ background: rgba(168,85,247,0.2); color: #a855f7; }}
            .main {{ margin-left: 260px; padding: 30px; }}
            table {{ width: 100%; border-collapse: collapse; background: rgba(255,255,255,0.05); border-radius: 10px; overflow: hidden; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }}
            th {{ background: rgba(168,85,247,0.2); }}
            select {{ background: rgba(255,255,255,0.1); color: white; padding: 5px 10px; border-radius: 5px; border: 1px solid #a855f7; cursor: pointer; }}
            .btn {{ background: #a855f7; padding: 10px 20px; color: white; text-decoration: none; border-radius: 8px; display: inline-block; margin-bottom: 20px; }}
            .success {{ background: #10b981; padding: 10px; border-radius: 5px; margin: 10px 0; display: none; position: fixed; top: 20px; right: 20px; z-index: 999; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div class="logo">👑 {SITE_NAME}</div>
            <a href="/owner-panel" class="nav-item">Overview</a>
            <a href="/owner-users" class="nav-item active">Users</a>
            <a href="/owner-attacks" class="nav-item">Attacks</a>
            <a href="/logout" class="nav-item">Logout</a>
        </div>
        <div class="main">
            <div id="successMsg" class="success"></div>
            <a href="/owner-panel" class="btn">← Back</a>
            <h2>All Users</h2>
            <table>
                <thead><tr><th>Username</th><th>Email</th><th>Plan</th><th>Days Left</th><th>Attacks</th><th>Upgrade</th></tr></thead>
                <tbody>{users_html if users_html else '<tr><td colspan="6" style="text-align:center">No users yet</td></tr>'}</tbody>
            </table>
        </div>
        <script>
            async function upgradeUser(userId, plan) {{
                let res = await fetch('/owner/upgrade-user', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{user_id: userId, plan: plan}})
                }});
                let data = await res.json();
                if(data.success) {{
                    document.getElementById('successMsg').innerHTML = '✅ User upgraded to ' + plan.toUpperCase();
                    document.getElementById('successMsg').style.display = 'block';
                    setTimeout(() => location.reload(), 1500);
                }} else {{
                    alert('Error: ' + data.error);
                }}
            }}
        </script>
    </body>
    </html>
    """

@app.route('/owner-attacks')
def owner_attacks():
    user = get_user()
    if not user or not user.get('is_owner'):
        return redirect('/login')
    
    attacks_html = ""
    if mongo_connected and attacks_col:
        all_attacks = list(attacks_col.find().sort("created_at", -1).limit(100))
        for a in all_attacks:
            attacks_html += f"""
            <tr>
                <td>{a.get('username', 'N/A')}</td>
                <td>{a.get('target', 'N/A')}</td>
                <td>{a.get('port', 'N/A')}</td>
                <td>{a.get('method', 'N/A')}</td>
                <td>{a.get('duration', 'N/A')}s</td>
                <td>{a.get('status', 'N/A')}</td>
                <td>{datetime.fromtimestamp(a.get('created_at', time.time())).strftime('%Y-%m-%d %H:%M:%S') if a.get('created_at') else 'N/A'}</td>
            </tr>
            """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>All Attacks - {SITE_NAME} Owner</title>
        <style>
            body {{ font-family: Arial; background: #0a0a0f; color: white; padding: 20px; }}
            .sidebar {{ position: fixed; left: 0; top: 0; width: 260px; height: 100%; background: rgba(10,10,15,0.95); padding: 30px 20px; }}
            .logo {{ font-size: 20px; font-weight: bold; color: #a855f7; margin-bottom: 40px; text-align: center; }}
            .nav-item {{ display: block; padding: 10px 15px; margin: 5px 0; border-radius: 10px; color: white; text-decoration: none; }}
            .nav-item:hover {{ background: rgba(168,85,247,0.2); color: #a855f7; }}
            .main {{ margin-left: 260px; padding: 30px; }}
            table {{ width: 100%; border-collapse: collapse; background: rgba(255,255,255,0.05); border-radius: 10px; overflow-x: auto; display: block; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }}
            th {{ background: rgba(168,85,247,0.2); }}
            .btn {{ background: #a855f7; padding: 10px 20px; color: white; text-decoration: none; border-radius: 8px; display: inline-block; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div class="logo">👑 {SITE_NAME}</div>
            <a href="/owner-panel" class="nav-item">Overview</a>
            <a href="/owner-users" class="nav-item">Users</a>
            <a href="/owner-attacks" class="nav-item active">Attacks</a>
            <a href="/logout" class="nav-item">Logout</a>
        </div>
        <div class="main">
            <a href="/owner-panel" class="btn">← Back</a>
            <h2>All Attacks (Last 100)</h2>
            <div style="overflow-x: auto;">
                <table>
                    <thead><tr><th>User</th><th>Target</th><th>Port</th><th>Method</th><th>Duration</th><th>Status</th><th>Time</th></tr></thead>
                    <tbody>{attacks_html if attacks_html else '<tr><td colspan="7" style="text-align:center">No attacks yet</td></tr>'}</tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/owner/upgrade-user', methods=['POST'])
def owner_upgrade_user():
    user = get_user()
    if not user or not user.get('is_owner'):
        return jsonify({"success": False, "error": "Unauthorized"})
    
    data = request.get_json()
    user_id = data.get('user_id')
    plan = data.get('plan')
    
    if not user_id or not plan or plan not in ['free', 'basic', 'premium', 'vip']:
        return jsonify({"success": False, "error": "Invalid request"})
    
    if mongo_connected and users_col:
        new_expiry = time.time() + (30 * 86400)
        result = users_col.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"plan": plan, "expiry": new_expiry, "upgraded_at": time.time()}}
        )
        if result.modified_count > 0:
            return jsonify({"success": True})
    
    return jsonify({"success": False, "error": "Database error"})

@app.route('/logout')
def logout():
    session.clear()
    return '<script>alert("Logged out!"); window.location.href="/";</script>'

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "mongo_connected": mongo_connected})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    
    print("=" * 50)
    print(f"🔥 {SITE_NAME} Panel Starting...")
    print("=" * 50)
    print(f"👑 Owner Username: {OWNER_USERNAME}")
    print(f"🔑 Owner Password: {OWNER_PASSWORD}")
    print(f"🌐 URL: {SITE_URL}")
    print(f"⚡ Attack Duration: {DEFAULT_DURATION} seconds")
    print(f"📊 MongoDB: {'Connected ✅' if mongo_connected else 'Disconnected ❌'}")
    print("=" * 50)
    
    # Start attack monitor
    monitor_thread = threading.Thread(target=attack_monitor, daemon=True)
    monitor_thread.start()
    
    app.run(host='0.0.0.0', port=port, debug=False)