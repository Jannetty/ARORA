from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.agent.cell import Cell
    from src.loc.vertex.vertex import Vertex


class PerimeterNeighborHelpers:
    """
    Provides utility functions for calculating the shared perimeter lengths between neighboring cells
    in the default geometry that share a common edge but do not share two vertices.
    """

    @staticmethod
    def get_default_len_perimeter_in_common(cell: "Cell", neighbor: "Cell") -> float:
        """
        Calculate the length of the common perimeter between two cells in default geometry.

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

        if cell.get_c_id() in rootcap_cell_ids:
            if (
                neighborqp.get_left_lateral_or_medial(neighbor.get_sim().get_root_midpointx())
                == "lateral"
            ):
                neighbor_vs_on_shared_edge = [
                    neighborqp.get_bottom_left(),
                    neighborqp.get_top_left(),
                ]
                cell_vs_on_shared_edge = [cellqp.get_bottom_right(), cellqp.get_top_right()]
                length = PerimeterNeighborHelpers.get_overlap(
                    neighbor_vs_on_shared_edge, cell_vs_on_shared_edge
                )
            elif (
                neighborqp.get_right_lateral_or_medial(neighbor.get_sim().get_root_midpointx())
                == "lateral"
            ):
                neighbor_vs_on_shared_edge = [
                    neighborqp.get_bottom_right(),
                    neighborqp.get_top_right(),
                ]
                cell_vs_on_shared_edge = [cellqp.get_bottom_left(), cellqp.get_top_left()]
                length = PerimeterNeighborHelpers.get_overlap(
                    neighbor_vs_on_shared_edge, cell_vs_on_shared_edge
                )

        elif neighbor.get_c_id() in rootcap_cell_ids:
            if (
                cellqp.get_left_lateral_or_medial(neighbor.get_sim().get_root_midpointx())
                == "lateral"
            ):
                cell_vs_on_shared_edge = [cellqp.get_bottom_left(), cellqp.get_top_left()]
                neighbor_vs_on_shared_edge = [
                    neighborqp.get_bottom_right(),
                    neighborqp.get_top_right(),
                ]
                length = PerimeterNeighborHelpers.get_overlap(
                    cell_vs_on_shared_edge, neighbor_vs_on_shared_edge
                )
            elif (
                cellqp.get_right_lateral_or_medial(neighbor.get_sim().get_root_midpointx())
                == "lateral"
            ):
                cell_vs_on_shared_edge = [cellqp.get_bottom_right(), cellqp.get_top_right()]
                neighbor_vs_on_shared_edge = [
                    neighborqp.get_bottom_left(),
                    neighborqp.get_top_left(),
                ]
                length = PerimeterNeighborHelpers.get_overlap(
                    cell_vs_on_shared_edge, neighbor_vs_on_shared_edge
                )

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

        return length

    @staticmethod
    def get_overlap(
        cell_vs_on_shared_edge: list["Vertex"], neighbor_vs_on_shared_edge: list["Vertex"]
    ) -> float:
        """
        Calculate the length of the overlap between two segments.

        Parameters
        ----------
        cell_vs_on_shared_edge: list
            The vertices of the cell on the shared edge.
        neighbor_vs_on_shared_edge: list
            The vertices of the neighbor on the shared edge.

        Returns
        -------
        float
            The length of the overlap between the two segments.
        """
        vertex_xs = [v.get_x() for v in cell_vs_on_shared_edge] + [
            v.get_x() for v in neighbor_vs_on_shared_edge
        ]
        assert (
            len(set(vertex_xs)) == 1
        ), "In PerimeterNeighborHelpers.get_overlap, the vertices of the shared membrane do not share an x value."
        cell_v_ys_on_shared_edge = sorted([v.get_y() for v in cell_vs_on_shared_edge])
        neighbor_v_ys_on_shared_edge = sorted([v.get_y() for v in neighbor_vs_on_shared_edge])
        if cell_v_ys_on_shared_edge[1] < neighbor_v_ys_on_shared_edge[0]:
            raise ValueError(
                "In PerimeterNeighborHelpers.get_overlap, the vertices of the shared membrane do not overlap."
            )
        else:
            return min(cell_v_ys_on_shared_edge[1], neighbor_v_ys_on_shared_edge[1]) - max(
                cell_v_ys_on_shared_edge[0], neighbor_v_ys_on_shared_edge[0]
            )
