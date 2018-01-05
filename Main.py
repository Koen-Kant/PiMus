from gmusicapi import Mobileclient      # pip install gmusicapi
import time
import RPi.GPIO as GPIO
import MusicPlayer
import LCDDisplay


class Main:
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)

        self.display = LCDDisplay.LCDThread()

        self.display.spool_string_value("GPM-Connecting..", "Please wait     ")

        self.mus = Mobileclient()
        fd = open('Secret.txt', 'r')
        data = fd.read().split("\n")
        fd.close()
        self.mus.login(data[0], data[1], Mobileclient.FROM_MAC_ADDRESS)

        self.Lib = self.mus.get_all_songs()
        self.playlists = self.mus.get_all_user_playlist_contents()

        tplay = self.playlists
        self.playlists = {}

        self.index = 0

        for pl in tplay:
            out = self.append_song_to_playlist(pl, songs=self.Lib)
            self.playlists[out["name"]] = out

        self.lists_w_id = [{'quit': 0}]
        for item in self.playlists.values():
            self.lists_w_id.append({item["name"]: item["id"]})

        self.display.spool_string_value("Ready           ", "Awaiting input  ")
        self.button_set_up()
        self.display.spool_string_value(self.lists_w_id[self.index].items()[0][0][:16])

        self.player = MusicPlayer.PlayerThread(self.playlists, self.display, self, self.Lib)
        self.working = True

        try:
            while self.working:
                time.sleep(10)
        except KeyboardInterrupt:
            pass
        finally:
            self.display.spool_string_value("Stopping...","Have a nice day")
            self.end_clear()

    def get_songs(self):
        return self.Lib

    def get_core(self):
        return self.mus

    # noinspection PyUnusedLocal
    def previous_button(self, channel):  # button left, pin 21
        self.index -= 1
        if self.index < 0:
            self.index = len(self.lists_w_id)-1

        self.display.spool_string_value(self.lists_w_id[self.index].items()[0][0][:16])

    # noinspection PyUnusedLocal
    def next_button(self, channel):  # button right, pin 2
        self.index += 1
        if self.index >= len(self.lists_w_id):
            self.index = 0

        self.display.spool_string_value(self.lists_w_id[self.index].items()[0][0][:16])

    # noinspection PyUnusedLocal
    def accept_button(self, channel):  # button down, pin 24
        if self.lists_w_id[self.index].items()[0][0] == "quit":
            self.working = False
        else:
            self.player.stop_music()
            self.player.set_playlist_to_play(self.lists_w_id[self.index].items()[0][1])

    # noinspection PyUnusedLocal
    def random_button(self, channel):  # button up, pin 19
        self.player.stop_music()
        self.player.play_random()

    def button_set_up(self):
        GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # up
        GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # left
        GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # right
        GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # down

        GPIO.add_event_detect(19, GPIO.RISING, callback=self.random_button, bouncetime=300)
        GPIO.add_event_detect(21, GPIO.RISING, callback=self.previous_button, bouncetime=300)
        GPIO.add_event_detect(23, GPIO.RISING, callback=self.next_button, bouncetime=300)
        GPIO.add_event_detect(24, GPIO.RISING, callback=self.accept_button, bouncetime=300)

    def end_clear(self):
        self.display.stop()
        self.player.stop()
        self.mus.logout()
        GPIO.cleanup()

    # noinspection PyMethodMayBeStatic
    def append_song_to_playlist(self, playlist, mus_entity=None, songs=None):
        if not songs:
            songs = mus_entity.get_all_songs()
        out_list = []
        for track in playlist['tracks']:
            if track['source'] == 2:
                out_list.append(track)
            else:
                for song in songs:
                    if song['id'] == track['trackId']:
                        out_list.append(song)
        playlist['songs'] = out_list
        return playlist


if __name__ == "__main__":
    Main()
