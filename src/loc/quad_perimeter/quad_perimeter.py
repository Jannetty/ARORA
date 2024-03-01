import math
from typing import TYPE_CHECKING
from src.sim.util.math_helpers import round_to_sf
from src.loc.vertex.vertex import Vertex

if TYPE_CHECKING:
    from src.agent.cell import Cell


def list_intersection(lst1: list, lst2: list) -> list:
    """
    Compute the intersection of two lists.

    Parameters
    ----------
    lst1 : List[Any]
        The first input list.
    lst2 : List[Any]
        The second input list.

    Returns
    -------
    List[Any]
        A new list containing the common elements between `lst1` and `lst2`.
    """
    intersection = [value for value in lst1 if value in lst2]
    return intersection


class QuadPerimeter:
    """
    Represents the perimeter of a cell defined by its four corner vertices.

    This class provides functionalities to calculate various geometric properties of a cell,
    such as area, perimeter length, and membrane lengths, based on the vertices that define
    the cell's perimeter. It facilitates spatial analyses within cellular models,
    including the identification of cell boundaries and the determination of cell neighbor
    relationships based on shared edges.

    Attributes
    ----------
    _perimeter_vs : List[Vertex]
        A list of four `Vertex` instances representing the cell's perimeter shape.
    _top_left : Vertex
        The top-left vertex of the cell's perimeter
    _top_right : Vertex
        The top-right vertex of the cell's perimeter
    _bottom_left : Vertex
        The bottom-left vertex of the cell's perimeter
    _bottom_right : Vertex
        The bottom-right vertex of the cell's perimeter
    _midpointx : float
        The x-coordinate of the midpoint of the cell's perimeter, calculated as the average
        x-coordinate of all vertices.
    _init_area : float
        The initial area of the cell, calculated using the vertices of the perimeter. This
        value is important for simulations that track cell growth or deformation over time.
    """

    def __init__(self, vertex_list: list["Vertex"]):
        """
        Initializes a QuadPerimeter object with a list of vertices.

        Parameters
        ----------
        vertex_list: list[Vertex]
            A list of vertices representing the quad perimeter.
        """
        self._perimeter_vs = vertex_list
        self.__assign_corners()
        self._midpointx = self.__calc_midpointx()
        self._init_area = self.get_area()

    def __calc_midpointx(self) -> float:
        """
        Calculates the central x-coordinate of the perimeter.

        Returns
        -------
        float
            The x-coordinate of the midpoint.
        """
        sumx = sum(corner.get_x() for corner in self._perimeter_vs)
        return sumx / len(self._perimeter_vs)

    def __calc_midpointy(self) -> float:
        """
        Calculates the central y-coordinate of the perimeter.

        Returns
        -------
        float
            The y-coordinate of the midpoint.
        """
        sumy = sum(corner.get_y() for corner in self._perimeter_vs)
        return sumy / len(self._perimeter_vs)

    def get_max_y(self) -> float:
        """
        Gets the maximum y-coordinate of the perimeter.

        Returns
        -------
        float
            The maximum y-coordinate of the perimeter.
        """
        return max(corner.get_y() for corner in self._perimeter_vs)

    def get_min_y(self) -> float:
        """
        Gets the minimum y-coordinate of the perimeter.

        Returns
        -------
        float
            The minimum y-coordinate of the perimeter.
        """
        return min(corner.get_y() for corner in self._perimeter_vs)

    def get_max_x(self) -> float:
        """
        Gets the maximum x-coordinate of the perimeter.

        Returns
        -------
        float
            The maximum x-coordinate of the perimeter.
        """
        return max(corner.get_x() for corner in self._perimeter_vs)

    def get_min_x(self) -> float:
        """
        Gets the minimum x-coordinate of the perimeter.

        Returns
        -------
        float
            The minimum x-coordinate of the perimeter.
        """
        return min(corner.get_x() for corner in self._perimeter_vs)

    def get_midpointx(self) -> float:
        """
        Gets the x-coordinate of the perimeter's midpoint.

        Returns
        -------
        float
            The x-coordinate of the perimeter's midpoint.
        """
        return self._midpointx

    def get_midpointy(self) -> float:
        """
        Gets the y-coordinate of the perimeter's midpoint.

        Returns
        -------
        float
            The y-coordinate of the perimeter's midpoint.
        """
        return self.__calc_midpointy()

    def point_inside(self, x: int, y: int) -> bool:
        """
        Determines if a point is inside the perimeter.

        Parameters
        ----------
        x: int
            The x-coordinate of the point.
        y: int
            The y-coordinate of the point.

        Returns
        -------
        bool
            True if the point is inside the perimeter, False otherwise.
        """
        if self.get_min_x() < x < self.get_max_x():
            if self.get_min_y() < y < self.get_max_y():
                return True
        return False

    def get_perimeter_len(self) -> float:
        """
        Calculates the full length of the perimeter.

        Returns
        -------
        float
            The length of the perimeter.
        """
        return (
            self.get_left_memlen()
            + self.get_right_memlen()
            + self.get_apical_memlen()
            + self.get_basal_memlen()
        )

    def get_left_memlen(self) -> float:
        """
        Returns the length of the left membrane of the quadrilateral.

        Returns
        -------
        float
            The length of the left membrane.
        """
        return math.dist(self._top_left.get_xy(), self._bottom_left.get_xy())

    def get_right_memlen(self) -> float:
        """
        Returns the length of the right membrane of the quadrilateral.

        Returns
        -------
        float
            The length of the right membrane.
        """
        return math.dist(self._top_right.get_xy(), self._bottom_right.get_xy())

    def get_apical_memlen(self) -> float:
        """
        Returns the length of the apical membrane of the quadrilateral.

        Returns
        -------
        float
            The length of the apical membrane.
        """
        return math.dist(self._top_left.get_xy(), self._top_right.get_xy())

    def get_basal_memlen(self) -> float:
        """
        Returns the length of the basal membrane of the quadrilateral.

        Returns
        -------
        float
            The length of the basal membrane.
        """
        return math.dist(self._bottom_left.get_xy(), self._bottom_right.get_xy())

    def __assign_corners(self) -> None:
        """
        Assigns the top left, top right, bottom left, and bottom right corners of the perimeter.
        """
        top_row = get_apical(self._perimeter_vs)
        bottom_row = [v for v in self._perimeter_vs if v not in top_row]
        self._top_left = get_left_v(top_row)
        self._top_right = get_right_v(top_row)
        self._bottom_left = get_left_v(bottom_row)
        self._bottom_right = get_right_v(bottom_row)

    def get_corners_for_disp(self) -> list[list[float]]:
        """
        Returns the (x,y) positions of the perimeter's vertices for display purposes.

        Returns
        -------
        list[list[float]]
            A list of the (x,y) coordinates of the perimeter's vertices.
        """
        return [
            self._bottom_right.get_xy(),
            self._bottom_left.get_xy(),
            self._top_left.get_xy(),
            self._top_right.get_xy(),
        ]

    def set_corners(self, vertex_list: list["Vertex"]) -> None:
        """
        Sets the corners of the perimeter.

        Parameters
        ----------
        vertex_list: list[Vertex]
            A list of vertices representing the perimeter's corners.
        """
        self._perimeter_vs = vertex_list
        self.__assign_corners()

    def get_top_left(self) -> Vertex:
        """
        Returns the top left vertex of the perimeter.

        Returns
        -------
        Vertex
            The top left vertex of the perimeter.
        """
        return self._top_left

    def get_top_right(self) -> Vertex:
        """
        Returns the top right vertex of the perimeter.

        Returns
        -------
        Vertex
            The top right vertex of the perimeter.
        """
        return self._top_right

    def get_bottom_left(self) -> Vertex:
        """
        Returns the bottom left vertex of the perimeter.

        Returns
        -------
        Vertex
            The bottom left vertex of the perimeter.
        """
        return self._bottom_left

    def get_bottom_right(self) -> Vertex:
        """
        Returns the bottom right vertex of the perimeter.

        Returns
        -------
        Vertex
            The bottom right vertex of the perimeter.
        """
        return self._bottom_right

    def get_vs(self) -> list["Vertex"]:
        """
        Returns the vertices of the perimeter.

        Returns
        -------
        list[Vertex]
            A list of the perimeter's vertices.
        """
        return [
            self.get_top_left(),
            self.get_top_right(),
            self.get_bottom_right(),
            self.get_bottom_left(),
        ]

    def get_area(self) -> float:
        """
        Calculates the area of the quadrilateral using Brahmagupta's formula.

        Returns
        -------
        float
            The area of the quadrilateral.
        """
        s = self.get_perimeter_len() / 2
        a = math.dist(self._top_left.get_xy(), self._bottom_left.get_xy())
        b = math.dist(self._top_right.get_xy(), self._bottom_right.get_xy())
        c = math.dist(self._top_left.get_xy(), self._top_right.get_xy())
        d = math.dist(self._bottom_left.get_xy(), self._bottom_right.get_xy())
        area = math.sqrt((s - a) * (s - b) * (s - c) * (s - d))
        return round_to_sf(area, 6)

    def get_init_area(self) -> float:
        """
        Returns the initial area of the cell.

        Returns
        -------
        float
            The initial area of the cell.
        """
        return self._init_area

    def get_height(self) -> float:
        """
        Returns the height of the quadrilateral.

        Returns
        -------
        float
            The height of the quadrilateral.
        """
        return self._top_left.get_y() - self._bottom_left.get_y()

    def determine_left_right(self, root_mid: float) -> tuple[str, str]:
        """
        Determines if the cell is to the left or right of the root's midpoint.

        Parameters
        ----------
        root_mid: float
            The x-coordinate of the root's midpoint.

        Returns
        -------
        tuple
            A tuple describing how "left" and "right" are defined for the cell.
            The first tuple element is the left direction, the second is the right direction.
        """
        cell_mid = self.get_midpointx()
        if cell_mid < root_mid:
            return ("lateral", "medial")
        if cell_mid == root_mid:
            return ("lateral", "lateral")
        return ("medial", "lateral")

    def get_left_lateral_or_medial(self, root_mid: float) -> str:
        """
        Determines if "left" is lateral or medial for this perimeter.

        Parameters
        ----------
        root_mid: int
            The x-coordinate of the root's midpoint.

        Returns
        -------
        str
            The direction of the left side of the cell.
        """
        return self.determine_left_right(root_mid)[0]

    def get_right_lateral_or_medial(self, root_mid: float) -> str:
        """
        Determines if "right" is lateral or medial for this perimeter.

        Parameters
        ----------
        root_mid: int
            The x-coordinate of the root's midpoint.

        Returns
        -------
        str
            The direction of the right side of the cell.
        """
        return self.determine_left_right(root_mid)[1]

    def get_memfrac(self, direction: str, left: str) -> float:
        """
        Calculate fraction of total membrane one direction's membrane represents

        Parameters
        ----------
        direction: str
            The direction of the membrane.
        left: str
            The side of the cell.

        Returns
        -------
        float
            The fraction of the total membrane that the direction's membrane represents.
        """
        cell_perimeter = self.get_perimeter_len()
        if direction == "a":
            memfrac = self.get_apical_memlen() / cell_perimeter
        elif direction == "b":
            memfrac = self.get_basal_memlen() / cell_perimeter
        elif direction == "l":
            if left == "lateral":
                memfrac = self.get_left_memlen() / cell_perimeter
            else:
                memfrac = self.get_right_memlen() / cell_perimeter
        elif direction == "m":
            if left == "medial":
                memfrac = self.get_left_memlen() / cell_perimeter
            else:
                memfrac = self.get_right_memlen() / cell_perimeter
        return round_to_sf(memfrac, 6)


