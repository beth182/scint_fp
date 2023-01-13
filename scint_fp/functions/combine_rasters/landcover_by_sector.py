# Beth Saunders 13/01/23
# split landcover dataset into sectors by angle and calculate land cover fraction

import matplotlib.pyplot as plt

from shapely.geometry import Point, Polygon
import math


def polar_point(origin_point, angle, distance):
    """
    helper function to calculate point from relative polar coordinates (degrees)
    :param origin_point:
    :param angle:
    :param distance:
    :return:
    """

    return [origin_point.x + math.sin(math.radians(angle)) * distance,
            origin_point.y + math.cos(math.radians(angle)) * distance]


def define_sectors(centre,
                   num_of_sectors,
                   radius,
                   start=0,
                   end=360,
                   steps=90):
    """

    :param centre: Centre point (coord) of circle. Given as a shapely.geometry.Point (e.g. Point(0, 0))
    :param num_of_sectors: number of sectors in the circle (12 means 30 degrees per sector)
    :param radius: circle radius
    :param start: start of circle in degrees
    :param end: end of circle in degrees
    :param steps: subdivision of circle. The higher, the smoother it will be
    :return:
    """

    # prepare parameters
    if start > end:
        start = start - 360
    else:
        pass

    step_angle_width = (end - start) / steps
    sector_width = (end - start) / num_of_sectors
    steps_per_sector = int(math.ceil(steps / num_of_sectors))

    polys = []
    for x in range(0, int(num_of_sectors)):
        segment_vertices = []

        # first the center and first point
        segment_vertices.append(polar_point(centre, 0, 0))
        segment_vertices.append(polar_point(centre, start + x * sector_width, radius))

        # then the sector outline points
        for z in range(1, steps_per_sector):
            segment_vertices.append((polar_point(centre, start + x * sector_width + z * step_angle_width, radius)))

        # then again the center point to finish the polygon
        segment_vertices.append(polar_point(centre, start + x * sector_width + sector_width, radius))
        segment_vertices.append(polar_point(centre, 0, 0))

        poly = Polygon(segment_vertices)

        polys.append(poly)

    return polys


if __name__ == "__main__":

    polys = define_sectors(centre=Point(0, 0),
                           num_of_sectors=12,
                           radius=90)

    # optional plot
    # """
    for poly in polys:
        x, y = poly.exterior.xy
        plt.plot(x, y)
    plt.show()
    # """

    print('end')
