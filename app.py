from flask import Flask,redirect, request, send_from_directory
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

blank=True
if blank:
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

MUSIC_FOLDER=os.path.expanduser(config["Folders"]["Music"])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join("cache","telegram")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mkv', 'webp', 'webm'}

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
    overflow-y: hidden;
    width: 100%;
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
figure details summary{
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

home_url = ""
shutdown = False

commands=config["Commands"]

known_forwards={}

def telegram_bot_send_document(chat, filename):
    if filename in known_forwards:
        from_chat, message = known_forwards[filename]
        return telegram_bot_execute("forwardMessage", {"chat_id": chat, "from_chat_id": from_chat, "message_id": message})
    import requests
    url="https://api.telegram.org/bot"+config["Telegram"]["Token"]
    if filename.lower().endswith(".mp4") or filename.lower().endswith(".webm"):
        url+="/sendVideo"
        thumbnail_url=os.path.join(os.path.expanduser(config["Folders"]["Thumbnails"]),get_thumbnail_location(filename))
        if os.path.exists(thumbnail_url):
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


def telegram_bot_execute(command, data=None, method=None):
    try:
        headers={}
        if data is not None:
            data=json.dumps(data).encode("utf-8")
            headers["Content-Length"]=len(data)
            headers["Content-Type"]="application/json"
        url="https://api.telegram.org/bot"+config["Telegram"]["Token"]+"/" + command
        request=urllib.request.Request(url,data,headers,method=method)
        return json.load(urllib.request.urlopen(request))
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode())  # Read the body of the error response
        if "too big" in body['description']:
            raise ValueError("File too big")
        print("ERROR:")
        print(body)
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

def telegram_bot_download_file(file_id, destination=None, chat=None, message=None):
    file_info=telegram_bot_execute("getFile", {"file_id": file_id})
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

def play_url(text):
    print(text)
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

def bot_command(text, chat_id):
    global shuffle
    global shutdown
    global porny
    global user_update_lock
    global hook_sticker_state
    if not blank:
        print("[telegram bot] "+text)
    if text.startswith("/vol"):
        player.volume = max(0, min(300,int(text.split(" ")[-1])))
        return False
    if text.startswith("/speed"):
        player.speed = float(text.lstrip("/speed "))
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
    if text=="/screenshot":
        os.makedirs(config["Folders"]["Screenshots"], exist_ok=True)
        filename=list(map(lambda x: get_info(x['filename']),itertools.dropwhile(lambda x: 'current' not in x or not x['current'], player.playlist)))[0]
        name=filename['title']
        filename=os.path.join("cache","screenshot","%s-%.2f.png"%(name,player.time_pos))
        player.screenshot_to_file(filename)
        while not os.path.exists(filename):
            time.sleep(0.1)
        telegram_bot_send_document(chat_id,filename)
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
    if text=="/next":
        create_player()
        if shuffle:
            perform_shuffle()
        player.playlist_next("force")
        return False
    if text=="/pause":
        create_player()
        player.pause = True
        return False
    if text=="/play":
        create_player()
        player.pause = False
        return False
    if text.startswith("/say "):
        basetext=""
        text=basetext+text[4:]
        telegram_bot_send_message_all(text, pinned=False)
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
    if text=="/hook":
        hook_sticker_state[chat_id]=player.path
        telegram_bot_send_message("Please send the sticker to bind to the currently playing file...", chat_id)
        return False
    if text.startswith("/download") and player is not None and not player.pause:
        filename=" ".join(text.split(" ")[1:])
        watching=False
        if filename=="":
            filename=list(map(lambda x: x['filename'],itertools.dropwhile(lambda x: 'current' not in x or not x['current'], player.playlist)))[0]
            watching=True
        if not (filename.startswith("/") or filename.startswith("cache")):
            text="Downloading..."
            length=len(text.encode('utf-16-le'))//2
            telegram_bot_send_message(text, chat_id, {"type": "italic", "offset": 0, "length": length})
            telegram_bot_execute("sendChatAction",{"chat_id":chat_id,"action":"typing"})
            with yt_dlp.YoutubeDL({"outtmpl": os.path.join(config["Folders"]["Uploads"],'%(title)s.%(ext)s')}) as ydl:
                info=ydl.extract_info(filename, download=True)
                filename = ydl.prepare_filename(info)
        if watching:
            open('cache/started/%s.started'%filename.split('/')[-1], 'a').close()
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
    if text.startswith("/seek"):
        seekpos= max(0, min(100,int(text.split(" ")[-1])))
        player.seek(seekpos,"absolute-percent")
        return False
    if text=="/start" or text=="/status":
        has_updates=True
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

