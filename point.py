class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def tup(self):
        return self.x, self.y

    # Flip a point by a symmetry axis described by two points
    def flip_by_line(self, start_point, end_point):
        # If points overlap, the axis cannot be chosen
        if start_point == end_point:
            return

        # Special case for a vertical line
        if start_point.x == end_point.x:
            self.x = 2 * start_point.x - self.x
            self.y = self.y
            return

        m = (end_point.y - start_point.y) / (end_point.x - start_point.x)
        b = end_point.y - m * end_point.x
        m_sq = pow(m, 2)

        x = (self.x * (1 - m_sq) + self.y * (2 * m) - 2 * m * b) / (1 + m_sq)
        y = (self.x * (2 * m) + self.y * (m_sq - 1) + 2 * b) / (1 + m_sq)
        self.x = x
        self.y = y

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        return False

    def translate(self, translation):
        self.x += translation.x
        self.y += translation.y

    def scale(self, scale_factor):
        self.x *= scale_factor
        self.y *= scale_factor

    def is_close_to(self, other_point, threshold):
        return abs(self.x - other_point.x) <= threshold and abs(self.y - other_point.y) <= threshold
