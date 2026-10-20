"""Entry point for the Local Loop backend (Puvanan).

Run from the project root (the folder that contains `backend/`):
    python -m backend.main
"""

from backend import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)