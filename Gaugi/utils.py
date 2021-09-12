#coding: utf-8
__all__ = []


import numpy as np
import pickle as cPickle
import gzip
import tarfile
import tempfile
import os
import sys
import shutil
import signal
import inspect
import numpy as np
from Gaugi import RCM_NO_COLOR, RCM_GRID_ENV
from time import sleep, time



def expand_path(path):
  " Returns absolutePath path expanding variables and user symbols "
  if not isinstance( path, basestring):
    raise BadFilePath(path)
  try:
    return os.path.abspath( os.path.join(os.path.dirname(path), os.readlink( os.path.expanduser( os.path.expandvars( path ) ) ) ) )
  except OSError:
    return os.path.abspath( os.path.expanduser( os.path.expandvars( path ) ) )



def expand_folders( pathList, filters = None, logger = None, level = None):
  """
    Expand all folders to the contained files using the filters on pathList

    Input arguments:

    -> pathList: a list containing paths to files and folders;
    filters;
    -> filters: return a list for each filter with the files contained on the
    list matching the filter glob.
    -> logger: whether to print progress using logger;
    -> level: logging level to print messages with logger;

    WARNING: This function is extremely slow and will severely decrease
    performance if used to expand base paths with several folders in it.
  """
  if not isinstance( pathList, (list,tuple,) ):
    pathList = [pathList]
  from glob import glob
  if filters is None:
    filters = ['*']
  if not( type( filters ) in (list,tuple,) ):
    filters = [ filters ]
  retList = [[] for idx in range(len(filters))]
  from Gaugi.utils import progressbar, traverse
  pathList = list(traverse([glob(path) if '*' in path else path for path in traverse(pathList,simple_ret=True)],simple_ret=True))
  for path in progressbar( pathList, len(pathList), 'Expanding folders: ', 60, 50,
                           True if logger is not None else False, logger = logger,
                           level = level):
    path = expand_path( path )
    if not os.path.exists( path ):
      raise ValueError("Cannot reach path '%s'" % path )
    if os.path.isdir(path):
      for idx, filt in enumerate(filters):
        cList = filter(lambda x: not(os.path.isdir(x)), [ f for f in glob( os.path.join(path,filt) ) ])
        if cList:
          retList[idx].extend(cList)
      folders = [ os.path.join(path,f) for f in os.listdir( path ) if os.path.isdir( os.path.join(path,f) ) ]
      if folders:
        recList = expand_folders( folders, filters )
        if len(filters) is 1:
          recList = [recList]
        for l in recList:
          retList[idx].extend(l)
    else:
      for idx, filt in enumerate(filters):
        if path in glob( os.path.join( os.path.dirname( path ) , filt ) ):
          retList[idx].append( path )
  if len(filters) is 1:
    retList = retList[0]
  return retList



def ensure_extension( filename, extension ):
  return filename if filename.endswith(extension) else filename + '.' + extension


def check_extension( filename , extension):
  return True if filename.endswith("."+extension) else False
  

def mkdir_p(path):
  import errno
  path = os.path.expandvars( path )
  try:
    if not os.path.exists( path ):
      os.makedirs(path)
  except OSError as exc: # Python >2.5
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else: raise IOError



def save( d, filename, protocol='savez_compressed', allow_pickle=True):
  if prototol == 'savez_compressed':
    np.savez(ensure_extension(filename, 'npz') , **d, protocol = 'savez_compressed', allow_pickle=allow_pickle)
  elif prototol == 'savez':
    f = gzip.GzipFile(ensure_extension(filename, 'pic.gz'), 'wb')
    cPickle.dump( d, f )
    f.close()
  else:
    f = open(ensure_extension(filename, 'pic'), 'w')
    cPickle.dump( d, f)
    f.close()


def load( filename, allow_pickle = True ):

  if check_extension(filename, 'npz'):
    return dict(np.load(filename, allow_pickle=allow_pickle))
  elif check_extension(filename, 'pic.gz'):
    return None
  elif check_extension(filename, 'pic'):
    return None
  else:
    return None



def get_property( kw, key, default = None ):
  """
  Use together with None to have only one default value for your job
  properties.
  """
  if not key in kw or kw[key] is None:
    kw[key] = default
  return kw.pop(key)


def check_for_unused_vars(d, fcn = None):
  """
    Checks if dict @d has unused properties and print them as warnings
  """
  for key in d.keys():
    if d[key] is None: continue
    msg = 'Obtained not needed parameter: %s' % key
    if fcn:
      fcn(msg)
    else:
      print('WARNING:%s' % msg)




