import os

from flask import Flask, redirect, render_template, request, session, url_for
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = "SAMPLE_KEY"

# 環境変数からの初期値（開発者用のデフォルトとして利用可能）
DEFAULT_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
DEFAULT_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
DEFAULT_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")


# セッションに保存された値（またはデフォルト）を用いてSpotifyOAuthインスタンスを生成するヘルパー関数
def get_spotify_oauth():
    # user_creds にユーザーBの情報が入っていればそれを使う
    user_creds = session.get("user_creds", {})
    client_id = user_creds.get("client_id") or DEFAULT_CLIENT_ID
    client_secret = user_creds.get("client_secret") or DEFAULT_CLIENT_SECRET
    redirect_uri = user_creds.get("redirect_uri") or DEFAULT_REDIRECT_URI

    print("Using credentials:")
    print("Client ID:", client_id)
    print("Client Secret:", client_secret)
    print("Redirect URI:", redirect_uri)

    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="user-top-read",
    )


@app.route("/")
def index():
    return render_template("index.html")


# フォーム送信値を受け取り、セッションに保存するエンドポイント
@app.route("/submit", methods=["POST"])
def submit():
    client_id = request.form.get("client_id")
    client_secret = request.form.get("client_secret")
    redirect_uri = request.form.get("redirect_uri")

    # 入力値が正しく送信されているかチェック
    if not all([client_id, client_secret, redirect_uri]):
        return "すべての項目を入力してください。", 400

    # ユーザー情報を1つの辞書にまとめてセッションに保存（トップレベルには保存しない）
    session["user_creds"] = {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
    }

    print("フォームから受け取ったユーザー情報をセッションに保存しました:", session["user_creds"])

    # 入力値を保存後、ログイン開始画面へ遷移
    return redirect(url_for("login_page"))


# ログイン開始前の画面（login.html）を表示するエンドポイント
@app.route("/login_page")
def login_page():
    print("callback セッションの内容:", dict(session))
    return render_template("login.html")


@app.route("/login")
def login():
    print("callback セッションの内容:", dict(session))
    try:
        sp_oauth = get_spotify_oauth()
    except ValueError as e:
        return str(e), 400

    # Spotifyの認証URLにリダイレクト
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route("/callback")
def callback():
    print("callback セッションの内容:", dict(session))
    try:
        sp_oauth = get_spotify_oauth()
    except ValueError as e:
        return str(e), 400

    # 認証コードを取得し、アクセストークンを取得
    code = request.args.get("code")
    if not code:
        return "認証コードが取得できませんでした。", 400

    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect(url_for("top_tracks"))


@app.route("/top-tracks")
def top_tracks():
    print("callback セッションの内容:", dict(session))
    token_info = session.get("token_info", None)
    if not token_info:
        return redirect(url_for("login"))

    try:
        sp_oauth = get_spotify_oauth()
    except ValueError as e:
        return str(e), 400

    # トークンの有効性を確認し、必要に応じてリフレッシュ
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        session["token_info"] = token_info

    # Spotify APIクライアントを作成
    sp = Spotify(auth=token_info["access_token"])

    # ユーザーのTOP楽曲（最大10曲）を取得
    results = sp.current_user_top_tracks(limit=10, time_range="long_term")
    tracks = results.get("items", [])

    # 取得できた件数に応じたメッセージを用意
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
            # 画像が1枚しかない場合も考慮
            "image_url": track["album"]["images"][1]["url"]
            if len(track["album"]["images"]) > 1
            else track["album"]["images"][0]["url"],
        }
        for track in tracks
    ]

    return render_template("top_tracks.html", top_tracks=top_tracks, message=message)


if __name__ == "__main__":
    app.run(debug=True)
