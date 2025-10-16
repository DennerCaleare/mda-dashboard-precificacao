"""Ponto de entrada da aplicação MDA Precificação de Áreas."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mda_app.app import main

if __name__ == "__main__":
    main()