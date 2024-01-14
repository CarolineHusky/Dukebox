from flask import Flask,redirect, request
import json
import yt_dlp
from functools import lru_cache
import time
import os.path
import os
import hashlib
import itertools
import random

MUSIC_FOLDER="/home/mii/Music/Music"

app = Flask(__name__)

import mpv

player = None

shuffle = False

@app.route("/style.css")
def style():
    return """
body{
    color: white;
    background: repeating-linear-gradient(
        120deg,
        rgba(32,96,128),
        rgba(16,96,96) 25%,
        rgba(0,80,64), 50%,
        rgba(0,0,0), 55%,
        rgba(24,16,32)
    );
    min-height: 100vh;
    font-family: sans;
    margin-top: 0;
    margin-bottom: 10vh;
    background-attachment: fixed;
    text-shadow: rgba(0,0,0,.5) 2px 3px 2px, black 0px 0px 2px;
}
table {
    width: 100%;
}
header {
    display: flex;
    position: sticky;
    top: 0px;
    margin-left: -8px;
    margin-right: -8px;
    padding: 8px;
    background: linear-gradient(
        rgba(53,57,61, .75),
        rgba(120,123,125, .75), 50%,
        rgba(0,0,0, .25), 51%,
        rgba(64,64,64, .5)
    );
    boder: 1px solid rgba(0,0,0,.25);
    box-shadow: 0 0 10px 1px rgba(255,255,255,.25);
    backdrop-filter: blur(15px) saturate(200%);
}
main > a:first-child{
    display: inline-block;
    padding-top: 8px;
}
footer {
    position: fixed;
    bottom: 0px;
    left: 0;
    right: 0;
    background-color: black;
    margin-left: -8px;
    margin-right: -8px;
    padding: 8px;
    background: linear-gradient(
        rgba(24,24,24, .75),
        rgba(32,32,32, .50), 50%,
        rgba(0,0,0, .75), 75%,
        rgba(16,16,16, .75)
    );
    border: 1px solid rgba(128,128,128,.25);
    box-shadow: 0 0 10px 1px rgba(0,0,0,.25);
    backdrop-filter: blur(15px) saturate(400%);
    text-shadow: rgba(0,0,0,.5) 2px 3px 2px, black 0px 0px 2px;
}
button {
    background: linear-gradient(
        rgba(24,24,24, .75),
        rgba(32,32,32, .50), 50%,
        rgba(0,0,0, .75), 75%,
        rgba(16,16,16, .75)
    );
    border: 1px solid rgba(128,128,128,.25);
    box-shadow: 0 0 10px 1px rgba(0,0,0,.25);
    color: white;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
    text-shadow: rgba(0,0,0,.5) 2px 3px 2px, black 0px 0px 2px;
}
header > * {
    font-size: 1.1em;
}
input#search {
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
    border: 1px solid rgba(128,128,128,.25);
    box-shadow: 0 0 10px 1px rgba(0,0,0,.25);
    background: linear-gradient(
        rgba(255,255,225, .75),
        rgba(240,240,240, .50), 50%,
        rgba(192,192,192, .75), 75%,
        rgba(224,224,224, .75)
    );
    padding-left: 12px;
    padding-right: 12px;
    letter-spacing: 2px;
    font-weight: bold;
    text-shadow: white 0px 0px 1px, white 0px 0px 3px;
    text-transform: uppercase;
}
input[type="range"] {
  -webkit-appearance: none;
  appearance: none;
  background: transparent;
  cursor: none;
  width: 15rem;
}
input[type="range"]::-webkit-slider-runnable-track {
    background: linear-gradient(
        rgba(255,255,225, .75),
        rgba(192,192,192, .50), 50%,
        rgba(64,64,64, .75), 75%,
        rgba(128,128,128, .75)
    );
    height: 0.75em;
  border-radius: 4px;
    border: 1px solid rgba(0,0,0,.25);
    box-shadow: 0 0 10px 1px rgba(0,0,0,.25);
}
input[type="range"]::-moz-range-track {
    background: linear-gradient(
        rgba(255,255,225, .75),
        rgba(192,192,192, .50), 50%,
        rgba(64,64,64, .75), 75%,
        rgba(128,128,128, .75)
    );
    height: 0.75em;
    border-radius: 4px;
    border: 1px solid rgba(0,0,0,.25);
    box-shadow: 0 0 10px 1px rgba(0,0,0,.25);
}
input[type="range"]::-moz-range-progress {
    background: linear-gradient(
        rgba(0,255,0, .75),
        rgba(0,224,0, .50), 50%,
        rgba(0,128,0, .75), 75%,
        rgba(0,192,0, .75)
    );
    height: 0.75em;
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
    border: 1px solid rgba(128,128,128,.25);
    box-shadow: 0 0 10px 1px rgba(0,0,0,.25);
}
input[type="range"]::-moz-range-thumb {
    opacity: 0;
}
footer {
    padding-bottom: 16px;
}
footer > * {
    margin: 8px;
}
header > *{
    flex-grow: 1;
}
header > #searchbutton{
    flex-grow: 0.25;
}
footer > div{
    display: flex;
    margin-top: 8px;
    margin-bottom: 8px;
}
footer > div > *{
    flex-grow: 1;
}
footer > div > #resume{
    flex-grow: 0.25;
}
a {
    color: white;
    text-decoration-color: #777;
}
#oopnext{
    max-height: 50vh;
    overflow-y: auto;
}
#oopnext>div{
    display: flex;
    flex-wrap: wrap;
    margin-left: -8px;
    margin-right: -8px;
}
img {
    width: 100%;
}
section.videogrid{
    display: flex;
    flex-wrap: wrap;
    margin-top: 1em;
    margin-left: -8px;
    margin-right: -8px;
}
section.videogrid>figure, #oopnext>div>figure{
    flex-grow: 1;
    max-width: 480px;
    flex-basis: 320px;
    margin: 0;
    margin-bottom: 16px;
}
figure details summary{
    padding: 4px;
    background: linear-gradient(
        rgba(24,24,24, .75),
        rgba(32,32,32, .50), 50%,
        rgba(0,0,0, .75), 75%,
        rgba(16,16,16, .75)
    );
    border: 1px solid rgba(128,128,128,.25);
    box-shadow: 0 0 10px 1px rgba(0,0,0,.25);
    color: white;
    border-bottom-left-radius: 4px;
    border-bottom-right-radius: 4px;
    text-shadow: rgba(0,0,0,.5) 2px 3px 2px, black 0px 0px 2px;
}
figure details span{
    display: block;
    padding: 6px;
    height: 100px;
    overflow-y: scroll;
    background: linear-gradient(
        rgba(0,0,0,.75),
        rgba(32,32,32, .25) 10%,
        rgba(32,32,32, .50), 75%,
        rgba(16,16,16, .75) 90%,
        rgba(0,0,0, .75)
    );
    margin-top: -3px;
    border: 1px solid rgba(128,128,128,.25);
    box-shadow: 0 0 10px 1px rgba(0,0,0,.25);
    backdrop-filter: blur(15px) saturate(400%);
    text-shadow: rgba(0,0,0,.5) 2px 3px 2px, black 0px 0px 2px;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
}
footer details .song{
    margin-left: 8px;
    margin-right: 8px;
    padding-top: 8px;
    padding-bottom: 12px;
    display: block;
}
small{
    opacity: 0.6;
}
    """.replace('\n','')


