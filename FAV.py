#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from urllib.parse import urlparse, unquote
import sqlite3

from config import config


class AttrDict(dict):
    def __getattr__(self, attr):
        return self.get(attr)
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Song(AttrDict):
    def __init__(self, **kwargs):
        super().__init__(self, **kwargs)
        self.path = unquote(urlparse(kwargs['filename']).path.decode('utf-8'))
        # Hardcode euristics
        # if not self.title:
        #     self._calculate_title()

    # def _calculate_title(self):
    #     """Method for songs without proper tags (shit happens and happens everytime"""
    #
    #     dirname, fname = os.path.split(self.path)
    #
    #     for sep in ['-']:
    #         if sep in fname:
    #             artist_or_number, title = fname.split(sep)
    #             break   # or not to break?
    #         print(title)
    #         self.title = title

    def __repr__(self):
        # return self._calculate_title()?
        return f'{self.get("artist")} - {self.get("title")}'


# https://docs.python.org/3.6/library/sqlite3.html
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class MusicLibrary:  # make it more abstract/special?
    def __init__(self, fname):  # for now we are assuming local storage (clementine)
        self.cursor = None
        if os.path.exists(fname):
            self.dbfile = fname
            self._connect()
        else:
            with open(fname) as f:
                f.read()

    def _connect(self):
        with sqlite3.connect(self.dbfile) as conn:
            conn.row_factory = dict_factory  # Make factory configurable (again)?
        # Maybe we shouldn't connect once and forever
        self.cursor = conn.cursor()

    def get_playes_and_rated_songs(self, play_count=10, rate=1.0):  # rate in db is float from 0 to 1
        # ToDo: do something with db scheme
        for x in self.cursor.execute('SELECT * FROM songs WHERE playcount>? and rating>=?', (play_count, rate,)):
            yield Song(**x)


def main():
    m = MusicLibrary(config.dbfile)
    for s in m.get_playes_and_rated_songs(10, 0.6):
        print(s)
        print(s.title, s.path, s.rating)
        print("Song attributes: ")
        for x in sorted(s.keys()):
            print(f'\t{x}')
        break
    print("Total rated & played songs: {}".format(len(list(m.get_playes_and_rated_songs(10, 0.6)))))


if __name__ == '__main__':
    config = AttrDict(config)
    main()
