import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

# Vercel expects a variable called 'app' or 'handler'
# Using app directly works for Vercel
app = app
