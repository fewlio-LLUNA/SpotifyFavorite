FROM python:3.12.7
WORKDIR /usr/src/app
RUN pip install blinker==1.9.0
RUN pip install certifi==2024.8.30
RUN pip install charset-normalizer==3.4.0
RUN pip install click==8.1.7
RUN pip install colorama==0.4.6
RUN pip install Flask==3.1.0
RUN pip install Flask-Session==0.8.0
RUN pip install greenlet==3.1.1
RUN pip install idna==3.10
RUN pip install itsdangerous==2.2.0
RUN pip install Jinja2==3.1.4
RUN pip install MarkupSafe==3.0.2
RUN pip install mypy==1.13.0
RUN pip install mypy-extensions==1.0.0
RUN pip install python-dotenv==1.0.1
RUN pip install redis==5.2.1
RUN pip install requests==2.32.3
RUN pip install spotipy==2.25.0
RUN pip install typing_extensions==4.12.2
RUN pip install urllib3==2.2.3
RUN pip install Werkzeug==3.1.3
CMD ["flask", "run", "--host=0.0.0.0", "--debug"]