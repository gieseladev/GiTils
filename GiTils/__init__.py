from .gitils import app


@app.route("/")
def index():
    return "Hello World!"


if __name__ == "__main__":
    app.run()
