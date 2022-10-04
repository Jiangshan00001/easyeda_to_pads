def arc_convert_calc(x1, y1, x2, y2, rx, ry, x_rotation, large_arc_flag, sweep_flag):
    # https://www.w3.org/TR/SVG11/paths.html#PathElement
    # https://blog.csdn.net/fuckcdn/article/details/83937140
    # https://github.com/regebro/svg.path/blob/master/src/svg/path/path.py
    # http://svn.apache.org/repos/asf/xmlgraphics/batik/branches/svg11/sources/org/apache/batik/ext/awt/geom/ExtendedGeneralPath.java
    # x1 y1 ab aa ax1 ay1 ax2 ay2

    # x1 y1 Beginning of the arc
    # ab Beginning angle of the arc in tenths of a degree
    # aa Number of degrees in the arc in tenths of a degree
    # ax1, ay1 Lower left point of the rectangle around the circle of the arc
    # ax2, ay2 Upper right point of the rectangle around the circle of the arc
    # ax2 – ax1 = ay2 – ay1 Diameter of the circle of the arc
    # (ax1 + ax2)/2, (ay1 +ay2)/2
    # Coordinates of the center of the arc circle
    import math
    # str->int/float
    x_rotation = float(x_rotation)
    large_arc_flag = int(large_arc_flag)
    sweep_flag = int(sweep_flag)

    dx2 = (x1 - x2) / 2
    dy2 = (y1 - y2) / 2
    sx2 = (x1 + x2) / 2.0
    sy2 = (y1 + y2) / 2.0
    x1_org = x1
    y1_org = y1
    # // Convert angle from degrees to radians

    angle = math.radians(x_rotation)
    # Compute the half distance between the current and the final point
    cosAngle = math.cos(angle)
    sinAngle = math.sin(angle)

    # Step 1 : Compute (x1prim, y1prim)
    x1 = cosAngle * dx2 + sinAngle * dy2
    Px1 = x1 * x1
    y1 = -sinAngle * dx2 + cosAngle * dy2
    Py1 = y1 * y1
    Prx = rx * rx
    Pry = ry * ry

    # check that radii are large enough
    # correct out of range radii
    radius_scale = (Px1 / Prx) + Py1 / Pry
    if radius_scale > 1:
        radius_scale = math.sqrt(radius_scale)
        rx *= radius_scale
        ry *= radius_scale
        Prx = rx * rx
        Pry = ry * ry
    else:
        # SVG spec only scales UP
        radius_scale = 1

    sign = -1 if large_arc_flag == sweep_flag else 1
    sq = ((Prx * Pry) - (Prx * Py1) - (Pry * Px1)) / ((Prx * Py1) + (Pry * Px1))
    if sq < 0:
        sq = 0
    coef = sign * math.sqrt(sq)
    cx1 = coef * ((rx * y1) / ry)
    cy1 = coef * (- (ry * x1) / rx)

    # //step3 compute cx cy from cx1 cy1

    center_x = sx2 + (cosAngle * cx1 - sinAngle * cy1)
    center_y = sy2 + (sinAngle * cx1 + cosAngle * cy1)

    # compute anglestart angleExtent

    # anglestart
    ux = (x1 - cx1) / rx
    uy = (y1 - cy1) / ry
    vx = (-x1 - cx1) / rx
    vy = (-y1 - cy1) / ry
    n = math.sqrt(ux * ux + uy * uy)
    p = ux
    sign = -1.0 if uy < 0 else 1.0
    start_angle = math.degrees(sign * math.acos(p / n))

    start_angle = start_angle % 360

    # angleExtent
    n = math.sqrt((ux * ux + uy * uy) * (vx * vx + vy * vy))
    p = ux * vx + uy * vy
    d = p / n
    sign = -1.0 if (ux * vy - uy * vx) < 0 else 1.0

    # In certain cases the above calculation can through inaccuracies
    # become just slightly out of range, f ex -1.0000000000000002.
    if d > 1.0:
        d = 1.0
    elif d < -1.0:
        d = -1.0
    angle_extent = math.degrees(sign * math.acos(d))

    angle_extent = angle_extent % 360

    if (not sweep_flag) and (angle_extent > 0):
        angle_extent -= 360.0
    elif sweep_flag and (angle_extent < 0):
        angle_extent += 360.0

    # angle_extent=-angle_extent

    return [x1_org, y1_org, int(start_angle * 10), int(angle_extent * 10), center_x - rx, center_y - ry,
            center_x + rx, center_y + ry]


if __name__=='__main__':
    #M 125,75 A100,50 0 0,0 225,125
    test1_param=[125,75,225,125,100,50,0,0,0]
    test2_param=[125,75,225,125,100,50,0,0,1]
    test3_param=[125,75,225,125,100,50,0,1,0]
    test4_param=[125,75,225,125,100,50,0,1,1]

    test_param=[test1_param, test2_param,test3_param, test4_param]
    for i in test_param:
        #x1, y1, x2, y2, rx, ry, x_rotation, large_arc_flag, sweep_flag
        x1,y1,start_angle, angle_delta, conerx1,conery1,conerx2,conery2 =arc_convert_calc(*i)
        print(x1,y1,start_angle, angle_delta, conerx1,conery1,conerx2,conery2)
        print('centerxy:', (conerx1+conerx2)/2,(conery1+conery2)/2 )
        print('start angle:', start_angle)
        print('angle_delta:', angle_delta)