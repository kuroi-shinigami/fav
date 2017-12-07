#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from unittest import TestCase

from FAV import MusicLibrary


class TestMusicLibrary(TestCase):
    def test_no_file(self):
        with self.assertRaises(FileNotFoundError):
            # doesn't exist
            m = MusicLibrary('clementine.db')
