#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска ArbTube
"""
from app import app, db

if __name__ == '__main__':
    # Создаем таблицы базы данных если их еще нет
    with app.app_context():
        db.create_all()
        print("Database initialized!")
        print("Starting server on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

