class Vertex:
    """
    Represents a vertex, or corner of a cell

    Attributes:
        x (float): The x-coordinate of the vertex.
        y (float): The y-coordinate of the vertex.
        xy (list): A list containing the x and y coordinates of the vertex.
        v_id (optional): An optional identifier for the vertex.
    """

    def __init__(self, x: float, y: float, v_id: int | None = None):
        self.x = x
        self.y = y
        self.xy = [x, y]
        self.v_id = v_id

    def get_xy(self) -> list[float]:
        """
        Get the x and y coordinates of the vertex.

        Returns:
            list: A list containing the x and y coordinates of the vertex.
        """
        return self.xy

    def get_y(self) -> float:
        """
        Get the y-coordinate of the vertex.

        Returns:
            float: The y-coordinate of the vertex.
        """
        return self.y

    def get_x(self) -> float:
        """
        Get the x-coordinate of the vertex.

        Returns:
            float: The x-coordinate of the vertex.
        """
        return self.x

    def set_x(self, newx: float) -> None:
        """
        Set the x-coordinate of the vertex.

        Args:
            newx (float): The new x-coordinate of the vertex.
        """
        self.x = newx
        self.xy[0] = self.x

    def set_y(self, newy: float) -> None:
        """
        Set the y-coordinate of the vertex.

        Args:
            newy (float): The new y-coordinate of the vertex.
        """
        self.y = newy
        self.xy[1] = self.y

    def get_vid(self) -> int | None:
        """
        Get the identifier of the vertex.

        Returns:
            int: The identifier of the vertex.
        """
        return self.v_id
