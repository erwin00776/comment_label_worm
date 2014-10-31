__author__ = 'erwin'

import sys
import os
import Image


def check_like(l, r):
    x = int(l) ^ int(r)
    c = 0
    while x > 0:
        c += 1
        x = x & (x-1)
    if c < 3:
        return True
    else:
        return False

def avhash(im):
    if not isinstance(im, Image.Image):
        im = Image.open(im)
    im = im.resize((8, 8), Image.ANTIALIAS).convert('L')
    avg = reduce(lambda x, y: x + y, im.getdate()) / 64
    hashcode = reduce(lambda x, (y, z): x | (z << y),
                       enumerate(map(lambda i: 0 if i < avg else 1, im.getdate())),
                       0)
    return hashcode

def hamming(h1, h2):
    h, d = 0, h1 ^ h2
    while d > 0:
        h += 1
        d &= (d - 1)
    return h

def cluster_fingers(fname):
    fin = open(fname, 'r')
    lines = fin.readlines()
    fin.close()

    fingers = {}
    groups = []
    for line in lines:
        line = line.strip()
        id, finger = line.split()

        group_id = -1
        for i in range(0, len(groups)):
            if group_id >= 0:
                break
            for j in range(0, len(groups[i])):
                other_id = groups[i][j]
                other_finger = fingers[other_id]['finger']
                if check_like(finger, other_finger):
                    group_id = i
                    groups[i].append(id)
                    break

        if group_id < 0:
            groups.append([id])
            group_id = len(groups) - 1
        fingers[id] = {"finger": finger, "group_id": group_id}

    for i in range(0, len(groups)):
        print("group %d %s" % (i, str(groups[i])))

if __name__=="__main__":
    if len(sys.argv)<2:
        print("prog filename")
        exit(0)
    cluster_fingers(sys.argv[1])
