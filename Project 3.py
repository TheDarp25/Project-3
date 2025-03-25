from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret_key'

def connect_db():
    return sqlite3.connect('expense_tracker.db')

# Initialize the database
def init_db():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                          id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          username TEXT UNIQUE, 
                          password TEXT)
                       ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                          id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          user_id INTEGER, 
                          date TEXT, 
                          amount REAL, 
                          category TEXT,
                          description TEXT)
                       ''')
        conn.commit()

init_db()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user[0]
                return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC", (session['user_id'],))
        expenses = cursor.fetchall()
    return render_template('dashboard.html', expenses=expenses)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect('/login')
    date = request.form['date']
    amount = request.form['amount']
    category = request.form['category']
    description = request.form['description']
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (user_id, date, amount, category, description) VALUES (?, ?, ?, ?, ?)", 
                       (session['user_id'], date, amount, category, description))
        conn.commit()
    return redirect('/dashboard')

@app.route('/view_report')
def view_report():
    if 'user_id' not in session:
        return redirect('/login')
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE user_id = ? GROUP BY category", (session['user_id'],))
        report = cursor.fetchall()
    return render_template('report.html', report=report)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
