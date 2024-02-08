class CellNeighborHelpers:
    """
    Helper functions for Cell to figure out its default neighbor information
    """

    def get_neighbor_direction_when_neighbor_shares_one_v_default_geo(cell, neighbor) -> str:
        if cell.get_id() == 10 and neighbor.get_id() == 20:
            return "a"
        elif cell.get_id() == 20 and neighbor.get_id() == 10:
            return "b"

        elif cell.get_id() == 11 and neighbor.get_id() == 25:
            return "a"
        elif cell.get_id() == 25 and neighbor.get_id() == 11:
            return "b"

        elif cell.get_id() == 16 and neighbor.get_id() == 36:
            return "a"
        elif cell.get_id() == 36 and neighbor.get_id() == 16:
            return "b"

        elif cell.get_id() == 19 and neighbor.get_id() == 37:
            return "a"
        elif cell.get_id() == 37 and neighbor.get_id() == 19:
            return "b"

        elif cell.get_id() == 20 and neighbor.get_id() == 26:
            return "b"
        elif cell.get_id() == 26 and neighbor.get_id() == 20:
            return "l"

        elif cell.get_id() == 20 and neighbor.get_id() == 36:
            return "a"
        elif cell.get_id() == 36 and neighbor.get_id() == 20:
            return "b"

        elif cell.get_id() == 25 and neighbor.get_id() == 27:
            return "b"
        elif cell.get_id() == 27 and neighbor.get_id() == 25:
            return "l"

        elif cell.get_id() == 25 and neighbor.get_id() == 37:
            return "a"
        elif cell.get_id() == 37 and neighbor.get_id() == 25:
            return "b"

        elif cell.get_id() == 38 and neighbor.get_id() == 39:
            return "m"
        elif cell.get_id() == 39 and neighbor.get_id() == 38:
            return "l"

        elif cell.get_id() == 39 and neighbor.get_id() == 46:
            return "l"
        elif cell.get_id() == 46 and neighbor.get_id() == 39:
            return "m"

        elif cell.get_id() == 42 and neighbor.get_id() == 43:
            return "l"
        elif cell.get_id() == 43 and neighbor.get_id() == 42:
            return "m"

        elif cell.get_id() == 42 and neighbor.get_id() == 47:
            return "l"
        elif cell.get_id() == 47 and neighbor.get_id() == 42:
            return "m"

        elif cell.get_id() == 44 and neighbor.get_id() == 50:
            return "m"
        elif cell.get_id() == 50 and neighbor.get_id() == 44:
            return "l"

        elif cell.get_id() == 45 and neighbor.get_id() == 51:
            return "m"
        elif cell.get_id() == 51 and neighbor.get_id() == 45:
            return "l"

        elif cell.get_id() == 50 and neighbor.get_id() == 52:
            return "l"
        elif cell.get_id() == 52 and neighbor.get_id() == 50:
            return "m"

        elif cell.get_id() == 51 and neighbor.get_id() == 59:
            return "l"
        elif cell.get_id() == 59 and neighbor.get_id() == 51:
            return "m"

        elif cell.get_id() == 54 and neighbor.get_id() == 65:
            return "a"
        elif cell.get_id() == 65 and neighbor.get_id() == 54:
            return "b"

        elif cell.get_id() == 54 and neighbor.get_id() == 66:
            return "a"
        elif cell.get_id() == 66 and neighbor.get_id() == 54:
            return "b"

        elif cell.get_id() == 57 and neighbor.get_id() == 69:
            return "a"
        elif cell.get_id() == 69 and neighbor.get_id() == 57:
            return "b"

        elif cell.get_id() == 57 and neighbor.get_id() == 70:
            return "a"
        elif cell.get_id() == 70 and neighbor.get_id() == 57:
            return "b"

        # This catches assignment of neighbor of root cap cells
        rootcap_cellIDs = [60, 90, 120, 136, 166, 210, 296, 75, 105, 135, 151, 181, 225, 311]
        if cell.get_id() in rootcap_cellIDs:
            return "m"
        if neighbor.get_id() in rootcap_cellIDs:
            return "l"

        return None
    
    def get_neighbor_direction_when_neighbor_shares_one_v(cell, neighbor) -> str:
        # This catches direction of neighbor sharing one vertex in regular geometry
        if (
            cell.get_quad_perimeter().get_top_left()
            == neighbor.get_quad_perimeter().get_top_right()
        ):
            if (
                cell.get_quad_perimeter().get_left_lateral_or_medial(cell.sim.get_root_midpointx())
                == "lateral"
            ):
                return "l"
            elif (
                cell.get_quad_perimeter().get_left_lateral_or_medial(cell.sim.get_root_midpointx())
                == "medial"
            ):
                return "m"

        elif (
            cell.get_quad_perimeter().get_top_right()
            == neighbor.get_quad_perimeter().get_top_left()
        ):
            if (
                cell.get_quad_perimeter().get_right_lateral_or_medial(cell.sim.get_root_midpointx())
                == "lateral"
            ):
                return "l"
            elif (
                cell.get_quad_perimeter().get_right_lateral_or_medial(cell.sim.get_root_midpointx())
                == "medial"
            ):
                return "m"

        elif (
            cell.get_quad_perimeter().get_bottom_left()
            == neighbor.get_quad_perimeter().get_bottom_right()
        ):
            if (
                cell.get_quad_perimeter().get_left_lateral_or_medial(cell.sim.get_root_midpointx())
                == "lateral"
            ):
                return "l"
            elif (
                cell.get_quad_perimeter().get_left_lateral_or_medial(cell.sim.get_root_midpointx())
                == "medial"
            ):
                return "m"

        elif (
            cell.get_quad_perimeter().get_bottom_right()
            == neighbor.get_quad_perimeter().get_bottom_left()
        ):
            if (
                cell.get_quad_perimeter().get_right_lateral_or_medial(cell.sim.get_root_midpointx())
                == "lateral"
            ):
                return "l"
            elif (
                cell.get_quad_perimeter().get_right_lateral_or_medial(cell.sim.get_root_midpointx())
                == "medial"
            ):
                return "m"
        elif (
            cell.get_quad_perimeter().get_top_left()
            == neighbor.get_quad_perimeter().get_bottom_left()
        ):
            return "a"
        elif (
            cell.get_quad_perimeter().get_top_right()
            == neighbor.get_quad_perimeter().get_bottom_right()
        ):
            return "a"
        elif (
            cell.get_quad_perimeter().get_bottom_left()
            == neighbor.get_quad_perimeter().get_top_left()
        ):
            return "b"
        elif (
            cell.get_quad_perimeter().get_bottom_right()
            == neighbor.get_quad_perimeter().get_top_right()
        ):
            return "b"
        
        return None

    def get_neighbor_direction_when_neighbor_shares_no_vs_default_geo(cell, neighbor) -> str:
        if cell.get_id() == 17 and neighbor.get_id() == 20:
            return "l"
        elif cell.get_id() == 20 and neighbor.get_id() == 17:
            return "b"
        elif cell.get_id() == 18 and neighbor.get_id() == 25:
            return "l"
        elif cell.get_id() == 25 and neighbor.get_id() == 18:
            return "b"

        # This catches assignment of neighbor of root cap cells
        rootcap_cellIDs = [60, 90, 120, 136, 166, 210, 296, 75, 105, 135, 151, 181, 225, 311]
        if cell.get_id() in rootcap_cellIDs:
            neighbor_midpointy = neighbor.get_quad_perimeter().get_midpointy()
            if (
                neighbor_midpointy < cell.get_quad_perimeter().get_max_y()
                and neighbor_midpointy > cell.get_quad_perimeter().get_min_y()
            ):
                return "m"
            else:
                return "cell no longer root cap cell neighbor"
        if neighbor.get_id() in rootcap_cellIDs:
            self_midpointy = cell.get_quad_perimeter().get_midpointy()
            if (
                self_midpointy < neighbor.get_quad_perimeter().get_max_y()
                and self_midpointy > neighbor.get_quad_perimeter().get_min_y()
            ):
                return "l"
            else:
                return "cell no longer root cap cell neighbor"
        raise ValueError("Neighbor shares no Vs, is not in root tip, and is not a root cap cell")
