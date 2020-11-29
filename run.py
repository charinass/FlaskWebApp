from Application import app
import os

app.secret_key = os.urandom(8)

if __name__ == "__main__":
    app.run(debug=True)