from src.plantem.loc.quad_perimeter.quad_perimeter import get_len_perimeter_in_common


class BaseCirculateModule:
    """
    Representation of auxin circulation
    """

    auxin = None
    arr = None
    aux_lax = None
    pina = None
    pinb = None
    pinl = None
    pinm = None
    cell = None
    # medial = None
    # lateral = None

    def __init__(self, cell, init_vals: dict):
        """
        initialize all values
        """
        self.cell = cell

        # set medial to either "left" or "right" and lateral to the opposite 
        # based on where self.cell.QuadPerimeter.get_midpointx() is in relation 
        # to self.cell.sim.root_midpointx

        self.init_auxin = init_vals.get("auxin")
        self.auxin = self.init_auxin

        self.init_arr = init_vals.get("arr")
        self.arr = self.init_arr

        self.init_aux_lax = init_vals.get("aux_lax")
        self.aux_lax = self.init_aux_lax

        self.init_pina = init_vals.get("pina")
        self.pina = self.init_pina

        self.init_pinb = init_vals.get("pinb")
        self.pinb = self.init_pinb

        self.init_pinl = init_vals.get("pinl")
        self.pinl = self.init_pinl

        self.init_pinm = init_vals.get("pinm")
        self.pinm = self.init_pinm

        self.k_arr_arr = init_vals.get("k_arr_arr")
        self.k_auxin_auxlax = init_vals.get("k_auxin_auxlax")
        self.k_auxin_pin = init_vals.get("k_auxin_pin")
        self.k_arr_pin = init_vals.get("k_arr_pin")

        self.ks = init_vals.get("ks")
        self.kd = init_vals.get("kd")

        self.timestep = 1
        self.area = 100

    def update(self):
        """
        Update changes to the current and neighbor cells to circulator

        Returns
        -------
        :
            An updated circulator
        """
        # calculates changes in self species and neighbor auxins
        # adds changes to self and neighbors to circulator with key=cell
        # instance value = change in auxin
        # REMEMBER cells will be neighbors and selves multiple times

        curr_cell = self.cell
        cell_dict = curr_cell.sim.circulator.delta_auxins

        # base calculations
        self.auxin = self.calculate_auxin(self.timestep, self.area)
        self.arr = self.calculate_arr(self.timestep, self.area)
        self.aux_lax = self.calculate_aux_lax(self.timestep, self.area)
        self.pina = self.calculate_neighbor_pin(self.init_pina, self.timestep, self.area)
        self.pinb = self.calculate_neighbor_pin(self.init_pinb, self.timestep, self.area)
        self.pinl = self.calculate_neighbor_pin(self.init_pinl, self.timestep, self.area)
        self.pinm = self.calculate_neighbor_pin(self.init_pinm, self.timestep, self.area)

        # find neighbors
        neighborsa = self.cell.neighbora
        neighborsb = self.cell.neighborb
        neighborsl = self.cell.neighborl
        neighborsm = self.cell.neighborm

        # change in auxin relative to current cell
        auxina = self.get_neighbor_auxin(self.init_pina, neighborsa, "a", self.timestep, self.area)
        auxinb = self.get_neighbor_auxin(self.init_pinb, neighborsb, "b", self.timestep, self.area)
        auxinl = self.get_neighbor_auxin(self.init_pinl, neighborsl, "l", self.timestep, self.area)
        auxinm = self.get_neighbor_auxin(self.init_pinm, neighborsm, "m", self.timestep, self.area)
        neighbors_auxin = [auxina, auxinb, auxinl, auxinm]

        # update current cell
        delta_auxin = self.calculate_delta_auxin(neighbors_auxin)
        cell_dict = self.update_current_cell(curr_cell, cell_dict, delta_auxin)

        # update neighbor cells
        cell_dict = self.update_neighbor_cell(cell_dict, neighbors_auxin)

        return cell_dict

    # Helper functions
    def calculate_auxin(self, timestep: float, area: float) -> float:
        """
        Calcualte the auxin expression of current cell
        """
        auxin = (self.ks - self.kd * self.init_auxin * area) * timestep
        return auxin

    def calculate_arr(self, timestep: float, area: float) -> float:
        """
        Calculate the ARR expression of current cell
        """
        arr = (
            self.ks * 1 / (self.init_arr / self.k_arr_arr + 1) - self.kd * self.init_arr * area
        ) * timestep
        return arr

    def calculate_aux_lax(self, timestep: float, area: float) -> float:
        """
        Calculate the AUX/LAX expression of current cell
        """
        auxin = self.calculate_auxin(timestep, area)
        aux_lax = (
            self.ks * (auxin / (auxin + self.k_auxin_auxlax)) - self.kd * self.init_aux_lax * area
        ) * timestep
        return aux_lax

    def calculate_pin(self, timestep: float, area: float) -> float:
        """
        Calculate the PIN expression of current cell
        """
        auxin = self.calculate_auxin(timestep, area)
        arr = self.calculate_arr(timestep, area)
        pin = (
            self.ks * (1 / (arr / self.k_arr_pin + 1)) * (auxin / (auxin + self.k_auxin_pin))
        ) * timestep
        return pin

    def calculate_neighbor_pin(self, init: float, timestep: float, area: float) -> float:
        """
        Calculate the PIN expression of neighbor cells
        """
        pin = self.calculate_pin(timestep, area)
        neighbor_pin = (0.25 * pin - self.kd * init * area) * timestep
        return neighbor_pin

    def calculate_memfrac(self, neighbor, neighbor_direction: str) -> float:
        """
        Calculate the fraction of total cell membrane that is in a defined direction
        """
        cell_perimeter = self.cell.quad_perimeter.get_perimeter_len()
        common_perimeter = get_len_perimeter_in_common(self.cell.quad_perimeter,
                                                       neighbor.quad_perimeter, neighbor_direction)
        memfrac = common_perimeter / cell_perimeter
        return memfrac

    def get_neighbor_auxin(self, init_pin: float, neighbors: list, direction: str, timestep: float,
                           area: float) -> dict:
        """
        Calculate the auxin expression of neighbor cells in a defined direction
        """
        aux_lax = self.calculate_aux_lax(timestep, area)
        pin = self.calculate_neighbor_pin(init_pin, timestep, area)
        neighbor_dict = {}
        for neighbor in neighbors:
            memfrac = self.calculate_memfrac(neighbor, direction)
            neighbor_aux = (self.ks * memfrac * aux_lax - self.kd * pin * area) * timestep
            neighbor_dict[neighbor] = neighbor_aux
        return neighbor_dict

    def calculate_delta_auxin(self, neighbors_auxin: list) -> float:
        """
        Calculate the total amound of change in auxin for current cell
        """
        total_auxin = self.auxin
        for neighbors in neighbors_auxin:
            auxin = sum(neighbors.values())
            total_auxin += auxin
        return total_auxin

    def update_current_cell(self, curr_cell, cell_dict: dict, delta_aux: float) -> dict:
        """
        Update the change in auxin of current cell in the circulator
        """
        if curr_cell not in cell_dict:
            cell_dict[curr_cell] = delta_aux
        else:
            cell_dict[curr_cell] += delta_aux
        return cell_dict

    def update_neighbor_cell(self, cell_dict: dict, neighbors_auxin: list) -> dict:
        """
        Update the change in auxin of neighbor cells in the circulator
        """
        for each_dirct in neighbors_auxin:
            for neighbor in each_dirct:
                if neighbor not in cell_dict:
                    cell_dict[neighbor] = -each_dirct[neighbor]
                else:
                    cell_dict[neighbor] += -each_dirct[neighbor]
        return cell_dict

    # getter functions
    def get_auxin(self) -> float:
        return self.auxin

    def get_arr(self) -> float:
        return self.arr

    def get_aux_lax(self) -> float:
        return self.aux_lax

    def get_apical_pin(self) -> float:
        return self.pina

    def get_basal_pin(self) -> float:
        return self.pinb

    # write getters for all attributes including all pins AND left and right pin
    def get_left_pin(self) -> float:
        # write logic to determine whether to return pinm or pinl
        