def get_len_perimeter_in_common(cell: "Cell", neighbor: "Cell") -> float:
    """
    Calculates the length of the common perimeter between two cells.

    Parameters
    ----------
    cell: Cell
        The reference cell from which the common perimeter length is calculated
    neighbor: Cell
        The neighboring cell adjacemt to the 'cell'.

    Returns
    -------
    float
        The length of the perimeter shared by the `cell` and its `neighbor`.

    Raises
    ------
    ValueError
        If `cell` and `neighbor` do not share a direct boundary, indicating an
        error in identifying neighboring cells or a potential issue with the cell
        geometry configuration.
    """

    length = 0.0
    rootcap_cell_ids = [
        60,
        90,
        120,
        136,
        166,
        210,
        296,
        75,
        105,
        135,
        151,
        181,
        225,
        311,
    ]
    cellqp = cell.get_quad_perimeter()
    neighborqp = neighbor.get_quad_perimeter()
    # if cellqp and neighborqp share two vertices, calculate euclidean distance between them
    cell_vs = cellqp.get_vs()
    neighbor_vs = neighborqp.get_vs()
    if len(list_intersection(cell_vs, neighbor_vs)) == 2:
        vs = list(set(cellqp.get_vs()).intersection(set(neighborqp.get_vs())))
        length = math.dist(vs[0].get_xy(), vs[1].get_xy())

    # cases for lateral root cap cells
    elif cell.get_c_id() in rootcap_cell_ids:
        if (
            neighborqp.get_left_lateral_or_medial(neighbor.get_sim().get_root_midpointx())
            == "lateral"
        ):
            length = neighborqp.get_left_memlen()
        elif (
            neighborqp.get_right_lateral_or_medial(neighbor.get_sim().get_root_midpointx())
            == "lateral"
        ):
            length = neighborqp.get_right_memlen()

    elif neighbor.get_c_id() in rootcap_cell_ids:
        if cellqp.get_left_lateral_or_medial(neighbor.get_sim().get_root_midpointx()) == "lateral":
            length = cellqp.get_left_memlen()
        elif (
            cellqp.get_right_lateral_or_medial(neighbor.get_sim().get_root_midpointx()) == "lateral"
        ):
            length = cellqp.get_right_memlen()

    # cases for unusual geometry in roottip
    elif cell.get_c_id() == 10 and neighbor.get_c_id() == 20:
        length = cell.get_quad_perimeter().get_apical_memlen()
    elif cell.get_c_id() == 20 and neighbor.get_c_id() == 10:
        length = neighbor.get_quad_perimeter().get_apical_memlen()

    elif cell.get_c_id() == 11 and neighbor.get_c_id() == 25:
        length = cell.get_quad_perimeter().get_apical_memlen()
    elif cell.get_c_id() == 25 and neighbor.get_c_id() == 11:
        length = neighbor.get_quad_perimeter().get_apical_memlen()

    elif cell.get_c_id() == 16 and neighbor.get_c_id() == 36:
        length = cell.get_quad_perimeter().get_apical_memlen()
    elif cell.get_c_id() == 36 and neighbor.get_c_id() == 16:
        length = neighbor.get_quad_perimeter().get_apical_memlen()

    elif cell.get_c_id() == 17 and neighbor.get_c_id() == 20:
        length = cell.get_quad_perimeter().get_apical_memlen()
    elif cell.get_c_id() == 20 and neighbor.get_c_id() == 17:
        length = neighbor.get_quad_perimeter().get_apical_memlen()

    elif cell.get_c_id() == 18 and neighbor.get_c_id() == 25:
        length = cell.get_quad_perimeter().get_apical_memlen()
    elif cell.get_c_id() == 25 and neighbor.get_c_id() == 18:
        length = neighbor.get_quad_perimeter().get_apical_memlen()

    elif cell.get_c_id() == 19 and neighbor.get_c_id() == 37:
        length = cell.get_quad_perimeter().get_apical_memlen()
    elif cell.get_c_id() == 37 and neighbor.get_c_id() == 19:
        length = neighbor.get_quad_perimeter().get_apical_memlen()

    elif cell.get_c_id() == 26 and neighbor.get_c_id() == 20:
        length = cell.get_quad_perimeter().get_left_memlen()
    elif cell.get_c_id() == 20 and neighbor.get_c_id() == 26:
        length = neighbor.get_quad_perimeter().get_left_memlen()

    elif cell.get_c_id() == 20 and neighbor.get_c_id() == 36:
        length = cell.get_quad_perimeter().get_apical_memlen()
    elif cell.get_c_id() == 36 and neighbor.get_c_id() == 20:
        length = neighbor.get_quad_perimeter().get_apical_memlen()

    elif cell.get_c_id() == 25 and neighbor.get_c_id() == 27:
        length = neighbor.get_quad_perimeter().get_right_memlen()
    elif cell.get_c_id() == 27 and neighbor.get_c_id() == 25:
        length = cell.get_quad_perimeter().get_right_memlen()

    elif cell.get_c_id() == 25 and neighbor.get_c_id() == 37:
        length = cell.get_quad_perimeter().get_apical_memlen()
    elif cell.get_c_id() == 37 and neighbor.get_c_id() == 25:
        length = neighbor.get_quad_perimeter().get_apical_memlen()

    elif cell.get_c_id() == 38 and neighbor.get_c_id() == 39:
        length = cell.get_quad_perimeter().get_right_memlen()
    elif cell.get_c_id() == 39 and neighbor.get_c_id() == 38:
        length = neighbor.get_quad_perimeter().get_right_memlen()

    elif cell.get_c_id() == 39 and neighbor.get_c_id() == 46:
        length = neighbor.get_quad_perimeter().get_right_memlen()
    elif cell.get_c_id() == 46 and neighbor.get_c_id() == 39:
        length = cell.get_quad_perimeter().get_right_memlen()

    elif cell.get_c_id() == 42 and neighbor.get_c_id() == 43:
        length = neighbor.get_quad_perimeter().get_left_memlen()
    elif cell.get_c_id() == 43 and neighbor.get_c_id() == 42:
        length = cell.get_quad_perimeter().get_left_memlen()

    elif cell.get_c_id() == 42 and neighbor.get_c_id() == 47:
        length = neighbor.get_quad_perimeter().get_left_memlen()
    elif cell.get_c_id() == 47 and neighbor.get_c_id() == 42:
        length = cell.get_quad_perimeter().get_left_memlen()

    elif cell.get_c_id() == 44 and neighbor.get_c_id() == 50:
        length = cell.get_quad_perimeter().get_right_memlen()
    elif cell.get_c_id() == 50 and neighbor.get_c_id() == 44:
        length = neighbor.get_quad_perimeter().get_right_memlen()

    elif cell.get_c_id() == 45 and neighbor.get_c_id() == 51:
        length = cell.get_quad_perimeter().get_left_memlen()
    elif cell.get_c_id() == 51 and neighbor.get_c_id() == 45:
        length = neighbor.get_quad_perimeter().get_left_memlen()

    elif cell.get_c_id() == 52 and neighbor.get_c_id() == 50:
        length = cell.get_quad_perimeter().get_right_memlen()
    elif cell.get_c_id() == 50 and neighbor.get_c_id() == 52:
        length = neighbor.get_quad_perimeter().get_right_memlen()

    elif cell.get_c_id() == 51 and neighbor.get_c_id() == 59:
        length = neighbor.get_quad_perimeter().get_left_memlen()
    elif cell.get_c_id() == 59 and neighbor.get_c_id() == 51:
        length = cell.get_quad_perimeter().get_left_memlen()

    # If it is either of 54's apical neighbors, return cell's basal length
    elif (
        cell.get_c_id() == 54
        and neighbor.get_quad_perimeter().get_bottom_left()
        == cell.get_quad_perimeter().get_top_left()
    ):
        length = neighbor.get_quad_perimeter().get_basal_memlen()
    elif (
        neighbor.get_c_id() == 54
        and cell.get_quad_perimeter().get_bottom_left()
        == neighbor.get_quad_perimeter().get_top_left()
    ):
        length = cell.get_quad_perimeter().get_basal_memlen()
    elif (
        cell.get_c_id() == 54
        and neighbor.get_quad_perimeter().get_bottom_right()
        == cell.get_quad_perimeter().get_top_right()
    ):
        length = neighbor.get_quad_perimeter().get_basal_memlen()
    elif (
        neighbor.get_c_id() == 54
        and cell.get_quad_perimeter().get_bottom_right()
        == neighbor.get_quad_perimeter().get_top_right()
    ):
        length = cell.get_quad_perimeter().get_basal_memlen()

    # If it is either of 57's apical neighbors, return cell's basal length
    elif (
        cell.get_c_id() == 57
        and neighbor.get_quad_perimeter().get_bottom_left()
        == cell.get_quad_perimeter().get_top_left()
    ):
        length = neighbor.get_quad_perimeter().get_basal_memlen()
    elif (
        neighbor.get_c_id() == 57
        and cell.get_quad_perimeter().get_bottom_left()
        == neighbor.get_quad_perimeter().get_top_left()
    ):
        length = cell.get_quad_perimeter().get_basal_memlen()
    elif (
        cell.get_c_id() == 57
        and neighbor.get_quad_perimeter().get_bottom_right()
        == cell.get_quad_perimeter().get_top_right()
    ):
        length = neighbor.get_quad_perimeter().get_basal_memlen()
    elif (
        neighbor.get_c_id() == 57
        and cell.get_quad_perimeter().get_bottom_right()
        == neighbor.get_quad_perimeter().get_top_right()
    ):
        length = cell.get_quad_perimeter().get_basal_memlen()

    if length == 0:
        raise ValueError("Neighbor list is incorrect, neighbor does not share membrane with cell")
    return length


