#!/usr/bin/env python
"""
Script pour exécuter les tests de l'API de subventions
----------------------------------------------------
"""

import os
import sys
import pytest

if __name__ == "__main__":
    # Ajouter le répertoire parent au chemin Python pour que les imports fonctionnent
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    
    # Exécuter les tests avec pytest
    exit_code = pytest.main(["-v", os.path.dirname(__file__)])
    
    sys.exit(exit_code)
