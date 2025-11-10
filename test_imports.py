#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки импортов
"""
try:
    print("Testing imports...")
    from flask import Flask
    print("[OK] Flask imported")
    
    from flask_sqlalchemy import SQLAlchemy
    print("[OK] Flask-SQLAlchemy imported")
    
    from sqlalchemy import or_
    print("[OK] SQLAlchemy or_ imported")
    
    from werkzeug.utils import secure_filename
    print("[OK] Werkzeug utils imported")
    
    from werkzeug.security import generate_password_hash
    print("[OK] Werkzeug security imported")
    
    print("\nAll imports successful!")
    print("You can now run: python run.py")
    
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print("Please install dependencies: pip install -r requirements.txt")
    exit(1)

except Exception as e:
    print(f"[ERROR] Error: {e}")
    exit(1)

