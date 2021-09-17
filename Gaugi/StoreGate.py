

__all__ = ['StoreGate','restoreStoreGate']


from Gaugi import Logger, LoggingLevel
from Gaugi import get_property
from Gaugi.utils import expand_path
from Gaugi.utils import ensure_extension

from ROOT import TFile
import numpy as np


#
# StoreGate manager
#
class StoreGate( Logger ) :

  #
  # Constructor
  #
  def __init__( self, outputFile, **kw ):

    Logger.__init__(self)

    outputFile = ensure_extension(outputFile,'root')
    self._restoreStoreGate = get_property(kw,'restoreStoreGate',False)
    filterDirs             = get_property(kw,'filterDirs', None)
    
    self._outputFile = expand_path( outputFile )

    if self._restoreStoreGate:
      import os.path
      if not os.path.exists( outputFile ):
        raise ValueError("File '%s' does not exist" % outputFile)
      self._file = TFile( outputFile, "read")
    else:
      self._file = TFile( outputFile, "recreate")
    
    self._currentDir = ""
    self._objects    = dict()
    self._dirs       = list()

    if self._restoreStoreGate:
      retrievedObjs = self.__restore(self._file, filterDirs=filterDirs)
      for name, obj in retrievedObjs:
        self._dirs.append(name)
        self._objects[name]=obj


  def local(self):
    return self._outputFile


  #
  # Save objects and delete storegate
  #
  def __del__(self):
    self._dirs = None
    self._objects = None
    import gc
    gc.collect()
    if not self._restoreStoreGate:
      self._file.Close()


  def write(self):
    self._file.Write()

  #
  # Create a folder
  #
  def mkdir(self, theDir):
    fullpath = (theDir).replace('//','/')    
    if not fullpath in self._dirs:
      self._dirs.append( fullpath )
      self._file.mkdir(fullpath)
      self._file.cd(fullpath)
      self._currentDir = fullpath
      self._logger.verbose('Created directory with name %s', theDir)

  #
  # Go to the pointed directory
  #
  def cd(self, theDir):
    self._currentDir = ''
    self._file.cd()
    fullpath = (theDir).replace('//','/')
    if fullpath in self._dirs:
      self._currentDir = fullpath
      if self._file.cd(fullpath):
        return True
    self._logger.error("Couldn't cd to folder %s", fullpath)
    return False


  def addHistogram( self, obj ):
    feature = obj.GetName()
    fullpath = (self._currentDir + '/' + feature).replace('//','/')
    if not fullpath.startswith('/'):
      fullpath='/'+fullpath
    if not fullpath in self._dirs:
      self._dirs.append(fullpath)
      self._objects[fullpath] = obj
      #obj.Write()
      MSG_DEBUG(self, 'Saving object type %s into %s',type(obj), fullpath)


  def addObject( self, obj ):
    feature = obj.GetName()
    fullpath = (self._currentDir + '/' + feature).replace('//','/')
    if not fullpath.startswith('/'):
      fullpath='/'+fullpath
    if not fullpath in self._dirs:
      self._dirs.append(fullpath)
      self._objects[fullpath] = obj
      obj.Write()
      MSG_DEBUG(self, 'Saving object type %s into %s',type(obj), fullpath)


  def histogram(self, feature):
    fullpath = (feature).replace('//','/')
    if not fullpath.startswith('/'):
      fullpath='/'+fullpath
    if fullpath in self._dirs:
      obj = self._objects[fullpath]
      #self._logger.verbose('Retrieving object type %s into %s',type(obj), fullpath)
      return obj
    else:
      MSG_WARNING(self, 'Object with path %s doesnt exist', fullpath)
      return None


  def getDir(self, path):
    return self._file.GetDirectory(path)

  #
  # Use this to set labels into the histogram
  #
  def setLabels(self, feature, labels):
    histo = self.histogram(feature)
    if not histo is None:
      try:
	      if ( len(labels)>0 ):
	        for i in range( min( len(labels), histo.GetNbinsX() ) ):
	          bin = i+1;  histo.GetXaxis().SetBinLabel(bin, labels[i])
	        for i in range( histo.GetNbinsX(), min( len(labels), histo.GetNbinsX()+histo.GetNbinsY() ) ):
	          bin = i+1-histo.GetNbinsX();  histo.GetYaxis().SetBinLabel(bin, labels[i])
      except:
        MSG_FATAL(self, "Can not set the labels! abort.")
    else:
      MSG_WARNING(self, "Can not set the labels because this feature (%s) does not exist into the storage",feature)


  def collect(self):
    self._objects.clear()
    self._dirs = list()


  def getObjects(self):
    return self._objects


  def getDirs(self):
    return self._dirs


  def merge(self, sg):
    if isinstance(sg, StoreGate):
      sg = [sg]
    if isinstance(sg, (list,tuple)):
      sg = StoreGateCollection(sg)
    if not isinstance(sg, StoreGateCollection):
      raise TypeError(type(sg))
    from ROOT import TH1, TH2
    for s in sg:
      for path, obj in s.getObjects().iteritems():
        if isinstance(obj, (TH1,TH2)):
          if path in self._objects:
            mobj = self.histogram(path)  
            if mobj: mobj.Add( obj )


  # Use this method to retrieve the dirname and root object
  def __restore(self,d, basepath="/", filterDirs=None):
    """
    Generator function to recurse into a ROOT file/dir and yield (path, obj) pairs
    Taken from: https://root.cern.ch/phpBB3/viewtopic.php?t=11049
    """
    try:
      for key in d.GetListOfKeys():
        kname = key.GetName()
        if key.IsFolder():
          if filterDirs and kname not in filterDirs: 
            continue
          for i in self.__restore(d.Get(kname), basepath+kname+"/"):
            yield i
        else:
          yield basepath+kname, d.Get(kname)
    except AttributeError as e:
      MSG_DEBUG(self, "Ignore reading object of type %s.",type(d))



# helper function to retrieve the storegate using
# a root file as base.
def restoreStoreGate( ifile ):
  return StoreGate( ifile, restoreStoreGate=True )


