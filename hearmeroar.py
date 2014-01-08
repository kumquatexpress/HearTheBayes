from flask import Flask, render_template
import Generator as g

app = Flask(__name__)


@app.route("/")
def base():
    return render_template("main_page.html")


if __name__ == '__main__':
    app.run()
