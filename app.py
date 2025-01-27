from flask import Flask,redirect, request, send_from_directory, url_for
import json
import yt_dlp
from yt_dlp import extractor
from functools import lru_cache
import time
import os.path
import os
import hashlib
import itertools
import random
import urllib, hashlib, re
import urllib.parse
import threading
import logging
import sys
import psutil
import traceback
import base64
import functools
from PIL import Image
import configparser
config=configparser.ConfigParser()
config.optionxform=str
config.read('config.ini')

import datetime
start_time=datetime.datetime.now().timestamp()

blank=False
if blank:
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

MUSIC_FOLDER=os.path.expanduser(config["Folders"]["Music"])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join("cache","telegram")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mkv', 'webp', 'webm', 'mp3'}

import mpv

player = None

shuffle = False

@app.route("/style.css")
def style():
    return """
body{
    color: white;
    background-color: black;
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
header > form {
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
main{
    padding-bottom: 25vh;
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
header > form > * {
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
input#time{
    width: 100%;
    margin-top: 1em;
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
input[type="range"]#time::-moz-range-progress {
    background: linear-gradient(
        rgba(0,128,255, .75),
        rgba(0,112,224, .50), 50%,
        rgba(0,64,128, .75), 75%,
        rgba(0,96,192, .75)
    );
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
header > form > * {
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
    display:block;
    overflow-y: hidden;
    display: flex;
    flex-wrap: wrap;
    margin-top: 1em;
    margin-left: -8px;
    margin-right: -8px;
}
section.videogrid>figure, #oopnext>div>figure{
    flex-grow: 1;
    max-width: 479px;
    flex-basis: 240px;
    margin: 0;
    margin-bottom: 16px;
}
figure details summary, .fakesummary{
    display: block;
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
figure details span:not(.fakesummary){
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
figure.notyt figcaption{
    margin-left: 8px;
    margin-right: 8px;
    padding-top: 8px;
    padding-bottom: 12px;
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


subtitle_font={
" ": [
"    ",
"    ",
"    ",
"    "],
"a": [
"     ",
" ──┐ ",
"┌──┤ ",
"└──┴ "],
"b": [
"┬    ",
"├──┐ ",
"│  │ ",
"┴──┘ "],
"c": [
"     ",
"┌──┐ ",
"│    ",
"└──┘ "],
"d": [
"   ┬ ",
"┌──┤ ",
"│  │ ",
"└──┴ "],
"e": [
"     ",
"┌──┐ ",
"├──┘ ",
"└──  "],
"f": [
"    ",
"┌── ",
"├── ",
"┴   "],
"g": [
"     ",
"┌──┐ ",
"│ ─┐ ",
"└──┘ "],
"h": [
"┬    ",
"├──┐ ",
"│  │ ",
"┴  ┴ "],
"i": [
"o  ",
"┐  ",
"│  ",
"┴  "],
"j": [
"  o ",
"  ┐ ",
"  │ ",
"└─┘ "],
"k": [
"┬     ",
"│ ┌─┘ ",
"│─┤   ",
"┴ └─┐ "],
"l": [
" ┐  ",
" │  ",
" │  ",
" ┴  "],
"m": [
"      ",
"┬─┬─┐ ",
"│ │ │ ",
"┴   ┴ "],
"n": [
"     ",
"┬──┐ ",
"│  │ ",
"┴  ┴ "],
"o": [
"     ",
"┌──┐ ",
"│  │ ",
"└──┘ "],
"p": [
"     ",
"┬──┐ ",
"├──┘ ",
"┴    "],
"q": [
"     ",
"┌──┬ ",
"└──┤ ",
"   ┴ "],
"r": [
"    ",
"┬─┐ ",
"│   ",
"┴   "],
"s": [
"    ",
"┌─┐ ",
"└─┐ ",
"└─┘ "],
"t": [
"┐   ",
"├─  ",
"│   ",
"└─┘ "],
"u": [
"     ",
"┐  ┐ ",
"│  │ ",
"└──┴ "],
"v": [
"     ",
"┌  ┐ ",
"└┐┌┘ ",
" └┘  "],
"w": [
"      ",
"┐   ┐ ",
"│ │ │ ",
"┴─┴─┘ "],
"x": [
"    ",
"\\ / ",
" X  ",
"/ \\ "],
"y": [
"     ",
"┬  ┬ ",
"└──┤ ",
" ──┘ "],
"z": [
"     ",
" ──┬ ",
" ┌─┘ ",
" ┴── "],
"'": [
"  ",
"┘ ",
"  ",
"  "],
",": [
"  ",
"  ",
"  ",
"┘ "],
".": [
"  ",
"  ",
"  ",
"o "],
"!": [
"│ ",
"│ ",
"┴ ",
"o ",],
"?": [
"┌─┐",
" ┌┘",
" ┴ ",
" o "],
";": [
"  ",
"o ",
"  ",
"┘ ",],
"-": [
"  ",
"  ",
"─ ",
"  "],
":": [
"  ",
"o ",
"  ",
"o "],
"(": [
"┌─ ",
"│  ",
"│  ",
"└─ "],
"[": [
"┌─ ",
"│  ",
"│  ",
"└─ "],
")": [
"─┐ ",
" │ ",
" │ ",
"─┘ "],
"]": [
"─┐ ",
" │ ",
" │ ",
"─┘ "],
}

widefont={"│": "║", "┌":"╓", "┐": "╖", "└":"╙", "┘": "╜", "├": "╟", "┤": "╢", "┬": "╥", "┴":"╨", "┼":"╬", "/":"╱", "\\": "╲", "X":"╳"}

def print_large(text):
    text=text.lower()
    rows=[]
    for i in range(4):
        rows.append("")
    for letter in text:
        if letter=="\n":
            for i in range(4):
                rows.append("")
        if letter in subtitle_font:
            for i in range(4):
                line=subtitle_font[letter][i]
                out=""
                for char in line:
                    if char in widefont:
                        out+=widefont[char]
                    else:
                        out+=char
                rows[-4+i]+=out+"\0"
    out=""
    for row in rows:
        if len(row)>240:
            if len(row.replace("\0",""))>240:
                out+=row.replace(" \0","")[:240].center(240)+"\n"
            else:
                out+=row.replace("\0","")[:240].center(240)+"\n"
        else:
            out+=row.replace("\0"," ")[:240].center(240)+"\n"
    print(out+"\n")


home_url = ""
shutdown = False

commands=config["Commands"]

known_forwards={}

def telegram_bot_send_document(chat, filename):
    if chat is None:
        return
    if filename in known_forwards:
        from_chat, message = known_forwards[filename]
        return telegram_bot_execute("forwardMessage", {"chat_id": chat, "from_chat_id": from_chat, "message_id": message})
    import requests
    url="https://api.telegram.org/bot"+config["Telegram"]["Token"]
    if filename.lower().endswith(".mp4") or filename.lower().endswith(".webm"):
        url+="/sendVideo"
        thumbnail_url_alt=os.path.join(os.path.expanduser(config["Folders"]["ThumbnailsAlt"]),get_thumbnail_location(filename))
        thumbnail_url=os.path.join(os.path.expanduser(config["Folders"]["Thumbnails"]),get_thumbnail_location(filename))
        if os.path.exists(thumbnail_url_alt):
            response=requests.post(url, data={'chat_id': chat}, files={'video': open(filename,"rb"), 'thumbnail':open(thumbnail_url_alt,'rb')})
        elif os.path.exists(thumbnail_url):
            response=requests.post(url, data={'chat_id': chat}, files={'video': open(filename,"rb"), 'thumbnail':open(thumbnail_url,'rb')})
        else:
            response=requests.post(url, data={'chat_id': chat}, files={'video': open(filename,"rb")})
        return response
    if filename.lower().endswith(".jpg") or filename.lower().endswith(".png"):
        url+="/sendPhoto"
        response=requests.post(url, data={'chat_id': chat}, files={'photo': open(filename,"rb")})
        return response
    if filename.lower().endswith(".ogg"):
        url+="/sendVoice"
        response=requests.post(url, data={'chat_id': chat}, files={'voice': open(filename,"rb")})
        return response
    url+="/sendDocument"
    response=requests.post(url, data={'chat_id': chat}, files={'document': open(filename,"rb")})
    return response

from enum import Enum

class DenonAvrCommand(Enum):
    CONFIG_BRAND = 1
    CONFIG_LANGUAGE = 2
    CONFIG_FRIENDLYNAME = 3
    CONFIG_ZONEPOWER = 4
    CONFIG_MODELTYPE = 5
    CONFIG_ZONE_RENAME = 6
    CONFIG_SOURCE_LIST = 7
    CONFIG_SETUPLOCK = 8
    CONFIG_BTSINGLEUSED = 9
    CONFIG_SPEAKER_PRESET = 10
    CONFIG_SYSTEM = 11
    VOLUME_MAIN = "MV"
    VOLUME_ZONE2 = "Z2"
    VOLUME_MAIN_FRONT_LEFT = "FL"
    VOLUME_MAIN_FRONT_RIGHT = "FR"
    VOLUME_MAIN_FRONT_CENTER = "C"
    VOLUME_MAIN_SUBWOOFER = "SW"
    VOLUME_MAIN_SURROUND_LEFT = "SL"
    VOLUME_MAIN_SURROUND_RIGHT = "SR"
    VOLUME_MAIN_SOUND_MODE_MOVIE = "MSMOVIE"
    VOLUME_MAIN_SOUND_MODE_MUSIC = "MSMUSIC"
    VOLUME_MAIN_SOUND_MODE_GAME = "MSDIRECR"
    VOLUME_MAIN_SOUND_MODE_PURE = "MSPURE DIRECT"
    VOLUME_MAIN_SOUND_MODE_STEREO = "MSSTEREO"
    VOLUME_MAIN_SOUND_MODE_DOLBY = "MSDOLBY DIGITAL"
    VOLUME_MAIN_SOUND_MODE_DTS = "MSDTS SURROUND"
    VOLUME_ZONE2_FRONT_LEFT = "Z2CVFL "
    VOLUME_ZONE2_FRONT_RIGHT = "Z2CVFR "

class DenonAvrMenuCommand(Enum):
    CONFIG_SETUPMENU = 1
    CONFIG_AUDIO = 2
    CONFIG_VIDEO = 3
    CONFIG_INPUTS = 4
    CONFIG_SPEAKERS = 5
    CONFIG_NETWORK = 6
    CONFIG_HEOSACCOUNT = 7
    CONFIG_GENERAL = 8
    CONFIG_SETUPASSISTANT = 9

def receiver_execute(command_type: DenonAvrCommand, command_data):
    import ssl
    myssl = ssl.create_default_context();
    myssl.check_hostname=False
    myssl.verify_mode=ssl.CERT_NONE
    headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0", "Accept":"text/plain, */*; q=0.01", "Connection":"keep-alive", "Priority":"u=0","Referer":"https://192.168.1.130:10443/general/general.html"}
    if isinstance(command_type.value, int):
        url="https://192.168.1.130:10443/ajax/globals/set_config?type=%d&data=%s"%(command_type.value, command_data.replace(" ", "%20"))
    else:
        url="http://192.168.1.130:8080/goform/formiPhoneAppDirect.xml?%s%s"%(command_type.value,command_data.replace(" ", "%20"))
    print(url)
    try:
        request=urllib.request.Request(url, None, headers)
        return urllib.request.urlopen(request, context=myssl)
    except urllib.error.HTTPError as e:
        print(e)
    return None

def telegram_bot_execute(command, data=None, method=None, snooper=False):
    try:
        headers={}
        if data is not None:
            data=json.dumps(data).encode("utf-8")
            headers["Content-Length"]=len(data)
            headers["Content-Type"]="application/json"
        if snooper:
            url="https://api.telegram.org/bot"+config["Telegram"]["ChatSnooper"]+"/" + command
        else:
            url="https://api.telegram.org/bot"+config["Telegram"]["Token"]+"/" + command
        request=urllib.request.Request(url,data,headers,method=method)
        return json.load(urllib.request.urlopen(request))
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode())  # Read the body of the error response
        if "too big" in body['description']:
            raise ValueError("File too big")
        print("ERROR:")
        print(body)
        print(command, data)
        raise

user_update_lock=None

def telegram_bot_get_updates():
    if not "Telegram" in config:
        return []
    updates=telegram_bot_execute("getUpdates", {"offset": int(config["Telegram"]["LastUpdate"])+1, "allowed_updates": ["message", "callback_query"]})["result"]
    for update in updates:
        if update['update_id']>int(config["Telegram"]["LastUpdate"]):
            config["Telegram"]["LastUpdate"] = str(update['update_id'])
            with open("config.ini", "w") as f:
                config.write(f)
        if "message" in update and "chat" in update["message"]:
            chat_id=str(update["message"]["chat"]["id"])
            if chat_id not in config["Telegram"]["Chats"]:
                config["Telegram"]["Chats"]+=","+str(chat_id)
                config["Telegram"]["Chats"]=config["Telegram"]["Chats"].strip(",")
                with open("config.ini", "w") as f:
                    config.write(f)
            if user_update_lock is not None and str(chat_id)!=str(user_update_lock):
                telegram_bot_send_message("UwU Bot not available QwQ",chat_id)
                continue
        if "message" in update:
            yield update["message"]
        elif "callback_query" in update:
            callback_query=update["callback_query"]
            telegram_bot_process_callback(update["callback_query"]["data"], str(update["callback_query"]["from"]["id"]))
            telegram_bot_execute("answerCallbackQuery",{"callback_query_id": callback_query["id"]})
    telegram_bot_snooper()

def telegram_bot_download_file(file_id, destination=None, chat=None, message=None, snooper=False):
    file_info=telegram_bot_execute("getFile", {"file_id": file_id}, snooper=snooper)
    file_path=file_info['result']['file_path']
    if destination is None:
        destination=file_info['result']['file_path'].split('/')[-1]
    if not destination.endswith("."+file_info['result']['file_path'].split(".")[-1]):
        destination+="."+file_info['result']['file_path'].split(".")[-1]
    os.makedirs(config["Folders"]["Uploads"], exist_ok=True)
    destination=os.path.join(config["Folders"]["Uploads"],destination)
    if os.path.exists(destination):
        return destination

    try:
        if snooper:
            url="https://api.telegram.org/file/bot"+config["Telegram"]["ChatSnooper"]+"/"+file_path
        else:
            url="https://api.telegram.org/file/bot"+config["Telegram"]["Token"]+"/"+file_path
        urllib.request.urlretrieve(url, destination)
        if chat is not None and message is not None:
            known_forwards[destination]=(chat,message)
        if destination.lower().split(".")[-1] in ("jpg","jpeg","png","bmp"):
            image = Image.open(destination)
            image.thumbnail((256,256))
            image.save(os.path.join(os.path.expanduser(config["Folders"]["Thumbnails"]),get_thumbnail_location(destination)))
        return destination
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode())  # Read the body of the error response
        print("ERROR:")
        print(body)
        raise

pornfolder = []

def download_from_url(url):
    destination=url.split("/")[-1]
    from urllib.parse import unquote
    destination=unquote(destination)
    os.makedirs(config["Folders"]["Uploads"], exist_ok=True)
    destination=os.path.join(config["Folders"]["Uploads"],destination)
    if os.path.exists(destination):
        return destination
    try:
        urllib.request.urlretrieve(url, destination)
        return destination
    except urllib.error.HTTPError as e:
        body = e.read().decode()  # Read the body of the error response
        print("ERROR:")
        print(body)
        raise

def telegram_bot_process_callback(command,chat_id):
    bot_command(command, chat_id)
    telegram_send_started(True)

hook_sticker_state={}

#https://ux.stackexchange.com/questions/22520/how-long-does-it-take-to-read-x-number-of-characters
def read_time(text):
    ''' Calculate the amount of time needed to read the notification '''
    wpm = 180  # readable words per minute
    word_length = 5  # standardized number of chars in calculable word
    words = len(text)/word_length
    words_time = ((words/wpm)*60)*1000
    delay = 1500  # milliseconds before user starts reading the notification
    bonus = 1000  # extra time

    return (delay + words_time + bonus)/1000.0


def de_emoji(text):
    emojis={
        ("☺️","🙂","😊","😀"): ":-)",
        ("😃","😄","😁","😆","😂","😂"): ":-D",
        ("😎"): "8-)",
        ("☹️","🙁","😞","😟","😣","😖","😪", "😒"): ":-(",
        ("😢"): ":'-(",
        ("😭"): ":=(",
        ("🥲","🥹"): ":'-)",
        ("😠","😡"): ">:-(",
        ("😨","😧","😦","😱","😫","😩","😮","😯","😲"): ":-O",
        ("😺","😸","🐱"): ":-3",
        ("😼"): ">:-3",
        ("😗","😙","😚","😘","😍"): ":-X",
        ("😉"): ";-)",
        ("😜"): ";-P",
        ("🫤"): ":-/",
        ("🤔"): ":-?",
        ("😕","😟","😐","😑","🤨"): ":-|",
        ("😳","😞","😖"): ":-$",
        ("🤐","😶"): ":-&",
        ("😇","👼"): "0:-3",
        ("😈"): ">:-)",
        ("😏"): ":-J",
        ("🥴"): "#-)",
        ("😵","😵‍💫"): "%-)",
        ("🤒","😷","🤢"): ":-#",
        ("☠️","💀","🏴‍☠️"): "8-X",
        ("🍆","🍌"): "8===D",
        ("❤️","💙","💚","💛","💜","🖤","🤎","🧡","🩵","🩶","🩷","🫀","❤️‍🔥"): "<3",
        ("🔥"): "=3",
        ("\""): "''", #fix your escaping guys, smh
        ("\\"): "/",
        ("🦝","🦨"): "•⩊•"
        }
    for emoji_kind in emojis:
        for emoji in emoji_kind:
            text=text.replace(emoji,f" {emojis[emoji_kind]} ")
    return text

def wall_text(text_line):
    text_line=de_emoji(text_line)
    create_player()
    text_line = text_line.lstrip('\n')
    text=player.osd_msg1+"\n"+text_line
    text=text.lstrip("\n")
    player.osd_msg1=text
    from threading import Timer
    def stop_wall():
        player.osd_msg1=player.osd_msg1.lstrip(text).lstrip("\n")
    t = Timer(read_time(text), stop_wall)
    t.start()

def sticker_overlay(download_file):
    from PIL import Image
    create_player()
    with Image.open(download_file) as im:
        overlay = player.create_image_overlay()
        x=random.randint(0,player.dwidth-im.width)
        y=random.randint(0,player.dheight-im.height)
        overlay.update(im, pos=(x,y))
        from threading import Timer
        def stop_s():
            overlay.remove()
        t = Timer(random.random()*4+1, stop_s)
        t.start()

def telegram_bot_snooper():
    if not "ChatSnooper" in config["Telegram"]:
        return
    updates=telegram_bot_execute("getUpdates", {"offset": int(config["Telegram"]["LastUpdateSnooper"])+1, "allowed_updates": ["message", "callback_query"]}, snooper=True)["result"]
    for update in updates:
        if update['update_id']>int(config["Telegram"]["LastUpdateSnooper"]):
            config["Telegram"]["LastUpdateSnooper"] = str(update['update_id'])
            with open("config.ini", "w") as f:
                config.write(f)
        if not "message" in update:
            continue
        if update["message"]["date"]<start_time:
            continue
        if "caption" in update["message"]:
            text=""
            if "first_name" in update["message"]["from"]:
                text+="["+update["message"]["from"]["first_name"].split(" ")[0]+"] "
            text+="[img] "
            text+=update["message"]["caption"].replace("\"","''")
            print(de_emoji(text))
            wall_text(text[:512])
        if "text" in update["message"]:
            text=""
            if "first_name" in update["message"]["from"]:
                text+="["+update["message"]["from"]["first_name"].split(" ")[0]+"] "
            if "reply_to_message" in update["message"]:
                text+="@"+update["message"]["reply_to_message"]["from"]["first_name"].split(" ")[0]+": "
            text+=update["message"]["text"].replace("\"","''")
            print(de_emoji(text))
            wall_text(text[:512])
        if "sticker" in update["message"]:
            if player is not None and player.vo_configured:
                if 'set_name' in update["message"]["sticker"]["set_name"]:
                    download_file=telegram_bot_download_file(update["message"]["sticker"]["file_id"],update["message"]["sticker"]["emoji"], update["message"]["chat"]["id"], update["message"]["message_id"], snooper=True)
                else:
                    download_file=telegram_bot_download_file(update["message"]["sticker"]["file_id"],update["message"]["sticker"]["set_name"]+" "+update["message"]["sticker"]["emoji"], update["message"]["chat"]["id"], update["message"]["message_id"], snooper=True)
                sticker_overlay(download_file)
            print(update["message"]["sticker"]["emoji"])

def play_url(text):
    for e in extractor.list_extractor_classes():
        if e.working() and e.suitable(text) and e.IE_NAME != "generic":
            try:
                mpv_handle_play_file(text, True)
                break
            except Exception as e:
                if type(e.exc_info[1]) is yt_dlp.utils.ExtractorError:
                    return e.exc_info[1].orig_msg
                else:
                    return "Sorry, this URL is currently broken..."
    else:
        try:
            get_info(text, text.replace("/","-"))
            mpv_handle_play_file(text, True)
        except Exception:
            if text.startswith("http") and text.split(".")[-1] in ALLOWED_EXTENSIONS:
                destination=download_from_url(text)
                mpv_handle_play_file(destination, True)
            else:
                return "Sorry, can't handle this URL or command..."


output_device_select_message={}
seekpos=None

def bot_command(text, chat_id, chat_name=None):
    global shuffle
    global shutdown
    global porny
    global user_update_lock
    global hook_sticker_state
    global output_device_select_message
    global player
    global seekpos
    text=text.strip()
    if not blank:
        if chat_name:
            print(("[telegram bot/%s] "%chat_name)+text)
        else:
            print("[telegram bot] "+text)
    if text=="/bedroom":
        text="Receiver BEDROOM remote: Do not wake up Caroline"
        t=[
            [
                {"text": "20%", "callback_data": "/bedroom 50"},
                {"text": "40%", "callback_data": "/bedroom 55"},
                {"text": "60%", "callback_data": "/bedroom 60"},
                {"text": "80%", "callback_data": "/bedroom 65"},
                {"text": "100%", "callback_data": "/bedroom 70"}],
           [
            {"text": "PC", "callback_data": "/bedroom pc"},
            {"text": "CD", "callback_data": "/bedroom cd"},
            {"text": "Front HDMI", "callback_data": "/bedroom front"}],[
            {"text": "Wii/OSSC", "callback_data": "/bedroom wii"},
            {"text": "Bluray", "callback_data": "/bedroom bluray"}],[
            {"text": "OFF", "callback_data": "/bedroom off"},
            {"text": "Mute", "callback_data": "/bedroom 10"},
            {"text": "ON", "callback_data": "/bedroom on"}
            ]]
        output_device_select_message[str(chat_id)] = telegram_bot_execute("sendMessage", {"chat_id": chat_id, "text":text, "reply_markup": {"inline_keyboard": t}})["result"]["message_id"]
        return False
    if text=="/bedroom off":
        receiver_execute(DenonAvrCommand.CONFIG_ZONEPOWER, "<MainZone><Power>3</Power></MainZone>")
        return False
    if text=="/bedroom on":
        receiver_execute(DenonAvrCommand.CONFIG_ZONEPOWER, "<MainZone><Power>1</Power></MainZone>")
        receiver_execute(DenonAvrCommand.CONFIG_SOURCE_LIST, "<Source zone=\"1\" index=\"1\"></Source>")
        receiver_execute(DenonAvrCommand.VOLUME_MAIN, "70")
        return False
    if text.startswith("/bedroom ") and text.lstrip("/bedroom ").isdecimal():
        value = int(text.lstrip("/bedroom "))
        if value>=10 and value<=70:
            receiver_execute(DenonAvrCommand.VOLUME_MAIN, str(value))
            return False
    if text.startswith("/bedroom "):
        if text.endswith("cd"):
            text=9
        elif text.endswith("pc"):
            text=1
        elif text.endswith("front"):
            text=7
        elif text.endswith("wii"):
            text=8
        elif text.endswith("bluray"):
            text=3
        else:
            text=1
        receiver_execute(DenonAvrCommand.CONFIG_SOURCE_LIST, "<Source zone=\"1\" index=\"%d\"></Source>"%text)
        receiver_execute(DenonAvrCommand.VOLUME_ZONE2, "70")
        if str(chat_id) in output_device_select_message:
            telegram_bot_execute("deleteMessage",{"message_id":output_device_select_message[str(chat_id)],"chat_id":chat_id})
            del output_device_select_message[str(chat_id)]
        return False
    if text.startswith("/living ") and text.lstrip("/living ").isdecimal():
        value = int(text.lstrip("/living "))
        if value>=10 and value<=70:
            receiver_execute(DenonAvrCommand.VOLUME_ZONE2, str(value))
            return False
    if text=="/living":
        text="Receiver LIVING ROOM remote: Do not wake up Evalyn"
        t=[
            [
                {"text": "20%", "callback_data": "/living 50"},
                {"text": "40%", "callback_data": "/living 55"},
                {"text": "60%", "callback_data": "/living 60"},
                {"text": "80%", "callback_data": "/living 65"},
                {"text": "100%", "callback_data": "/living 70"}],
            [
            {"text": "PC", "callback_data": "/living pc"},
            {"text": "CD", "callback_data": "/living cd"},
            {"text": "Front HDMI", "callback_data": "/living front"}],[
            {"text": "Wii/OSSC", "callback_data": "/living wii"},
            {"text": "Bluray", "callback_data": "/living bluray"}],[
            {"text": "OFF", "callback_data": "/living off"},
            {"text": "Mute", "callback_data": "/living 10"},
            {"text": "ON", "callback_data": "/living on"}
            ]]
        output_device_select_message[str(chat_id)] = telegram_bot_execute("sendMessage", {"chat_id": chat_id, "text":text, "reply_markup": {"inline_keyboard": t}})["result"]["message_id"]
        return False
    if text=="/living off":
        receiver_execute(DenonAvrCommand.CONFIG_SOURCE_LIST, "<Zone2><Power>3</Power></Zone2>")
        return False
    if text=="/living on":
        receiver_execute(DenonAvrCommand.CONFIG_ZONEPOWER, "<Zone2><Power>1</Power></Zone2>")
        receiver_execute(DenonAvrCommand.CONFIG_SOURCE_LIST, "<Source zone=\"2\" index=\"1\"></Source>")
        receiver_execute(DenonAvrCommand.VOLUME_ZONE2, "70")
        return False
    if text.startswith("/living "):
        if text.endswith("cd"):
            text=9
        elif text.endswith("pc"):
            text=1
        elif text.endswith("front"):
            text=7
        elif text.endswith("wii"):
            text=8
        elif text.endswith("bluray"):
            text=3
        else:
            text=1
        receiver_execute(DenonAvrCommand.CONFIG_SOURCE_LIST, "<Source zone=\"2\" index=\"%d\"></Source>"%text)
        if str(chat_id) in output_device_select_message:
            telegram_bot_execute("deleteMessage",{"message_id":output_device_select_message[str(chat_id)],"chat_id":chat_id})
            del output_device_select_message[str(chat_id)]
        return False
    if text.startswith("/vol"):
        player.volume = max(0, min(300,int(text.split(" ")[-1])))
        return False
    if text.startswith("/speedcore"):
        player.speed = 45.0/33
        player["audio-pitch-correction"] = False
        return False
    if text.startswith("/speed"):
        player.speed = float(text.lstrip("/speed "))
        player["audio-pitch-correction"] = True
        return False
    if text.startswith("/sub"):
        player['sub-visibility']=True
        if len(text)>4:
            player['slang']=text[4:]
        return False
    if text=="/dub":
        player['sub-visibility']=False
        return False
    if text=="/private":
        if user_update_lock is None:
            user_update_lock=chat_id
            print(chat_id)
            text="Private mode engaged..."
            length=len(text.encode('utf-16-le'))//2
            telegram_bot_send_message(text,chat_id, [{"type": "italic", "offset": 0, "length": length}])
            return False
    if text=="/public":
        if user_update_lock is not None:
            user_update_lock=None
            text="Public mode engaged..."
            length=len(text.encode('utf-16-le'))//2
            telegram_bot_send_message(text,chat_id, [{"type": "italic", "offset": 0, "length": length}])
            return False
    if text=="/shuffle":
        shuffle = True
        create_player()
        player.pause = False
        perform_shuffle()
        return False
    if text=="/noshuffle":
        shuffle = False
        return False
    if text=="/output":
        t=[]
        create_player()
        text="Select output device..."
        for ele in player.audio_device_list:
            t.append([{"text": ele["description"], "callback_data": "/output %s"%ele["name"]}])
        output_device_select_message[str(chat_id)] = telegram_bot_execute("sendMessage", {"chat_id": chat_id, "text":text, "reply_markup": {"inline_keyboard": t}})["result"]["message_id"]
        return False
    if text.startswith("/output "):
        player.audio_device = text.strip("/output ")
        config["Player"]["AudioDevice"]=player.audio_device
        with open("config.ini", "w") as f:
            config.write(f)
        if str(chat_id) in output_device_select_message:
            telegram_bot_execute("deleteMessage",{"message_id":output_device_select_message[str(chat_id)],"chat_id":chat_id})
            del output_device_select_message[str(chat_id)]
        return False
    if text=="/jack":
        if player:
            player.audio_device = "auto"
        config["Player"]["AudioDevice"]="auto"
        with open("config.ini","w") as f:
           config.write(f)
        del player
        player=None
        create_player()
        return False
    if text=="/video":
        t=[]
        create_player()
        text="Select video device..."
        for ele in player["display-names"]:
            t.append([{"text": ele, "callback_data": "/video %s"%ele}])
        output_device_select_message[str(chat_id)] = telegram_bot_execute("sendMessage", {"chat_id": chat_id, "text":text, "reply_markup": {"inline_keyboard": t}})["result"]["message_id"]
        return False
    if text.startswith("/video "):
        player["drm-connector"] = text.strip("/video ")
        config["Player"]["AudioDevice"]=player["drm-connector"]
        with open("config.ini", "w") as f:
            config.write(f)
        if str(chat_id) in output_device_select_message:
            telegram_bot_execute("deleteMessage",{"message_id":output_device_select_message[str(chat_id)],"chat_id":chat_id})
            del output_device_select_message[str(chat_id)]
    if text=="/aspect":
        player["video-aspect-override"]=-1
        config["Player"]["VideoAspectOverride"]=-1
        with open("config.ini", "w") as f:
            config.write(f)
        return False
    if text.startswith("/aspect "):
        player["video-aspect-override"]=text.strip("/aspect ")
        config["Player"]["VideoAspectOverride"]=text.strip("/aspect ")
        with open("config.ini", "w") as f:
            config.write(f)
        return False
    if text=="/play":
        create_player()
        player.pause = False
        return False
    if text.startswith("/say "):
        basetext=""
        if chat_name is not None:
            basetext="["+chat_name+"]:"
        text=basetext+text[4:]
        if text=="":
            return
        telegram_bot_send_message_all(text, pinned=False)
        wall_text(text)
        return False
    if text=="/porny":
        porny = True
        text="Porny mode engaged..."
        length=len(text.encode('utf-16-le'))//2
        telegram_bot_send_message(text,chat_id, [{"type": "italic", "offset": 0, "length": length}])
        if not shuffle:
            shuffle=True
            create_player()
            perform_shuffle()
        return False
    if text[0]=="/" and text[1:].capitalize() in commands:
        if text[1:].capitalize() in pornfolder:
            pornfolder.remove(text[1:].capitalize())
            text="%s mode disengaged..."%text[1:].capitalize()
            length=len(text.encode('utf-16-le'))//2
            if len(pornfolder)!=0:
                text+="\n\nCurrently engaged modes: %s"%", ".join(list(map(lambda x: x.lower(),pornfolder))).capitalize()
            telegram_bot_send_message(text,chat_id, [{"type": "italic", "offset": 0, "length": length}])
            return False
        porny = True
        pornfolder.append(text[1:].capitalize())
        if len(pornfolder)>1:
            text="%s modes engaged..."%", ".join(list(map(lambda x: x.lower(),pornfolder))).capitalize()
        else:
            text="%s mode engaged..."%text[1:].capitalize()
        length=len(text.encode('utf-16-le'))//2
        telegram_bot_send_message(text,chat_id, [{"type": "italic", "offset": 0, "length": length}])
        if not shuffle:
            shuffle=True
            create_player()
            perform_shuffle()
        return False
    if text=="/normie":
        porny = False
        text="Porny mode disengaged..."
        length=len(text.encode('utf-16-le'))//2
        telegram_bot_send_message(text,chat_id, [{"type": "italic", "offset": 0, "length": length}])
        return False
    if text=="/start":
        return True
    if text=="/status":
        return False
    if text=="/oofvideo":
        mpv_handle_play_file(
            "https://www.youtube.com/watch?v=0twDETh6QaI",
            True)
        return True
    if text=="/shutdown" and str(chat_id)==config["Telegram"]["Chats"].split(",")[0]:
        shutdown = True
        quit()
        return False #should never happen lmao
    if player is None or player.idle_active:
        return
    if text=="/share":
        create_player()
        telegram_bot_send_message(player.path, chat_id)
        return False
    if text=="/stop":
        create_player()
        player.pause = True
        telegram_bot_send_message("%s /seek %ds"%(player.path, player.time_pos), chat_id)
        return False
    if text.startswith("/seek"):
        create_player()
        while player.seeking or player.paused_for_cache:
            pass
        seek_pos=text.split(" ")[-1]
        if seek_pos.endswith("s"):
            try:
                player.seek(int(seek_pos[:-1]), "absolute")
                seekpos = None
            except SystemError:
                seekpos = int(seek_pos[:-1])
        else:
            seek_pos= max(0, min(100,int(seek_pos)))
            player.seek(seek_pos,"absolute-percent")
        return False
    if text=="/watched":
        player.seek(player.duration)
        return False
    if text=="/next":
        create_player()
        pause=player.pause
        if shuffle:
            perform_shuffle()
        player.playlist_next("force")
        if not pause:
            player.wait_for_playback()
        return False
    if text=="/pause":
        create_player()
        player.pause = True
        return False
    if text=="/hook":
        hook_sticker_state[chat_id]=player.path
        telegram_bot_send_message("Please send the sticker to bind to the currently playing file...", chat_id)
        return False
    if player.vo_configured and text=="/screenshot":
        screenshot=player.screenshot_raw()
        filename=os.path.join("cache","screenshot","%s-%.2f.png"%(player.filename,player.time_pos))
        screenshot.save(filename)
        telegram_bot_send_document(chat_id,filename)
        return False
    if text.startswith("/download") or (text=="/screenshot" and not player.vo_configured):
        filename=" ".join(text.split(" ")[1:])
        watching=False
        if filename=="" or filename==None:
            filename=player.path
            watching=True
        og_filename=filename
        if not (filename.startswith("/") or filename.startswith("cache")):
            text="Downloading..."
            length=len(text.encode('utf-16-le'))//2
            telegram_bot_send_message(text, chat_id, {"type": "italic", "offset": 0, "length": length})
            telegram_bot_execute("sendChatAction",{"chat_id":chat_id,"action":"typing"})
            with yt_dlp.YoutubeDL({"outtmpl": os.path.join(config["Folders"]["Uploads"],'%(title)s.%(ext)s'), "format": "bestvideo[ext!=webm]+bestaudio[ext!=webm]/best[ext!=webm]", "recode-video": "mp4", "remux-video": "mp4", "merge-output-format": "mp4"}) as ydl:
                info=ydl.sanitize_info(ydl.extract_info(filename, download=True))
                filename = ydl.prepare_filename(info)
            if watching:
                open('cache/started/%s.started'%filename.split('/')[-1].split('=')[-1], 'a').close()
            if "UploadsInfo" in config["Folders"]:
                os.makedirs(config["Folders"]["UploadsInfo"], exist_ok=True)
                with open(os.path.join(os.path.expanduser(config["Folders"]["UploadsInfo"]),filename.split('/')[-1].split('=')[-1]+".json"), "w") as f:
                    json.dump(info, f, indent="\t")
            try:
                get_thumbnail_for_downloader(get_info(og_filename), filename)
            except Exception:
                print(traceback.format_exc())
        file_stats=os.stat(filename)
        if file_stats.st_size<1024*1024*50:
            telegram_bot_send_document(chat_id, filename)
            return False
        else:
            file_url=home_url+"download/"+filename.split("/")[-1]
            file_url=file_url.replace(" ","%20")
            text="File available at "
            offset=len(text.encode('utf-16-le'))//2
            text+=file_url
            length=len(text.encode('utf-16-le'))//2-offset
            telegram_bot_send_message(text,chat_id, {"type": "url", "offset": offset, "length": length})
            return False

def telegram_bot_process_updates():
    global hook_sticker_state
    has_updates=False
    important_command=False
    for update in telegram_bot_get_updates():
        botname="[Telegram bot"
        if "first_name" in update["chat"]:
            botname+="/"+update["chat"]["first_name"]
        botname+="]"
        for ele in update:
            if ele=="text":
                text=update[ele]
                if text=="." and player.pause:
                    player.frame_step()
                    continue
                if text=="," and player.pause:
                    player.frame_back_step()
                    continue
                if text.lower()=="m" and player.pause:
                    player.sub_seek(1)
                    continue
                if text.lower()=="z" and player.pause:
                    player.sub_seek(-1)
                    continue
            if ele=="entities":
                for entity in update[ele]:
                    if entity["type"]=="url" and "text" in update:
                        text=update["text"][entity["offset"]:entity["offset"]+entity["length"]]
                        print(botname,text)
                        important_command=True
                        result = play_url(text)
                        if result is not None:
                            telegram_bot_send_message(result, update["chat"]["id"])
                        else:
                            has_updates=True
                    if entity["type"]=="text_link":
                        text=entity["url"]
                        print(botname,text)
                        important_command=True
                        result = play_url(text)
                        if result is not None:
                            telegram_bot_send_message(result, update["chat"]["id"])
                        else:
                            has_updates=True
                    if entity["type"]=="bot_command" and "text" in update:
                        text=update["text"][entity["offset"]:]
                        #text="/"+text.split("/")[1]
                        username=None
                        if "first_name" in update["chat"]:
                            username=update["chat"]["first_name"]
                        result=bot_command(text, update["chat"]["id"],username)
                        if result is not None:
                            has_updates=True
                            important_command=result
                        else:
                            telegram_bot_send_message("Cannot handle command: "+text, update["chat"]["id"])
                if has_updates:
                    break
            elif isinstance(update[ele],dict) and "file_id" in update[ele]:
                important_command=True
                telegram_bot_execute("sendChatAction",{"chat_id":update["chat"]["id"],"action":"typing"})
                try:
                    if "file_name" in update[ele]:
                        download_file=telegram_bot_download_file(update[ele]["file_id"],update[ele]["file_name"], update["chat"]["id"], update["message_id"])
                    elif "set_name" in update[ele] and "emoji" in update[ele]:
                        if update["chat"]["id"] in hook_sticker_state:
                            if not "StickerHooks" in config:
                                config["StickerHooks"]={}
                            config["StickerHooks"][update[ele]["set_name"]+update[ele]["emoji"]]=hook_sticker_state[update["chat"]["id"]]
                            del hook_sticker_state[update["chat"]["id"]]
                            with open("config.ini", "w") as f:
                                config.write(f)
                            telegram_bot_send_message("Fantastic, binding set!", update["chat"]["id"])
                            download_file=None
                        elif update[ele]["set_name"]+update[ele]["emoji"] in config["StickerHooks"]:
                            download_file=config["StickerHooks"][update[ele]["set_name"]+update[ele]["emoji"]]
                            important_command=False
                        else:
                            download_file=telegram_bot_download_file(update[ele]["file_id"],update[ele]["set_name"]+" "+update[ele]["emoji"], update["chat"]["id"], update["message_id"])
                        if player is not None and download_file is not None:
                            print(botname, "Sticker "+update[ele]["set_name"]+update[ele]["emoji"]+": "+download_file)
                            if player.path == download_file:
                                player.seek(0,"absolute")
                            else:
                                playlist=get_safe_playlist()
                                try:
                                    _ = next(playlist)
                                except StopIteration:
                                    pass
                                playlist=list(playlist)
                                player.play(download_file)
                                for ele in playlist:
                                    player.playlist_append(ele["id"])
                            continue
                    elif "file_unique_id" in update[ele]:
                        download_file=telegram_bot_download_file(update[ele]["file_id"],update[ele]["file_unique_id"], update["chat"]["id"], update["message_id"])
                    else:
                        download_file=telegram_bot_download_file(update[ele]["file_id"], None, update["chat"]["id"], update["message_id"])
                    if download_file is not None:
                        print(botname,"File: ",download_file)
                        mpv_handle_play_file(download_file, True)
                        has_updates=True
                    #print(download_file)
                except ValueError:
                    telegram_bot_send_message("Sorry, this file is too big.\nThese simple bots support files up to 20MB...",update["chat"]["id"])
            elif ele=="photo":
                important_command=True
                telegram_bot_execute("sendChatAction",{"chat_id":update["chat"]["id"],"action":"typing"})
                photos=sorted(update[ele], key=lambda p:-p["height"])
                bestphoto=photos[0]
                for photo in photos:
                    if photo['height']<1080:
                        break
                    bestphoto=photo
                if "file_unique_id" in bestphoto:
                    download_file=telegram_bot_download_file(bestphoto["file_id"],bestphoto["file_unique_id"], update["chat"]["id"], update["message_id"])
                else:
                    download_file=telegram_bot_download_file(bestphoto['file_id'], None, update["chat"]["id"], update["message_id"])
                print(botname,"Photo: ",download_file)
                mpv_handle_play_file(download_file, True)
                has_updates=True
        if not important_command:
            telegram_bot_execute("deleteMessage",{"message_id":update["message_id"],"chat_id":update["chat"]["id"]})
    if has_updates:
        telegram_send_started(True)

def telegram_bot_send_message(text, chat, entries=None, silent=False):
    if chat is None:
        return
    if entries is None:
        return telegram_bot_execute("sendMessage", {"chat_id": chat, "text": text, "disable_notification": silent})
    else:
        return telegram_bot_execute("sendMessage", {"chat_id": chat, "text": text, "entities": entries, "disable_notification": silent})

last_global_messages=None

def telegram_bot_send_message_all(text, entries=None, silent=True, pinned=True):
    if not "Telegram" in config:
        return
    global last_global_messages
    global shuffle
    global current_telegram_message


    if pinned:
        firstrow=[]
        if player is not None:
            if not player.pause:
                firstrow.append({"text": "Pause", "callback_data": "/pause"})
            else:
                firstrow.append({"text": "Play", "callback_data": "/play"})
        if shuffle:
            firstrow.append({"text": "Stop shuffle", "callback_data": "/noshuffle"})
        else:
            firstrow.append({"text": "Shuffle", "callback_data": "/shuffle"})
        if player is not None and len(player.playlist)>0 and not player.pause:
            firstrow.append({"text": "Next", "callback_data": "/next"})
        keyboard=[firstrow, [{"text": "Browse...", "url": home_url}]]
    if last_global_messages is not None and pinned:
        if (text,keyboard)==current_telegram_message:
            return
        current_telegram_message = (text,keyboard)
        for message, chat in last_global_messages:
            if entries is None:
                try:
                    telegram_bot_execute("editMessageText", {"chat_id": chat, "message_id": message, "text":text, "reply_markup": {"inline_keyboard": keyboard}})
                except Exception:
                    print("[Exception whilst updating status update] "+traceback.format_exc())
                    return
            else:
                try:
                    telegram_bot_execute("editMessageText", {"chat_id": chat, "message_id": message, "text": text, "entities": entries, "reply_markup": {"inline_keyboard": keyboard}})
                except Exception:
                    print("[Exception whilst updating status update] "+traceback.format_exc())
                    return
        return

    if pinned:
        last_global_messages = []
    for chat in config["Telegram"]["Chats"].split(","):
        if chat!="":
            try:
                if not pinned:
                    result = telegram_bot_send_message(text, chat, entries, silent)["result"]
                else:
                    if entries is None:
                        result=telegram_bot_execute("sendMessage", {"chat_id": chat, "text":text, "reply_markup": {"inline_keyboard": keyboard}})["result"]
                    else:
                        result=telegram_bot_execute("sendMessage", {"chat_id": chat, "text": text, "entities": entries, "reply_markup": {"inline_keyboard": keyboard}})["result"]
                if pinned:
                    telegram_bot_execute("pinChatMessage",{"chat_id":chat, "message_id":result["message_id"], "disable_notification":True})
                    last_global_messages.append((result["message_id"],chat))
            except Exception:
                print("[Exception during status update] "+traceback.format_exc())
                return

def render_telegram_info(filename, title, text, entities):
    try:
        entry=get_info(filename)
    except Exception:
        print(traceback.format_exc())
        entry={"id": filename, "title": title}
    if 'uploader' in entry or 'tumblr_url' in entry:
        offset=len(text.encode('utf-16-le'))//2
        if 'tumblr_url' not in entry:
            text+=entry['uploader']
            length=len(text.encode('utf-16-le'))//2-offset
            if 'uploader_id' in entry:
                url = home_url + "user/%s"%entry['uploader_id'][1:]
                entities.append({"type": "text_link", "offset": offset, "length": length, "url": url})
            elif 'channel_id' in entry:
                url = home_url + "channel/%s"%entry['channel_id']
                entities.append({"type": "text_link", "offset": offset, "length": length, "url": url})
            text+=": "
    filetitle=entry['id']
    if 'title' in entry:
        filetitle=entry['title']
    text+="%s"%filetitle.replace("@","\uFF20")
    if 'tumblr_url' in entry:
        length=len(text.encode('utf-16-le'))//2-offset
        entities.append({"type": "text_link", "offset": offset, "length": length, "url": entry['tumblr_url']})
    text+="\n"
    return text

current_telegram_message = None
alerted_low_battery = False
def telegram_send_started(silent=True):
    if shutdown:
        return
    global alerted_low_battery
    text=""
    entities=[]
    #if player is not None and not player.idle_active and player.sub_text:
    #    text+=player.sub_text
    #    length=len(text.encode('utf-16-le'))//2
    #    entities.append({"type": "blockquote", "offset": 0, "length": length})
        #text+="\n\n"
    battery = psutil.sensors_battery()
    if battery.power_plugged==True and battery.percent<99:
        text+="\u26A1 %02d%% "%battery.percent
        alerted_low_battery = False
    elif battery.percent<36:
        text+="\U0001FAAB %02d%% "%battery.percent
    if player is not None and not player.idle_active and player.filename:
        offset=len(text.encode('utf-16-le'))//2
        if player.seeking or player.paused_for_cache:
            text+="Loading:\n"
        else:
            text+="Currently playing:\n"
        length=len(text.encode('utf-16-le'))//2-offset
        entities.append({"type": "bold", "offset": offset, "length": length})
        text=render_telegram_info(player.path, player.media_title, text, entities)

    has_up_next=False
    if player is not None and not player.idle_active:
        for playlist_entry in player.playlist[player.playlist_playing_pos+1:]:
            if not has_up_next:
                offset=len(text.encode('utf-16-le'))//2
                text+="\nUp next:\n"
                has_up_next=True
                length=len(text.encode('utf-16-le'))//2-offset
                entities.append({"type": "bold", "offset": offset, "length": length})
            if "title" in playlist_entry:
                text=render_telegram_info(playlist_entry["filename"], playlist_entry["title"], text, entities)
            else:
                text=render_telegram_info(playlist_entry["filename"], playlist_entry["filename"], text, entities)
    if text=="" and player is not None and not player.idle_active:
        return
    if shuffle:
        offset=len(text.encode('utf-16-le'))//2
        shuffletext="shuffle"
        if porny:
            shuffletext="random"
        if len(pornfolder)>0:
            shuffletext=", ".join(list(map(lambda x: x.lower(),pornfolder)))
        text+="And then %s...\n"%shuffletext
        length=len(text.encode('utf-16-le'))//2-offset
        entities.append({"type": "italic", "offset": offset, "length": length})
    text+="\n"
    text+="For sheduling new media visit "
    offset=len(text.encode('utf-16-le'))//2
    text+=home_url
    length=len(text.encode('utf-16-le'))//2-offset
    entities.append({"type": "url", "offset": offset, "length": length})
    text+=" or send a file or link!"
    telegram_bot_send_message_all(text, entities, silent)

#scrapy scrapy
ALLOWED_EXTENSIONS = {'mp4', 'mkv', 'webm', 'mp3', 'aac', 'flac'}

def get_source_links(url):
    import urllib.request, bs4
    headers = {
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0"
    }
    try:
        request=urllib.request.Request(url, headers=headers)
        for link in bs4.BeautifulSoup(urllib.request.urlopen(request, timeout=4), features="html5lib").find_all("a"):
            if link.has_attr('href'):
                yield link['href']
    except urllib.error.URLError:
        print(url,traceback.format_exc())
        return []

def scrape_google(query):
    import urllib.parse
    query = urllib.parse.quote_plus(query)
    #links = get_source_links("https://www.google.co.uk/search?q=" + query)
    links = get_source_links("https://duckduckgo.com/html/?q=" + query)
    google_domains = ('https://www.google.',
                      'https://google.',
                      'https://webcache.googleusercontent.',
                      'http://webcache.googleusercontent.',
                      'https://policies.google.',
                      'https://support.google.',
                      'https://maps.google.',
                      'https://www.youtube.com')

    for url in links:
        if url.startswith("//duckduckgo.com/l/?uddg="):
            url=url.lstrip("//duckduckgo.com/l/?uddg=")
            url=urllib.parse.unquote_plus(url.split("&")[0])
        if not url.startswith('http'):
            continue
        if "google" in url:
            continue
        if url.startswith(google_domains):
            continue
        yield url

def simpleid(text):
    out=""
    for letter in text.lower():
        if letter in "abcdefghijklmnopqrstuvwxyz":
            out+=letter
    return out

def search_results_deepweb(query):
    from urllib.parse import urljoin, unquote_plus
    for url in set(scrape_google("-inurl:(htm|html|php) intitle:\"index of\" + \"last modified\" + \"parent directory\" + \"mp3\" + \""+query+"\"")):
        links = get_source_links(url)
        for ele in links:
            if ele.split(".")[-1].lower() in ALLOWED_EXTENSIONS and simpleid(query) in simpleid(ele):
                hashie=int.from_bytes(hashlib.sha256(urljoin(url,ele).encode('utf-8')).digest()[:8], byteorder='big', signed=True)
                with open("cache/search/%d.txt"%hashie, "w") as f:
                    f.write(urljoin(url,ele))
                yield {"title": unquote_plus(ele.split("/")[-1]), "id": "%d"%hashie}

#sponsorblock
sponsorblock_times=[]

# based on https://github.com/po5/mpv_sponsorblock/blob/master/sponsorblock_shared/sponsorblock.py
def sponsorblock(video_id):
    if "Sponsorblock" not in config:
        return
    global sponsorblock_times
    sponsorblock_times=[]
    VIDEO_ID_REGEX = re.compile(
    r"(.+?)(\/)(watch\x3Fv=)?(embed\/watch\x3Ffeature\=player_embedded\x26v=)?([a-zA-Z0-9_-]{11})+"
)
    video_id_match = VIDEO_ID_REGEX.match(video_id)
    if video_id_match is None:
        return
    if not video_id.startswith("https://"):
        return
    video_id = video_id_match.group(5)
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "mpv_sponsorblock/1.0 (https://github.com/po5/mpv_sponsorblock)")]
    urllib.request.install_opener(opener)
    sha = hashlib.sha256(video_id.encode("utf-8")).hexdigest()[:4]
    times = []
    try:
        response = urllib.request.urlopen(config["Sponsorblock"]["Url"] + sha)
        segments = json.load(response)
        for segment in segments:
            if sha and video_id != segment["videoID"]:
                continue
            if sha:
                for s in segment["segments"]:
                    times.append(s["segment"][0:2])
        #print(":".join(times))
    except (TimeoutError, urllib.error.URLError) as e:
        print("sponsorblock error %s"%str(e))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("")
        else:
            print("sponsorblock error %s"%str(e))
    sponsorblock_times=times
    return times

#TODO: This is really bad
def is_in_playlist(video):
    global player
    if player == None or player.idle_active:
        return None
    playlist=list(map(lambda x: x['filename'],player.playlist[player.playlist_playing_pos:]))
    if video in playlist:
        return playlist.index(video)
    return None

def html_idify(text):
    out=""
    for letter in text:
        if letter.lower() not in "abcdefghijklmnopqrstuvwxyz0123456789-_":
            if len(out)>0 and out[-1]!="_":
                out+="_"
        else:
            out+=letter
    return out

@functools.cache
def generate_b64thumb(filename):
    if os.path.exists(os.path.join(config["Folders"]["ThumbnailsAlt"],filename)):
        with open(os.path.expanduser(os.path.join(config["Folders"]["ThumbnailsAlt"],filename)), "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
    else:
        with open(os.path.expanduser(os.path.join(config["Folders"]["Thumbnails"],filename)), "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
    return "data:image/png;base64, "+encoded_string.decode('ascii')

def get_thumbnail_for_downloader(info, destination, wsize=256, hsize=256):
    image = None
    if not 'thumbnails' in info:
        if 'thumbnail' in info:
            image=info["thumbnail"]["url"]
    if image is None:
        for ele in sorted(filter(lambda x: 'width' in x,info['thumbnails']), key=lambda x: -x['width']):
            if ele["width"]<=wsize and ele["height"]<=hsize:
                image=ele["url"]
                break
    if image is None:
        return
    image = Image.open(urllib.request.urlopen(image))
    image.thumbnail((wsize,hsize))
    os.makedirs(config["Folders"]["ThumbnailsAlt"], exist_ok=True)
    dest = os.path.join(config["Folders"]["ThumbnailsAlt"], get_thumbnail_location(destination))
    image.save(dest)
    import shutil
    shutil.copy2(dest, os.path.expanduser(config["Folders"]["Thumbnails"]))

def generate_thumbnail(info, uploader=None):
    if "telegram_thumbnail" in info and info['telegram_thumbnail'] is not None:
        return "<img src='%s'/>"%generate_b64thumb(info['telegram_thumbnail'])
    if not 'thumbnails' in info or len(info['thumbnails'])==0:
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

def generate_description(info, uploader=None, clickable=False, mainpage=True, fromhome=False):
    if fromhome and not os.path.exists('cache/started/%s.started'%info['id']):
        fromhome=False
    if 'fulltitle' in info:
        title=info['fulltitle']
    else:
        title=info['title']
    if clickable:
        idify=html_idify(info['id'].split('/')[-1])
        if mainpage==False:
            idify=""
        if not info['id'].startswith("/") and not info['id'].startswith("cache"):
            html="<figure id=\"%s\">"%idify
        else:
            html="<figure class='notyt' id=\"%s\">"%idify
    else:
        html="<figure>"
    if not fromhome:
        if clickable:
            if "/" in info['id']:
                html+="<a href=\"play/%s\">"%info['id'].split("/")[-1]
            else:
                html+="<a href=\"play/%s\">"%info['id']
        if not fromhome:
            html+=generate_thumbnail(info,uploader)
        if clickable:
            html+="</a>"
    html+="<figcaption>"
    if fromhome:
        html+="<span class=\"fakesummary\">"
        html+="<a href=\"play/%s\">"%info['id'].split("/")[-1]
    elif ("ie_key" in info and info["ie_key"].lower()=="youtube") or "youtu" in info["id"]:
        html+="<details data-source=\"/describe/%s\"><summary>"%info['id']
    else:
        if info['id'].startswith(os.path.expanduser(config["Folders"]["Music"])):
            html+="<a class='song' href=\"/music/play/%s\">"%info['title']
        else:
            html+="<a class='song' href=\"play/%s\">"%info['id'].split("/")[-1]
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
    if fromhome:
        html+="</a>"
    if uploader is None and 'uploader' in info:
        if 'uploader_id' in info and info['uploader_id'] is not None:
            html+=' <a href="/user/%s/">%s</a>'%(info['uploader_id'][1:],info['uploader'])
        elif 'channel_id' in info and info['channel_id'] is not None:
            html+=' <a href="/channel/%s/">%s</a>'%(info['channel_id'],info['uploader'])
    if not info['id'].startswith("/") and not info['id'].startswith("cache") and not fromhome:
        html+="</summary>"
        html+="<span>"
        if 'description' in info and info['description'] is not None:
            html+=info['description'].replace('\n','<br/>')
        html+="</span>"
        html+="</details>"
    else:
        if fromhome:
            html+="</span>"
        html+='</a>'
    html+="</figcaption></figure>"
    return html

def generate_channelpage(info, endless=False, subscriptions=None):
    html="<h1>%s</h1>"%(info['channel'])

    if subscriptions is not None and info['uploader_id'][1:].lower().replace(' ','') in subscriptions.split(','):
        html+="<a href='subscribe'>Unsubscribe</a>"
    else:
        html+="<a href='subscribe'>Subscribe</a>"
    html+=" - <a href='/'>Home</a>"
    html+="<p>"
    html+=info['description'].replace('\n','<br/>')
    html+="</p>"
    html+="<section class='videogrid'>"
    yield html
    html=""
    for ele in info['entries']:
        yield generate_description(ele, uploader=info['channel'], clickable=True)
    yield "</section>"
    if not endless and len(info['entries'])>=36:
        yield "<h2 style='margin:auto;'><a href='endless/#%s'>Load all...</a></h2>"%html_idify(info['entries'][-1]['id'])
    return html

def generate_searchpage(info,searchterm, songsearch, deepwebsearch):
    html="<h1><small>Searched for: </small>%s</h1>"%(searchterm)
    html+="<a href=\"/\">Home</a>"
    yield html
    if len(songsearch)>0:
        html="<h2><small>From the </small>local music library:</h2>"
        html+="<table><tbody>"
        html+="<tr><th></th><th>Artist</th><th colspan=\"2\">Album</th><th>Song</th></tr>"
        yield html
        for song in songsearch:
            yield generate_music_row(*song)
        yield "</tbody></table>"
        found=False
        for ele in deepwebsearch:
            if not found:
                yield "<h2><small>From </small>The Deep Web:</h2>"
            yield generate_description(ele, clickable=True)
            found=True
    yield "<h2><small>From </small>YouTube:</h2><section class='videogrid'>"
    for ele in info['entries']:
        yield generate_description(ele, clickable=True)
    yield "</section>"

def get_order(filename):
    #if player is not None:
    #    playlist=list(map(lambda x: x['filename'], player.playlist))
    #    if filename in playlist:
    #        return -playlist.index(filename)
    filename=filename.split("/")[-1]
    startfile=os.path.join("cache","started", filename+".started")
    if os.path.exists(startfile):
        return sys.maxsize-os.path.getmtime(startfile)
    startfile=os.path.join("cache","watched", filename+".watched")
    if os.path.exists(startfile):
        return sys.maxsize-os.path.getmtime(startfile)
    return sys.maxsize

def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

def generate_folderpage(folder=None, ext=None):
    html=""
    if folder is not None:
        html+="<h1><small>Folder:</small> %s</h1>"%folder.capitalize()
    html+="<a href='/'>Home</a> - <a href='/music/'>Music</a> - <a href='/telegram/'>Uploads</a>"
    for ele in config["Commands"]:
        if folder is not None:
            html+=" - <a href='../%s'>%s</a>"%(ele, ele.capitalize())
        else:
            html+=" - <a href='%s'>%s</a>"%(ele, ele.capitalize())
    html+="<section class='videogrid'>"
    yield html
    if folder is not None:
        basepath=os.path.expanduser(config["Commands"][folder])
        for filename in sorted(os.listdir(basepath), key=alphanum_key):
            if ext is not None and not filename.split(".")[-1] in ext:
                continue
            yield generate_description(get_info(os.path.join(basepath,filename)), clickable=True)
        yield "</section>"

def generate_telegrampage(ext=None, downloads=False):
    files=os.listdir(config["Folders"]["Uploads"])
    files=list(map(lambda x: os.path.join(config["Folders"]["Uploads"],x), files))
    files=sorted(files, key=lambda x: get_order(x))
    html="<h1>Recently uploaded...</h1>"
    html+="<a href=\"/\">Home</a>"
    if downloads:
        html+=" - <a href=\"/telegram/\">Back...</a>"
    elif ext is None:
        html+=" - <a href=\"/telegram/videos/\">Videos</a>"
        html+=" - <a href=\"/download/\">Download</a>"
    else:
        html+=" - <a href=\"/telegram/\">All uploads</a>"
    html+=" - <a href='/folder/'>Folders</a>"
    html+="<br/><br/>"
    if ext is None and not downloads:
        html+="""<form method="post"" enctype="multipart/form-data"><input type="file" name="file"></input><input type="submit" value="Upload file..."></input></form>"""
    html+="<section class='videogrid'>"
    yield html
    for filename in files:
        if ext is not None and not filename.split(".")[-1] in ext:
            continue
        yield generate_description(get_info(filename), clickable=True)
    yield "</section>"

