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

import glob
import os
import fuse
import stat
import datetime
import time

from concatenated_file_reader import *
from vdr import *

class NodeAttributes(fuse.Stat):
    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

class MpgNode:
    def __init__(self, path):
        self.path = path
        self.mpeg_files = glob.glob(path + '/[0-9]*.vdr')
        if not self.mpeg_files:
            self.mpeg_files = glob.glob(path + '/[0-9]*.ts')
        self.mpeg_files.sort()
        self.file_system_name = os.path.basename(os.path.abspath(path + '/..')) + '_' + os.path.basename(path) + '.mpg'
        self.reader = ConcatenatedFileReader(self.mpeg_files)

    def size(self):
        size = 0
        for file in self.mpeg_files:
            size += os.path.getsize(file)
        return size

    def read(self, offset, size):
        return self.reader.read(offset, size)

    def release(self):
        self.reader.release()

    def get_stat(self):
        attr = NodeAttributes()
        attr.st_mode = stat.S_IFREG | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
        attr.st_nlink = 1
        attr.st_size = self.size()
        timevalues = self.path.rsplit('/', 1)[1][:16].replace('.', '-').split('-')
        attr.st_mtime = time.mktime(datetime.datetime(*[ int(s) for s in timevalues ]).timetuple())
        return attr


class NfoNode:
    def __init__(self, path):
        self.path = path
        self.file_system_name = os.path.basename(os.path.abspath(path + '/..')) + '_' + os.path.basename(path) + '.nfo'
        if os.path.exists(path + '/info.vdr'):
            info_vdr = InfoVdr(path + '/info.vdr')
        elif os.path.exists(path + '/info'):
            info_vdr = InfoVdr(path + '/info')
        else:
           info_vdr = InfoVdr()
        self.nfo_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<movie>
  <title>%s</title>
  <plot>%s</plot>
</movie>
""" % (info_vdr['T'], info_vdr['D'])

    def size(self):
        return len(self.nfo_content)

    def read(self, offset, size):
       return self.nfo_content[offset:offset+size]

    def get_stat(self):
        attr = NodeAttributes()
        attr.st_mode = stat.S_IFREG | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
        attr.st_nlink = 1
        attr.st_size = self.size()
        timevalues = self.path.rsplit('/', 1)[1][:16].replace('.', '-').split('-')
        attr.st_mtime = time.mktime(datetime.datetime(*[ int(s) for s in timevalues ]).timetuple())
        return attr

    def release(self):
        return

class DirNode:
    def __init__(self, path):
        self.path = path
        self.file_system_name = os.path.basename(path)
        self.cache = []

    def content(self):
        if not self.cache:
            for entry in os.listdir(self.path):
                entry = self.path + '/' + entry
                if self.is_sub_folder(entry):
                    self.cache.append(DirNode(entry))
                for recording in glob.glob(entry + '/*.rec'):
                    if os.path.exists(recording + '/info.vdr') or os.path.exists(recording + '/info'):
                        self.cache.append(MpgNode(recording))
                        self.cache.append(NfoNode(recording))
        return self.cache

    def is_sub_folder(self, dir):
        if not os.path.isdir(dir):
            return False
        if dir.endswith('.rec'):
            return False
        for entry in os.listdir(dir):
            if not entry.endswith('.rec'):
                return True
        return False

    def get_stat(self):
        attr = NodeAttributes()
        attr.st_mode = stat.S_IFDIR | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
        attr.st_nlink = 2 + len(self.content())
        return attr
