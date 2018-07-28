#!/usr/bin/env python

import cv2

# expects rect( x1, y1, w, h )
def combine( rects, thresh = 1 ):

    if len( rects ) == 0:
        return ( 0, 0, 0, 0 )

    rect_array_x = [ [ rect[ 0 ], rect[ 0 ] + rect[ 2 ] ] for rect in rects ]
    rect_array_y = [ [ rect[ 1 ], rect[ 1 ] + rect[ 3 ] ] for rect in rects ]

    rect_array_x = [ number for inner in rect_array_x for number in inner ]
    rect_array_y = [ number for inner in rect_array_y for number in inner ]

    max_x = max( rect_array_x )
    max_y = max( rect_array_y )
    min_x = min( rect_array_x )
    min_y = min( rect_array_y )

    return ( min_x, min_y, max_x, max_y )

# expects rect( x1, y1, x2, y2 )
def intersection_rect( rect1, rect2 ):
    #  rect is ( x, y, w, h )
    #            0  1  2  3

    #  rect is ( x1, y1, x2, y2 )
    #            0   1   2   3
    x_tl = max( rect1[ 0 ], rect2[ 0 ] )
    y_tl = max( rect1[ 1 ], rect2[ 1 ] )
    x_br = min( rect1[ 2 ], rect2[ 2 ] )
    y_br = min( rect1[ 3 ], rect2[ 3 ] )
    if ( x_tl < x_br and y_tl < y_br ):
        #return (x_tl, y_tl, x_br - x_tl, y_br - y_tl);
        return (x_tl, y_tl, x_br, y_br);

    return None

def intersection( rects ):
    num_rects = len( rects )
    if num_rects == 0:
        return None
    if num_rects == 1:
        return rects[ 0 ]

    intersect_rect = None
    for rect_outer in rects:
        if intersect_rect == None:
            intersect_rect = rect_outer
            continue

        intersect_rect = intersection_rect( rect_outer, intersect_rect )

        # we only care about when all intersect
        if intersect_rect == None:
            break

    return intersect_rect

def draw_rect( dst, x, y, w, h, color ):
    cv2.rectangle( dst, ( int( x ), int( y ) ), ( int( w ), int( h ) ), color, -1 )

# blatently stolen from opencv/samples/python2/common.py
def clock():
    return cv2.getTickCount() / cv2.getTickFrequency()

def draw_str(dst, x, y, s):
    cv2.putText(dst, s, (x+1, y+1), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness = 2, lineType=cv2.LINE_AA)
    cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), lineType=cv2.LINE_AA)


'''
x_overlap = Math.max(0, Math.min(x12,x22) - Math.max(x11,x21));
y_overlap = Math.max(0, Math.min(y12,y22) - Math.max(y11,y21));
'''