def progressbar(it, count ,prefix="", size=60, step=1, disp=True, logger = None, level = None,
                no_bl = RCM_GRID_ENV or sys.stdout.isatty(), 
                measureTime = True):
  """
    Display progressbar.

    Input arguments:
    -> it: the iterations collection;
    -> count: total number of iterations on collection;
    -> prefix: the strings preceding the progressbar;
    -> size: number of chars to use on the progressbar;
    -> step: the number of iterations needed for updating;
    -> disp: whether to display progressbar or not;
    -> logger: use this logger object instead o sys.stdout;
    -> level: the output level used on logger;
    -> no_bl: whether to show messages without breaking lines;
    -> measureTime: display time measurement when completing progressbar task.
  """
  from Gaugi import LoggingLevel
  from logging import StreamHandler
  from Gaugi.Logger import nlStatus, resetNlStatus, MyStreamHandler
  import sys
  if level is None: level = LoggingLevel.INFO
  def _show(_i):
    x = int(size*_i/count) if count else 0
    if _i % (step if step else 1): return
    if logger:
      if logger.isEnabledFor(level):
        try:
          fn, lno, func = logger.findCaller() 
        except:
          fn, lno, func, _ = logger.findCaller() 

        record = logger.makeRecord(logger.name, level, fn, lno, 
                                   "%s|%s%s| %i/%i\r",
                                   (prefix, "#"*x, "-"*(size-x), _i, count,), 
                                   None, 
                                   func=func)
        record.nl = False
        # emit message
        logger.handle(record)
    else:
      sys.stdout.write("%s|%s%s| %i/%i\r" % (prefix, "#"*x, "-"*(size-x), _i, count))
      sys.stdout.flush()



  # end of (_show)
  # prepare for looping:
  try:
    if disp:
      if measureTime:
        from time import time
        start = time()
      # override emit to emit_no_nl
      if logger:
        if not nlStatus(): 
          sys.stdout.write("\n")
          sys.stdout.flush()
        if no_bl:
          prev_emit = []
          # TODO On python3, all we need to do is to change the Handler.terminator
          for handler in logger.handlers:
            if type(handler) is StreamHandler:
              stream = MyStreamHandler( handler )
              prev_emit.append( handler.emit )
              setattr(handler, StreamHandler.emit.__name__, stream.emit_no_nl)
      _show(0)
    # end of (looping preparation)
    # loop
    try:
      for i, item in enumerate(it):
        yield item
        if disp: _show(i+1)
    except GeneratorExit:
      pass
    # end of (looping)
    # final treatments
    step = 1 # Make sure we always display last printing
    if disp:
      if measureTime:
        end = time()
      if logger:
        if no_bl:
          # override back
          for handler in logger.handlers:
            if type(handler) is StreamHandler:
              setattr( handler, StreamHandler.emit.__name__, prev_emit.pop() )
          _show(i+1)
        if measureTime:
          logger.log( level, "%s... finished task in %3fs.", prefix, end - start )
        if no_bl:
          resetNlStatus()
      else:
        if measureTime:
          sys.stdout.write("\n%s... finished task in %3fs.\n" % ( prefix, end - start) )
        else:
          sys.stdout.write("\n" )
        sys.stdout.flush()
  except (BaseException) as e:
    import traceback
    print (traceback.format_exc())
    step = 1 # Make sure we always display last printing
    if disp:
      if logger:
        # override back
        if no_bl:
          for handler in logger.handlers:
            if type(handler) is StreamHandler:
              try:
                setattr( handler, StreamHandler.emit.__name__, prev_emit.pop() )
              except IndexError:
                pass
        try:
          _show(i+1)
        except NameError:
          _show(0)
        for handler in logger.handlers:
          if type(handler) is StreamHandler:
            handler.stream.flush()
      else:
        sys.stdout.write("\n")
        sys.stdout.flush()
    # re-raise:
    raise e
  # end of (final treatments)