def get_thumbnail_location(filename):
    filename=os.path.abspath(filename)
    filename="file://"+filename.replace(" ", "%20")
    filename=hashlib.md5(filename.encode()).hexdigest()+".png"
    return filename

def get_thumbnail(filename):
    filename=os.path.abspath(filename)
    filename="file://"+filename.replace(" ", "%20")
    filename=hashlib.md5(filename.encode()).hexdigest()+".png"
    if os.path.exists(os.path.expanduser(config["Folders"]["Thumbnails"])) and os.path.exists(os.path.expanduser(os.path.join(config["Folders"]["Thumbnails"],filename))):
        return filename
    return None

def get_info(videourl):
    if videourl is None:
        raise Exception("Broken link")
    if not videourl.strip().startswith("http"):
        if "UploadsInfo" in config["Folders"]:
            os.makedirs(config["Folders"]["UploadsInfo"], exist_ok=True)
            filename=os.path.join(os.path.expanduser(config["Folders"]["UploadsInfo"]),videourl.split('/')[-1].split('=')[-1]+".json")
            if os.path.exists(filename):
                with open(filename) as f:
                    info = json.load(f)
                    info["id"] = videourl
                    return info
        thumbnail=get_thumbnail(videourl)
        name = videourl.split("/")[-1]
        name_regular = name.replace("%20"," ").replace("_"," ")
        if videourl.split("/")[-2].lower() == "tumblr":
            breakdown=name.split(".")[0].split("_")
            if len(breakdown)>1:
                tumblr_url="https://www.tumblr.com/%s/%s"%(breakdown[0],breakdown[1])
                if thumbnail is None:
                    return {'title': name_regular, 'id': videourl, 'tumblr_url': tumblr_url, 'telegram_thumbnail':thumbnail}
                else:
                    return {'title': name_regular, 'id': videourl, 'tumblr_url': tumblr_url}
        if thumbnail is None:
            return {'title': name_regular, 'id': videourl}
        else:
            return {'title': name_regular, 'id': videourl, 'telegram_thumbnail': thumbnail}
    videoid=""
    for e in extractor.list_extractor_classes():
        if e.working() and e.suitable(videourl) and e.IE_NAME != "generic":
            videoid=e.IE_NAME.replace(":","_").lower()+"/"+e.get_temp_id(videourl).replace("/","-")
            break

    #videoid=videourl.lstrip("https://www.youtube.com/watch?v=")
    try:
        info = get_ytdlp_info(videourl, "video/%s.json"%videoid)
        if not videourl.startswith("https://www.youtu") and not videourl.startswith('https://youtu'):
            del info['uploader']
    except Exception:
        for ele in player.playlist:
            if "filename" in ele and ele["filename"]==videourl:
                if "title" in ele:
                    return {"title": ele["title"], "id": ele["filename"]}
                return {"title": ele["filename"], "id": ele["filename"]}
        raise
    return info