def get_apical(vertex_list: list["Vertex"]) -> list["Vertex"]:
    """
    Returns two apical vertices from the given vertex list.

    Parameters
    ----------
    vertex_list: list[Vertex]
        A list of four vertices.

    Returns
    -------
    list[Vertex]
        A list of the cell's two apical vertices.
    """
    vs = vertex_list
    assert len(vs) == 4
    maxy = float("-inf")
    apical_vs = []
    for v in vs:
        if v.get_y() > maxy:
            maxy = v.get_y()
            apical_v = v
    apical_vs.append(apical_v)
    maxy = float("-inf")
    for v in vs:
        if v.get_y() > maxy and v not in apical_vs:
            maxy = v.get_y()
            apical_v = v
    apical_vs.append(apical_v)
    return apical_vs


def get_basal(vertex_list: list["Vertex"]) -> list["Vertex"]:
    """
    Returns two basal vertices from the given vertex list.

    Parameters
    ----------
    vertex_list: list[Vertex]
        A list of four vertices.

    Returns
    -------
    list[Vertex]
        A list of the cell's two basal vertices.
    """
    apical = get_apical(vertex_list)
    return [v for v in vertex_list if v not in apical]


def get_left_v(vertex_list: list["Vertex"]) -> Vertex:
    """
    Return the leftmost vertex from a specified list of two vertices.

    Parameters
    ----------
    vertex_list : list[Vertex]
        A list containing exactly two `Vertex` instances.

    Returns
    -------
    Vertex
        The leftmost vertex based on the x-coordinate.

    Raises
    ------
    ValueError
        If `vertex_list` does not contain exactly two vertices.

    """
    if len(vertex_list) != 2:
        raise ValueError("get_left_v called on vertex list of length != 2")
    vs = vertex_list
    minx = float("inf")
    for v in vs:
        if v.get_x() < minx:
            minx = v.get_x()
            left_v = v
    return left_v


def get_right_v(vertex_list: list["Vertex"]) -> Vertex:
    """
    Return the rightmost vertex from a specified list of two vertices.

    This function identifies and returns the vertex with the smallest x-coordinate,
    effectively determining the leftmost vertex among a pair. This operation assumes
    the vertex list contains exactly two vertices.

    Parameters
    ----------
    vertex_list : list[Vertex]
        A list containing exactly two `Vertex` instances.

    Returns
    -------
    Vertex
        The rightmost vertex based on the x-coordinate.

    Raises
    ------
    ValueError
        If `vertex_list` does not contain exactly two vertices.

    """
    if len(vertex_list) != 2:
        raise ValueError("get_right_v called on vertex list of length != 2")
    left = get_left_v(vertex_list)
    for v in vertex_list:
        if v is not left:
            right = v
    return right
