"""Artist for matplotlib Wedge patches (pie chart segments)."""

from __future__ import annotations

import math

from matplotlib.patches import Wedge

from mpl_ascii.artists.transform_helpers import Point, to_mapping
from mpl_ascii.artists.types import Color, LineMark, PointMark, Shape


_ARC_STEPS = 24  # number of points to approximate the arc


def parse(obj: Wedge) -> Shape:
    cx, cy = obj.center
    r = obj.r
    theta1 = math.radians(obj.theta1)
    theta2 = math.radians(obj.theta2)

    # If this is a donut (has width), use the outer radius for the arc
    # and inner radius for inner edge
    inner_r = 0.0 if obj.width is None else r - obj.width

    facecolor = Color(*obj.get_facecolor())
    edgecolor = Color(*obj.get_edgecolor())

    # Build points along the outer arc from theta1 to theta2
    steps = max(4, int(_ARC_STEPS * abs(theta2 - theta1) / (2 * math.pi)))
    outer_points: list[Point] = []
    for i in range(steps + 1):
        t = theta1 + (theta2 - theta1) * i / steps
        outer_points.append(Point(cx + r * math.cos(t), cy + r * math.sin(t)))

    if inner_r > 0:
        # Donut: build inner arc in reverse
        inner_points: list[Point] = []
        for i in range(steps + 1):
            t = theta2 - (theta2 - theta1) * i / steps
            inner_points.append(Point(cx + inner_r * math.cos(t), cy + inner_r * math.sin(t)))
        all_points = outer_points + inner_points
    else:
        # Full wedge: center + arc
        center = Point(cx, cy)
        all_points = [center] + outer_points

    point_marks = [PointMark(p) for p in all_points]

    # Lines connecting consecutive points to form the closed shape
    lines = [
        LineMark(all_points[i], all_points[i + 1])
        for i in range(len(all_points) - 1)
    ]
    # Close the polygon
    lines.append(LineMark(all_points[-1], all_points[0]))

    return Shape(
        point_marks,
        lines,
        to_mapping(obj.get_transform()),
        point_color=edgecolor,
        line_color=edgecolor,
        fill=facecolor,
    )
