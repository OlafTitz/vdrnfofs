# VDR-NFO-FS creates a file system for VDR recordings, which maps each
# recording to a single mpg-file and nfo-file containing some meta data.
#
# Copyright (C) 2010 - 2011 by Tobias Grimm
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import sys
import os
import unittest
import xml.etree.ElementTree

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vdrnfofs.vdrnfofs import *

class TestNfo(unittest.TestCase):
    def setUp(self):
        self.video = self.video_dir = os.path.abspath(os.path.dirname(__file__) + '/sample_video_dir')

    def test_not_existing(self):
        node = get_node(self.video, '/does_not_exist_2008-03-28.20.13.99.99.rec.nfo')
        self.assertEqual(None, node)

    def test_nfo(self):
        node = get_node(self.video, '/sample_2008-03-28.20.13.99.99.rec.nfo')
        nfo = xml.etree.ElementTree.fromstring(node.read(0, 4096))
        self.assertEqual('Movie Title', nfo.find('title').text)
        self.assertEqual('A movie about something', nfo.find('plot').text)

    def test_nfo_new(self):
        node = get_node(self.video, '/sample-vdr1.7_2008-03-28.20.13.99.99.rec.nfo')
        nfo = xml.etree.ElementTree.fromstring(node.read(0, 4096))
        self.assertEqual('Movie Title', nfo.find('title').text)
        self.assertEqual('A movie about something', nfo.find('plot').text)
