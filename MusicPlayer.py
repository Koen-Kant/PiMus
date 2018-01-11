import vlc                              # pip install python-vlc
import random
import threading
import time


class PlayerThread(threading.Thread):
    def __init__(self, pls, display, host, lib):
        super(PlayerThread, self).__init__()
        self.go = True
        self.mus_go = True
        self.playlist_to_play = None
        self.playing = None
        self.playlists = pls
        self.core = host.get_core()
        self.library = host.get_songs()
        self.LCD = display
        self.lib = lib
        self.inst = vlc.Instance()
        self.player = self.inst.media_player_new()
        self.start()

    def run(self):
        while self.go:
            if self.playlist_to_play:
                self.play_playlists(self.playlist_to_play)
            else:
                time.sleep(0.2)

    def set_playlist_to_play(self, pl):
        self.mus_go = True
        self.playlist_to_play = pl

    def play_playlists(self, pl_id):
        final = None
        if pl_id == "rand":
            final = {'songs': self.lib}
        else:
            for pl in self.playlists.values():
                if pl["id"] == pl_id:
                    final = pl
                    break

        while self.mus_go:
            if final:
                self.play_song(random.choice(final["songs"]))
            else:
                self.mus_go = False
                self.stop_music()

    def play_song(self, song):
        sonx = self.core.get_stream_url(song['id'])
        media = self.inst.media_new(sonx)
        self.player.set_media(media)
        self.player.play()
        song_len = (int(song['durationMillis'])/1000)
        self.LCD.spool_string_value(top_string_to_lcd="{}".format(song["title"][:16]))
        while 0 <= self.player.get_position() < 0.985:
            sec = int(self.player.get_position()*float(song_len))
            percent = int(self.player.get_position()*100)
            self.LCD.spool_string_value(lower_string_to_lcd="{:3}/{:3}s: {:3}%  ".format(sec, song_len, percent))
            time.sleep(0.3)
        self.player.stop()

    def play_random(self):
        self.set_playlist_to_play("rand")

    def stop(self):
        self.go = False
        self.mus_go = False
        self.player.stop()

    def stop_music(self):
        self.player.stop()
        self.mus_go = False
        self.playlist_to_play = None
        self.LCD.spool_string_value("Stopping music..", "  Please wait   ")
        time.sleep(0.3)
