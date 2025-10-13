from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configure SQLite database - try different approaches
basedir = os.path.abspath(os.path.dirname(__file__))

# Try to use a writable directory
import tempfile
temp_dir = tempfile.gettempdir()
db_path = os.path.join(temp_dir, "mydatabase.db")

print(f"Attempting to create database at: {db_path}")
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'

db = SQLAlchemy(app)

# Define your User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Define your Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


#loads the mainpage
@app.route('/')
def load_main_page():
    return render_template('login.html')
#loads the register page when clicked from the login page
@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


#def handle_error(message, status_code=400):
#    return jsonify(error=message), status_code

#this function registers you
@app.route('/registerUser', methods=['POST'])
def new_user():
    try:
        # Get username and password from form data
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if both fields are provided
        if not username or not password:
            return "Username and password are required", 400

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "User already exists", 400

        # Create new user
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('load_main_page'))

    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        return f"Registration failed: {str(e)}", 500
#this function logs you in
@app.route('/login', methods=['POST'])
def login():
    try:
        # Get username and password from form data
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if both fields are provided
        if not username or not password:
            return "Username and password are required", 400

        # Query for user with matching credentials
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            # Store user info in session for task management
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            # Check if user exists but password is wrong
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return "Invalid password", 401
            else:
                return "Account not found. Please register first.", 404

    except Exception as e:
        return f"Login failed: {str(e)}", 500

# Dashboard route to show tasks
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('load_main_page'))

    try:
        # Get all tasks for the current user
        tasks = Task.query.filter_by(user_id=session['user_id']).order_by(Task.created_at.desc()).all()
        return render_template('homepage.html', tasks=tasks, username=session['username'])
    except Exception as e:
        return f"Error loading dashboard: {str(e)}", 500

# Add task route
@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('load_main_page'))

    try:
        title = request.form.get('title')
        description = request.form.get('description', '')

        if not title:
            return "Task title is required", 400

        new_task = Task(
            title=title,
            description=description,
            user_id=session['user_id']
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('dashboard'))

    except Exception as e:
        db.session.rollback()
        return f"Error adding task: {str(e)}", 500

# Delete task route
@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('load_main_page'))

    try:
        task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
        if not task:
            return "Task not found", 404

        db.session.delete(task)
        db.session.commit()
        return redirect(url_for('dashboard'))

    except Exception as e:
        db.session.rollback()
        return f"Error deleting task: {str(e)}", 500

# Toggle task completion
@app.route('/toggle_task/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('load_main_page'))

    try:
        task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
        if not task:
            return "Task not found", 404

        task.completed = not task.completed
        db.session.commit()
        return redirect(url_for('dashboard'))

    except Exception as e:
        db.session.rollback()
        return f"Error updating task: {str(e)}", 500

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('load_main_page'))

# Route to manually initialize database (for debugging)
@app.route('/init_db')
def init_db():
    try:
        db.create_all()
        return "Database initialized successfully!"
    except Exception as e:
        return f"Error initializing database: {str(e)}"

# Initialize database when app starts
def init_database():
    try:
        with app.app_context():
            # Check if we can write to the database location
            print(f"Database will be created at: {db_path}")

            # Try to create the database directory if it doesn't exist
            db_dir = os.path.dirname(db_path)
            if not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                print(f"Created directory: {db_dir}")

            db.create_all()
            print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database: {e}")
        print("Falling back to in-memory database...")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            print("In-memory database created successfully!")

if __name__ == '__main__':
    init_database()
    app.run(debug=True)
    
    
    


