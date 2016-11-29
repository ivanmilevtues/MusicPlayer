from prettytable import PrettyTable
from random import randint
import json
from os import walk
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import pygame as music_player
import time


class Song:
    def __init__(self, title, artist, album, length):
        self.title = title
        self.artist = artist
        self.album = album
        self.time = length

    def __str__(self):
        return "{artist} - {title} from {album} - {length}".format(self.artist,
                                                                   self.title,
                                                                   self.album,
                                                                   self.time)

    def __eq__(self, other):
        return self.time == other.time and self.title == other.title and \
               self.artist == other.artist and self.album == other.album

    def __hash__(self):
        return self.title + self.artist + self.album + self.length

    def length(self, seconds=False, minutes=False, hours=False):
        time_list = self.time.split(':')
        time_in_seconds = 0
        time_list = time_list[::-1]
        for i in range(0, len(time_list)):
            time_in_seconds += int(time_list[i]) * 60 ** i
        if seconds:
            return time_in_seconds
        elif minutes:
            return time_in_seconds / 60
        elif hours:
            return time_in_seconds / 60**2

        return self.time


class Playlist:
    def __init__(self, name, repeat=False, shuffle=False):
        self.name = name
        self.repeat = repeat
        self.shuffle = shuffle
        self.songs = []
        self.current = 0

    def add_song(self, song):
        self.songs.append(song)

    def remove_song(self, song):
        for i in range(len(self.songs)):
            if song == self.songs[i]:
                del self.songs[i]
                break

    def add_songs(self, songs):
        self.songs += songs

    def total_length(self):
        return len(self.songs)

    def artist(self):
        result_dict = {}
        for i in self.songs:
            if i.artist in result_dict.keys():
                result_dict[i.artist] += 1
            else:
                result_dict[i.artist] = 1
        return result_dict

    def next_song(self):
        if(self.shuffle):
            self.current = random.ranint(0, len(self.songs) - 1)
        else:
            self.current += 1
            if self.current >= len(self.songs) and self.repeat:
                self.current = 0
            else:
                return "End of playlist reached!"
        return self.songs[self.current]

    def pprint(self):
        t = PrettyTable(['Artist', 'Song', 'Length'])
        for i in self.songs:
            t.add_row([i.artist, i.title, i.time])
        print(t)

    def save(self):
        with open("{0}.json".format(self.name), "w") as of:
            json.dump({"songs": [{i.artist: [i.title, i.album, i.time]}
                                 for i in self.songs]}, of, indent=4)

# Add folder variable or smth so that I know where my music is...
    def play_playlist(self):
        music_player.init()
        while(1):
            music_player.mixer.music.load("../MusicFolder/" + self.songs[self.current].title +
                                    " - " + self.songs[self.current].artist + ".mp3")
            music_player.mixer.music.play()
            time.sleep(float(self.songs[self.current].time))
            self.next_song()

    @staticmethod
    def load(path):
        data = {}
        song_list = []
        with open(path, "r") as of:
            p = Playlist(path.split("."), 0)
            data = json.load(of)
        for i in data["songs"]:
            key = list(i.keys())[0]
            song_list.append(Song(title=i[key][0], artist=key, album=i[key][1],
                                  length=i[key][2]))
        p.add_songs(song_list)
        return p


class MusicCrawler:
    def __init__(self, path):
        self.path = path

    def take_all_files(self):
        music_files = []
        for(dirpath, dirname, filenames) in walk(self.path):
            # print(mutagen.File(filename))
            music_files = ([dirpath + '/' + i for i in filenames])
        return music_files

    def generate_playlist(self):
        New_Playlist = Playlist(self.path.split('/')[-1])
        for i in self.take_all_files():
            curr_song = ID3(i)
            New_Playlist.add_song(Song(title=str(curr_song['TPE1']), artist=str(curr_song["TIT2"]),
                                       album="None", length=str((MP3(i).info.length))))
            # print(str(curr_song['TPE1']) + str("TIT2"))
        return New_Playlist


def main():
    # b = Song(title="Fiesta", artist="Clown", album="The Sons of Odin",
    #          length="3:44")
    # a = Song(title="Kircho", artist="Manowar", album="The Sons of Odin",
    #          length="3:44")
    # s = Song(title="Odin", artist="Manowar", album="The Sons of Odin",
    #          length="3:44")
    # print(s.length())
    # print(s.length(seconds=True))
    # print(s.length(minutes=True))
    # print(s.length(hours=True))
    # pl = Playlist("Playlist1")
    # pl.add_song(b)
    # pl.add_songs([a, s])
    # print(pl.artist())
    # pl.pprint()
    # # pl.save()
    # r_l = Playlist.load("Playlist1.json")
    # r_l.pprint()
    a = MusicCrawler("../MusicFolder")
    pl = a.generate_playlist()
    pl.pprint()
    pl.next_song()
    pl.play_playlist()

if __name__ == '__main__':
    main()