def telegram_bot_process_updates():
    global hook_sticker_state
    has_updates=False
    important_command=False
    for update in telegram_bot_get_updates():
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
                    player.seek(1)
                    continue
                if text.lower()=="z" and player.pause:
                    player.seek(-1)
                    continue
            if ele=="entities":
                for entity in update[ele]:
                    if entity["type"]=="url" and "text" in update:
                        text=update["text"][entity["offset"]:entity["offset"]+entity["length"]]
                        print("[Telegram bot]",text)
                        important_command=True
                        result = play_url(text)
                        if result is not None:
                            telegram_bot_send_message(result, update["chat"]["id"])
                        else:
                            has_updates=True
                    if entity["type"]=="text_link":
                        text=entity["url"]
                        print("[Telegram bot]",text)
                        important_command=True
                        result = play_url(text)
                        if result is not None:
                            telegram_bot_send_message(result, update["chat"]["id"])
                        else:
                            has_updates=True
                    if entity["type"]=="bot_command" and "text" in update:
                        text=update["text"][entity["offset"]:]
                        text="/"+text.split("/")[1]
                        result=bot_command(text, update["chat"]["id"])
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
                            config["StickerHooks"][update[ele]["file_unique_id"]]=hook_sticker_state[update["chat"]["id"]]
                            del hook_sticker_state[update["chat"]["id"]]
                            with open("config.ini", "w") as f:
                                config.write(f)
                            telegram_bot_send_message("Fantastic, binding set!", update["chat"]["id"])
                            download_file=None
                        elif update[ele]["file_unique_id"] in config["StickerHooks"]:
                            download_file=config["StickerHooks"][update[ele]["file_unique_id"]]
                            important_command=False
                        else:
                            download_file=telegram_bot_download_file(update[ele]["file_id"],update[ele]["set_name"]+" "+update[ele]["emoji"], update["chat"]["id"], update["message_id"])
                        if player is not None and download_file is not None:
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
                mpv_handle_play_file(download_file, True)
                has_updates=True
        if not important_command:
            telegram_bot_execute("deleteMessage",{"message_id":update["message_id"],"chat_id":update["chat"]["id"]})
    if has_updates:
        telegram_send_started(True)

def telegram_bot_send_message(text, chat, entries=None, silent=False):
    if entries is None:
        return telegram_bot_execute("sendMessage", {"chat_id": chat, "text": text, "disable_notification": silent})
    else:
        return telegram_bot_execute("sendMessage", {"chat_id": chat, "text": text, "entities": entries, "disable_notification": silent})

last_global_messages=None

def telegram_bot_send_message_all(text, entries=None, silent=True, pinned=True):
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
                telegram_bot_execute("editMessageText", {"chat_id": chat, "message_id": message, "text":text, "reply_markup": {"inline_keyboard": keyboard}})
            else:
                telegram_bot_execute("editMessageText", {"chat_id": chat, "message_id": message, "text": text, "entities": entries, "reply_markup": {"inline_keyboard": keyboard}})
        return

    if pinned:
        last_global_messages = []
    for chat in config["Telegram"]["Chats"].split(","):
        if chat!="":
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

