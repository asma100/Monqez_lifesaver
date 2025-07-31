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
    try:
        data = request.get_json()
        
        if "message" in data:
            chat_id = data['message']['chat']['id']
            user_name = data['message']['from'].get('first_name', 'User')
            text = data['message'].get('text', '')
            
            # Check if user sent location
            location = data['message'].get('location')
            user_coords = None
            
            if location:
                # User shared their location
                lat = location['latitude']
                lon = location['longitude']
                user_coords = (lat, lon)
                print(f"[📍] Telegram user {user_name} shared location: {lat}, {lon}")
                
                # Acknowledge location received
                location_msg = f"""تم استلام موقعك بنجاح! �
الإحداثيات: {lat:.4f}, {lon:.4f}

الآن يمكنني أن أعطيك معلومات دقيقة عن أقرب المستشفيات إليك.
أرسل لي سؤالك الطبي وسأساعدك! 🏥"""
                
                requests.post(TELEGRAM_URL, json={
                    "chat_id": chat_id,
                    "text": location_msg
                })
                return jsonify({'status': 'ok'})
            
            print(f"[�📱] Telegram message from {user_name}: {text}")
            
            # Handle commands
            if text.startswith('/start'):
                welcome_msg = f"""مرحباً {user_name}! 🏥

أنا مساعد طبي ذكي من منصة منقذ الحياة.
يمكنني مساعدتك في:
• الإسعافات الأولية
• معلومات المستشفيات القريبة
• نصائح طبية عامة

📍 لمساعدة أفضل: شارك موقعك معي لأجد أقرب المستشفيات إليك

أرسل لي أي سؤال طبي وسأساعدك! 🩺"""
                
                # Add location request button
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": welcome_msg,
                    "reply_markup": {
                        "keyboard": [
                            [{"text": "📍 شارك موقعي", "request_location": True}],
                            [{"text": "❓ مساعدة", "text": "/help"}]
                        ],
                        "resize_keyboard": True,
                        "one_time_keyboard": False
                    }
                })
                
            elif text.startswith('/help'):
                help_msg = """كيفية الاستخدام:

📝 اكتب أي سؤال طبي مثل:
• "عندي صداع"
• "كيف أعالج الحروق؟"
• "أين أقرب مستشفى؟"

📍 شارك موقعك معي لأجد أقرب المستشفيات إليك

🆘 في حالات الطوارئ:
اتصل بـ 999 فوراً

🌐 للمزيد من الخدمات:
زر موقعنا على الإنترنت"""
                
                requests.post(TELEGRAM_URL, json={
                    "chat_id": chat_id,
                    "text": help_msg
                })
                
            elif text == "📍 شارك موقعي":
                # User clicked location button but didn't actually share location
                location_request_msg = """لمشاركة موقعك:

1️⃣ اضغط على زر "📍 شارك موقعي" أدناه
2️⃣ أو اضغط على زر 📎 (المرفقات) في تليجرام
3️⃣ اختر "الموقع" 
4️⃣ اختر "إرسال موقعي الحالي"

بعد مشاركة الموقع، ستحصل على معلومات دقيقة عن أقرب المستشفيات! 🏥"""
                
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": location_request_msg,
                    "reply_markup": {
                        "keyboard": [
                            [{"text": "📍 شارك موقعي", "request_location": True}]
                        ],
                        "resize_keyboard": True,
                        "one_time_keyboard": True
                    }
                })
                
            else:
                # Process medical question
                # TODO: In real implementation, you might want to store user locations in session/database
                response = ask_question(text, user_coords=user_coords)
                
                # Split long messages (Telegram has 4096 character limit)
                if len(response) > 4000:
                    # Send in chunks
                    chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
                    for chunk in chunks:
                        requests.post(TELEGRAM_URL, json={
                            "chat_id": chat_id,
                            "text": chunk
                        })
                else:
                    requests.post(TELEGRAM_URL, json={
                        "chat_id": chat_id,
                        "text": response
                    })
        
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        print(f"[❌] Telegram webhook error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/telegram_status')
def telegram_status():
    """Check Telegram bot configuration"""
    token = os.environ.get('TELEGRAM_TOKEN')
    
    if not token or token == 'your-telegram-bot-token-here':
        return jsonify({
            'status': 'error',
            'message': 'Telegram token not configured'
        })
    
    try:
        # Test bot token
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe")
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info['ok']:
                return jsonify({
                    'status': 'success',
                    'bot_name': bot_info['result']['first_name'],
                    'bot_username': bot_info['result']['username'],
                    'webhook_url': f"{request.host_url}telegram_webhook"
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid bot token'
                })
        else:
            return jsonify({
                'status': 'error',
                'message': f'HTTP error: {response.status_code}'
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

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
    # Get all chat history for current user, ordered by timestamp
    chats = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp).all()
    
    # Group conversations by session_id
    conversations = {}
    for chat in chats:
        session_key = chat.session_id
        
        if session_key not in conversations:
            conversations[session_key] = []
        conversations[session_key].append(chat)
    
    # Sort sessions by the timestamp of their first message (newest sessions first)
    sorted_conversations = {}
    session_times = {}
    
    # Get the earliest timestamp for each session
    for session_id, messages in conversations.items():
        session_times[session_id] = min(msg.timestamp for msg in messages)
    
    # Sort sessions by their start time (newest first)
    sorted_session_ids = sorted(session_times.keys(), 
                              key=lambda x: session_times[x], 
                              reverse=True)
    
    # Build sorted conversations dict
    for session_id in sorted_session_ids:
        sorted_conversations[session_id] = conversations[session_id]
    
    return render_template("history.html", conversations=sorted_conversations)


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
def get_response():  # Removed @login_required to allow unregistered users
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

        # Save to database only if user is logged in
        if current_user.is_authenticated:
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
        # If user is not logged in, just return the response without saving

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