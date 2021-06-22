"""Utility functions for Mininet."""

import re
import sys
import os

# Python 2/3 compatibility

Python3 = sys.version_info[0] == 3
BaseString = str if Python3 else getattr( str, '__base__' )
Encoding = 'utf-8' if Python3 else None


def dijsktra(src, graph):
    if graph is None:
        return None
    graph = graph
    nodes = [i for i in range(len(graph))]  # Get all nodes
    visited = []  # set of nodes that have been routed
    if src in nodes:
        visited.append(src)
        nodes.remove(src)
    else:
        return None
    distance = {src: 0}  # distances to all nodes from src
    for i in nodes:
        distance[i] = graph[src][i]  # initialize
    path = {src: {src: []}}  # paths to all nodes from src
    k = pre = src
    while nodes:
        mid_distance = float('inf')
        for v in visited:
            for d in nodes:
                new_distance = graph[src][v] + graph[v][d]
                if new_distance < mid_distance:
                    mid_distance = new_distance
                    graph[src][d] = new_distance  # update distance
                    k = d
                    pre = v
        distance[k] = mid_distance
        path[src][k] = [i for i in path[src][pre]]
        path[src][k].append(k)
        visited.append(k)
        nodes.remove(k)
        # print(visited, nodes)
    # return distance, path
    return path


def dijsktra_all(graph):
    dijkstra_path = []
    # print("input graph:")
    # print(graph)
    for i in range(len(graph)):
        dijkstra_path.append(dijsktra(i, graph))
    # print("output path:")
    # print(dijkstra_path)
    return dijkstra_path


def build_graph(nodes, links):
    # print('build graph: ')
    graph = [[float('inf')] * len(nodes) for i in range(len(nodes))]
    for i in range(len(nodes)):
        graph[i][i] = 0
    for link in links:
        node1, node2 = nodes.index(link[0]), nodes.index(link[1])
        graph[node1][node2] = 1
        graph[node2][node1] = 1
    # print(graph)
    return graph


def natural(text):
    "To sort sanely/alphabetically: sorted( l, key=natural )"
    def num(s):
        "Convert text segment to int if necessary"
        return int(s) if s.isdigit() else s
    return [  num( s ) for s in re.split( r'(\d+)', str( text ) ) ]


def naturalSeq( t ):
    "Natural sort key function for sequences"
    return [ natural( x ) for x in t ]


def irange(start, end):
    """Inclusive range from start to end (vs. Python insanity.)
       irange(1,5) -> 1, 2, 3, 4, 5"""
    return range( start, end + 1 )


def list_gml_file(file_dir, write_file):
    files = os.listdir(file_dir)
    files = [file for file in files if file[-4:] == '.gml']
    f = open(write_file, 'w')
    for file in files:
        f.write(file)
        f.write('\n')
    f.close()


def is_gbps(str):
    if str == 'Gbps' or str == 'Gbit/s' or str == 'Gb/s' or str == 'GB/s' or str == 'Gbit/s' or str == 'G' or str == 'gb/s' or str == 'GE':
        return True
    return False


def is_mbps(str):
    if str == 'Mbps' or str == 'Mpbs' or str == 'Mb/s' or str == 'MB/s' or str == 'Mbit/s' or str == 'M' or str == 'mb/s' or str == 'Mb':
        return True
    return False


def return_num_g(str):
    if str == '':
        return False
    if str[0] == '>' or str[0] == '<':
        str = str[1:]
    bw = str.split('*')
    if len(bw) == 2:
        if bw[0] == 'N':
            return float(bw[1])
        return float(bw[0]) * float(bw[1])
    elif len(bw) == 1:
        bw = str.split('-')
        if len(bw) == 2:
            bw = bw[1]
        else:
            bw = bw[0]
        for c in bw:
            if (c < '0' or c > '9') and c != '.':
                return False
        return float(bw)
    return False