def is_in_playlist(video):
    global player
    if player == None:
        return None
    videopath="https://youtu.be/"+video
    playlist=list(map(lambda x: x['filename'],itertools.dropwhile(lambda x: 'current' not in x or not x['current'], player.playlist)))
    if videopath in playlist:
        return playlist.index(videopath)
    if video in playlist:
        return playlist.index(video)
    return None

def generate_thumbnail(info, uploader=None):
    if not 'thumbnails' in info:
        return ""
    if 'fulltitle' in info:
        title=info['fulltitle']
    else:
        title=info['title']
    if uploader is not None:
        uploader=info['uploader']
    imgtag='<img alt="thumbnail for &quot;%s&quot; by &quot;%s&quot;"'%(title,uploader)
    srcset=[]
    knownwidths=[]
    for ele in info['thumbnails']:
        if not 'width' in ele or ele['width'] in knownwidths:
            continue
        knownwidths.append(ele['width'])
        srcset.append("%s %dw"%(ele['url'],ele['width']))
    src=sorted(info['thumbnails'], key=lambda k: -k['preference'] if 'preference' in k else -99999)[0]['url']
    imgtag+=' src="%s"'%src
    if len(srcset)>1:
        imgtag+=' srcset="%s"'%(",".join(srcset))
    imgtag+='>'
    return imgtag

