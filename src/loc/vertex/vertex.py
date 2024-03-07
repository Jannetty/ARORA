class Vertex:
    """
    Represents a vertex, or a point in 2D space, typically a corner of a geometric shape.

    Attributes
    ----------
    x : float
        The x-coordinate of the vertex.
    y : float
        The y-coordinate of the vertex.
    xy : list[float]
        A list containing the x and y coordinates of the vertex.
    v_id : int, optional
        An optional identifier for the vertex.

    Parameters
    ----------
    x : float
        The x-coordinate of the vertex upon initialization.
    y : float
        The y-coordinate of the vertex upon initialization.
    v_id : int or None, optional
        An optional identifier for the vertex, by default None.
    """

    def __init__(self, x: float, y: float, v_id: int | None = None):
        """
        Initialize a new Vertex instance.

        Parameters
        ----------
        x : float
            The x-coordinate of the vertex.
        y : float
            The y-coordinate of the vertex.
        v_id : int, optional
            An optional identifier for the vertex. Useful for tracking vertices or referencing them
            in complex structures. Defaults to None if not provided.

        Notes
        -----
        The input module will automatically assign v_id to be the row number of
        each vertex, so if vertices are read from a file v_ids will be assigned.
        """
        self.x = x
        self.y = y
        self.xy = [x, y]
        self.v_id = v_id

    def get_xy(self) -> list[float]:
        """
        Get the x and y coordinates of the vertex.

        Returns
        -------
        list[float]
            A list containing the x and y coordinates of the vertex.
        """
        return self.xy

    def get_y(self) -> float:
        """
        Get the y-coordinate of the vertex.

        Returns
        -------
        float
            The y-coordinate of the vertex.
        """
        return self.y

    def get_x(self) -> float:
        """
        Get the x-coordinate of the vertex.

        Returns
        -------
        float
            The x-coordinate of the vertex.
        """
        return self.x

    def set_x(self, newx: float) -> None:
        """
        Set the x-coordinate of the vertex.

        Parameters
        ----------
        newx : float
            The new x-coordinate to be set for the vertex.
        """
        self.x = newx
        self.xy[0] = self.x

    def set_y(self, newy: float) -> None:
        """
        Set the y-coordinate of the vertex.

        Parameters
        ----------
        newy : float
            The new y-coordinate to be set for the vertex.
        """
        self.y = newy
        self.xy[1] = self.y

    def get_vid(self) -> int | None:
        """
        Retrieve the identifier of the vertex, if it exists.

        Returns
        -------
        int or None
            The identifier of the vertex, or None if not set.
        """
        return self.v_id
