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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vdrnfofs.vdrnfofs import *

class TestPathToNodeMapping(unittest.TestCase):
    def setUp(self):
        self.video = os.path.abspath(os.path.dirname(__file__) + '/sample_video_dir')

    def test_root(self):
        node = get_node(self.video, '/')
        self.assertEqual('', node.file_system_name)
        self.assertEqual(self.video + '/', node.path)

    def test_subdir(self):
        node = get_node(self.video, '/folder')
        self.assertEqual('folder', node.file_system_name)
        self.assertEqual(self.video + '/folder', node.path)

    def test_mpg(self):
        node = get_node(self.video, '/sample_2008-03-28.20.13.99.99.rec.mpg')
        self.assertEqual('sample_2008-03-28.20.13.99.99.rec.mpg', node.file_system_name)
        self.assertEqual(self.video + '/sample/2008-03-28.20.13.99.99.rec', node.path)
