from shapely.geometry import Polygon, Point

# Only used on a PC, rough polygon around Karlskrona
karlskrona_points = [
    (56.14734956862526, 15.586271493512454),
    (56.150334159404075, 15.553677161724607),
    (56.18132703102676, 15.556504980464192),
    (56.200291606779295, 15.59505261538964),
    (56.222404800173166, 15.587732167603242),
    (56.233229575765215, 15.657859958677804),
    (56.22594924565782, 15.6778035227375),
    (56.20459154548599, 15.672414169208913),
    (56.18692350679527, 15.675556589911697),
    (56.174828546151055, 15.6572748430866),
    (56.14595162668099, 15.662908840363544)
]

karlskrona_polygon = Polygon(karlskrona_points)


def within_karlskrona_polygon(lat, lon) -> bool:
    return karlskrona_polygon.contains(Point(lat, lon))


TARGET_LOCATION = (56.18684333961802, 15.61205558484464)
MAX_DISTANCE = 0.05


def within_karlskrona_radius(lat, lon) -> bool:
    return ((lat - TARGET_LOCATION[0])**2
            + (lon - TARGET_LOCATION[1])**2) <= (MAX_DISTANCE * MAX_DISTANCE)
