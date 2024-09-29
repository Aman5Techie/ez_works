#!/bin/bash

# Check if virtual environment folder exists
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  # Create virtual environment
  python3 -m venv venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install the required dependencies
if [ -f "requirements.txt" ]; then
  echo "Installing dependencies from requirements.txt..."
  pip install -r requirements.txt
else
  echo "requirements.txt file not found!"
  exit 1
fi

echo "Making migrations..."
python manage.py makemigrations

echo "Applying migrations..."
python manage.py migrate

echo "Setup complete. Virtual environment is ready, and migrations have been applied!"
