__author__ = 'erwin'
#coding=utf-8

import numpy

def my_markou():
    '''
    马氏链
    sum( init_status ) == 1
    '''
    transfer_matrix = numpy.matrix([[0.65, 0.28, 0.07],
                                    [0.15, 0.67, 0.18],
                                    [0.12, 0.36, 0.52]
                                    ])
    init_status = numpy.array([0.21, 0.68, 0.11])
    prev_status = init_status
    print('first')
    for i in range(0, 1000):
        cur_status = numpy.dot(prev_status, transfer_matrix)
        if (cur_status == prev_status).all():
            break
        prev_status = cur_status
        print(i, cur_status)

    print('second')
    init_status2 = numpy.array([0.31, 0.12, 0.57])
    #init_status2 = numpy.array([0.75, 0.15, 0.1])
    prev_status = init_status2
    for i in range(0, 1000):
        cur_status = numpy.dot(prev_status, transfer_matrix)
        if (cur_status == prev_status).all():
            break
        prev_status = cur_status
        print(i, cur_status)

if __name__ == '__main__':
    my_markou()
