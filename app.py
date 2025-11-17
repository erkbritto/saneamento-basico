#!/usr/bin/env python3
"""
Sistema de Saneamento Básico com Autenticação Facial
Ponto de entrada principal da aplicação
"""

from app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)