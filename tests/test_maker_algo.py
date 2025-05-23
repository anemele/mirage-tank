from mirage_tank.maker.algo import convex_hull


def test_convex_hull():
    points = [
        (0, 3),
        (2, 2),
        (1, 1),
        (2, 1),
        (2, 0),
        (1, 0),
        (0, 0),
        (3, 3),
        (3, 2),
        (3, 1),
    ]
    expected = [(0, 0), (2, 0), (3, 1), (3, 3), (0, 3)]

    assert convex_hull(points) == expected
