import os

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = os.urandom(24)  # セッション管理のための秘密鍵

load_dotenv()

# Spotify APIのクライアントID、シークレット、およびリダイレクトURIを環境変数から取得
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Spotipyの認証設定
sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-top-read",
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    # Spotifyの認証URLにリダイレクト
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route("/callback")
def callback():
    # 認証コードを取得し、アクセストークンを取得
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect(url_for("top_tracks"))


@app.route("/top-tracks")
def top_tracks():
    # トークンの有効性を確認し、必要に応じてリフレッシュ
    token_info = session.get("token_info", None)
    if not token_info:
        return redirect(url_for("login"))

    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        session["token_info"] = token_info

    # Spotify APIクライアントを作成
    sp = Spotify(auth=token_info["access_token"])

    # ユーザーのTOP10楽曲を取得
    results = sp.current_user_top_tracks(limit=10, time_range="long_term")
    top_tracks = [
        {
            "name": track["name"],
            "artists": ", ".join(artist["name"] for artist in track["artists"]),
            "image_url": track["album"]["images"][1]["url"],  # 中サイズのジャケット画像
            # "preview_url": track["preview_url"],  # プレビューURL
        }
        for track in results["items"]
    ]

    return render_template("top_tracks.html", top_tracks=top_tracks)


if __name__ == "__main__":
    app.run(debug=True)