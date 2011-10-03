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

class InfoVdr:
    def __init__(self, filename = None):
        self.values = {'T' : 'Unknown', 'D': 'No Description'}
        if filename:
            with open(filename, 'r') as file:
                for line in file:
                    line = line.rstrip("\r\n")
                    self.values[line[0]] = line[2:]

    def __getitem__(self, key):
        return self.values[key] if self.values.has_key(key) else ''
