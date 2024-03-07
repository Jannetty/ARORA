from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.agent.cell import Cell

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

class NeighborHelpers:
    """
    Helper functions to determine the direction of a neighbor cell relative to a cell
    when initializing model to default geometry.
    """
    
    @staticmethod
    def get_neighbor_dir_neighbor_shares_one_v_default_geo(cell: "Cell", neighbor: "Cell") -> str:
        """
        Determines the direction of the neighbor based on the cell IDs.

        Args:
            cell (Cell): The current cell.
            neighbor (Cell): The neighboring cell.

        Returns:
            str: The direction of the neighbor ('a', 'b', 'l', 'm')
                or None if no direction is found.
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
        rootcap_cell_ids = ROOTCAP_CELL_IDs
        if cell.get_c_id() in rootcap_cell_ids:
            neighbor_direct = "m"
        if neighbor.get_c_id() in rootcap_cell_ids:
            neighbor_direct = "l"

        return neighbor_direct


    @staticmethod
    def check_if_now_neighbors_with_new_root_cap_cell(cell: "Cell", neighbor: "Cell") -> str:
        """
        Checks if the neighbor is the next root cap cell.

        Args:
            cell (Cell): The current cell.
            neighbor (Cell): The neighboring cell.

        Returns:
            str: The direction of the neighbor ('a', 'b', 'l', 'm')
                or None if no direction is found.
        """
        self_midpointx = cell.get_quad_perimeter().get_midpointx()
        yval = cell.get_quad_perimeter().get_midpointy()
        all_lrc_cells = [lrc_cell for lrc_cell in cell.get_sim().get_cell_list() if lrc_cell.get_c_id() in ROOTCAP_CELL_IDs]
        non_neighbor_lrc_cells = [lrc_cell for lrc_cell in all_lrc_cells if lrc_cell not in cell.get_l_neighbors()]
        # if left is lateral
        if cell.get_quad_perimeter().get_left_lateral_or_medial(cell.get_sim().get_root_midpointx()) == "lateral":
            # distance to lateral neighbor is negative
            x_dist_to_lateral_neighbor = -((cell.get_quad_perimeter().get_apical_memlen()/2) + 1)
        else:
            # distance to medial neighbor is positive
            x_dist_to_lateral_neighbor = ((cell.get_quad_perimeter().get_apical_memlen()/2) + 1)
        for lrc_cell in non_neighbor_lrc_cells:
            if lrc_cell.get_quad_perimeter().point_inside(self_midpointx + x_dist_to_lateral_neighbor, yval):
                cell.add_neighbor(lrc_cell)
                lrc_cell.add_neighbor(cell)

        

    @staticmethod
    def get_neighbor_dir_neighbor_shares_no_vs_default_geo(cell: "Cell", neighbor: "Cell") -> str:
        """
        Determines the direction of the neighbor based on the cell IDs.

        Args:
            cell (Cell): The current cell.
            neighbor (Cell): The neighboring cell.

        Returns:
            str: The direction of the neighbor ('a', 'b', 'l', 'm')
                or None if no direction is found.
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
        rootcap_cell_ids = ROOTCAP_CELL_IDs
        if cell.get_c_id() in rootcap_cell_ids:
            neighbor_midpointy = neighbor.get_quad_perimeter().get_midpointy()
            if (
                cell.get_quad_perimeter().get_min_y()
                < neighbor_midpointy
                < cell.get_quad_perimeter().get_max_y()
            ):
                neighbor_direct = "m"
            else:
                neighbor_direct = "cell no longer root cap cell neighbor"
        if neighbor.get_c_id() in rootcap_cell_ids:
            self_midpointy = cell.get_quad_perimeter().get_midpointy()
            if (
                neighbor.get_quad_perimeter().get_min_y()
                < self_midpointy
                < neighbor.get_quad_perimeter().get_max_y()
            ):
                neighbor_direct = "l"
            else:
                neighbor_direct = "cell no longer root cap cell neighbor"
                NeighborHelpers.check_if_now_neighbors_with_new_root_cap_cell(cell, neighbor)
        return neighbor_direct
    
    @staticmethod #This relies on the assumption that only cells that were previously neighbors with root cap cells will ever be neighbors with root cap cells
    def fix_lrc_neighbors_after_growth(sim):
        for cell in [cell for cell in sim.get_cell_list() if cell.get_cell_type() != 'roottip']:
            for neighbor in cell.get_l_neighbors():
                if neighbor.get_c_id() in ROOTCAP_CELL_IDs:
                    NeighborHelpers.check_if_now_neighbors_with_new_root_cap_cell(cell, neighbor)
                    NeighborHelpers.check_if_no_longer_neighbors_with_root_cap_cell(cell, neighbor)

    @staticmethod
    def check_if_no_longer_neighbors_with_root_cap_cell(cell, neighbor):
        self_midpointy = cell.get_quad_perimeter().get_midpointy()
        if cell.get_c_id() == 134:
            print(f"Cell {cell.get_c_id()} midpointy: {self_midpointy}")
            print(f"Neighbor {neighbor.get_c_id()} miny: {neighbor.get_quad_perimeter().get_min_y()}, maxy: {neighbor.get_quad_perimeter().get_max_y()}")
        if (
            neighbor.get_quad_perimeter().get_min_y()
            < self_midpointy
            < neighbor.get_quad_perimeter().get_max_y()
            ):
            pass
        else:
            if cell.get_c_id() == 134:
                print("=============== removing neighbor ==================")
            cell.remove_neighbor(neighbor)
            neighbor.remove_neighbor(cell)