def get_safe_playlist():
    if player is None or player.idle_active:
        return []
    for ele in player.playlist[player.playlist_playing_pos:]:
        try:
            yield get_info(ele['filename'])
        except Exception as e:
            print(traceback.format_exc())
            yield {"id": ele["filename"], "title": ele["title"]}

def generate_footer():
    html=""
    if player is not None and not player.idle_active:
        playlist=list(get_safe_playlist())
        if len(playlist)>0:
            html+="<footer id='footer'><div>"
            html+="<details id='oopnext'><summary>Currently playing"
            if len(playlist)>1:
                html+=" (%d)"%len(playlist)
            html+=": <strong>"+playlist[0]['title']+"</strong></summary>"
            if player.duration and player.time_pos:
                html+="<input type='range' id='time' min='0' max='%d' value='%d'/>"%(int(player.duration),int(player.time_pos))
            else:
                html+="<input type='range' id='time' min='0' max='3' value='0'/>"
            html+=generate_description(playlist[0], clickable=True, mainpage=False)
            yield html
            html=""
            if len(playlist)>1:
                yield "Up next: <div>"
                for ele in playlist[1:]:
                    yield generate_description(ele, clickable=True, mainpage=False)
                html+="</div>"
            html+="</details>"
            html+="</div><div>"
            if player.pause:
                html+="<a id='pause' href='pause'>Resume</a>"
            else:
                html+="<a id='resume' href='pause'>Pause</a>"
            html+="<input type='range' id='volume' min='0' max='100' value='%d'/>"%player.volume
            html+="</div></footer>"
    yield html