def generate_description(info, uploader=None, clickable=False):
    if 'fulltitle' in info:
        title=info['fulltitle']
    else:
        title=info['title']
    html="<figure>"
    if clickable:
        html+="<a href=\"play/%s\">"%info['id']
    html+=generate_thumbnail(info,uploader)
    if clickable:
        html+="</a>"
    html+="<figcaption>"
    if not info['id'].startswith("/"):
        html+="<details data-source=\"/describe/%s\"><summary>"%info['id']
    else:
        html+="<a class='song' href=\"/music/play/%s\">"%info['title']
    if is_in_playlist(info['id']) is not None:
        index = is_in_playlist(info['id'])
        if index==0:
            if player.pause:
                html+='[Paused] '
            else:
                html+='[Playing] '
        elif index==1:
            html+='[Next] '
        elif index==2:
            html+='[2nd next] '
        elif index==3:
            html+='[3rd next] '
        else:
            html+='[%dth next] '%index
    elif os.path.exists('cache/watched/%s.watched'%info['id']):
        html+='[Watched] '
    elif os.path.exists('cache/started/%s.started'%info['id']):
        html+='[Started] '
    html+="<strong>%s</strong>"%title
    if uploader is None:
        if 'uploader_id' in info and info['uploader_id'] is not None:
            html+=' <a href="/user/%s">%s</a>'%(info['uploader_id'][1:],info['uploader'])
        elif 'channel_id' in info and info['channel_id'] is not None:
            html+=' <a href="/channel/%s">%s</a>'%(info['channel_id'],info['uploader'])
    if not info['id'].startswith("/"):
        html+="</summary>"
        html+="<span>"
        if 'description' in info and info['description'] is not None:
            html+=info['description'].replace('\n','<br/>')
        html+="</span>"
        html+="</details>"
    else:
        html+='</a>'
    html+="</figcaption></figure>"
    return html

def generate_channelpage(info, endless=False):
    html="<h1>%s</h1>"%(info['channel'])

    subscriptions = request.cookies.get('subscriptions')
    if subscriptions is not None and info['uploader_id'][1:].lower().replace(' ','') in subscriptions.split(','):
        html+="<a href='subscribe'>Unsubscribe</a>"
    else:
        html+="<a href='subscribe'>Subscribe</a>"
    html+=" - <a href='/'>Home</a>"
    html+="<p>"
    html+=info['description'].replace('\n','<br/>')
    html+="</p>"
    html+="<section class='videogrid'>"
    for ele in info['entries']:
        html+=generate_description(ele, uploader=info['channel'], clickable=True)
    if not endless and len(info['entries'])>=36:
        html+="<h2 style='margin:auto;'><a href='endless'>Load all...</a></h2>"
    html+="</section>"
    return html

