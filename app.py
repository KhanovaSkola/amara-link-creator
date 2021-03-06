#!/usr/bin/env python3

import re
# Run Flask server in debug mode
# export FLASK_ENV=development
# python -m flask run
from flask import Flask, render_template, request
from kstools.api.amara_api import Amara
app = Flask(__name__)

AMARA_TEAM = "khan-academy"
AMARA_USERNAME = 'danekhollas'
AMARA_UI_LANG = 'en'

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/<lang>/<youtube_id>')
def get_amara_link(lang, youtube_id):
    """Polls Amara API for AmaraID for a given YouTubeID
    and constructs a link to the Amara subtitling editor"""
    # TODO: manage multiple YouTubeIDs per request

    public = request.args.get('public', 0, type=bool)
    if public:
        team = None
    else:
        team = AMARA_TEAM

    # Amara URLs are case sensitive
    lang = lang.lower()

    create_requests = False
    # List of languages for which we allow to create new subtitle requests
    # on Team Amara
    allowed_languages = ('az', 'bg', 'cs', 'de', 'hu', 'ky', 'kk', 'lv', 'pl', 'ro')
    if lang in allowed_languages:
        create_requests = request.args.get('create-requests', 0, type=bool)

    ytid_regex = r'^[a-zA-Z0-9_-]{11}$'
    if not re.fullmatch(ytid_regex, youtube_id):
        return {youtube_id: ("invalid YouTube ID", "", "")}

    video_url = "https://youtube.com/watch?v=%s" % youtube_id
    amara = Amara(AMARA_USERNAME)
    amara_response = amara.check_video(video_url, team)

    # Create subtitle request if it does not exist
    if create_requests and not public:
        amara_id = amara_response['objects'][0]['id']
        r = amara.list_subtitle_requests(amara_id, lang, AMARA_TEAM)
        if r['meta']['total_count'] == 0:
            r = amara.create_subtitle_request(amara_id, lang, AMARA_TEAM)
            # TODO: Check the response (should be 201)

    # If video does not exist on Amara and we want public link
    # we need to create it first
    if public and amara_response['meta']['total_count'] == 0:
        amara_response = amara.add_video(video_url, lang)
        if not amara_response:
            return {youtube_id: ("Could not add video to Amara", "")}

        amara_id = amara_response['id']
        editor_url = "%s/%s/subtitles/editor/%s/%s/" % \
            (amara.AMARA_BASE_URL, AMARA_UI_LANG, amara_id, lang)
        return {youtube_id: (amara_id, editor_url)}

    for r in amara_response['objects']:
        if not public and r['team'] == AMARA_TEAM:
            amara_id = r['id']
            video_url = "%s/%s/videos/%s/%s/?team=%s" % \
                (amara.AMARA_BASE_URL, AMARA_UI_LANG, amara_id, lang, team)
            return {youtube_id: (amara_id, video_url)}

        elif public and r['team'] is None:
            amara_id = r['id']
            editor_url = "%s/%s/subtitles/editor/%s/%s/" % \
                (amara.AMARA_BASE_URL, AMARA_UI_LANG, amara_id, lang)
            return {youtube_id: (amara_id, editor_url)}

    return {youtube_id: ("Could not find video on Amara", "")}
