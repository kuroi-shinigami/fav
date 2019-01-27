#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import hashlib
import logging
import sqlite3
import datetime

from urllib.parse import urlparse, unquote

from conf import config


# FixMe: won't work woth UserDict
class AttrDict(dict):
    def __getattr__(self, attr):
        return self.get(attr)
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Song(AttrDict):
    """
    Song attributes (Clementine 1.3.1):
        album
        albumartist
        art_automatic
        art_manual
        artist
        beginning
        bitrate
        bpm
        comment
        compilation
        composer
        ctime
        cue_path
        directory
        disc
        effective_albumartist
        effective_compilation
        effective_originalyear
        etag
        filename
        filesize
        filetype
        forced_compilation_off
        forced_compilation_on
        genre
        grouping
        lastplayed
        length
        lyrics
        mtime
        originalyear
        path
        performer
        playcount
        rating
        sampler
        samplerate
        score
        skipcount
        title
        track
        unavailable
        year
    """
    def __init__(self, **kwargs):
        super().__init__(self, **kwargs)
        self.path = unquote(urlparse(kwargs['filename']).path.decode('utf-8'))

    def __repr__(self):
        # return self._calculate_title()?
        return f'{self.get("artist")} - {self.get("title")}'

    @property
    def normalized_tile(self):
        return self.__repr__() + os.path.splitext(self.path)[-1]

    # ToDo: Yes, I known that calculating the hash is expensive and shouldn't be in property
    @property
    def sha256hash(self):
        return get_hash(self.path)

    def copy_to_reference_name(self, dir_to_copy):
        """
        For now, I use '%artist% - %title%.ext' format
        :return:
        """
        if not os.path.exists(dir_to_copy):
            logging.warning("Desired temporary directory doesn't exist: {}. Creating...".format(dir_to_copy))
            os.makedirs(dir_to_copy)

        target_file = os.path.join(dir_to_copy, self.normalized_tile)
        logging.info("Copying {} as {}".format(self.path, target_file))
        shutil.copy2(self.path, target_file)


# https://docs.python.org/3.6/library/sqlite3.html
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_hash(some_file):
    # ToDo: do it in chunks
    if os.path.exists(some_file):
        with open(some_file, 'rb') as f:
            binary = f.read()
        return hashlib.sha256(binary).hexdigest()
    else:
        logging.warning("Couldn't find file to open: {}. Doing nothing!".format(some_file))


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

    def get_played_and_rated_songs(self, play_count=10, rate=1.0):  # rate in db is float from 0 to 1
        # ToDo: do something with db scheme
        for x in self.cursor.execute('SELECT * FROM songs WHERE playcount>? and rating>=?', (play_count, rate,)):
            yield Song(**x)


class SimpleLocalRegistry:
    """
    Keeps hashes of already seen songs
    """
    def __init__(self, storage=os.path.join(os.path.dirname(__file__), 'data', 'registry.txt')):
        self.storage = storage
        self.res = self.get_registry()

    def __contains__(self, item):
        return item in self.res

    # ToDo: Maybe, I want to keep it as local script's sqlite either
    def get_registry(self):
        res = set()
        if not os.path.exists(self.storage):
            return res
        else:
            with open(self.storage, 'r') as f:
                for x in f.read().split("\n"):
                    if x:
                        res.add(x)
            return res

    def add(self, some_string):
        self.res.add(some_string)
        with open(self.storage, 'a') as f:
            f.write(some_string + '\n')


def main():
    m = MusicLibrary(config.dbfile)
    for s in m.get_played_and_rated_songs(config.play_count, config.rate):
        logging.info(s)
        # ToDo: but file may change in original collection idependently of script
        song_hash = s.sha256hash
        if song_hash not in local_registry:
            s.copy_to_reference_name(config.tmp_dir)
            local_registry.add(song_hash)
        else:
            logging.info("It seems that {} has already been copied before. Skipping".format(s))
    logging.info("Total rated & played songs: {}".format(len(list(m.get_played_and_rated_songs(10, 0.6)))))


log_fname = os.path.splitext(os.path.split(__file__)[-1])[0]
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_fname = '{}-{}.log'.format(log_fname, datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
log_fname = os.path.join(log_dir, log_fname)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.FileHandler(log_fname),
                              logging.StreamHandler()])


if __name__ == '__main__':
    config = AttrDict(config)
    local_registry = SimpleLocalRegistry()
    main()