def generate_searchpage(info,searchterm, songsearch):
    html="<h1><small>Searched for: </small>%s</h1>"%(searchterm)
    if len(songsearch)>0:
        html+="<h2><small>From the </small>local music library:</h2>"
        html+="<table><tbody>"
        html+="<tr><th></th><th>Artist</th><th colspan=\"2\">Album</th><th>Song</th></tr>"
        for song in songsearch:
            html+=generate_music_row(*song)
        html+="</tbody></table>"
        html+="<h2><small>From </small>YouTube:</h2>"
    html+="<section class='videogrid'>"
    for ele in info['entries']:
        html+=generate_description(ele, clickable=True)
    html+="</section>"
    return html


def get_info(videourl):
    if videourl.startswith(MUSIC_FOLDER+"/"):
        name = videourl.split("/")[-1]
        return {'title': name, 'id': videourl}
    videoid=videourl.lstrip("https://www.youtube.com/watch?v=")
    info = get_ytdlp_info(videourl, "video/%s.json"%videoid)
    return info

def generate_page(page, title):
    html="<html><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><link rel=\"stylesheet\" href=\"/style.css\"><title>%s</title>"%title
    if player is not None and not player.pause and player.time_remaining is not None:
        html+="<meta http-equiv=\"refresh\" content=\"%d\">"%(player.time_remaining+random.randint(5,10))
    html+="</head><body>"
    html+="<header><input id='search'/><button id='searchbutton'>Search YT</button>"
    html+="</header>"
    html+="<main>"
    html+=page
    html+="</main>"
    if player is not None:
        playlist=list(map(lambda x: get_info(x['filename']),itertools.dropwhile(lambda x: 'current' not in x or not x['current'], player.playlist)))
        if len(playlist)>0:
            html+="<footer><div>"
            html+="<details id='oopnext'><summary>Currently playing"
            if len(playlist)>1:
                html+=" (%d)"%len(playlist)
            html+=": <strong>"+playlist[0]['title']+"</strong></summary>"
            html+=generate_description(playlist[0], clickable=True)
            if len(playlist)>1:
                html+="Up next: <div>"
                for ele in playlist[1:]:
                    html+=generate_description(ele, clickable=True)
                html+="</div>"
            html+="</details>"
            html+="</div><div>"
            if player.pause:
                html+="<a id='pause' href='pause'>Resume</a>"
            else:
                html+="<a id='resume' href='pause'>Pause</a>"
            html+="<input type='range' id='volume' min='0' max='100' value='%d'/>"%player.volume
            html+="</div></footer>"
    html+="""
<script>
var details = document.querySelectorAll("details");
details.forEach((detail) => {
    detail.addEventListener("toggle", function(event) {
    if(detail.dataset.source)
        fetch(detail.dataset.source).then((response) => response.text()).then((text) => {
            detail.lastChild.innerHTML = text;
            detail.removeAttribute('data-source');
        });
    });
});
var search = document.getElementById('search');
var searchbutton = document.getElementById('searchbutton');
searchbutton.addEventListener("click", function(event) {
    if(search.value){
        window.location.href = '/search/'+ search.value;
    }
});
var volume = document.getElementById('volume');
volume.addEventListener("change", function(event) {
    fetch('/volume/'+volume.value).then((response) => {});
});
</script>
""".replace('\n','')
    html+="</body></html>"
    return html


def _get_ytdlp_info(url, endless=False):
    if endless:
        ydl_opts = {'extract_flat': 'in_playlist' }
    else:
        ydl_opts = {'extract_flat': 'in_playlist', 'playlistend': 36  }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return info

def get_ytdlp_info(url, cache, endless=False):
    info = None
    os.makedirs("cache/"+cache.split('/')[0], exist_ok=True)
    if os.path.exists("cache/"+cache):
        with(open("cache/"+cache) as f):
            info=json.load(f)
    if info is None or ttl()>info['ttl'] or info['endless']!=endless:
        info=_get_ytdlp_info(url, endless)
        info['ttl']=ttl()+60*15
        info['endless']=endless
        with(open("cache/"+cache, "w") as f):
            json.dump(info,f, indent="\t")
    return info

