from flask import Flask
from canvas_controller import canvas_bp

app = Flask(__name__)
app.register_blueprint(canvas_bp, url_prefix="/api/canvas")

if __name__ == "__main__":
    app.run(port=3000, debug=True)