def generate_page(page, title):
    html="<html><head><title>%s</title><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"%title#<link rel=\"stylesheet\" href=\"/style.css\">"%title
    html+="<style>"+style()+"</style>"
    if player is not None and not player.pause and player.time_remaining is not None and blank:
        html+="<meta http-equiv=\"refresh\" content=\"%d\">"%(player.time_remaining+random.randint(5,10))
    html+="</head><body>"
    html+="<header><form action='/search/' method='GET'><input id='search' name='search'/><button id='searchbutton' type='submit'>Search YT</button></form>"
    html+="</header>"
    yield html
    for ele in generate_footer():
        yield ele
    html=""
    html+="""
<script>
var volume = document.getElementById('volume');
if(volume)
volume.addEventListener("change", function(event) {
    fetch('/volume/'+volume.value).then((response) => {});
});
var footer = document.getElementById('footer');
var timeslider = document.getElementById('time');
if(timeslider){

timeslider.addEventListener("change", function(event) {
    fetch('/seek/'+timeslider.value).then((response) => {});
});
var interval=setInterval(function() {
    timeslider.value = parseInt(timeslider.value)+1;
    if(parseInt(timeslider.value) == parseInt(timeslider.max))
        fetch('/footer/')
        .then(r => r.text())
        .then(function(html)
            {
            var parser = new DOMParser();
            var doc = parser.parseFromString(html, "text/html");
            var footintern =  doc.querySelector('footer');
            if(footintern){
            footer.innerHTML = footintern.innerHTML;
            timeslider = document.getElementById('time');
            }
            else{
            clearInterval(interval);
            footer.remove();
            }
            }
        );
}, 1000);
}
if(volume)
volume.addEventListener("change", function(event) {
    fetch('/volume/'+volume.value).then((response) => {});
});
</script>
    """.replace('\n','')
    html+="<main>"
    yield html
    if hasattr(page, '__iter__') and not hasattr(page, '__len__'):
        for ele in page:
            yield ele
    else:
        yield page
    html="</main>"
    html+="""
<script>
var details = document.querySelectorAll("details");
details.forEach((detail) => {
    detail.addEventListener("toggle", function(event) {
    if(detail.dataset.source)
        fetch(detail.dataset.source).then((response) => response.ok ? response.text() : Promise.reject(response)).then((text) => {
            detail.lastChild.innerHTML = text;
            detail.removeAttribute('data-source');
        }).catch(response => console.log(response.status,response.statusText));
    });
});
</script>
""".replace('\n','')
    html+="</body></html>"
    yield html


