#!/usr/bin/env python
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
import re

from distutils.core import setup
from distutils.file_util import copy_file
from distutils.command.build_py import build_py
from distutils.command.install_data import install_data

from glob import glob
from subprocess import check_call

setup (
    name='vdrnfofs',
    version='1.0',
    maintainer = "Tobias Grimm",
    maintainer_email = "vdr@e.tobi.net",
    description = "Access VDR recordings as mpg and nfo files",
    license = "GNU GPL v2",
    scripts = ['bin/vdrnfofs'],
    packages = ['vdrnfofs'],
)
