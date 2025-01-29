import os

from flask import Flask, redirect, render_template, request, session, url_for
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = os.urandom(24)  # セッション管理のための秘密鍵


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    session["client_id"] = request.form["client_id"]
    session["client_secret"] = request.form["client_secret"]
    session["redirect_uri"] = request.form["redirect_uris"]
    return redirect(url_for("login"))


@app.route("/login")
def login():
    if "client_id" not in session or "client_secret" not in session or "redirect_uri" not in session:
        return redirect(url_for("index"))

    sp_oauth = SpotifyOAuth(
        client_id=session["client_id"],
        client_secret=session["client_secret"],
        redirect_uri=session["redirect_uri"],
        scope="user-top-read",
    )
    return redirect(sp_oauth.get_authorize_url())


@app.route("/callback")
def callback():
    if "client_id" not in session or "client_secret" not in session or "redirect_uri" not in session:
        return redirect(url_for("index"))

    sp_oauth = SpotifyOAuth(
        client_id=session["client_id"],
        client_secret=session["client_secret"],
        redirect_uri=session["redirect_uri"],
        scope="user-top-read",
    )

    code = request.args.get("code")
    if not code:
        print("Error: No code received from Spotify")
        return redirect(url_for("index"))

    token_info = sp_oauth.get_access_token(code)
    if not token_info:
        print("Error: Failed to retrieve token_info")
        return redirect(url_for("index"))

    session["token_info"] = token_info
    print("Token info saved:", session["token_info"])

    return redirect(url_for("top_tracks"))


@app.route("/top-tracks")
def top_tracks():
    if "token_info" not in session:
        print("Error: No token_info in session")
        return redirect(url_for("login"))

    token_info = session["token_info"]
    print("Using token_info:", token_info)

    sp = Spotify(auth=token_info["access_token"])
    results = sp.current_user_top_tracks(limit=10, time_range="long_term")

    if not results or "items" not in results:
        print("Error: Failed to fetch top tracks")
        return redirect(url_for("index"))

    top_tracks = [
        {
            "name": track["name"],
            "artists": ", ".join(artist["name"] for artist in track["artists"]),
            "image_url": track["album"]["images"][1]["url"],
            "preview_url": track["preview_url"],
        }
        for track in results["items"]
    ]

    return render_template("top_tracks.html", top_tracks=top_tracks)


if __name__ == "__main__":
    app.run(debug=True)
