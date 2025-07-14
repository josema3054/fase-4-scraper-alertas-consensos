"""
Tests básicos del sistema
"""

import pytest
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Tests importados
from .test_scraper import *
from .test_database import *
from .test_notifications import *
