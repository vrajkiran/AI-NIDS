"""AI-NIDS Launcher Script.

Starts the Flask backend server, initializes the database, and automatically
opens the dashboard in the default browser.
"""

from __future__ import annotations

import os
import sys
import time
import webbrowser
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import DATABASE_PATH, HOST, MODEL_PATH, PORT
from database.db import create_database


def print_banner() -> None:
    banner = f"""========================================
        AI-NIDS
 Network Intrusion Detection System
========================================

Starting application...

Backend: Flask
Database: SQLite ({DATABASE_PATH.name})
ML Model: Random Forest ({'Loaded' if MODEL_PATH.exists() else 'Not found - train with python ml/train.py'})

Dashboard:
http://{HOST}:{PORT}

Starting browser...
"""
    print(banner)


def open_browser(url: str, delay: float = 1.5) -> None:
    """Open default browser after server initializes."""
    time.sleep(delay)
    try:
        webbrowser.open(url)
    except Exception as error:
        print(f"Notice: Could not automatically open browser ({error}). Please navigate to {url}")


def main() -> None:
    print_banner()

    # Ensure SQLite database structure exists
    create_database(DATABASE_PATH)

    url = f"http://{HOST}:{PORT}"

    # Launch browser in a background thread before starting Flask app loop
    browser_thread = threading.Thread(target=open_browser, args=(url, 1.5), daemon=True)
    browser_thread.start()

    from app import app
    try:
        app.run(host=HOST, port=PORT, debug=False)
    except KeyboardInterrupt:
        print("\nAI-NIDS server stopped cleanly.")
    except Exception as error:
        print(f"\nServer error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
