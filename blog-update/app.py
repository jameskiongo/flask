import sys

sys.path.append("backend")
import index
from config import app, db

if __name__ == "__main__":
    app.run(debug=True)