def _get_ytdlp_info(url, endless=False):
    if endless:
        ydl_opts = {'extract_flat': 'in_playlist', "quiet": "true" }
    else:
        ydl_opts = {'extract_flat': 'in_playlist', "quiet": "true", 'playlistend': 36  }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.sanitize_info(ydl.extract_info(url, download=False))
    return info

infolist={}

from threading import Lock
ytdlp_info_lock = Lock()

def get_ytdlp_info(url, cache, endless=False):
    with ytdlp_info_lock:
        infolist[url]=cache
        info = None
        os.makedirs(os.path.join(config["Folders"]["Cache"],"/".join(cache.split('/')[:-1])), exist_ok=True)
        if os.path.exists(os.path.join(config["Folders"]["Cache"],cache)):
            with open(os.path.join(config["Folders"]["Cache"],cache)) as f:
                info=json.load(f)
        if info is None or ttl()>info['ttl'] or info['endless']!=endless:
            info=_get_ytdlp_info(url, endless)
            if "extractor" in info and "ie_key" not in info:
                info["ie_key"]=info["extractor"]
            info['ttl']=ttl()+60*15
            info['endless']=endless
            with open(os.path.join(config["Folders"]["Cache"],cache), "w") as f:
                json.dump(info, f, indent="\t")
        return info