def mpv_handle_start(event):
    os.makedirs("cache/started", exist_ok=True)
    filename = list(filter(lambda x: x['id']==event.data.playlist_entry_id, player.playlist))[0]['filename']
    filename=filename.split('/')[-1]
    open('cache/started/%s.started'%filename, 'a').close()

def mpv_handle_end(event):
    if event.data.reason==0: #EOF
        os.makedirs("cache/watched", exist_ok=True)
        filename = list(filter(lambda x: x['id']==event.data.playlist_entry_id, player.playlist))[0]['filename']
        filename=filename.split('/')[-1]
        open('cache/watched/%s.watched'%filename, 'a').close()
        if player.playlist[-1]['id']==event.data.playlist_entry_id and shuffle and not player.pause:
            played_files=set(os.listdir('cache/started'))
            tracks = list(map(lambda x: x[0],list_tracks()))
            random.shuffle(tracks)
            for ele in tracks:
                if not os.path.exists('cache/started/%s.started'%ele):
                    player.play(find_track(ele))
                    break
            else:
                for ele in tracks:
                    os.remove('cache/started/%s.started'%ele)
                player.play(find_track(ele))


def mpv_handle_play(video):
    global player
    if video is None:
        return
    if player is None:
        player=mpv.MPV(ytdl=True)

    @player.event_callback('start-file')
    def start(event):
        mpv_handle_start(event)

    @player.event_callback('end-file')
    def end(event):
        mpv_handle_end(event)

    videopath="https://youtu.be/"+video
    playlist=list(map(lambda x: x['filename'],player.playlist))
    if len(player.playlist) == 0:
        player.play(videopath)
    elif is_in_playlist(video) is not None:
        player.playlist_remove(playlist.index(videopath))
    elif not any(filter(lambda x:'current' in x and x['current'], player.playlist)):
        player.play(path)
    else:
        player.playlist_append(videopath)

def mpv_handle_play_file(path):
    global player
    if path is None:
        return
    if player is None:
        player=mpv.MPV(ytdl=True)

    @player.event_callback('start-file')
    def start(event):
        mpv_handle_start(event)

    @player.event_callback('end-file')
    def end(event):
        mpv_handle_end(event)

    playlist=list(map(lambda x: x['filename'],player.playlist))
    if len(player.playlist) == 0:
        player.play(path)
    elif is_in_playlist(path) is not None:
        player.playlist_remove(playlist.index(path))
    elif not any(filter(lambda x:'current' in x and x['current'], player.playlist)):
        player.play(path)
    else:
        player.playlist_append(path)

def mpv_handle_pause():
    global player
    if player is None:
        return
    player.pause = not player.pause

def list_tracks(prefix="", folder=MUSIC_FOLDER, excludius=False):
    for filename in os.listdir(folder):
        if not "." in filename:
            if prefix=="":
                for ele in list_tracks(filename+" - ",folder+"/"+filename):
                    yield ele
            else:
                for ele in list_tracks(prefix+filename+" - ",folder+"/"+filename):
                    yield ele
            continue
        if excludius:
            continue
        name = ".".join(filename.split('.')[:-1])
        if not name.startswith(prefix):
            name = prefix+name
        nameparts = name.split(" - ")
        artist = None
        album = None
        number = None
        if len(nameparts)==3:
            album = nameparts[1].strip()
        if len(nameparts)==4:
            album = nameparts[1].strip()
            number = nameparts[2].strip()
        if len(nameparts)>4:
            album = nameparts[1].strip()
            number = nameparts[2].strip() + nameparts[-2].strip()
        if len(nameparts)>=2:
            artist = nameparts[0].strip()
        track = nameparts[-1].strip()
        if "(" in track:
            track=track[:track.index("(")]+"<small>"+track[track.index("("):]+"</small>"
        yield (filename, artist, album, number, track)

