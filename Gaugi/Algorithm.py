
__all__ = ['Algorithm']

from Gaugi import Logger
from Gaugi import EnumStringification
from Gaugi import StatusCode
from Gaugi import StoreGate
from Gaugi.macros import *
from Gaugi.enumerators import StatusTool, StatusWTD




# Base class used for all tools for this framework
class Algorithm( Logger ):

  def __init__(self, name):
    Logger.__init__(self)
    self._name = name
    # flags
    self._wtd  = StatusWTD.DISABLE
    self._status = StatusTool.ENABLE
    self._initialized = StatusTool.NOT_INITIALIZED
    self._finalized = StatusTool.NOT_FINALIZED
    # services and EDMs
    self._context      = None
    self._storegateSvc = None
    self._dataframe    = None



  def name(self):
    return self._name


  @property
  def dataframe(self):
    return self._dataframe


  @dataframe.setter
  def dataframe(self,v):
    self._dataframe = v


  def setContext( self, context ):
    self._context = context


  def getContext(self):
    return self._context


  def setStoreGateSvc(self,sg):
    self._storegateSvc=sg


  def getStoreGateSvc(self):
    return self._storegateSvc


  @property
  def storeSvc(self):
    if self._storegateSvc is not None:
      return self._storegateSvc
    else:
      MSG_FATAL( self, "Attempted to access storeSvc which wasn't set.")


  @storeSvc.setter
  def storeSvc(self, s):
    if not isinstance(s, StoreGate):
      PRH_MSG_FATAL( self, "Attempted to set StoreGate to instance of non StoreGate type")
    self._storegateSvc=s



  def initialize(self):
    return StatusCode.SUCCESS


  def execute(self, context):
    self.setContext(context)
    self._wtd = StatusWTD.DISABLE
    return StatusCode.SUCCESS


  def finalize(self):
    return StatusCode.SUCCESS



  @property
  def wtd(self):
    "Retrieve the watch dog status"
    return self._wtd

  @wtd.setter
  def wtd(self, v):
    self._wtd = StatusWTD.retrieve(v)


  @property
  def status(self):
    return self._status



  def disable(self):
    MSG_INFO( self, 'Disable %s tool service.',self._name)
    self._status = StatusTool.DISABLE

  def enable(self):
    MSG_INFO( self, 'Enable %s tool service.',self._name)
    self._status = StatusTool.ENABLE



  def init_lock(self):
    self._initialized = StatusTool.IS_INITIALIZED

  def fina_lock(self):
    self._finalized = StatusTool.IS_FINALIZED



  def isInitialized(self):
    if self._initialized is StatusTool.IS_INITIALIZED:
      return True
    else:
      return False

  def isFinalized(self):
    if self._finalized is StatusTool.IS_FINALIZED:
      return True
    else:
      return False


