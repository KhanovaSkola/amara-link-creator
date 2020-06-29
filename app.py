#!/usr/bin/env python3

# Run Flask server in debug mode
# export FLASK_ENV=development
# python -m flask run

from flask import Flask, render_template
from api.amara_api import Amara
app = Flask(__name__)

AMARA_TEAM = "khan-academy"

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/<lang>/<youtube_id>')
def test(lang, youtube_id):
    # TODO: some validation here
    # TODO: manage multiple YouTubeIDs per request
    video_url = "https://youtube.com/watch?v=%s" % youtube_id
    amara = Amara()
    amara_response = amara.check_video(video_url, AMARA_TEAM)
    print(amara_response)
    for r in amara_response['objects']:
        if r['team'] == AMARA_TEAM:
            amara_id = r['id']
            url = "%s/%s/subtitles/editor/%s/%s/?team=%s" % \
                (amara.AMARA_BASE_URL, lang, amara_id, lang, AMARA_TEAM)
            return {youtube_id: url}

    return {youtube_id: "Could not find video on Amara"}