screenoff=False
def mpv_handle_start(event):
    global screenoff
    global seekpos
    os.makedirs("cache/started", exist_ok=True)
    if len(list(filter(lambda x: x['id']==event.data.playlist_entry_id, player.playlist)))==0:
        perform_shuffle()
        return
    filename = list(filter(lambda x: x['id']==event.data.playlist_entry_id, player.playlist))[0]['filename']
    name=filename.split('/')[-1]
    name=name.split('=')[-1]
    if os.path.exists('cache/started/%s.started'%name):
        os.remove('cache/started/%s.started'%name)
    open('cache/started/%s.started'%name, 'a').close()
    if seekpos is not None:
        player.seek=seekpos
        seekpos=None
    sponsorblock(filename)
    if player.vo_configured:
        #print(player.video_params)
        if screenoff:
            player.stop_screensaver="no"
            if blank and "Blanking" in config:
                os.system(config["Blanking"]["Unblank"])
            screenoff = False
    elif not screenoff:
        player.stop_screensaver="yes"
        if blank and "Blanking" in config:
            os.system(config["Blanking"]["Blank"])
        screenoff = True
    telegram_send_started()

def mpv_handle_end(event):
    if event.data.reason==0: #EOF
        os.makedirs("cache/watched", exist_ok=True)
        filename = list(filter(lambda x: x['id']==event.data.playlist_entry_id, player.playlist))
        if len(filename)<1:
            return
        filename = filename[0]['filename']
        if filename in known_forwards:
            chat, message = known_forwards[filename]
            telegram_bot_execute("deleteMessage",{"message_id":message,"chat_id":chat})
            del known_forwards[filename]
        filename=filename.split('/')[-1]
        filename=filename.split('=')[-1]
        open('cache/watched/%s.watched'%filename, 'a').close()
        perform_shuffle()

prev_telegram_time=None
def time_observer(value):
    global prev_telegram_time
    global alerted_low_battery
    if value is None:
        return
    for start,end in sponsorblock_times:
        if start<=value<end:
            print("Sponsorblock skipped from %f to %f"%(value,end))
            player.time_pos = end
    if player.time_remaining != None:
        if player.time_remaining in range(90,91):
            for url in infolist:
                get_ytdlp_info(url,infolist[url])
        battery = psutil.sensors_battery()
        if player is not None and player.playtime_remaining is not None and battery.power_plugged!=True and battery.secsleft is not None and battery.secsleft<player.playtime_remaining and battery.secsleft>0 and not alerted_low_battery:
            telegram_bot_send_message_all("\u26A0\U0001FAAB Battery empty in %02d:%02d! \U0001FAAB\u26A0"%divmod(battery.secsleft, 60), pinned=False)
            alerted_low_battery = True



def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

