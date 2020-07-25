#!/usr/bin/env python3

import re
# Run Flask server in debug mode
# export FLASK_ENV=development
# python -m flask run
from flask import Flask, render_template
from kstools.api.amara_api import Amara
app = Flask(__name__)

AMARA_TEAM = "khan-academy"

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/<lang>/<youtube_id>')
def get_amara_link(lang, youtube_id):
    """Polls Amara API for AmaraID for a given YouTubeID
    and constructs a link to the Amara subtitling editor"""
    # TODO: manage multiple YouTubeIDs per request
    # TODO: Add option to generate public Amara links
    # (need to validate the video exists, and if not, create it, and add a language)

    ytid_regex = r'^[a-zA-Z0-9_-]{11}$'
    if not re.fullmatch(ytid_regex, youtube_id):
        return {youtube_id: ("invalid YouTube ID", "", "")}

    video_url = "https://youtube.com/watch?v=%s" % youtube_id
    amara = Amara()
    amara_response = amara.check_video(video_url, AMARA_TEAM)
    for r in amara_response['objects']:
        if r['team'] == AMARA_TEAM:
            amara_id = r['id']

            # This is all too complicated, let's just generate one link to
            # video page
            #editor_url = "%s/%s/subtitles/editor/%s/%s/?team=%s" % \
            #    (amara.AMARA_BASE_URL, lang, amara_id, lang, AMARA_TEAM)
            #assign_url = "%s/%s/videos/%s/collaborations/%s/join/subtitler/" % \
            #    (amara.AMARA_BASE_URL, lang, amara_id, lang)
            #review_url = "%s/%s/videos/%s/collaborations/%s/join/reviewer/" % \
            #    (amara.AMARA_BASE_URL, lang, amara_id, lang)

            video_url = "%s/%s/videos/%s/%s/?team=%s" % \
                (amara.AMARA_BASE_URL, lang, amara_id, lang, AMARA_TEAM)
            return {youtube_id: (amara_id, video_url)}

    return {youtube_id: ("Could not find video on Amara", "", "")}