current_telegram_message = None
alerted_low_battery = False
def telegram_send_started(silent=True):
    global alerted_low_battery
    playlist=list(map(lambda x: get_info(x['filename']),itertools.dropwhile(lambda x: 'current' not in x or not x['current'], player.playlist)))
    text=""
    battery = psutil.sensors_battery()
    if battery.power_plugged==True and battery.percent<99:
        text+="\u26A1 %02d%% "%battery.percent
        alerted_low_battery = False
    elif battery.percent<36:
        text+="\U0001FAAB %02d%% "%battery.percent
    entities=[]
    for index,entry in enumerate(playlist):
        if index<2:
            offset=len(text.encode('utf-16-le'))//2
            if index==0:
                text+="Currently playing:\n"
            elif index==1:
                text+="\nUp next:\n"
            length=len(text.encode('utf-16-le'))//2-offset
            entities.append({"type": "bold", "offset": offset, "length": length})
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
        text+="%s"%entry['title'].replace("@","\uFF20")
        if 'tumblr_url' in entry:
            length=len(text.encode('utf-16-le'))//2-offset
            entities.append({"type": "text_link", "offset": offset, "length": length, "url": entry['tumblr_url']})
        text+="\n"
    if text=="" and not player.idle_active:
        return
    if shuffle:
        offset=len(text.encode('utf-16-le'))//2
        text+="And then shuffle...\n"
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
    if player == None:
        return None
    videopath="https://youtu.be/"+video
    playlist=list(map(lambda x: x['filename'],itertools.dropwhile(lambda x: 'current' not in x or not x['current'], player.playlist)))
    if videopath in playlist:
        return playlist.index(videopath)
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
    with open(os.path.expanduser(os.path.join(config["Folders"]["Thumbnails"],filename)), "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return "data:image/png;base64, "+encoded_string.decode('ascii')

def generate_thumbnail(info, uploader=None):
    if "telegram_thumbnail" in info and info['telegram_thumbnail'] is not None:
        return "<img src='%s'/>"%generate_b64thumb(info['telegram_thumbnail'])
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

def generate_description(info, uploader=None, clickable=False, mainpage=True):
    if 'fulltitle' in info:
        title=info['fulltitle']
    else:
        title=info['title']
    if clickable and mainpage:
        html="<figure id='%s'>"%html_idify(info['id'].split('/')[-1])
    else:
        html="<figure>"
    if clickable:
        if "/" in info['id']:
            html+="<a href=\"play/%s\">"%info['id'].split("/")[-1]
        else:
            html+="<a href=\"play/%s\">"%info['id']
    html+=generate_thumbnail(info,uploader)
    if clickable:
        html+="</a>"
    html+="<figcaption>"
    if not info['id'].startswith("/") and not info['id'].startswith("cache"):
        html+="<details data-source=\"/describe/%s\"><summary>"%info['id']
    else:
        if info['id'].startswith(os.path.join("cache","telegram")):
            html+="<a class='song' href=\"play/%s\">"%info['title']
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
    if uploader is None and 'uploader' in info:
        if 'uploader_id' in info and info['uploader_id'] is not None:
            html+=' <a href="/user/%s/">%s</a>'%(info['uploader_id'][1:],info['uploader'])
        elif 'channel_id' in info and info['channel_id'] is not None:
            html+=' <a href="/channel/%s/">%s</a>'%(info['channel_id'],info['uploader'])
    if not info['id'].startswith("/") and not info['id'].startswith("cache"):
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

def generate_searchpage(info,searchterm, songsearch):
    html="<h1><small>Searched for: </small>%s</h1>"%(searchterm)
    html+="<a href=\"/\">Home</a>"
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

def generate_telegrampage(ext=None, downloads=False):
    files=os.listdir(config["Folders"]["Uploads"])
    files=list(map(lambda x: os.path.join(config["Folders"]["Uploads"],x), files))
    files=sorted(files, key=lambda x: get_order(x))
    html="<h1>Recently uploaded...</h1>"
    html+="<a href=\"/\">Home</a>"
    if downloads:
        html+=" - <a href=\"/telegram/\">Back...</a><br/><br/>"
    elif ext is None:
        html+=" - <a href=\"/telegram/videos/\">Videos</a>"
        html+=" - <a href=\"/download/\">Download</a><br/><br/>"
    else:
        html+=" - <a href=\"/telegram/\">All uploads</a><br/><br/>"
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
    if not videourl.startswith("http"):
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
        raise
    return info

def get_safe_playlist():
    current=False

    for ele in player.playlist:
        if 'current' in ele and ele['current']:
            current = True
        if current:
            try:
                yield get_info(ele['filename'])
            except Exception as e:
                print(traceback.format_exc())
    if not current:
        return []

def generate_page(page, title):
    html="<html><head><title>%s</title><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"%title#<link rel=\"stylesheet\" href=\"/style.css\">"%title
    html+="<style>"+style()+"</style>"
    if player is not None and not player.pause and player.time_remaining is not None:
        html+="<meta http-equiv=\"refresh\" content=\"%d\">"%(player.time_remaining+random.randint(5,10))
    html+="</head><body>"
    html+="<header><input id='search'/><button id='searchbutton'>Search YT</button>"
    html+="</header>"
    if player is not None:
        playlist=list(get_safe_playlist())
        if len(playlist)>0:
            html+="<footer><div>"
            html+="<details id='oopnext'><summary>Currently playing"
            if len(playlist)>1:
                html+=" (%d)"%len(playlist)
            html+=": <strong>"+playlist[0]['title']+"</strong></summary>"
            html+=generate_description(playlist[0], clickable=True, mainpage=False)
            if len(playlist)>1:
                html+="Up next: <div>"
                for ele in playlist[1:]:
                    html+=generate_description(ele, clickable=True, mainpage=False)
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
var volume = document.getElementById('volume');
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
var search = document.getElementById('search');
var searchbutton = document.getElementById('searchbutton');
searchbutton.addEventListener("click", function(event) {
    if(search.value){
        window.location.href = '/search/'+ search.value;
    }
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
        info = ydl.extract_info(url, download=False)
    return info

infolist={}

def get_ytdlp_info(url, cache, endless=False):
    infolist[url]=cache
    info = None
    os.makedirs(os.path.join(config["Folders"]["Cache"],"/".join(cache.split('/')[:-1])), exist_ok=True)
    if os.path.exists(os.path.join(config["Folders"]["Cache"],cache)):
        with open(os.path.join(config["Folders"]["Cache"],cache)) as f:
            info=json.load(f)
    if info is None or ttl()>info['ttl'] or info['endless']!=endless:
        info=_get_ytdlp_info(url, endless)
        info['ttl']=ttl()+60*15
        info['endless']=endless
        with open(os.path.join(config["Folders"]["Cache"],cache), "w") as f:
            json.dump(info, f, indent="\t")
    return info

screenoff=False
def mpv_handle_start(event):
    global screenoff
    os.makedirs("cache/started", exist_ok=True)
    if len(list(filter(lambda x: x['id']==event.data.playlist_entry_id, player.playlist)))==0:
        perform_shuffle()
        return
    filename = list(filter(lambda x: x['id']==event.data.playlist_entry_id, player.playlist))[0]['filename']
    sponsorblock(filename)
    filename=filename.split('/')[-1]
    if os.path.exists('cache/started/%s.started'%filename):
        os.remove('cache/started/%s.started'%filename)
    open('cache/started/%s.started'%filename, 'a').close()

    if player.vo_configured:
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
        if player is not None and player.playtime_remaining is not None and battery.power_plugged!=True and battery.secsleft<player.playtime_remaining and not alerted_low_battery:
            telegram_bot_send_message_all("\u26A0\U0001FAAB Battery empty in %02d:%02d! \U0001FAAB\u26A0"%divmod(battery.secsleft, 60), pinned=False)
            alerted_low_battery = True



def mpv_handle_play(video):
    global player
    if video is None:
        return
    create_player()

    videopath="https://youtu.be/"+video
    get_info(videopath) #prevents bad paths from entering the queue
    playlist=list(map(lambda x: x['filename'],player.playlist))
    if len(player.playlist) == 0:
        player.play(videopath)
    elif is_in_playlist(video) is not None:
        player.playlist_remove(playlist.index(videopath))
    elif not any(filter(lambda x:'current' in x and x['current'], player.playlist)):
        player.play(videopath)
    else:
        player.playlist_append(videopath)
    telegram_send_started()

def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

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

        @player.property_observer('idle-active')
        def observe_idle(_name, value):
            telegram_send_started(True)

        @player.property_observer('time-pos')
        def observe_time(_name, value):
            time_observer(value)

def mpv_handle_play_file(path, by_telegram=False):
    get_info(path) #prevents bad paths from entering the queue
    create_player()

    playlist=list(map(lambda x: x['filename'],player.playlist))
    if len(player.playlist) == 0:
        player.play(path)
    elif is_in_playlist(path) is not None:
        player.playlist_remove(playlist.index(path))
    elif not any(filter(lambda x:'current' in x and x['current'], player.playlist)):
        player.play(path)
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

def generate_music_page():
    html=generate_shuffle_button()
    html+=" - <a href='/'>Home</a>"
    html+="<table><thead><tr><th></th><th>Track</th><th><a href='/music/artist'>Artist</a></th>"
    #html+="<th colspan='2'><a href='/music/album'>Album</a></th>"
    html+="</tr></thead><tbody>"
    yield html
    for filename, artist, album, number, track in sorted(regular_list_tracks(), key=lambda x: x[-1]):
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
    if len(player.playlist)>1 and len(list(itertools.dropwhile(lambda x: 'current' not in x or not x['current'], player.playlist)))>1:
        return
    #if not any(filter(lambda x:'current' in x and x['current'], player.playlist)):
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
        if not os.path.exists('cache/started/%s.started'%ele.split("/")[-1]):
            if porny:
                if pornfolder==[]:
                    mpv_handle_play_file(os.path.join(config["Folders"]["Uploads"],ele), True)
                else:
                    mpv_handle_play_file(ele, True)
            else:
                mpv_handle_play_file(find_track(ele), True)
            break
    else:
        for ele in tracks:
            os.remove('cache/started/%s.started'%ele.split("/")[-1])
        perform_shuffle(True)
    if porny:
        perform_shuffle(True)
    if not inner:
        telegram_send_started()

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
    return generate_page(generate_telegrampage(), "Telegram")

@app.route("/telegram/play/<name>")
def telegram_play(name):
    mpv_handle_play_file(os.path.join(config['Folders']["Uploads"],name))
    return redirect('/telegram/#%s'%name)

@app.route("/telegram/videos/")
def telegram_videopage():
    return generate_page(generate_telegrampage(["mp4",'mkv',"webm"]), "Telegram")

@app.route("/telegram/videos/play/<name>")
def telegram_videoplay(name):
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
    mpv_handle_play(video)
    return redirect('/#%s'%html_idify(video))

@app.route("/user/<name>/play/<video>")
def user_play(name, video):
    mpv_handle_play(video)
    return redirect('/user/%s/#%s'%(name, video))

@app.route("/user/<name>/endless/play/<video>")
def user_play_endless(name, video):
    mpv_handle_play(video)
    return redirect('/user/%s/endless/#%s'%(name, html_idify(video)))

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
    mpv_handle_play(video)
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
    mpv_handle_play(videoid)
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
    mpv_handle_play(video)
    return redirect('/search/%s/#%s'%(name, html_idify(video)))

@app.route("/search/<name>/pause")
def search_pause(name):
    mpv_handle_pause()
    return redirect('/search/%s/'%name)

@app.route("/search/<path:name>/")
def search(name):
    full_name=name
    if request.query_string:
        full_name+="?"+request.query_string.decode()
    print(full_name)
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
    info = get_ytdlp_info("ytsearch12:%s"%name, "search/%16x.json"%hashname)
    songsearch = sorted(set(filter(lambda x: (x[1] is not None and name.lower() in x[1].lower()) or (x[2] is not None and name.lower() in x[2].lower()) or name.lower() in x[-1].lower(), regular_list_tracks())), key=lambda x: list(map(lambda x: "" if x is None else x, x[1:])))
    name=name.replace("<","&gt;").replace("&","&amp;")
    return generate_page(generate_searchpage(info, name, songsearch), "Searched for: %s"%name)

def generate_home_page(index, subscriptions):
    windex=int(index)+1
    index=windex*36
    html='<h1>Welcome to Mii\'s Dukebox!</h1>'
    html+='<a href="/music/">Local music</a> - <a href="/telegram/">Uploads</a>'
    yield html
    html=""
    if subscriptions is not None:
        subscriptions = set(sorted(subscriptions.split(',')))
        pages = []
        for i in range(index):
            pages.append([])
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
                    pages[i].append(ment)
        html+='<section class="videogrid">'
        for page in pages:
            page=sorted(page, key=lambda info: info['uploader_id'])
            page=sorted(page, key=lambda info: os.path.exists('cache/started/%s.started'%info['id']))
            for info in page:
                if not os.path.exists("cache/watched/%s.watched"%info["id"]):
                    html+=generate_description(info, clickable=True)
                    yield html
                    html=""
        html+="</section>"
        html+="<h2 style='margin:auto;'><a href='%d'>Load more...</a></h2>"%windex
        yield html
    #return html

@app.route("/")
@app.route("/<int:index>")
def home(index=0):
    if index>99:
        index=0
    subscriptions=request.cookies.get('subscriptions')
    return generate_page(generate_home_page(index, subscriptions), 'Mii\'s Dukebox!')

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

other_thread=None
other_thread_stop=False

def quit(*args, **kwargs):
    global other_thread_stop
    other_thread_stop = True
    if blank and "Blanking" in config:
        os.system(config["Blanking"]["Unblank"])
    telegram_bot_send_message_all("Goodbye and 'till next time!", pinned=False)
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
    text="Good morning my ladies and gents."
    telegram_bot_send_message_all("Good morning my ladies and gents.", pinned=False)
    telegram_bot_send_message_all("To play a file please visit http://%s or send a file or link!"%home_url)
    text="This bot is for managing the media player at @MiifoxNew's home. Send files to it or have fun!"
    telegram_bot_execute("setMyDescription", {"language_code":"en", "description":text})
    telegram_bot_execute("setMyShortDescription", {"language_code":"en", "short_description":text})
    app.run(host=ip, port=config["Server"]["Port"])