swearwords=[r"\b[a@][s$][s$]\b", r"\b[a@][s$][s$]h.*\b", r"\b[a@][s$][s$]w.*\b", r"[a@][s$-][s$-]?h[o0][l1][e3][s$]?", r"b[a@][s$][t+][a@]rd ", r"b[a@]d[a@]ss ", r"b[e3][a@][s$][t+][i1][a@]?[l1]([i1][t+]y)?", r"b[e3][a@][s$][t+][i1][l1][i1][t+]y", r"b[e3][s$][t+][i1][a@][l1]([i1][t+]y)?", r"b[i1][t+]ch[s$]?", r"b[i1][t+]ch[e3]r[s$]?", r"b[i1][t+]ch[e3][s$]", r"b[i1][t+]ch[i1]ng?", r"b[l1][o0]wj[o0]b[s$]?", r"b[l1][o0]w m[e3]?", r"bu[l1][l1][s$]h[i1][t+]", r"c[l1][i1][t+]", r"c[l1][i1][t+]", r"\b(c|k|ck|q)[o0](c|k|ck|q)[s$]?\b", r"(c|k|ck|q)[o0](c|k|ck|q)[s$]u", r"(c|k|ck|q)[o0](c|k|ck|q)[s$]u(c|k|ck|q)[e3]d ", r"(c|k|ck|q)[o0](c|k|ck|q)[s$]u(c|k|ck|q)[e3]r", r"(c|k|ck|q)[o0](c|k|ck|q)[s$]u(c|k|ck|q)[i1]ng", r"(c|k|ck|q)[o0](c|k|ck|q)[s$]u(c|k|ck|q)[s$]", r"\bcum[s$]?\b", r"cumm??[e3]r", r"cumm?[i1]ngcock", r"(c|k|ck|q)um[s$]h[o0][t+]", r"(c|k|ck|q)un[i1][l1][i1]ngu[s$]", r"(c|k|ck|q)un[i1][l1][l1][i1]ngu[s$]", r"(c|k|ck|q)unn[i1][l1][i1]ngu[s$]", r"(c|k|ck|q)un[t+][s$]?", r"(c|k|ck|q)un[t+][l1][i1](c|k|ck|q)", r"(c|k|ck|q)un[t+][l1][i1](c|k|ck|q)[e3]r", r"(c|k|ck|q)un[t+][l1][i1](c|k|ck|q)[i1]ng", r"cyb[e3]r(ph|f)u(c|k|ck|q)", r"d[a@]mn", r"d[i1]ck", r"d[i1][l1]d[o0]", r"d[i1][l1]d[o0][s$]", r"d[i1]n(c|k|ck|q)", r"d[i1]n(c|k|ck|q)[s$]", r"[e3]j[a@]cu[l1]", r"(ph|f)[a@]g[s$]?", r"(ph|f)[a@]gg[i1]ng", r"(ph|f)[a@]gg?[o0][t+][s$]?", r"(ph|f)[a@]gg[s$]", r"(ph|f)[e3][l1][l1]?[a@][t+][i1][o0]", r"(ph|f)u(c|k|ck|q)", r"(ph|f)u(c|k|ck|q)[s$]?", r"g[a@]ngb[a@]ng[s$]?", r"g[a@]ngb[a@]ng[e3]d", r"g[a@]y", r"h[o0]m?m[o0]", r"h[o0]rny", r"j[a@](c|k|ck|q)\-?[o0](ph|f)(ph|f)?", r"j[e3]rk\-?[o0](ph|f)(ph|f)?", r"j[i1][s$z][s$z]?m?", r"[ck][o0]ndum[s$]?", r"mast(e|ur)b(8|ait|ate)", r"n+[i1]+[gq]+[e3]*r+[s$]*", r"[o0]rg[a@][s$][i1]m[s$]?", r"[o0]rg[a@][s$]m[s$]?", r"p[e3]nn?[i1][s$]", r"p[i1][s$][s$]", r"p[i1][s$][s$][o0](ph|f)(ph|f) ", r"p[o0]rn", r"p[o0]rn[o0][s$]?", r"p[o0]rn[o0]gr[a@]phy", r"pr[i1]ck[s$]?", r"pu[s$][s$][i1][e3][s$]", r"pu[s$][s$]y[s$]?", r"[s$][e3]x", r"[s$]h[i1][t+][s$]?", r"[s$][l1]u[t+][s$]?", r"[s$]mu[t+][s$]?", r"[s$]punk[s$]?","[t+]w[a@][t+][s$]?"]

import re, random

def swear(length):
    out=""
    for letter in range(length):
        t=random.choice("!@#$%^&*?~m")
        while out!="" and out[-1]==t:
            t=random.choice("!@#$%^&*?~")
        out+=t
    return out

last_subtitle_text=""
def show_sub(text):
    if text is None:
        return
    global last_subtitle_text
    for row in text.split("\n"):
        if row.strip()=="":
            continue
        if row!=last_subtitle_text:
            bad=False
            for pattern in swearwords:
                if re.search(pattern, text, re.IGNORECASE):
                    bad=True
                    text=re.sub(pattern, lambda m: swear(len(m.group(0))), text, 0, re.IGNORECASE)
            print(row)
            #mpv.show_text(text)
            #print_large(row)
    if row.strip()!="":
        last_subtitle_text=row

def create_player():
    global player
    if blank and "Blanking" in config:
        os.system(config["Blanking"]["Blank"])
    if player is None:
        player_config_base = config["Player"]
        player_config={}
        player_flags=[]
        for ele in player_config_base:
            ment=player_config_base[ele]
            if ment == "":
                player_flags.append(camel_to_snake(ele))
                continue
            player_config[camel_to_snake(ele)]=ment
        player_config_ytdl_raw = config["Ytdl"]
        player_config_ytdl=""
        for ele in player_config_ytdl_raw:
            propname=camel_to_snake(ele).replace("_","-")
            player_config_ytdl+=propname+"="+player_config_ytdl_raw[ele]+","
        player_config["ytdl_raw_options"]=player_config_ytdl[:-1]
        player=mpv.MPV(*player_flags, **player_config)

        @player.event_callback('start-file')
        def start(event):
            mpv_handle_start(event)

        @player.event_callback('end-file')
        def end(event):
            mpv_handle_end(event)

        @player.property_observer('pause')
        def observe_pause(_name, value):
            telegram_send_started(True)

        @player.property_observer('sub-text')
        def observe_sub(_name, value):
            show_sub(value)

        @player.property_observer('seeking')
        def observe_seek(_name, value):
            telegram_send_started(True)

        @player.property_observer('paused-for-cache')
        def observe_pause(_name, value):
            telegram_send_started(True)

        @player.property_observer('idle-active')
        def observe_idle(_name, value):
            telegram_send_started(True)

        @player.property_observer('time-pos')
        def observe_time(_name, value):
            time_observer(value)

def mpv_handle_play_file(path, by_telegram=False):
    get_info(path) #prevents bad paths from entering the queue
    create_player()

    if len(player.playlist) == 0 or player.idle_active:
        player.play(path)
    else:
        for index,ele in enumerate(player.playlist[player.playlist_playing_pos:]):
            if "filename" in ele and ele["filename"].split("/")[-1]==path.split("/")[-1]:
                player.playlist_remove(index+player.playlist_pos)
                break
            elif "playlist-path" in ele and ele["playlist-path"].split("/")[-1]==path.split("/")[-1]:
                player.playlist_remove(index+player.playlist_playing_pos)
                break
        else:
            player.playlist_append(path)
    telegram_send_started()

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
        if track.strip().isdigit() and track!="42": #by coldplay, yes i know this is cheating
            number = track
            track = "~unknown (%s)"%track
        if "(" in track:
            track=track[:track.index("(")]+"<small>"+track[track.index("("):]+"</small>"
        yield (filename, artist, album, number, track)

@functools.cache
def regular_list_tracks():
    return list(list_tracks())

def find_track(filename):
    for root, dirs, files in os.walk(MUSIC_FOLDER, topdown=False):
        if filename in files:
            return root+"/"+filename


def generate_music_row(filename, artist, album, number, track, trackfirst=False):
    html="<tr>"
    html+="<td id='%s'>"%html_idify(filename.split('/')[-1])
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

import unicodedata

def generate_music_page():
    html=generate_shuffle_button()
    html+=" - <a href='/'>Home</a>"
    html+="<table><thead><tr><th></th><th>Track</th><th><a href='/music/artist'>Artist</a></th>"
    #html+="<th colspan='2'><a href='/music/album'>Album</a></th>"
    html+="</tr></thead><tbody>"
    yield html
    for filename, artist, album, number, track in sorted(regular_list_tracks(), key=lambda x: (unicodedata.normalize("NFKD", x[-1]),x[1])):
        yield generate_music_row(filename, artist, album, number, track, trackfirst=True)
    yield "</tbody></table>"

def generate_artists_page():
    html="<a href='/music/'>Back to music...</a>"
    html+="<table><tbody>"
    yield html
    for ele in sorted(filter(lambda x: x is not None,set(map(lambda x: x[1], regular_list_tracks())))):
        if ele.strip().isnumeric():
            continue
        if len(sorted(filter(lambda x: x[1]==ele, regular_list_tracks()), key=lambda x: x[-1]))<6:
            continue
        yield "<tr><td><a href=\"%s/\">%s</a></td></tr>"%(ele,ele)
    yield "</tbody></table>"

def generate_artist_page(artist):
    albums = sorted(filter(lambda x: x is not None,set(map(lambda x: x[2], filter(lambda x: x[1]==artist, regular_list_tracks())))))
    html=""
    html+="<a href='/music/artist/'>Back to artists...</a>"
    if len(albums)>0:
        html+="<h1><small>Albums by </small>%s</h1>"%artist
        html+="<table><tbody>"
        for ele in albums:
            html+="<tr><td><a href=\"playalbum/%s\"><h2>%s</h2></a>"%(ele, ele)
            songs = sorted(filter(lambda x: x[1]==artist and x[2]==ele, regular_list_tracks()), key=lambda x: x[-2] if x[-2] is not None else x[-1])
            html+="<table><tbody>"
            for song in songs:
                html+=generate_music_row(*song, trackfirst=None)
            html+="</tbody></table>"
            html+="</td></tr>"
            yield html
            html=""
        html+="</tbody></table>"
    yield html
    songs = sorted(filter(lambda x: x[1]==artist and x[2] is None, regular_list_tracks()), key=lambda x: x[-1])
    if len(songs)>0:
        html=""
        if len(albums)>0:
            html+="<hr/>"
        html+="<h1><small>Songs by </small>%s</h1>"%artist
        html+="<table><tbody>"
        yield html
        for song in songs:
            yield generate_music_row(*song, trackfirst=None)
        yield "</tbody></table>"

porny=False
def perform_shuffle(inner=False):
    if not shuffle:
        return
    create_player()
    if not player.idle_active and len(player.playlist)-player.playlist_playing_pos>1:
        return
    played_files=set(os.listdir('cache/started'))
    if porny:
        if pornfolder==[]:
            tracks = list(os.listdir(config["Folders"]["Uploads"]))
        else:
            tracks = []
            for folder in pornfolder:
                for root, dirs, files in os.walk(os.path.expanduser(commands[folder]), topdown=False):
                    for f in files:
                        if f[0]==".":
                            continue
                        if f.split(".")[-1].lower() not in config["Shuffle"]["AllowedExtensions"].split(","):
                            continue
                        tracks.append(os.path.join(root,f))
    else:
        tracks = list(map(lambda x: x[0],regular_list_tracks()))
    random.shuffle(tracks)
    for ele in tracks:
      try:
        if not os.path.exists('cache/started/%s.started'%ele.split("/")[-1]):
            if porny:
                if pornfolder==[]:
                    mpv_handle_play_file(os.path.join(config["Folders"]["Uploads"],ele), True)
                else:
                    mpv_handle_play_file(ele, True)
            else:
                mpv_handle_play_file(find_track(ele), True)
            break
      except Exception:
        continue
    else:
        for ele in tracks:
          if os.path.exists('cache/started/%s.started'%ele.split("/")[-1]):
            os.remove('cache/started/%s.started'%ele.split("/")[-1])
        if not inner:
          perform_shuffle(True)
    if porny and not inner:
        perform_shuffle(True)
    if not inner:
        telegram_send_started()

resolve_url=None
def unfold_resolve(yieldeable):
    global resolve_url
    text=""
    for ele in yieldeable:
        if resolve_url is not None:
            text+=ele
            if f"id=\"{resolve_url}\"" in text:
                yield text
                resolve_url=None
        else:
            yield ele


@app.route("/folder/")
def folder_basepage():
    return generate_page(generate_folderpage(), "Folders")


