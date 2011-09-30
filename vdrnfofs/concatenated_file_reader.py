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

class ConcatenatedFileReader:
    def __init__(self, filenames):
        self.files = [(f, os.path.getsize(f)) for f in filenames]
        self.current_filename = None
        self.current_file = None

    def read(self, offset, size):
        buffer = ""
        ptr = offset
        while (len(buffer) < size):
            (filename, file_offset) = self.filename_from_offset(ptr)
            if filename:
                if (self.current_filename != filename):
                    if self.current_file:
                        self.current_file.close()
                    self.current_filename = filename
                    self.current_file = open(filename, 'r')
                self.current_file.seek(file_offset)
                buffer += self.current_file.read(size - len(buffer))
                ptr = offset + len(buffer)
            else:
                break
        return buffer

    def release(self):
        if self.current_file:
            self.current_file.close()

    def filename_from_offset(self, offset):
        for (filename, size) in self.files:
            if offset >= size:
                offset -= size
            else:
                return (filename, offset)
        return (None, 0)
