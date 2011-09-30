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

import os
import stat
import errno
import sys
import fuse
import syslog

from concatenated_file_reader import *
from vdr import *
from filesystemnodes import *

fuse.fuse_python_api = (0, 2)

def get_node(video, path):
    virtual_path, virtual_file_extension = os.path.splitext(path)
    if virtual_file_extension in ['.mpg', '.nfo']:
        p = virtual_path.rfind('_')
        if p > 0:
            video_path = video + '/' + virtual_path[0:p] + '/' + virtual_path[p+1:]
            if not os.path.isdir(video_path):
               return None
            elif virtual_file_extension == '.mpg':
                return MpgNode(video_path)
            elif virtual_file_extension == '.nfo':
                return NfoNode(video_path)
    else:
        if os.path.isdir(video + '/' + path):
            return DirNode(video + path)
    return None

class VdrNfoFsFile:
    def __init__(self, path, flags, *mode):
        self.path = path
        self.node = get_node(VdrNfoFsFile.video_root, path)

    def read(self, size, offset):
        try:
            if not self.node:
                return -errno.ENOENT
            return self.node.read(offset, size)
        except:
            syslog.syslog('VdrFuseFs: Unexpected error for read(%s)' % self.path)

    def release(self, flags):
        self.node.release()

#    def write(self, buf, offset):
#        return 0

#    def _fflush(self):
#        if 'w' in self.file.mode or 'a' in self.file.mode:
#            self.file.flush()

#    def fsync(self, isfsyncfile):

#    def flush(self):

#    def fgetattr(self):
#        return 0

#    def ftruncate(self, len):

#    def lock(self, cmd, owner, **kw):


class VdrNfoFs(fuse.Fuse):
    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        self.video = ""

    def getattr(self, path):
        try:
            node = get_node(self.video, path)
            if node:
                return node.get_stat()
            return -errno.ENOENT
        except:
            syslog.syslog('VdrFuseFs: Unexpected error for getattr(%s): %s' % path)

    def readdir(self, path, offset):
        try:
            yield fuse.Direntry('.')
            yield fuse.Direntry('..')
            node = get_node(self.video, path)
            if node:
                for item in node.content():
                    yield fuse.Direntry(item.file_system_name)
        except:
            syslog.syslog('VdrFuseFs: Unexpected error for readdir(%s)' % path)

    def main(self, *a, **kw):
        VdrNfoFsFile.video_root = self.video
        self.file_class = VdrNfoFsFile
        return fuse.Fuse.main(self, *a, **kw)

def main():
    usage =  "\nVDR-NFO-FS - access VDR recordings as mpg and nfo files\n"
    usage += fuse.Fuse.fusage

    version = "%prog " + fuse.__version__

    fs = VdrNfoFs(version=version,  usage=usage, dash_s_do='setsingle')
    fs.parser.add_option(mountopt="video", default='', help="The video directory containing the VDR recordings")
    fs.parse(values=fs, errex=1)
    fs.main()

if __name__ == '__main__':
    main()