def find_track(filename):
    for root, dirs, files in os.walk(MUSIC_FOLDER, topdown=False):
        if filename in files:
            return root+"/"+filename


def generate_music_row(filename, artist, album, number, track, trackfirst=False):
    html="<tr>"
    html+="<td>"
    if is_in_playlist(filename) is not None:
        index = is_in_playlist(filename)
        if index==0:
            if player.pause:
                html+='[Paused] '
            else:
                html+='[Playing] '
        elif index==1:
            html+='[Next] '
        elif index==2:
            html+='[2nd next] '
        elif index==3:
            html+='[3rd next] '
        else:
            html+='[%dth next] '%index
    html+="</td>"
    if trackfirst or trackfirst is None:
        html+="<td><a href=\"play/%s\">%s</a></td>"%(filename,track)
    if trackfirst is not None:
        if artist is None:
            html+="<td></td>"
        else:
            html+="<td><a href=\"/music/artist/%s/\">%s</a></td>"%(artist, artist)
        if not trackfirst:
            if album is None:
                if number is None:
                    html+="<td colspan='2'></td>"
                else:
                    html+="<td></td><td>%s</td>"%number
            else:
                if number is None:
                    html+="<td colspan='2'>%s</td>"%album
                else:
                    html+="<td>%s</td><td>%s</td>"%(album, number)
            html+="<td><a href='/music/play/%s'>%s</a></td>"%(filename,track)
    html+="</tr>"
    return html

def generate_shuffle_button():
    if shuffle:
        return "<a href='/music/shuffle'>Turn shuffle off</a>"
    return "<a href='/music/shuffle'>Shuffle</a>"

def generate_music_page():
    html=generate_shuffle_button()
    html+=" - <a href='/'>Home</a>"
    html+="<table><thead><tr><th></th><th>Track</th><th><a href='/music/artist'>Artist</a></th>"
    #html+="<th colspan='2'><a href='/music/album'>Album</a></th>"
    html+="</tr></thead><tbody>"
    for filename, artist, album, number, track in sorted(list_tracks(), key=lambda x: x[-1]):
        html+=generate_music_row(filename, artist, album, number, track, trackfirst=True)
    html+="</tbody></table>"
    return html

def generate_artists_page():
    html="<a href='/music/'>Back to music...</a>"
    html+="<table><tbody>"
    for ele in sorted(filter(lambda x: x is not None,set(map(lambda x: x[1], list_tracks())))):
        html+="<tr><td><a href=\"%s/\">%s</a></td></tr>"%(ele,ele)
    html+="</tbody></table>"
    return html

def generate_artist_page(artist):
    albums = sorted(filter(lambda x: x is not None,set(map(lambda x: x[2], filter(lambda x: x[1]==artist, list_tracks())))))
    html=""
    html+="<a href='/music/artist/'>Back to artists...</a>"
    if len(albums)>0:
        html+="<h1><small>Albums by </small>%s</h1>"%artist
        html+="<table><tbody>"
        for ele in albums:
            html+="<tr><td><a href=\"playalbum/%s\"><h2>%s</h2></a>"%(ele, ele)
            songs = sorted(filter(lambda x: x[1]==artist and x[2]==ele, list_tracks()), key=lambda x: x[-2] if x[-2] is not None else x[-1])
            html+="<table><tbody>"
            for song in songs:
                html+=generate_music_row(*song, trackfirst=None)
            html+="</tbody></table>"
            html+="</td></tr>"
        html+="</tbody></table>"
    songs = sorted(filter(lambda x: x[1]==artist and x[2] is None, list_tracks()), key=lambda x: x[-1])
    if len(songs)>0:
        if len(albums)>0:
            html+="<hr/>"
        html+="<h1><small>Songs by </small>%s</h1>"%artist
        html+="<table><tbody>"
        for song in songs:
            html+=generate_music_row(*song, trackfirst=None)
        html+="</tbody></table>"
    return html

