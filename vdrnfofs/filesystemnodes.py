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
from indexed_file_reader import *
from vdr import *

class FileNode(object):
    def __init__(self, path, extension):
        self.path = path
        self._file_system_name = None
        self.extension = extension

    def file_system_name(self):
        if not self._file_system_name:
            self._file_system_name = '_'.join(self.path.rsplit('/', 3)[-2:]) + '.' + self.extension
        return self._file_system_name

    def get_stat(self):
        orig = os.lstat(self.path)
        attr = fuse.Stat()
        attr.st_mode = stat.S_IFREG | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
        attr.st_nlink = 1
        attr.st_size = self.size()
        timevalues = self.path.rsplit('/', 1)[1][:16].replace('.', '-').split('-')
        attr.st_mtime = time.mktime(datetime.datetime(*[ int(s) for s in timevalues ]).timetuple())
        attr.st_uid = orig.st_uid
        attr.st_gid = orig.st_gid
        return attr

class MpgNode(FileNode):
    def __init__(self, path):
        super(MpgNode, self).__init__(path, 'mpg')
        self._mpeg_files = None
        self._reader = None

    def mpeg_files(self):
        if not self._mpeg_files:
            self._mpeg_files = glob.glob(self.path + '/[0-9]*.ts')
            if not self._mpeg_files:
                self._mpeg_files = glob.glob(self.path + '/[0-9]*.vdr')
            self._mpeg_files.sort()
        return self._mpeg_files

    def reader(self):
        if not self._reader:
            if os.path.exists(self.path + '/cutindex'):
                self._reader = IndexedFileReader(self.path)
            else:
                self._reader = ConcatenatedFileReader(self.mpeg_files())
        return self._reader

    def size(self):
        return self.reader().size

    def read(self, offset, size):
        return self.reader().read(offset, size)

    def release(self):
        if self._reader:
            self._reader.release()


class NfoNode(FileNode):
    def __init__(self, path):
        super(NfoNode, self).__init__(path, 'nfo')
        self._nfo_content = None

    def nfo_content(self):
        if not self._nfo_content:
            info_path = self.path + '/info'
            if not os.path.exists(info_path):
                info_path = self.path + '/info.vdr'
                if not os.path.exists(info_path):
                    info_path = None
            info_vdr = InfoVdr(info_path)
            self._nfo_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<movie>
  <title>%s</title>
  <plot>%s</plot>
</movie>
""" % (info_vdr['T'], info_vdr['D'])
        return self._nfo_content

    def size(self):
        return len(self.nfo_content())

    def read(self, offset, size):
       return self.nfo_content()[offset:offset+size]

    def release(self):
        pass

class DirNode:
    def __init__(self, path):
        self.path = path
        self.cache = []
        self._file_system_name = None

    def file_system_name(self):
        if not self._file_system_name:
            self._file_system_name = self.path.rsplit('/',1)[1]
        return self._file_system_name

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
        orig = os.lstat(self.path)
        attr = fuse.Stat()
        attr.st_mode = stat.S_IFDIR | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
        attr.st_nlink = 2 + len(self.content())
        attr.st_mtime = orig.st_mtime
        attr.st_atime = orig.st_atime
        attr.st_ctime = orig.st_ctime
        attr.st_uid = orig.st_uid
        attr.st_gid = orig.st_gid
        return attr
