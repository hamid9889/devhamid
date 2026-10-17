"""
DevHamid Portfolio - Root Application Proxy
Allows Render deployments to start smoothly even if the service's Root Directory
is configured as the repository root instead of 'backend'.
"""
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from backend.app import app  # noqa: F401

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