@app.route("/music/")
def music():
    return generate_page(generate_music_page(), "Music")

@app.route("/music/shuffle")
def music_shuffle():
    global shuffle
    shuffle = not shuffle
    global player
    if player is None:
        player=mpv.MPV(ytdl=True)

    @player.event_callback('start-file')
    def start(event):
        mpv_handle_start(event)

    @player.event_callback('end-file')
    def end(event):
        mpv_handle_end(event)
    if not any(filter(lambda x:'current' in x and x['current'], player.playlist)):
        played_files=set(os.listdir('cache/started'))
        tracks = list(map(lambda x: x[0],list_tracks()))
        random.shuffle(tracks)
        for ele in tracks:
            if not os.path.exists('cache/started/%s.started'%ele):
                player.play(find_track(ele))
                break
        else:
            for ele in tracks:
                os.remove('cache/started/%s.started'%ele)
            player.play(find_track(ele))
    return redirect("/music")

@app.route("/music/artist/")
def music_artists():
    return generate_page(generate_artists_page(), "Artists")

@app.route("/music/artist/<name>/")
def music_artist(name):
    return generate_page(generate_artist_page(name), name)

@app.route("/music/play/<name>")
def music_play(name):
    mpv_handle_play_file(find_track(name))
    return redirect('/music')

@app.route("/music/artist/<artist>/play/<name>")
def music_artist_play(artist,name):
    mpv_handle_play_file(find_track(name))
    return redirect('/music/artist/'+artist)

@app.route("/music/artist/<artist>/pause")
def music_artist_pause(artist):
    mpv_handle_pause()
    return redirect('/music/artist/'+artist)

@app.route("/music/artist/<artist>/playalbum/<name>")
def music_album_play(artist,name):
    for ele in sorted(filter(lambda x: x[1]==artist and x[2]==name, list_tracks()), key=lambda x: x[-2] if x[-2] is not None else x[-1]):
        mpv_handle_play_file(find_track(ele[0]))
    return redirect('/music/artist/'+artist)

@app.route("/music/pause")
def music_pause():
    mpv_handle_pause()
    return redirect('/music')


@app.route("/user/<name>/pause")
def user_pause(name):
    mpv_handle_pause()
    return redirect('/user/%s/'%name)

@app.route("/user/<name>/subscribe")
def user_subscribe(name):
    subscriptions = request.cookies.get('subscriptions')
    subscriptions = set(subscriptions.lower().split(',')) if subscriptions is not None else set()
    if name.lower().replace(' ','') in subscriptions:
        subscriptions.remove(name.lower().replace(' ',''))
    else:
        subscriptions.add(name.lower())
    result = redirect('/user/%s/'%name)
    result.set_cookie('subscriptions', ",".join(sorted(subscriptions)), max_age=34560000)
    return result

@app.route("/play/<video>")
@app.route("/<int:index>/play/<video>")
def home_play(video, index=0):
    mpv_handle_play(video)
    return redirect('/')

@app.route("/user/<name>/play/<video>")
def user_play(name, video):
    mpv_handle_play(video)
    return redirect('/user/%s/'%name)

@app.route("/user/<name>/endless/play/<video>")
def user_play_endless(name, video):
    mpv_handle_play(video)
    return redirect('/user/%s/endless/'%name)

@app.route("/user/<name>/")
def user(name):
    if '..' in name or '/' in name:
        return
    name=name.lower()
    info = get_ytdlp_info("https://www.youtube.com/@%s/videos"%name, "user/%s.json"%name)
    return generate_page(generate_channelpage(info), info['channel'])

@app.route("/user/<name>/endless")
def user_endless(name):
    if '..' in name or '/' in name:
        return
    name=name.lower()
    info = get_ytdlp_info("https://www.youtube.com/@%s/videos"%name, "user/%s.json"%name, True)
    return generate_page(generate_channelpage(info, True), info['channel'])

