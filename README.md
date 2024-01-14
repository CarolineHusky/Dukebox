# Dukebox
My own personal watchparty / music listening dealio

```
Warning: This is absolutely not a secure app!

Run it on your local network, among friends; but always keep an eye out and don't be insane.
Cause the programming on this is not how you should design a secure web app.

This is just a bit of fun I made for myself; don't expect too much.
```

This is a music and video (through `yt-dlp`) playing application made entirely in Python, using the `mpv`, `yt-dlp` and `flask` packages.

You can use it to browse youtube and/or a local music library, and queue things to watch on the big screen _(i.e. the laptop running this program)_.

__Functionalities__:
* Multiple users for a single player
* Allows one to search youtube, visit channels, and "subscribe" to a channel  
   (videos from subscribed channels will be shown on the home page, per user cookie)
* Supports sponsorblock
* Allows one to browse a local music library by song name, artist and album; and search.  
   (no IDv3 support, artist album track number and track name are derived from the filename and folder structure)
* Shuffle on the local music folder when the queue runs out
* Queue what video you want to play next by clicking on its thumbnail, or queue an audio file by clicking on its trackname

Run with `python app.py`
