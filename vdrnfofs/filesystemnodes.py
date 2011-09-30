# -*- coding: utf-8 -*-
#
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

import glob
import os
import fuse
import stat

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
        self.path = os.path.normpath(path)
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
         return self.reader.release()

    def get_stat(self):
        attr = NodeAttributes()
        attr.st_mode = stat.S_IFREG | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
        attr.st_nlink = 1
        attr.st_size = self.size()
        return attr


class NfoNode:
    def __init__(self, path):
        self.path = os.path.normpath(path)
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
        return attr


class DirNode:
    def __init__(self, path):
        self.path = os.path.normpath(path)
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