@app.route("/channel/<name>/play/<video>")
def channel_play(name, video):
    mpv_handle_play(video)
    return redirect('/channel/%s/'%name)

@app.route("/channel/<name>/pause")
def channel_pause(name):
    mpv_handle_pause()
    return redirect('/channel/%s/'%name)

@app.route("/pause")
@app.route("/<int:index>/pause")
def home_pause(index=0):
    mpv_handle_pause()
    return redirect('/')

@app.route("/channel/<name>/")
def channel(name, videoid=None):
    if '..' in name or '/' in name:
        return
    mpv_handle_play(videoid)
    info = get_ytdlp_info("https://www.youtube.com/channel/%s/videos"%name, "channel/%s.json"%name)
    return generate_page(generate_channelpage(info), info['channel'])

@app.route("/search/<name>/play/<video>")
def search_play(name, video):
    mpv_handle_play(video)
    return redirect('/search/%s/'%name)

@app.route("/search/<name>/pause")
def search_pause(name):
    mpv_handle_pause()
    return redirect('/search/%s/'%name)

@app.route("/search/<name>/")
def search(name):
    if '..' in name or '/' in name:
        return
    hashname = int.from_bytes(hashlib.sha256(name.encode('utf-8')).digest()[:8], byteorder='big', signed=True)
    info = get_ytdlp_info("ytsearch12:%s"%name, "search/%16x.json"%hashname)
    songsearch = sorted(set(filter(lambda x: (x[1] is not None and name.lower() in x[1].lower()) or (x[2] is not None and name.lower() in x[2].lower()) or name.lower() in x[-1].lower(), list_tracks())), key=lambda x: list(map(lambda x: "" if x is None else x, x[1:])))
    return generate_page(generate_searchpage(info, name, songsearch), "Searched for: %s"%name)

def generate_home_page(index):
    subscriptions = request.cookies.get('subscriptions')
    windex=int(index)+1
    index=windex*3
    html='<h1>Welcome to Mii\'s Dukebox!</h1>'
    html+='<a href="/music/">Local music</a>'
    if subscriptions is not None:
        subscriptions = set(sorted(subscriptions.split(',')))
        ydl_opts = {'extract_flat': 'in_playlist', 'playlist_items': '1:%d'%index }
        pages = []
        for i in range(index):
            pages.append([])
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for user in subscriptions:
                if user=='':
                    continue
                info = ydl.extract_info("https://www.youtube.com/@%s/videos"%user, download=False)
                for i, ment in enumerate(info['entries']):
                    ment['channel']=info['channel']
                    ment['channel_id']=info['channel_id']
                    ment['uploader']=info['uploader']
                    ment['uploader_id']=info['uploader_id']

                    pages[i].append(ment)
        html+='<section class="videogrid">'
        for page in pages:
            page=sorted(page, key=lambda info: info['uploader_id'])
            page=sorted(page, key=lambda info: os.path.exists('cache/started/%s.started'%info['id']))
            for info in page:
                html+=generate_description(info, clickable=True)
        html+="</section>"
        html+="<h2 style='margin:auto;'><a href='%d'>Load more...</a></h2>"%windex
    return html

@app.route("/")
@app.route("/<int:index>")
def home(index=0):
    if index>99:
        index=0
    return generate_page(generate_home_page(index), 'Mii\'s Dukebox!')

@app.route("/describe/<videoid>/")
def describe(videoid):
    if '..' in videoid or '/' in videoid:
        return
    info = get_ytdlp_info("https://www.youtube.com/watch?v=%s"%videoid, "video/%s.json"%videoid)
    return info['description'].replace('\n','<br/>')

@app.route("/volume/<int:value>")
def volume(value):
    if player is not None:
        player.volume=value
    return ""

def ttl(seconds=60*20):
    """Return the same value withing `seconds` time period"""
    return round(time.time())

import socket
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == "__main__":
    ip=get_ip()
    print("connect to %s:5968"%ip)
    app.run(host=ip, port=5968)
