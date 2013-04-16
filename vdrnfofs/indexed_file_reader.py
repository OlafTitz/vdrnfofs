# -*- coding: utf-8 -*-
#
# VDR-NFO-FS creates a file system for VDR recordings, which maps each
# recording to a single mpg-file and nfo-file containing some meta data.
#
# Copyright (c) 2010 - 2013 by Tobias Grimm, Olaf Titz
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
from cStringIO import StringIO

class IndexedFileReader:
    def __init__(self, path):
        self.index = []
        self.size = 0
        with open(path + '/cutindex', 'r') as f:
            offset = 0
            for line in f:
                x = line.split()
                len = int(x[2]) - int(x[1])
                self.index.append([ offset, len, path + '/' + x[0], int(x[1]) ])
                offset += len
            self.size = offset
        self.current_filename = None
        self.current_file = None

    def read(self, offset, size):
        buffer = StringIO()
        ptr = offset
        while (buffer.tell() < size):
            (filename, file_offset, part_len) = self.part_from_offset(ptr)
            if filename:
                if (self.current_filename != filename):
                    if self.current_file:
                        self.current_file.close()
                    self.current_filename = filename
                    self.current_file = open(filename, 'r')
                self.current_file.seek(file_offset)
                r = size - buffer.tell()
                if (r > part_len):
                    r = part_len
                buffer.write(self.current_file.read(r))
                ptr = offset + buffer.tell()
            else:
                break
        return buffer.getvalue()

    def release(self):
        if self.current_file:
            self.current_file.close()

    def part_from_offset(self, offset):
        for x in self.index:
            o = offset - x[0]
            if (o < x[1]):
                return (x[2], x[3] + o, x[1] - o)
        return (None, 0, 0)
