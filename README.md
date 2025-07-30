# Monqez Lifesaver 🚑

A comprehensive first aid assistant application built with Flask that combines AI-powered chatbot functionality with location-based hospital finder and volunteer coordination system.

## 🌟 Features

### 🤖 AI-Powered First Aid Assistant
- **Smart Chatbot**: Powered by Google Gemini AI for intelligent first aid guidance
- **PDF Knowledge Base**: Trained on comprehensive first aid manuals and medical documents
- **Vector Search**: Uses FAISS for efficient document retrieval and context-aware responses
- **Conversation History**: Maintains chat history for better user experience

### 📍 Location-Based Services
- **Hospital Finder**: Locates the 7 nearest hospitals based on user's current location
- **Geographic Data**: Integrated with Sudan health facilities data
- **Distance Calculation**: Uses GeoPy for accurate distance measurements

### 👥 Volunteer Management
- **Volunteer Registration**: Healthcare professionals can register and specify availability
- **Real-time Matching**: Connects users with available volunteers based on time and specialty
- **Scheduling System**: Manages volunteer availability by days and time slots

### 🔐 User Management
- **User Authentication**: Secure login/registration system
- **Password Security**: Bcrypt encryption for password protection
- **Session Management**: Flask-Login for secure session handling
- **User Profiles**: Personalized user experience

### 🤖 Telegram Integration
- **Bot Support**: Telegram webhook integration for extended accessibility
- **Real-time Responses**: Instant first aid assistance through Telegram

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 3.1.1
- **Database**: SQLite with SQLAlchemy ORM
- **Migration**: Alembic for database migrations
- **Authentication**: Flask-Login + Bcrypt

### AI & Machine Learning
- **LLM**: Google Generative AI (Gemini)
- **Document Processing**: LangChain for PDF processing and text splitting
- **Embeddings**: HuggingFace Transformers (all-MiniLM-L6-v2)
- **Vector Database**: FAISS for similarity search
- **ML Framework**: PyTorch

### Frontend
- **Template Engine**: Jinja2
- **Forms**: Flask-WTF with WTForms
- **Styling**: Custom CSS with responsive design

### External APIs & Services
- **Location Services**: GeoPy for geocoding and distance calculations
- **HTTP Requests**: Requests library for API calls
- **Environment Management**: python-dotenv for configuration

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/asma100/Monqez_lifesaver.git
   cd Monqez_lifesaver
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **Linux/Mac:**
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   # Flask Configuration
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here-change-this
   
   # Database Configuration
   SQLALCHEMY_DATABASE_URI=sqlite:///site.db
   SQLALCHEMY_TRACK_MODIFICATIONS=False
   
   # Google Gemini AI API Configuration
   GEMINI_API_KEY=your-gemini-api-key-here
   
   # Telegram Bot Configuration (Optional)
   TELEGRAM_TOKEN=your-telegram-bot-token-here
   
   # Debug Mode
   DEBUG=True
   ```

6. **Initialize the database**
   ```bash
   flask db upgrade
   ```

7. **Run the application**
   ```bash
   python run.py
   ```

   The application will be available at `http://localhost:5000`

## 🔧 Configuration

### Required API Keys

1. **Google Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it to your `.env` file as `GEMINI_API_KEY`

2. **Telegram Bot Token (Optional)**
   - Create a bot using [@BotFather](https://t.me/botfather) on Telegram
   - Get the bot token
   - Add it to your `.env` file as `TELEGRAM_TOKEN`

### Database Setup

The application uses SQLite by default. For production, you can configure PostgreSQL or MySQL by updating the `SQLALCHEMY_DATABASE_URI` in your `.env` file.

## 📁 Project Structure

```
Monqez_lifesaver/
├── app/
│   ├── __init__.py              # Flask app initialization
│   ├── config.py                # Configuration settings
│   ├── models.py                # Database models
│   ├── routes.py                # Application routes
│   ├── forms.py                 # WTForms definitions
│   ├── gemini.py                # AI chatbot logic
│   ├── loction.py               # Location services
│   ├── volunteer_utils.py       # Volunteer management
│   ├── static/                  # CSS, JS, images
│   ├── templates/               # HTML templates
│   └── pdfs/                    # First aid knowledge base
├── data/                        # Geographic data files
├── migrations/                  # Database migration files
├── venv/                        # Virtual environment (not in git)
├── .env                         # Environment variables (not in git)
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
└── README.md                    # Project documentation
```

## 🚀 Usage

### Web Application
1. Navigate to `http://localhost:5000`
2. Register a new account or login
3. Access the chatbot for first aid assistance
4. Use location services to find nearby hospitals
5. Browse available volunteers

### API Endpoints
- `/` - Landing page
- `/register` - User registration
- `/login` - User login
- `/chat` - AI chatbot interface
- `/volunteer` - Volunteer registration/management
- `/telegram_webhook` - Telegram bot webhook

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/asma100/Monqez_lifesaver/issues) page
2. Create a new issue if your problem isn't already reported
3. Provide detailed information about your environment and the error

## 🙏 Acknowledgments

- Google Gemini AI for providing advanced language model capabilities
- HuggingFace for pre-trained embedding models
- OpenStreetMap for health facility data
- Flask community for excellent documentation and tools

---

**⚠️ Medical Disclaimer**: This application provides general first aid information and should not replace professional medical advice. In case of serious medical emergencies, always call emergency services immediately.
