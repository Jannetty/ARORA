from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.agent.cell import Cell
    from src.sim.simulation.sim import GrowingSim


class NeighborHelpers:
    """
    Helper functions to determine the direction of a neighbor cell relative to a cell
    when initializing model to default geometry.
    """
    ROOTCAP_CELL_IDs = [
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

    @staticmethod
    def get_neighbor_dir_neighbor_shares_one_v_default_geo(cell: "Cell", neighbor: "Cell") -> str:
        """
        Determine the direction of a neighbor cell sharing one vertex in default geometry.

        Parameters
        ----------
        cell : Cell
            The reference cell.
        neighbor : Cell
            The neighboring cell being considered.

        Returns
        -------
        str
            The direction of the neighbor relative to the cell ('a', 'b', 'l', 'm'),
            or an empty string if no direction is applicable.

        Notes
        -----
        The direction is determined by comparing cell IDs. These directions will
        only be correct if model is initialized to default geometry.
        """
        neighbor_direct = ""
        if cell.get_c_id() == 10 and neighbor.get_c_id() == 20:
            neighbor_direct = "a"
        elif cell.get_c_id() == 20 and neighbor.get_c_id() == 10:
            neighbor_direct = "b"

        elif cell.get_c_id() == 11 and neighbor.get_c_id() == 25:
            neighbor_direct = "a"
        elif cell.get_c_id() == 25 and neighbor.get_c_id() == 11:
            neighbor_direct = "b"

        elif cell.get_c_id() == 16 and neighbor.get_c_id() == 36:
            neighbor_direct = "a"
        elif cell.get_c_id() == 36 and neighbor.get_c_id() == 16:
            neighbor_direct = "b"

        elif cell.get_c_id() == 19 and neighbor.get_c_id() == 37:
            neighbor_direct = "a"
        elif cell.get_c_id() == 37 and neighbor.get_c_id() == 19:
            neighbor_direct = "b"

        elif cell.get_c_id() == 20 and neighbor.get_c_id() == 26:
            neighbor_direct = "b"
        elif cell.get_c_id() == 26 and neighbor.get_c_id() == 20:
            neighbor_direct = "l"

        elif cell.get_c_id() == 20 and neighbor.get_c_id() == 36:
            neighbor_direct = "a"
        elif cell.get_c_id() == 36 and neighbor.get_c_id() == 20:
            neighbor_direct = "b"

        elif cell.get_c_id() == 25 and neighbor.get_c_id() == 27:
            neighbor_direct = "b"
        elif cell.get_c_id() == 27 and neighbor.get_c_id() == 25:
            neighbor_direct = "l"

        elif cell.get_c_id() == 25 and neighbor.get_c_id() == 37:
            neighbor_direct = "a"
        elif cell.get_c_id() == 37 and neighbor.get_c_id() == 25:
            neighbor_direct = "b"

        elif cell.get_c_id() == 38 and neighbor.get_c_id() == 39:
            neighbor_direct = "m"
        elif cell.get_c_id() == 39 and neighbor.get_c_id() == 38:
            neighbor_direct = "l"

        elif cell.get_c_id() == 39 and neighbor.get_c_id() == 46:
            neighbor_direct = "l"
        elif cell.get_c_id() == 46 and neighbor.get_c_id() == 39:
            neighbor_direct = "m"

        elif cell.get_c_id() == 42 and neighbor.get_c_id() == 43:
            neighbor_direct = "l"
        elif cell.get_c_id() == 43 and neighbor.get_c_id() == 42:
            neighbor_direct = "m"

        elif cell.get_c_id() == 42 and neighbor.get_c_id() == 47:
            neighbor_direct = "l"
        elif cell.get_c_id() == 47 and neighbor.get_c_id() == 42:
            neighbor_direct = "m"

        elif cell.get_c_id() == 44 and neighbor.get_c_id() == 50:
            neighbor_direct = "m"
        elif cell.get_c_id() == 50 and neighbor.get_c_id() == 44:
            neighbor_direct = "l"

        elif cell.get_c_id() == 45 and neighbor.get_c_id() == 51:
            neighbor_direct = "m"
        elif cell.get_c_id() == 51 and neighbor.get_c_id() == 45:
            neighbor_direct = "l"

        elif cell.get_c_id() == 50 and neighbor.get_c_id() == 52:
            neighbor_direct = "l"
        elif cell.get_c_id() == 52 and neighbor.get_c_id() == 50:
            neighbor_direct = "m"

        elif cell.get_c_id() == 51 and neighbor.get_c_id() == 59:
            neighbor_direct = "l"
        elif cell.get_c_id() == 59 and neighbor.get_c_id() == 51:
            neighbor_direct = "m"

        elif cell.get_c_id() == 54 and neighbor.get_c_id() == 65:
            neighbor_direct = "a"
        elif cell.get_c_id() == 65 and neighbor.get_c_id() == 54:
            neighbor_direct = "b"

        elif cell.get_c_id() == 54 and neighbor.get_c_id() == 66:
            neighbor_direct = "a"
        elif cell.get_c_id() == 66 and neighbor.get_c_id() == 54:
            neighbor_direct = "b"

        elif cell.get_c_id() == 57 and neighbor.get_c_id() == 69:
            neighbor_direct = "a"
        elif cell.get_c_id() == 69 and neighbor.get_c_id() == 57:
            neighbor_direct = "b"

        elif cell.get_c_id() == 57 and neighbor.get_c_id() == 70:
            neighbor_direct = "a"
        elif cell.get_c_id() == 70 and neighbor.get_c_id() == 57:
            neighbor_direct = "b"

        # This catches assignment of neighbor of root cap cells
        rootcap_cell_ids = NeighborHelpers.ROOTCAP_CELL_IDs
        if cell.get_c_id() in rootcap_cell_ids:
            neighbor_direct = "m"
        if neighbor.get_c_id() in rootcap_cell_ids:
            neighbor_direct = "l"

        return neighbor_direct

    @staticmethod
    def check_if_now_neighbors_with_new_root_cap_cell(cell: "Cell", sim: "GrowingSim") -> str:
        """
        Checks if the neighbor is the next root cap cell.

        Args:
            cell (Cell): The current cell.
            neighbor (Cell): The neighboring cell.

        Returns:
            str: The direction of the neighbor ('a', 'b', 'l', 'm')
                or None if no direction is found.
        """
        all_lrc_cells = [cell for cell in sim.get_cell_list() if cell.get_c_id() in  NeighborHelpers.ROOTCAP_CELL_IDs]
        non_current_neighbor_lrc_cells = [lrc_cell for lrc_cell in all_lrc_cells if lrc_cell not in cell.get_l_neighbors()]
        for lrc_cell in non_current_neighbor_lrc_cells:
            if NeighborHelpers.cell_and_lrc_cell_are_neighbors(cell, lrc_cell):
                    cell.add_l_neighbor(lrc_cell)
                    lrc_cell.add_m_neighbor(cell)

    @staticmethod
    def get_neighbor_dir_neighbor_shares_no_vs_default_geo(cell: "Cell", neighbor: "Cell") -> str:
        """
        Determine the direction of a neighbor cell without shared vertices in default geometry.

        Parameters
        ----------
        cell : Cell
            The reference cell.
        neighbor : Cell
            The neighboring cell being considered.

        Returns
        -------
        str
            The direction of the neighbor relative to the cell ('a', 'b', 'l', 'm'),
            or an appropriate message if no standard direction is found.

        Notes
        -----
        This method accounts for special cases where neighboring cells do not share
        a common vertex. These assignments will only be true if model is initialized
        to default geometry.
        """
        neighbor_direct = ""

        if cell.get_c_id() == 17 and neighbor.get_c_id() == 20:
            neighbor_direct = "l"
        elif cell.get_c_id() == 20 and neighbor.get_c_id() == 17:
            neighbor_direct = "b"
        elif cell.get_c_id() == 18 and neighbor.get_c_id() == 25:
            neighbor_direct = "l"
        elif cell.get_c_id() == 25 and neighbor.get_c_id() == 18:
            neighbor_direct = "b"

        # This catches assignment of neighbor of root cap cells
        rootcap_cell_ids = NeighborHelpers.ROOTCAP_CELL_IDs
        if cell.get_c_id() in rootcap_cell_ids:
            neighbor_miny = neighbor.get_quad_perimeter().get_min_y()
            if (
                cell.get_quad_perimeter().get_min_y()
                <= neighbor_miny
                < cell.get_quad_perimeter().get_max_y()
            ):
                neighbor_direct = "m"
            else:
                neighbor_direct = "cell no longer root cap cell neighbor"
        if neighbor.get_c_id() in rootcap_cell_ids:
            cell_miny = cell.get_quad_perimeter().get_min_y()
            if (
                neighbor.get_quad_perimeter().get_min_y()
                <= cell_miny
                < neighbor.get_quad_perimeter().get_max_y()
            ):
                neighbor_direct = "l"
            else:
                neighbor_direct = "cell no longer root cap cell neighbor"
                NeighborHelpers.check_if_now_neighbors_with_new_root_cap_cell(cell, neighbor)
        return neighbor_direct

    @staticmethod  # This relies on the assumption that only cells that were previously neighbors with root cap cells will ever be neighbors with root cap cells
    def fix_lrc_neighbors_after_growth(sim):
        non_root_tip_cells = [cell for cell in sim.get_cell_list() if cell.get_cell_type() != "roottip"]
        for non_root_tip_cell in non_root_tip_cells:
            for l_neighbor in non_root_tip_cell.get_l_neighbors():
                if l_neighbor.get_c_id() in NeighborHelpers.ROOTCAP_CELL_IDs:
                    NeighborHelpers.check_if_now_neighbors_with_new_root_cap_cell(non_root_tip_cell, sim)
                    NeighborHelpers.check_if_no_longer_neighbors_with_root_cap_cell(non_root_tip_cell, l_neighbor)

    @staticmethod
    def check_if_no_longer_neighbors_with_root_cap_cell(cell, lrc_neighbor):
        if (not NeighborHelpers.cell_and_lrc_cell_are_neighbors(cell, lrc_neighbor)):
            if cell.get_c_id() in [119, 134]:
                cell_miny = cell.get_quad_perimeter().get_min_y()
                cell_maxy = cell.get_quad_perimeter().get_max_y()
                lrc_cell_miny = lrc_neighbor.get_quad_perimeter().get_min_y()
                lrc_cell_maxy = lrc_neighbor.get_quad_perimeter().get_max_y()
            cell.remove_l_neighbor(lrc_neighbor)
            lrc_neighbor.remove_m_neighbor(cell)

    @staticmethod
    def cell_and_lrc_cell_are_neighbors(cell, lrc_cell):
        cell_left_l_or_m = cell.get_quad_perimeter().get_left_lateral_or_medial(cell.get_sim().get_root_midpointx())
        lrc_cell_left_l_or_m = lrc_cell.get_quad_perimeter().get_left_lateral_or_medial(lrc_cell.get_sim().get_root_midpointx())
        # If cells are on opposite sides of the root
        if cell_left_l_or_m != lrc_cell_left_l_or_m:
            return False
        cell_miny = cell.get_quad_perimeter().get_min_y()
        cell_maxy = cell.get_quad_perimeter().get_max_y()
        lrc_cell_miny = lrc_cell.get_quad_perimeter().get_min_y()
        lrc_cell_maxy = lrc_cell.get_quad_perimeter().get_max_y()
        if lrc_cell_miny <= cell_miny <= lrc_cell_maxy or lrc_cell_miny <= cell_maxy <= lrc_cell_maxy or (cell_miny <= lrc_cell_miny <= cell_maxy and cell_miny <= lrc_cell_maxy <= cell_maxy):
            return True
        else:
            return False