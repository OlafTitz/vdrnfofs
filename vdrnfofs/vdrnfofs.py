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

import os
import stat
import errno
import sys
import fuse
import traceback
import logging

from concatenated_file_reader import *
from vdr import *
from filesystemnodes import *
from nodecache import *

fuse.fuse_python_api = (0, 2)

def format_exception_info(level = 6):
    error_type, error_value, trbk = sys.exc_info()
    tb_list = traceback.format_tb(trbk, level)
    return 'Error: %s \nDescription: %s \nTraceback: %s' % (error_type.__name__, error_value, '\n'.join(tb_list))

def get_node(video, path):
    virtual_path, virtual_file_extension = os.path.splitext(path)
    if virtual_file_extension in ['.mpg', '.nfo']:
        p = virtual_path.rfind('_')
        if p > 0:
            video_path = '/'.join((video, virtual_path[1:p], virtual_path[p+1:]))
            if not os.path.isdir(video_path):
               return None
            elif virtual_file_extension == '.mpg':
                return MpgNode(video_path)
            elif virtual_file_extension == '.nfo':
                return NfoNode(video_path)
    else:
        dir = video + path
        if os.path.isdir(dir):
            return DirNode(dir)
    return None

class VdrNfoFsFile:
    def __init__(self, path, flags, *mode):
        self.path = path
        self.node = get_node(VdrNfoFsFile.video_root, path)
        self.keep_cache = True
        self.direct_io = False

    def read(self, size, offset):
        try:
            if not self.node:
                return -errno.ENOENT
            return self.node.read(offset, size)
        except:
           logging.error('VdrFuseFs: Unexpected error for read(%s): %s' % (self.path, format_exception_info()))

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
        self.video = ''
        self.log = ''
        self.loglevel = 'info'
        self.cache = NodeCache()

    def getattr(self, path):
        try:
            node = self.cache.get(path, lambda x: get_node(self.video, x))
            if node:
                return node.get_stat()
            return -errno.ENOENT
        except:
            logging.error('VdrFuseFs: Unexpected error for getattr(%s): %s' % (path, format_exception_info()))

    def readdir(self, path, offset):
        try:
            yield fuse.Direntry('.')
            yield fuse.Direntry('..')
            node = self.cache.get(path, lambda x: get_node(self.video, x))
            if node:
                for item in node.content():
                    yield fuse.Direntry(item.file_system_name())
        except:
            logging.error('VdrFuseFs: Unexpected error for readdir(%s): %s' % (path, format_exception_info()))

    def main(self, *a, **kw):
        if self.log and self.log != None:
            logging.basicConfig(filename=self.log, level=getattr(logging, self.loglevel.upper()))
        else:
            logging.basicConfig(level=self.loglevel.upper())
        logging.info('Starting vdrnfofs')

        VdrNfoFsFile.video_root = self.video
        self.file_class = VdrNfoFsFile
        return fuse.Fuse.main(self, *a, **kw)

def main():
    usage =  "\nVDR-NFO-FS - access VDR recordings as mpg and nfo files\n"
    usage += fuse.Fuse.fusage

    version = "%prog " + fuse.__version__

    fs = VdrNfoFs(version=version,  usage=usage, dash_s_do='setsingle')
    fs.multithreaded = False
    fs.parser.add_option(mountopt="video", default='', help="The video directory containing the VDR recordings")
    fs.parser.add_option(mountopt="log", default='', help="The log file (default = console)")
    fs.parser.add_option(mountopt="loglevel", default='info', help="The log level (debug, info, warning or error)")
    fs.parse(values=fs, errex=1)
    fs.main()

if __name__ == '__main__':
    main()
