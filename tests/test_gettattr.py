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
import stat

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vdrnfofs.vdrnfofs import *

class TestPathToNodeMapping(unittest.TestCase):
    def setUp(self):
        self.fs = VdrNfoFs()
        self.fs.video = self.video_dir = os.path.abspath(os.path.dirname(__file__) + '/sample_video_dir')

    def test_root(self):
        attr = self.fs.getattr('/')
        self.assertEqual(stat.S_IFDIR | 0555, attr.st_mode)
        self.assertEqual(2 + 5, attr.st_nlink)

    def test_dir(self):
        attr = self.fs.getattr('/folder')
        self.assertEqual(stat.S_IFDIR | 0555, attr.st_mode)
        self.assertEqual(2 + 6, attr.st_nlink)

    def test_mpg(self):
        attr = self.fs.getattr('/sample_2008-03-28.20.13.99.99.rec.mpg')
        self.assertEqual(stat.S_IFREG | 0444, attr.st_mode)

    def test_nfo(self):
        attr = self.fs.getattr('/sample_2008-03-28.20.13.99.99.rec.nfo')
        self.assertEqual(stat.S_IFREG | 0444, attr.st_mode)
