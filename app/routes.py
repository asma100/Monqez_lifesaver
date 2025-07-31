from flask import Flask, abort, render_template, url_for, flash, redirect, request, send_file, jsonify
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required
# Use simplified gemini without RAG/PDF dependencies
from app.gemini_simple import ask_question
from flask import session
from flask import Flask
import requests
from flask import request
from app.forms import VolunteerForm
from app.models import Volunteer
from datetime import datetime
from app.models import ChatHistory
from flask_login import login_required, current_user
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

@app.route('/telegram_webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')

        # Your Gemini assistant logic here
        response = ask_question(text)  # This can be your Gemini function

        requests.post(TELEGRAM_URL, json={
            "chat_id": chat_id,
            "text": response
        })

    return jsonify({'status': 'ok'})

@app.route("/home", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        return redirect(url_for('chat'))
    return render_template('landingpage.html')


@app.route('/submit_location', methods=['POST'])
def submit_location():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    session['user_coords'] = (lat, lon)
    print(f"[✅] Received user location: {lat}, {lon}")
    return jsonify({'status': 'ok'})

@app.route("/set_location", methods=["POST"])
def set_location():
    lat = request.form.get("lat")
    lon = request.form.get("lon")
    if lat and lon:
        session['user_coords'] = (float(lat), float(lon))  # << use 'user_coords' here!
        flash("Location received!")
    else:
        flash("Failed to get location.")
    return redirect(url_for("chat"))


@app.route("/volunteer", methods=["GET", "POST"])
@login_required
def volunteer():
    form = VolunteerForm()
    existing = Volunteer.query.filter_by(user_id=current_user.id).first()

    if form.validate_on_submit():
        if existing:
            # Update existing entry
            existing.name = form.name.data
            existing.phone_number = form.phone_number.data
            existing.available_days = ','.join(form.available_days.data)  # Convert list to comma-separated string
            existing.available_times = form.available_times.data
            existing.specialty = form.specialty.data
        else:
            # Create new volunteer entry
            new_vol = Volunteer(
                name=form.name.data,
                phone_number=form.phone_number.data,
                available_days=','.join(form.available_days.data),
                available_times=form.available_times.data,
                specialty=form.specialty.data,
                user_id=current_user.id
            )
            db.session.add(new_vol)

        db.session.commit()
        flash("تم حفظ بيانات التطوع بنجاح!", "success")
        return redirect(url_for("volunteer"))

    # Pre-populate form with existing data
    if existing:
        form.name.data = existing.name
        form.phone_number.data = existing.phone_number
        form.available_days.data = existing.available_days.split(',') if existing.available_days else []
        form.available_times.data = existing.available_times
        form.specialty.data = existing.specialty
    else:
        # Initialize with empty list to prevent None error
        if form.available_days.data is None:
            form.available_days.data = []

    return render_template("volunteer.html", form=form, volunteer=existing)


@app.route("/delete_volunteer", methods=["POST"])
@login_required
def delete_volunteer():
    volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()
    if volunteer:
        db.session.delete(volunteer)
        db.session.commit()
        flash("Volunteer entry deleted.", "info")
    return redirect(url_for("volunteer"))


@app.route("/chat", methods=['GET', 'POST'])
def chat():
    query = None
    answer = None
    user_coords = session.get('user_coords')
    
    # Always create a new conversation session when visiting chat page
    session['chat_session_id'] = str(uuid.uuid4())
    
    print(user_coords)  # ← Get user location

    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            answer = ask_question(query, user_coords=user_coords)

    return render_template('chatbot.html', query=query, answer=answer)

@app.route('/history')
@login_required
def history():
    # Get all chat history for current user
    chats = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.desc()).all()
    
    # Group conversations by session_id
    conversations = {}
    for chat in chats:
        session_key = chat.session_id
        
        if session_key not in conversations:
            conversations[session_key] = []
        conversations[session_key].append(chat)
    
    return render_template("history.html", conversations=conversations)


@app.route('/delete_chat/<int:chat_id>', methods=['POST'])
@login_required
def delete_chat(chat_id):
    chat = ChatHistory.query.get_or_404(chat_id)
    if chat.user_id != current_user.id:
        abort(403)
    db.session.delete(chat)
    db.session.commit()
    flash("تم حذف المحادثة بنجاح", "success")
    return redirect(url_for("history"))


@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html', title='About')


from app.models import ChatHistory  # make sure this is imported
from datetime import datetime
import uuid

@app.route('/get_response', methods=['POST'])
@login_required
def get_response():
    data = request.get_json()
    query = data.get('query')
    if query:
        # Get or create session ID for this conversation
        session_id = session.get('chat_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['chat_session_id'] = session_id
        
        user_coords = session.get('user_coords')
        answer = ask_question(query, user_coords=user_coords)

        # Save user message
        user_chat = ChatHistory(
            user_id=current_user.id,
            session_id=session_id,
            content=query,
            message_type='user'
        )
        db.session.add(user_chat)
        
        # Save bot response
        bot_chat = ChatHistory(
            user_id=current_user.id,
            session_id=session_id,
            content=answer,
            message_type='bot'
        )
        db.session.add(bot_chat)
        db.session.commit()

        return jsonify({'response': answer})
    return jsonify({'response': 'No query provided.'})



@app.route("/", methods=['GET', 'POST'])
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))