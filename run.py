#!/usr/bin/env python3
"""
Launcher script for Ollama Desktop
Entry point for the modularized application
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main application
from app import main

if __name__ == "__main__":
    main()
