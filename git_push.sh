#!/bin/bash

# Navigate to the project directory
cd "C:/Users/sw126/my_flask_app"

# Configure Git user details
git config --global user.email "sw1261@naver.com"
git config --global user.name "sw1261"

# Add all changes to Git
git add .

# Commit changes with a message
git commit -m "Update code and configuration for deployment"

# Push changes to the main branch
git push origin main
