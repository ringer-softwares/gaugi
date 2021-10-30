#!/usr/bin/env python3


from Gaugi import LoggingLevel, Logger
from Gaugi import expand_folders
from Gaugi.macros import *

from multiprocessing import Process, Event
from multiprocessing import Queue
from pprint import pprint

import multiprocessing
import os, time, random, sys
import subprocess
import argparse


class Merge( Logger ):

  def __init__(self, fList):
    
    Logger.__init__(self)
    self.fList = expand_folders( fList )
    self.process_pipe = []
    self.output_stack = []
    random.seed(time.time())
    self._base_id = random.randrange(100000)



  def run( self, output, nFilesPerMerge, maxJobs):
    
 

    def chunks(l, n):
      """Yield successive n-sized chunks from l."""
      for i in range(0, len(l), n):
        yield l[i:i + n]
    f = []
    for l in chunks(self.fList, nFilesPerMerge):
      f.append(l)
    fList = f


    while len(fList) > 0:
      if len(self.process_pipe) < int(maxJobs):
        job_id = len(fList)
        f = fList.pop()
        f_str = ''
        for o in f:  f_str+=' '+o
        self.output_stack.append( ('output_%d_%d_merge.root') % (self._base_id, job_id) )
        command = ('hadd -f %s%s') % (self.output_stack[-1],f_str)
        #MSG_INFO( self,  ('adding process into the stack with id %d')%(job_id), extra={'color':'0;35'})
        MSG_INFO( self,  ('adding process into the stack with id %d')%(job_id) )
        proc = subprocess.Popen(command.split(' '))
        pprint(command)
        self.process_pipe.append( (job_id, proc) )
    
      for proc in self.process_pipe:
        if not proc[1].poll() is None:
          #MSG_INFO( self,  ('pop process id (%d) from the stack')%(proc[0]), extra={'color':'0;35'})
          MSG_INFO( self,  ('pop process id (%d) from the stack')%(proc[0]) )
          # remove proc from the pipe
          self.process_pipe.remove(proc)
    
    # Check pipe process
    # Protection for the last jobs
    while len(self.process_pipe)>0:
      for proc in self.process_pipe:
        if not proc[1].poll() is None:
          #MSG_INFO( self,  ('pop process id (%d) from the stack')%(proc[0]), extra={'color':'0;35'})
          MSG_INFO( self,  ('pop process id (%d) from the stack')%(proc[0]) )
          # remove proc from the pipe
          self.process_pipe.remove(proc)
    
    # merge all
    #MSG_INFO( self,  'merge all files...', extra={'color':'0;35'})
    MSG_INFO( self,  'merge all files...')
    f_str = ' '
    for o in self.output_stack:
      f_str+=o+' '
    os.system('hadd %s %s'%(output, f_str))




mainLogger = Logger.getModuleLogger("prometheus.merge")
parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()

parser.add_argument('-i','--inputFiles', action='store', 
    dest='fList', required = True, nargs='+',
    help = "The input files.")

parser.add_argument('-o','--outputFile', action='store', 
    dest='output', required = True, default = 'merged.root',
    help = "The output file name.")

parser.add_argument('-nm','--nFilesPerMerge', action='store', 
    dest='nFilesPerMerge', required = False, default = 20, type=int,
    help = "The number of files per merge")

parser.add_argument('-mt','--numberOfThreads', action='store', 
    dest='mt', required = False, default = multiprocessing.cpu_count(), type=int,
    help = "The number of threads")



if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)
args = parser.parse_args()

job = Merge(args.fList)
job.run( args.output, args.nFilesPerMerge, args.mt)