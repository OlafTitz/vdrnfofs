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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vdrnfofs.vdrnfofs import *

class TestPathToNodeMapping(unittest.TestCase):
    def setUp(self):
        self.video = self.video_dir = os.path.abspath(os.path.dirname(__file__) + '/sample_video_dir')

    def test_root(self):
        node = get_node(self.video, '/')
        self.assertEqual('', node.file_system_name)
        self.assertEqual(self.video, node.path)

    def test_subdir(self):
        node = get_node(self.video, '/folder')
        self.assertEqual('folder', node.file_system_name)
        self.assertEqual(self.video + '/folder', node.path)

    def test_mpg(self):
        node = get_node(self.video, '/sample_2008-03-28.20.13.99.99.rec.mpg')
        self.assertEqual('sample_2008-03-28.20.13.99.99.rec.mpg', node.file_system_name)
        self.assertEqual(self.video + '/sample/2008-03-28.20.13.99.99.rec', node.path)
