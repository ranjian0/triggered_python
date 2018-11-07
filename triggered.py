import os
import sys
import math
import heapq
import random
import pickle
import pprint as pp
import pyglet as pg
import pymunk as pm
import operator as op
import itertools as it

from enum import Enum
from pyglet.gl import *
from pyglet.window import key, mouse
from contextlib import contextmanager
from pymunk import pyglet_util as putils
from pyglet.text import layout, caret, document
from collections import defaultdict, namedtuple
