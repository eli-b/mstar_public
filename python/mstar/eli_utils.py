#!/usr/bin/python

import argparse
import od_mstar
import time
import subprocess
import multiprocessing
import traceback
import sys
import Queue
from col_set_addition import OutOfTimeError


"""Code to help Eli make his paper"""


def main():
    parser = argparse.ArgumentParser(
        description='Finds to the specified instance file using OD-rM*.  ' +
        'Prints run time then path cost to stdout.  If error, print the ' +
        'string form of the error instead. Will print "Out Of Time" if ' +
        'timed out.  If an unexpected error occurs, will print "ERROR" ' +
        'then the string representation of the error.  Assumes 4 connected ' +
        'grid using sum of costs metric')
    parser.add_argument('test_file', help='Name of instance file to run')
    parser.add_argument('-t', dest='time_limit', action='store',
                        type=float, default=300, help='Time limit to run')
    sys.setrecursionlimit(9999999)
    args = parser.parse_args()

    obs_map, init_pos, goals = read_eli_instance_file(args.test_file)

    # Have found some cases where my timing code slips up, so run in a
    # separate process that can kill runaway processes.  Also forces a
    # cleanup after every run
    try:
        res = timeout_function(
            test_func, (obs_map, init_pos, goals, args.time_limit),
            args.time_limit + 10)
    except OutOfTimeError:
        print 'Out Of Time'
        return
    except Exception as e:
        print 'ERROR: ' + str(e)
        return
    if res is None:
        print 'Out Of Time'
        return
    print res[2]
    print res[1]
    if res[1] < 20000:
        print_solution(res[0])


def test_func(obs_map, init_pos, goals, time_limit):
    start_time = time.clock()
    path, planner = od_mstar.find_path(
        obs_map, init_pos, goals, connect_8=False,
        time_limit=time_limit, get_obj=True)
    cost = planner.get_node(planner.goals, True).cost
    end_time = time.clock() - start_time
    return path, cost, end_time


def print_solution(solution):
    for time_step_position in solution:
        print '|{}|'.format('|'.join('({},{})'.format(x, y) for x,y in time_step_position))


def read_eli_instance_file(file_name):
    """Reads an Eli problem instance and returns converts to M* format

    file_name - name of instance file

    returns: obs_map, init_pos, goals
    obs_map  - occupancy grid matrix
    init_pos - ((x1, y1), (x2, y2), ...) initial position
    goals    - ((x1, y1), (x2, y2), ...) initial position
    """
    f = open(file_name)
    l = f.readline().split('#')[0]
    while not l.startswith('Grid:'):
        l = f.readline().split('#')[0]
    l = f.readline().split('#')[0]
    rows, columns = map(int, l.split(','))
    obs_map = [[0 for x in xrange(columns)] for y in xrange(rows)]
    for row in xrange(rows):
        l = f.readline()
        for col in xrange(columns):
            if l[col] == '@':
                obs_map[row][col] = 1
    l = f.readline()
    assert l.startswith('Agents:')
    l = f.readline().split('#')[0]
    num_agents = int(l)
    init_pos = []
    goals = []
    for i in xrange(num_agents):
        vals = f.readline().split('#')[0].split(',')[1:]
        goals.append((int(vals[0]), int(vals[1])))
        init_pos.append((int(vals[2]), int(vals[3])))
    return obs_map, init_pos, goals


def inner_func(func, args, queue):
    try:
        queue.put(func(*args))
    except Exception as e:
        e_type, e_val, e_traceback = sys.exc_info()
        e.traceback = traceback.format_tb(e_traceback)
        queue.put(e)


def timeout_function(func, args, timeout, run_id=None):
    """Wrapper function to run a function in subprocess with timeout

    func - function to wrap
    args - tuple of arguments
    timeout - timeout in seconds
    run_id  - optional identifier of the run, used for printing

    return:
    result of func(*args)
    None if the process ran away

    raises any exception raised by func
    """

    ret_queue = multiprocessing.Queue()
    inner_proc = multiprocessing.Process(target=inner_func,
                                         args=(func, args, ret_queue))
    inner_proc.start()
    try:
        # Raises Queue.Empty if timeout is exceeded
        val = ret_queue.get(timeout=timeout)
        if isinstance(val, Exception):
            # for l in val.traceback:
            #     print l
            raise val
        return val
    except Queue.Empty:
        # Any processes started by func will be orphaned
        inner_proc.terminate()
        return None


if __name__ == '__main__':
    main()
