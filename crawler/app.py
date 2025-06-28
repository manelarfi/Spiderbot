from flask import Flask, render_template, request
from crawler import crawl

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        start_url = request.form.get("start_url")
        max_depth = int(request.form.get("max_depth", 0))
        results = crawl(start_url, max_depth=max_depth)
    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