def bw_single(bw):
    if return_num_g(bw):
        return return_num_g(bw)
    bw = bw.split('-')
    if len(bw) == 1:
        bw = bw[0]
        if is_gbps(bw[-6:]):
            return return_num_g(bw[0:-6])
        if is_gbps(bw[-2:]):
            return return_num_g(bw[0:-2])
        if is_gbps(bw[-4:]):
            return return_num_g(bw[0:-4])
        elif is_mbps(bw[-4:]):
            return return_num_g(bw[0:-4]) / 1000
        elif is_gbps(bw[-1:]):
            return return_num_g(bw[0:-1])
        elif is_mbps(bw[-1:]):
            return return_num_g(bw[0:-1]) / 1000
        elif is_mbps(bw[-2:]):
            return return_num_g(bw[0:-2]) / 1000
    elif len(bw) == 2:
        return bw_single(bw[1])
    return False


def isnum(str):
    for c in str:
        if c < '0' or c > '9':
            return True
    return False


def linklabel1(str):
    l = len(str)
    if str[l-4:] == 'GEx2':
        return [linklabel(str[:l-4]), 2]
    elif str[l-4:] == 'GEx4':
        return [linklabel(str[:l-4]), 2]
    elif str[l-5:] == 'GEx12' or str[l-5:] == 'Gex12':
        return [linklabel(str[:l-5]), 12]
    elif str[l-4:] == 'GEx8':
        return [linklabel(str[:l-4]), 8]
    elif str[:2] == '2x':
        return [linklabel(str[2:]), 2]
    elif str[:2] == '4*':
        return [linklabel(str[2:]), 4]
    elif str[:3] == '10*':
        return [linklabel(str[3:]), 10]
    elif str[-2:] == 'x2':
        return [linklabel(str[:-2]), 2]
    elif str[-2:] == 'x4':
        return [linklabel(str[:-2]), 4]
    return [linklabel(str), 1]


def linklabel(str):
    if str == 'STM-64':
        return 10
    if str == 'STM-16':
        return 2.5
    if str == 'STM-4':
        return 0.62
    if str[-4:] == '*GbE':
        return linklabel(str[0:-4])
    if str != '':
        bw = str.split(' ')
        if bw[0] == 'Managed' and bw[1] == 'Fiber':
            return bw_single(bw[2][1:-1])
        elif bw[0] == 'Dark' and bw[1] == 'Fiber':
            return bw_single(bw[2][1:-1])
        elif bw[0] == 'CANARIE':
            return bw_single(bw[1][2:])
        if len(bw) == 1:
            a = bw_single(bw[0])
            if a is not False:
                return a
        elif len(bw) == 2:
            if is_gbps(bw[1]):
                return bw_single(bw[0])
            elif is_mbps(bw[1]):
                bw = bw[0].split('-')
                bw = bw[0].split('/')
                if len(bw) == 1:
                    return float(bw[0]) / 1000
                else:
                    return float(bw[1]) / 1000
            elif bw_single(bw[1]) is not False:
                return bw_single(bw[1])
            elif bw_single(bw[0]) is not False:
                return bw_single(bw[1])
        elif len(bw) == 3 or len(bw) == 4:
            if is_gbps(bw[2]):
                return float(bw[1])
            elif is_gbps(bw[1]):
                return float(bw[0])
            elif is_mbps(bw[2]):
                return float(bw[1]) / 1000
            elif is_mbps(bw[1]):
                return return_num_g(bw[0]) / 1000
            elif len(bw) == 4 and bw[3] == 'Gbps':
                return float(bw[2])
            elif len(bw) == 4 and bw[3] == 'Gbps)':
                return return_num_g(bw[2][1:])
            elif len(bw) == 4 and bw[3] == 'MB)':
                return float(bw[2][1:]) / 1000
        elif len(bw) == 7:
            if is_gbps(bw[6]):
                return float(bw[5])
            elif is_mbps(bw[6]):
                return float(bw[5]) / 1000
        elif len(bw) == 5:
            if is_gbps(bw[1]):
                if bw[0][-2:] == 'x1':
                    return float(bw[0][0:-2])

    if str != '' and str != 'Blue Line' and str != 'Light Blue Line' and str != 'fiber':
        print(str)
    return False
