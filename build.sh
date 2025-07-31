#!/bin/bash
# Install dependencies
pip install -r requirements.txt

# Initialize the database
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created!')
"