@app.route("/folder/<foldername>/")
def folder(foldername):
    if "/" in foldername:
        return
    return unfold_resolve(generate_page(generate_folderpage(foldername,["mp3","flac","wav","mp4",'mkv',"webm", "jpg","jpeg","png","gif"]), foldername.capitalize()))


@app.route("/folder/<foldername>/play/<name>")
def folder_play(foldername,name):
    global resolve_url
    resolve_url=html_idify(name)
    mpv_handle_play_file(os.path.expanduser(os.path.join(config['Commands'][foldername],name)))
    return redirect('/folder/%s/#%s'%(foldername,html_idify(name)))

@app.route("/download/<filename>")
def download(filename):
    if "/" in filename:
        return
    return send_from_directory(config["Folders"]["Uploads"], filename)

@app.route("/download/")
def telegram_download():
    return generate_page(generate_telegrampage(None, True), "Download")

@app.route("/download/play/<filename>")
def telegram_download_play(filename):
    return redirect('/download/'+filename)

@app.route("/telegram/", methods=['GET', 'POST'])
def telegram_page():
    if request.method == 'POST':
        file = request.files['file']
        if '/' in file.filename:
            return ''
        if file.filename != '':
            file.save(os.path.join(config['Folders']["Uploads"], file.filename))
            mpv_handle_play_file(os.path.join(config['Folders']["Uploads"],file.filename))
        return redirect('/telegram')
    return unfold_resolve(generate_page(generate_telegrampage(), "Telegram"))

@app.route("/telegram/play/<name>")
def telegram_play(name):
    global resolve_url
    resolve_url=html_idify(name)
    mpv_handle_play_file(os.path.join(config['Folders']["Uploads"],name))
    return redirect('/telegram/#%s'%html_idify(name))

@app.route("/telegram/videos/")
def telegram_videopage():
    return unfold_resolve(generate_page(generate_telegrampage(["mp4",'mkv',"webm"]), "Telegram"))

@app.route("/telegram/videos/play/<name>")
def telegram_videoplay(name):
    global resolve_url
    resolve_url=html_idify(name)
    mpv_handle_play_file(os.path.join(config['Folders']["Uploads"],name))
    return redirect('/telegram/videos/#%s'%html_idify(name))

@app.route("/music/")
def music():
    return generate_page(generate_music_page(), "Music")

@app.route("/music/shuffle")
def music_shuffle():
    global shuffle
    shuffle = not shuffle
    create_player()
    perform_shuffle()
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
    return redirect('/music/#%s'%html_idify(name))

@app.route("/music/artist/<artist>/play/<name>")
def music_artist_play(artist,name):
    mpv_handle_play_file(find_track(name))
    return redirect('/music/artist/'+artist+"/#"+html_idify(name))

@app.route("/music/artist/<artist>/pause")
def music_artist_pause(artist):
    mpv_handle_pause()
    return redirect('/music/artist/'+artist)

@app.route("/music/artist/<artist>/playalbum/<name>")
def music_album_play(artist,name):
    for ele in sorted(filter(lambda x: x[1]==artist and x[2]==name, regular_list_tracks()), key=lambda x: x[-2] if x[-2] is not None else x[-1]):
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
    mpv_handle_play_file("https://www.youtube.com/watch?v="+video)
    return redirect('/#%s'%html_idify(video))

@app.route("/user/<name>/play/<video>")
def user_play(name, video):
    mpv_handle_play_file("https://www.youtube.com/watch?v="+video)
    return redirect('/user/%s/#%s'%(name, video))

@app.route("/user/<name>/endless/play/<video>")
def user_play_endless(name, video):
    mpv_handle_play_file("https://www.youtube.com/watch?v="+video)
    return redirect('/user/%s/endless/#%s'%(name, html_idify(video)))

@app.route("/user/")
def users():
    def generate_users_page():
        yield "<a href='/'>Home</a><br/><br/><table>"
        for ele in sorted(os.listdir(os.path.join(config["Folders"]["Cache"],"user"))):
            name=ele.split(".")[0]
            yield "<tr><td><a href=\"%s\">%s</a></td></tr>"%(name,name)
        yield "</table>"
    return generate_page(generate_users_page(), "Recent youtube channels")
@app.route("/user/<name>/")
def user(name):
    if '..' in name or '/' in name:
        return
    name=name.lower()
    info = get_ytdlp_info("https://www.youtube.com/@%s/videos"%name, "user/%s.json"%name)
    return generate_page(generate_channelpage(info,
    subscriptions = request.cookies.get('subscriptions')), info['channel'])

@app.route("/user/<name>/endless/")
def user_endless(name):
    if '..' in name or '/' in name:
        return
    name=name.lower()
    info = get_ytdlp_info("https://www.youtube.com/@%s/videos"%name, "user/%s.json"%name, True)
    return generate_page(generate_channelpage(info, True, request.cookies.get('subscriptions')), info['channel'])

@app.route("/channel/<name>/play/<video>")
def channel_play(name, video):
    mpv_handle_play_file("https://www.youtube.com/watch?v="+video)
    return redirect('/channel/%s/#%s'%(name, html_idify(video)))

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
    mpv_handle_play_file("https://www.youtube.com/watch?v="+videoid)
    info = get_ytdlp_info("https://www.youtube.com/channel/%s/videos"%name, "channel/%s.json"%name)
    return generate_page(generate_channelpage(info), info['channel'])

@app.route("/channel/<name>/endless")
def channel_endless(name):
    if '..' in name or '/' in name:
        return
    name=name.lower()
    info = get_ytdlp_info("https://www.youtube.com/channel/%s/videos"%name, "channel/%s.json"%name, True)
    return generate_page(generate_channelpage(info, True), info['channel'])

@app.route("/search/<name>/play/<video>")
def search_play(name, video):
    if os.path.exists("cache/search/%s.txt"%video):
        with open("cache/search/%s.txt"%video, "r") as f:
            mpv_handle_play_file(download_from_url(f.read()))
    else:
        mpv_handle_play_file("https://www.youtube.com/watch?v="+video)
    return redirect('/search/%s/#%s'%(name, html_idify(video)))

@app.route("/search/<name>/pause")
def search_pause(name):
    mpv_handle_pause()
    return redirect('/search/%s/'%name)

@app.route("/search/")
def search_base():
    searchtterm=request.args.get('search')
    if searchtterm is None:
        return redirect("/user/")
    if searchtterm.startswith("/"):
        bot_command(searchtterm, None)
        return redirect("/")
    for e in extractor.list_extractor_classes():
        if e.working() and e.suitable(searchtterm) and e.IE_NAME != "generic":
            try:
                mpv_handle_play_file(searchtterm, True)
                return redirect('/')
            except Exception as e:
                pass
    return redirect(url_for('search',name = searchtterm))

@app.route("/search/<path:name>/")
def search(name):
    full_name=name
    if request.query_string:
        full_name+="?"+request.query_string.decode()
    print(full_name)
    if full_name.startswith(">"):
        bot_command("/"+full_name[1:], None)
        return redirect("/")
    for e in extractor.list_extractor_classes():
        if e.working() and e.suitable(full_name) and e.IE_NAME != "generic":
            try:
                mpv_handle_play_file(full_name, True)
                return redirect('/')
            except Exception as e:
                pass
    #if '..' in name or '/' in name:
    #    return
    hashname = int.from_bytes(hashlib.sha256(name.encode('utf-8')).digest()[:8], byteorder='big', signed=True)
    deepwebsearch=search_results_deepweb(name)
    info = get_ytdlp_info("ytsearch12:%s"%name, "search/%16x.json"%hashname)
    songsearch = sorted(set(filter(lambda x: (x[1] is not None and name.lower() in x[1].lower()) or (x[2] is not None and name.lower() in x[2].lower()) or name.lower() in x[-1].lower(), regular_list_tracks())), key=lambda x: list(map(lambda x: "" if x is None else x, x[1:])))
    name=name.replace("<","&gt;").replace("&","&amp;")
    return generate_page(generate_searchpage(info, name, songsearch, deepwebsearch), "Searched for: %s"%name)

def generate_home_page(index, subscriptions):
    windex=int(index)+1
    index=windex*36
    html='<h1>Welcome to Mii\'s Dukebox!</h1>'
    html+='<a href="/music/">Local music</a> - <a href="/telegram/">Uploads</a> - <a href="/folder/">Folders</a>'
    yield html
    html=""
    if subscriptions is not None:
        subscriptions = set(sorted(subscriptions.split(',')))
        pages = []
        for i in range(index):
            pages.append([])
        yield '<section class="videogrid">'
        anydone=False
        for user in subscriptions:
            if user=='':
                continue
            info = get_ytdlp_info("https://www.youtube.com/@%s/videos"%user, "user/%s.json"%user)
            for i, ment in enumerate(info['entries']):
                if 'availability' in ment and ment['availability'] is not None and ment['availability'] not in ('unlisted','public'):
                    continue
                ment['channel']=info['channel']
                ment['channel_id']=info['channel_id']
                ment['uploader']=info['uploader']
                ment['uploader_id']=info['uploader_id']
                if i==0:
                    if not os.path.exists("cache/watched/%s.watched"%ment["id"]):
                        yield generate_description(ment, clickable=True, fromhome=True)
                        anydone=True
                else:
                    pages[i-1].append(ment)
        yield "</section>"
        if anydone:
            yield "<hr/>"
        for page in pages:
            page=sorted(page, key=lambda info: info['uploader_id'])
            page=sorted(page, key=lambda info: os.path.exists('cache/started/%s.started'%info['id']))
            html='<section class="videogrid">'
            anydone=False
            for info in page:
                if not os.path.exists("cache/watched/%s.watched"%info["id"]):
                    anydone=True
                    html+=generate_description(info, clickable=True, fromhome=True)
            html+="</section><hr/>"
            if anydone:
                yield html
        yield ", ".join(sorted(subscriptions))
        yield "<h2 style='margin:auto;'><a href='%d'>Load more...</a></h2>"%windex
    #return html

@app.route("/")
@app.route("/<int:index>")
def home(index=0):
    if index>99:
        index=0
    subscriptions=request.cookies.get('subscriptions')
    return generate_page(generate_home_page(index, subscriptions), 'Mii\'s Dukebox!')

@app.route("/footer/")
def footer():
    return generate_footer()

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

@app.route("/seek/<int:value>")
def seek(value):
    if player is not None:
        seekpos = max(0, min(player.duration,value))
        player.seek(seekpos,"absolute")
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

other_thread=None
other_thread_stop=False

def quit(*args, **kwargs):
    global other_thread_stop
    other_thread_stop = True
    if blank and "Blanking" in config:
        os.system(config["Blanking"]["Unblank"])
    telegram_bot_send_message_all("Goodbye and 'till next time!", pinned=False)
    if last_global_messages is not None:
        for message, chat in last_global_messages:
            telegram_bot_execute("unpinAllChatMessages", {"chat_id": chat})
            telegram_bot_execute("deleteMessage",{"message_id":message,"chat_id":chat})
    #if other_thread:
    #    other_thread.terminate()
    if shutdown and "Blanking" in config:
        os.system(config["Blanking"]["Shutdown"])
    sys.exit(0)

if __name__ == "__main__":
    import signal
    if blank and "Blanking" in config:
        os.system(config["Blanking"]["Init"])
    ip=get_ip()
    home_url = "%s:%s/"%(ip, config["Server"]["Port"])
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)
    print("connect to %s"%home_url)
    def bot_updates():
        while True:
            try:
                telegram_bot_process_updates()
            except Exception as e:
                print(traceback.format_exc())
            time.sleep(1)
            if other_thread_stop:
                break
    other_thread = threading.Thread(target=bot_updates)
    other_thread.daemon = True
    other_thread.start()
    if "Telegram" in config:
     text="Good morning my ladies and gents."
     telegram_bot_send_message_all("Good morning my ladies and gents.", pinned=False)
     telegram_bot_send_message_all("To play a file please visit http://%s or send a file or link!"%home_url)
     text="This bot is for managing the media player at @MiifoxNew's home. Send files to it or have fun!"
     telegram_bot_execute("setMyDescription", {"language_code":"en", "description":text})
     telegram_bot_execute("setMyShortDescription", {"language_code":"en", "short_description":text})
    app.run(host=ip, port=config["Server"]["Port"])
