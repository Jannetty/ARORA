from src.plantem.loc.quad_perimeter.quad_perimeter import get_len_perimeter_in_common
from src.plantem.agent.cell import GrowingCell


class BaseCirculateModule:

    auxin = None
    arr = None
    aux_lax = None
    pina = None
    pinb = None
    pinl = None
    pinm = None
    cell = None

    def __init__(self, cell: GrowingCell, init_vals: dict):
        # initialize all values
        self.cell = cell

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

        self.k_ARR_ARR = init_vals.get("k_ARR_ARR")
        self.k_auxin_AUXLAX = init_vals.get("k_auxin_AUXLAX")
        self.k_auxin_PIN = init_vals.get("k_auxin_PIN")
        self.k_ARR_PIN = init_vals.get("k_ARR_PIN")

        self.ks = init_vals.get("ks")
        self.kd = init_vals.get("kd")

        self.timestep = 1
        self.area = 100

    def update(self):
        pass
        # calculates changes in self species and neighbor auxins
        # adds changes to self and neighbors to circulator with key=cell instance value = change in auxin
        # REMEMBER cells will be neighbors and selves multiple times

        curr_cell = self.cell
        cell_dict = curr_cell.sim.circulator.delta_auxins

        # base calculations
        self.auxin = self.calculate_auxin(self.timestep, self.area)
        self.arr = self.calculate_arr(self.timestep, self.area)
        self.aux_lax = self.calculate_aux_lax(self.timestep, self.area)
        self.PIN = self.calculate_pin(self.timestep, self.area)
        self.pina = self.calculate_neighbor_pin(self.init_pina, self.timestep, self.area)
        self.pinb = self.calculate_neighbor_pin(self.init_pinb, self.timestep, self.area)
        self.pinl = self.calculate_neighbor_pin(self.init_pinl, self.timestep, self.area)
        self.pinm = self.calculate_neighbor_pin(self.init_pinm, self.timestep, self.area)

        # find neighbors
        neighborsa = self.cell.neighbora
        neighborsb = self.cell.neighborb
        neighborsl = self.cell.neighborl
        neighborsm = self.cell.neighborm

        # auxin import
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
            self.ks * 1 / (self.init_arr / self.k_ARR_ARR + 1) - self.kd * self.init_arr * area
        ) * timestep
        return arr

    def calculate_aux_lax(self, timestep: float, area: float) -> float:
        """
        Calculate the AUX/LAX expression of current cell
        """
        auxin = self.calculate_auxin(timestep, area)
        aux_lax = (
            self.ks * (auxin / (auxin + self.k_auxin_AUXLAX)) - self.kd * self.init_aux_lax * area
        ) * timestep
        return aux_lax

    def calculate_pin(self, timestep: float, area: float) -> float:
        """
        Calculate the PIN expression of current cell
        """
        auxin = self.calculate_auxin(timestep, area)
        arr = self.calculate_arr(timestep, area)
        pin = (
            self.ks * (1 / (arr / self.k_ARR_PIN + 1)) * (auxin / (auxin + self.k_auxin_PIN))
        ) * timestep
        return pin

    def calculate_neighbor_pin(self, init: float, timestep: float, area: float) -> float:
        pin = self.calculate_pin(timestep, area)
        neighbor_pin = (0.25 * pin - self.kd * init * area) * timestep
        return neighbor_pin

    def calculate_memfrac(self, neighbor, neighbor_direction: str) -> float:
        cell_perimeter = self.cell.quad_perimeter.get_perimeter_len()
        common_perimeter = get_len_perimeter_in_common(self.cell.quad_perimeter,
                                                       neighbor.quad_perimeter, neighbor_direction)
        memfrac = common_perimeter / cell_perimeter
        return memfrac

    def get_neighbor_auxin(self, init_pin: float, neighbors: list, direction: str, timestep, area) -> dict:
        aux_lax = self.calculate_aux_lax(timestep, area)
        pin = self.calculate_neighbor_pin(init_pin, timestep, area)
        neighbor_dict = {}
        for neighbor in neighbors:
            memfrac = self.calculate_memfrac(neighbor, direction)
            neighbor_aux = (self.ks * memfrac * aux_lax - self.kd * pin * area) * timestep
            neighbor_dict[neighbor] = neighbor_aux
        return neighbor_dict

    def calculate_delta_auxin(self, neighbors_auxin: list) -> float:
        total_auxin = self.auxin
        for neighbors in neighbors_auxin:
            auxin = sum(neighbors.values())
            total_auxin += auxin
        return total_auxin

    def update_current_cell(self, curr_cell, cell_dict, delta_aux: float) -> dict:
        if curr_cell not in cell_dict:
            cell_dict[curr_cell] = delta_aux
        else:
            cell_dict[curr_cell] += delta_aux
        return cell_dict

    def update_neighbor_cell(self, cell_dict: dict, neighbors_auxin: list) -> dict:
        for i in range(len(neighbors_auxin)):
            for neighbor in neighbors_auxin[i]:
                if neighbor not in cell_dict:
                    cell_dict[neighbor] = -neighbors_auxin[i][neighbor]
                else:
                    cell_dict[neighbor] += -neighbors_auxin[i][neighbor]
            i += 1
        return cell_dict
