import time
from flask import Blueprint, render_template, session, redirect, url_for, abort
from .wiki import get_random_article, get_article

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/start", methods=["POST"])
def start():
    start_title = get_random_article()
    target_title = get_random_article()
    while target_title == start_title:
        target_title = get_random_article()

    session["game"] = {
        "start": start_title,
        "target": target_title,
        "path": [start_title],
        "start_time": time.time(),
    }
    return redirect(url_for("main.play", title=start_title.replace(" ", "_")))


@main.route("/play/<path:title>")
def play(title):
    game = session.get("game")
    if not game:
        return redirect(url_for("main.index"))

    article = get_article(title)
    if article is None:
        abort(404)

    canonical = article["title"]

    if not game["path"] or game["path"][-1] != canonical:
        game["path"].append(canonical)
        session.modified = True

    if canonical == game["target"]:
        elapsed = time.time() - game["start_time"]
        path = list(game["path"])
        start = game["start"]
        target = game["target"]
        session.pop("game", None)
        return render_template("win.html", path=path, elapsed=elapsed,
                               target=target, start=start)

    return render_template("play.html", article=article, game=game)


@main.route("/give-up", methods=["POST"])
def give_up():
    session.pop("game", None)
    return redirect(url_for("main.index"))


@main.route("/health")
def health():
    return {"status": "ok"}
