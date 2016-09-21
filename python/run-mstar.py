"""Runs OD-rM* on 50-agent mazes and all DAO map where the map ID modulo 3 = int(sys.argv[1])"""

import subprocess
import multiprocessing
import os
import argparse
import time
import glob
import signal
import sys

    
if __name__ == '__main__':
    def myworker(filepath):
        if 'output' in filepath:
            return
        output_path = os.path.join(os.path.dirname(filepath), 'macbs-over-odrmstar-results', '{}_output.txt'.format(os.path.basename(filepath)))
        if os.path.exists(output_path):
            return
        if not os.path.exists(filepath):
            return
        command = 'python run-macbs-over-odrmstar.py {} --merge_thresh=-17 > {}'.format(filepath, output_path)
        print 'running {}'.format(command)
        try:
            start = time.time()
            subprocess.check_call(command, shell=True)
            end = time.time()
        except:
            #pool.terminate()
            raise
            
    def gen():
        for agents in xrange(50, 51):
            for i in xrange(100):
                if i % 3 == int(sys.argv[1]):
                    yield '/home/ubuntu/efs/maze512-1-2-{}-{}'.format(agents, i)
                    yield '/home/ubuntu/efs/maze512-1-6-{}-{}'.format(agents, i)
                    yield '/home/ubuntu/efs/maze512-1-9-{}-{}'.format(agents, i)
                    yield '/home/ubuntu/efs/maze512-2-2-{}-{}'.format(agents, i)
                    yield '/home/ubuntu/efs/maze512-2-5-{}-{}'.format(agents, i)
                    yield '/home/ubuntu/efs/maze512-2-9-{}-{}'.format(agents, i)
        for agents in xrange(5, 85, 5):
            for i in xrange(100):
                if i % 3 == int(sys.argv[1]):
                    yield '/home/ubuntu/efs/ost003d-{}-{}'.format(agents, i)
                    yield '/home/ubuntu/efs/den520d-{}-{}'.format(agents, i)
                    yield '/home/ubuntu/efs/brc202d-{}-{}'.format(agents, i)
    
    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    pool = multiprocessing.Pool()
    signal.signal(signal.SIGINT, original_sigint_handler)
    try:
        res = pool.map_async(myworker, gen(), chunksize=1)
        res.get(60 * 60 * 24 * 3)
    except KeyboardInterrupt:
        pool.terminate()
    else:
        pool.close()
    pool.join()
