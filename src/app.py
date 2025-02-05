import os
from flask import Flask, abort, redirect, render_template, request, session, url_for
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from flask_session import Session  # サーバーサイドセッションを利用

app = Flask(__name__)
app.secret_key = "SAMPLE_KEY"

# サーバーサイドセッションの設定（filesystemなど）
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# 開発者A用の環境変数は参考情報として残すが、今回はユーザー入力がなければエラーにする
DEFAULT_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
DEFAULT_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
DEFAULT_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# ユーザーが入力したAPI情報が必ずセッションにあるか確認する関数
def get_user_creds():
    creds = session.get("user_creds")
    if not creds or not all([creds.get("client_id"), creds.get("client_secret"), creds.get("redirect_uri")]):
        abort(400, description="ユーザーのAPI情報が正しく設定されていません。再度入力してください。")
    return creds

# ユーザーのAPI情報を使ってSpotifyOAuthのインスタンスを生成
def get_spotify_oauth():
    creds = get_user_creds()
    client_id = creds["client_id"]
    client_secret = creds["client_secret"]
    redirect_uri = creds["redirect_uri"]

    print("Using credentials:")
    print("Client ID:", client_id)
    print("Client Secret:", client_secret)
    print("Redirect URI:", redirect_uri)

    # ユーザーごとにキャッシュファイルを分ける（これにより以前のキャッシュと混在しない）
    cache_path = f".cache-{client_id}"

    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="user-top-read",
        cache_path=cache_path,
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    client_id = request.form.get("client_id")
    client_secret = request.form.get("client_secret")
    redirect_uri = request.form.get("redirect_uri")

    # 入力値のチェック
    if not all([client_id, client_secret, redirect_uri]):
        return "すべての項目を入力してください。", 400

    # ユーザー情報は必ず「user_creds」に保存（他の場所には保存しない）
    session["user_creds"] = {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
    }
    print("フォームから受け取ったユーザー情報をセッションに保存しました:", session["user_creds"])
    return redirect(url_for("login_page"))

@app.route("/login_page")
def login_page():
    print("login_page セッションの内容:", dict(session))
    return render_template("login.html")

@app.route("/login")
def login():
    print("login セッションの内容:", dict(session))
    try:
        sp_oauth = get_spotify_oauth()
    except Exception as e:
        return str(e), 400

    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    print("callback セッションの内容:", dict(session))
    try:
        sp_oauth = get_spotify_oauth()
    except Exception as e:
        return str(e), 400

    code = request.args.get("code")
    if not code:
        return "認証コードが取得できませんでした。", 400

    try:
        token_info = sp_oauth.get_access_token(code)
    except Exception as e:
        print("get_access_token error:", e)
        return str(e), 400

    session["token_info"] = token_info
    return redirect(url_for("top_tracks"))

@app.route("/top-tracks")
def top_tracks():
    print("top_tracks セッションの内容:", dict(session))
    token_info = session.get("token_info")
    if not token_info:
        return redirect(url_for("login"))

    try:
        sp_oauth = get_spotify_oauth()
    except Exception as e:
        return str(e), 400

    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        session["token_info"] = token_info

    sp = Spotify(auth=token_info["access_token"])
    results = sp.current_user_top_tracks(limit=10, time_range="long_term")
    tracks = results.get("items", [])

    if not tracks:
        message = "再生記録がありません。"
    elif len(tracks) < 10:
        message = "再生記録が少ないため、利用可能な楽曲のみ表示しています。"
    else:
        message = ""

    top_tracks = [
        {
            "name": track["name"],
            "artists": ", ".join(artist["name"] for artist in track["artists"]),
            "image_url": track["album"]["images"][1]["url"]
            if len(track["album"]["images"]) > 1
            else track["album"]["images"][0]["url"],
        }
        for track in tracks
    ]
    return render_template("top_tracks.html", top_tracks=top_tracks, message=message)

if __name__ == "__main__":
    app.run(debug=True)
