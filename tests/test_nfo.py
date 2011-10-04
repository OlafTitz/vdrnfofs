# -*- coding: utf-8 -*-
#
# VDR-NFO-FS creates a file system for VDR recordings, which maps each
# recording to a single mpg-file and nfo-file containing some meta data.
#
# Copyright (c) 2010 - 2011 by Tobias Grimm
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#   * Neither the name of the author/copyright holder nor the names of
#     contributors may be used to endorse or promote products derived from this
#     software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
