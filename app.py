from flask import Flask
import Generator as g

app = Flask(__name__)


@app.route("/")
def base():
    return render_template("views/main_page.html")
