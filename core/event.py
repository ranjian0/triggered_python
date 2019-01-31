
#  Copyright 2019 Ian Karanja <karanjaichungwa@gmail.com
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

from enum import Enum

class EventType(Enum):
    KEY_PRESS     = 1
    KEY_RELEASE       = 2
    MOUSE_PRESS   = 3
    MOUSE_RELEASE     = 4
    MOUSE_MOTION = 5
    MOUSE_DRAG   = 6
    MOUSE_SCROLL = 7
    RESIZE = 8

    TEXT = 9
    TEXT_MOTION = 10
    TEXT_MOTION_SELECT = 11

class Signal:

    def __init__(self):
        self.callbacks = set()

    def connect(self, func):
        self.callbacks.add(func)

    def emit(self, *args, **kwargs):
        for meth in self.callbacks:
            if callable(meth):
                meth(*args, **kwargs)
