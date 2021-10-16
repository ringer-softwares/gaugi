

__all__ = ['StoreGate','restoreStoreGate']


from Gaugi import Logger, LoggingLevel
from Gaugi.macros import *
from Gaugi import get_property
from Gaugi.utils import expand_path
from Gaugi.utils import ensure_extension

from ROOT import TFile
import numpy as np
import os.path
import gc


#
# StoreGate manager
#
class StoreGate( Logger ) :

  #
  # Constructor
  #
  def __init__( self, outputFile, restore=False ):

    Logger.__init__(self)

    outputFile = ensure_extension(outputFile,'root')
    self.__outputFile = expand_path( outputFile )

    if restore:
      if not os.path.exists( self.__outputFile ):
        raise ValueError("File '%s' does not exist" % self.__outputFile)
      self.__file = TFile( self.__outputFile, "read")
    else:
      self.__file = TFile( self.__outputFile, "recreate")
    self.__currentDir = ""
    self.__objects    = dict()
    self.__dirs       = list()

    if restore:
      objs = self.restore(self.__ile)
      for name, obj in objs:
        self.__dirs.append(name)
        self.__objects[name]=obj

  #
  # Get the stored file path
  #
  def local(self):
    return self.__outputFile


  #
  # Save objects and delete storegate
  #
  def __del__(self):
    self.__dirs = None
    self.__objects = None
    gc.collect()
    self.__file.Close()


  def write(self):
    self.__file.Write()

  #
  # Create a folder
  #
  def mkdir(self, theDir):
    fullpath = (theDir).replace('//','/')    
    if not fullpath in self._dirs:
      self.__dirs.append( fullpath )
      self.__file.mkdir(fullpath)
      self.__file.cd(fullpath)
      self.__currentDir = fullpath
      MSG_DEBUG(self, 'Created directory with name %s', theDir)

  #
  # Go to the pointed directory
  #
  def cd(self, theDir):

    self.__currentDir = ''
    self.__file.cd()
    fullpath = (theDir).replace('//','/')
    if fullpath in self.__dirs:
      self.__currentDir = fullpath
      if self.__file.cd(fullpath):
        return True
    MSG_ERROR(self , "Couldn't cd to folder %s", fullpath)
    return False


  def addHistogram( self, obj ):

    feature = obj.GetName()
    fullpath = (self.__currentDir + '/' + feature).replace('//','/')
    if not fullpath.startswith('/'):
      fullpath='/'+fullpath
    if not fullpath in self.__dirs:
      self.__dirs.append(fullpath)
      self.__objects[fullpath] = obj
      #obj.Write()
      MSG_DEBUG(self, 'Saving object type %s into %s',type(obj), fullpath)


  def addObject( self, obj ):

    feature = obj.GetName()
    fullpath = (self.__currentDir + '/' + feature).replace('//','/')
    if not fullpath.startswith('/'):
      fullpath='/'+fullpath
    if not fullpath in self.__dirs:
      self.__dirs.append(fullpath)
      self.__objects[fullpath] = obj
      obj.Write()
      MSG_DEBUG(self, 'Saving object type %s into %s',type(obj), fullpath)


  def histogram(self, feature):
    fullpath = (feature).replace('//','/')
    if not fullpath.startswith('/'):
      fullpath='/'+fullpath
    if fullpath in self.__dirs:
      obj = self.__objects[fullpath]
      #self._logger.verbose('Retrieving object type %s into %s',type(obj), fullpath)
      return obj
    else:
      MSG_WARNING(self, 'Object with path %s doesnt exist', fullpath)
      return None


  def getDir(self, path):
    return self.__file.GetDirectory(path)

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
    self.__objects.clear()
    self.__dirs = list()


  def getObjects(self):
    return self.__objects


  def getDirs(self):
    return self.__dirs


  #
  # Use this method to retrieve the dirname and root object
  #
  def restore(self,d, basepath="/", filterDirs=None):
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
  return StoreGate( ifile, restore=True )


