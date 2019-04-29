# flake8: noqa

import logging
from qtpy import QT_VERSION


__appname__ = 'labelme'

QT5 = QT_VERSION[0] == '5'
del QT_VERSION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__appname__)


import _version

import testing
import utils