def traverse(o, tree_types=(list, tuple),
    max_depth_dist=0, max_depth=np.iinfo(np.uint64).max, 
    level=0, parent_idx=0, parent=None,
    simple_ret=False, length_ret=False):
  """
  Loop over each holden element. 
  Can also be used to change the holden values, e.g.:
  a = [[[1,2,3],[2,3],[3,4,5,6]],[[[4,7],[]],[6]],7]
  for obj, idx, parent in traverse(a): parent[idx] = 3
  [[[3, 3, 3], [3, 3], [3, 3, 3, 3]], [[[3, 3], []], [3]], 3]
  Examples printing using max_depth_dist:
  In [0]: for obj in traverse(a,(list, tuple),0,simple_ret=False): print obj
  (1, 0, [1, 2, 3], 0, 3)
  (2, 1, [1, 2, 3], 0, 3)
  (3, 2, [1, 2, 3], 0, 3)
  (2, 0, [2, 3], 0, 3)
  (3, 1, [2, 3], 0, 3)
  (3, 0, [3, 4, 5, 6], 0, 3)
  (4, 1, [3, 4, 5, 6], 0, 3)
  (5, 2, [3, 4, 5, 6], 0, 3)
  (6, 3, [3, 4, 5, 6], 0, 3)
  (4, 0, [4, 7], 0, 4)
  (7, 1, [4, 7], 0, 4)
  (6, 0, [6], 0, 3)
  (7, 2, [[[1, 2, 3], [2, 3], [3, 4, 5, 6]], [[[4, 7], []], [6]], 7], 0, 1) 
  In [1]: for obj in traverse(a,(list, tuple),1): print obj
  ([1, 2, 3], 0, [[1, 2, 3], [2, 3], [3, 4, 5, 6]], 1, 3)
  ([2, 3], 0, [[1, 2, 3], [2, 3], [3, 4, 5, 6]], 1, 3)
  ([3, 4, 5, 6], 0, [[1, 2, 3], [2, 3], [3, 4, 5, 6]], 1, 3)
  ([4, 7], 0, [[4, 7], []], 1, 4)
  ([6], 0, [[[4, 7], []], [6]], 1, 3)
  ([[[1, 2, 3], [2, 3], [3, 4, 5, 6]], [[[4, 7], []], [6]], 7], 2, None, 1, 1)
  In [2]: for obj in traverse(a,(list, tuple),2,simple_ret=False): print obj
  ([[1, 2, 3], [2, 3], [3, 4, 5, 6]], 0, [[[1, 2, 3], [2, 3], [3, 4, 5, 6]], [[[4, 7], []], [6]], 7], 2, 2)
  ([[4, 7], []], 0, [[[4, 7], []], [6]], 2, 3)
  ([[[4, 7], []], [6]], 1, [[[1, 2, 3], [2, 3], [3, 4, 5, 6]], [[[4, 7], []], [6]], 7], 2, 2)
  In [3]: for obj in traverse(a,(list, tuple),3): print obj
  ([[[1, 2, 3], [2, 3], [3, 4, 5, 6]], [[[4, 7], []], [6]], 7], 0, None, 3, 1)
  In [4]: for obj in traverse(a,(list, tuple),4): print obj
  ([[[1, 2, 3], [2, 3], [3, 4, 5, 6]], [[[4, 7], []], [6]], 7], 1, None, 4, 1)
  In [5]: for obj in traverse(a,(list, tuple),5): print obj
  <NO OUTPUT>
  """
  if isinstance(o, tree_types):
    level += 1
    # FIXME Still need to test max_depth
    if level > max_depth:
      if simple_ret:
        yield o
      elif length_ret:
        yield level
      else:
        yield o, parent_idx, parent, 0, level
      return
    skipped = False
    isDict = isinstance(o, dict)
    if isDict:
      loopingObj = o.iteritems()
    else:
      loopingObj = enumerate(o)
    for idx, value in loopingObj:
      try:
        for subvalue, subidx, subparent, subdepth_dist, sublevel in traverse(value 
                                                                            , tree_types     = tree_types
                                                                            , max_depth_dist = max_depth_dist
                                                                            , max_depth      = max_depth
                                                                            , level          = level
                                                                            , parent_idx     = idx
                                                                            , parent         = o ):
          if subdepth_dist == max_depth_dist:
            if skipped:
              subdepth_dist += 1
              break
            else:
              if simple_ret:
                yield subvalue
              elif length_ret:
                yield sublevel
              else:
                yield subvalue, subidx, subparent, subdepth_dist, sublevel 
          else:
            subdepth_dist += 1
            break
        else: 
          continue
      except SetDepth as e:
        if simple_ret:
          yield o
        elif length_ret:
          yield level
        else:
          yield o, parent_idx, parent, e.depth, level
        break
      if subdepth_dist == max_depth_dist:
        if skipped:
          subdepth_dist += 1
          break
        else:
          if simple_ret:
            yield o
          elif length_ret:
            yield level
          else:
            yield o, parent_idx, parent, subdepth_dist, level
          break
      else:
        if level > (max_depth_dist - subdepth_dist):
          raise SetDepth(subdepth_dist+1)
  else:
    if simple_ret:
      yield o
    elif length_ret:
      yield level
    else:
      yield o, parent_idx, parent, 0, level



def list2stdvector(vecType,l):
  from ROOT.std import vector
  vec = vector(vecType)()
  for v in l:
    vec.push_back(v)
  return vec


def stdvector2list(vec, size=None):
  if size:
    l=size*[0]
  else:
    l = vec.size()*[0]
  for i in range(vec.size()):
    l[i] = vec[i]
  return l



def get_attributes(o, **kw):
  """
    Return attributes from a class or object.
  """
  onlyVars = kw.pop('onlyVars', False)
  getProtected = kw.pop('getProtected', True)
  check_for_unused_vars(kw)
  return [(a[0] if onlyVars else a) for a in inspect.getmembers(o, lambda a:not(inspect.isroutine(a))) \
             if not(a[0].startswith('__') and a[0].endswith('__')) \
                and (getProtected or not( a[0].startswith('_') or a[0].startswith('__') ) ) ]