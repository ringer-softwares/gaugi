
__all__ = []

try:
    xrange
except NameError:
    xrange = range

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

try:
  basestring
except NameError:
  basestring = str

import os, multiprocessing
RCM_GRID_ENV = 0 #int(os.environ.get('RCM_GRID_ENV',0))
RCM_NO_COLOR = 0 #int(os.environ.get('RCM_NO_COLOR',1))
OMP_NUM_THREADS = int(os.environ.get('OMP_NUM_THREADS',multiprocessing.cpu_count()))




from . import utils
__all__.extend(utils.__all__)
from .utils import *

from . import StatusCode
__all__.extend(StatusCode.__all__)
from .StatusCode import *

from . import enumerators
__all__.extend(enumerators.__all__)
from .enumerators import *

from . import Logger
__all__.extend(Logger.__all__)
from .Logger import *

from . import Property
__all__.extend(Property.__all__)
from .Property import *

from . import MultiProcessing
__all__.extend(MultiProcessing.__all__)
from .MultiProcessing import *

from . import constants
__all__.extend(constants.__all__)
from .constants import *

from . import EventContext
__all__.extend(EventContext.__all__)
from .EventContext import *

from . import Service
__all__.extend(Service.__all__)
from .Service import *

from . import Algorithm
__all__.extend(Algorithm.__all__)
from .Algorithm import *

from . import StoreGate
__all__.extend(StoreGate.__all__)
from .StoreGate import *

# Import all root classes
try:
  import ROOT
  useROOT=True
except:
  useROOT=Fal
  print ('WARNING: ROOT not found. You will not be able to use the TEventLoop, StoreGate and monet  services provied by the gaugi core.')


if useROOT:
  print('Using all sub packages with ROOT dependence')
  from . import TEventLoop
  __all__.extend(TEventLoop.__all__)
  from .TEventLoop import *

  from . import EDM
  __all__.extend(EDM.__all__)
  from .EDM import *








