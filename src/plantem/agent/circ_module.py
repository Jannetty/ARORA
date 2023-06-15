from src.plantem.loc.quad_perimeter.quad_perimeter import QuadPerimeter, get_len_perimeter_in_common


class BaseCirculateModule:

    auxin = None
    arr = None
    aux_lax = None
    pina = None
    pinb = None
    pinl = None
    pinm = None
    cell = None

    def __init__(self, cell, init_vals):
        self.cell = cell
        # initialize all values
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
        AuxinA = self.calculate_neighbor_auxin(self.init_pina, self.timestep, self.area)
        AuxinB = self.calculate_neighbor_auxin(self.init_pinb, self.timestep, self.area)
        AuxinL = self.calculate_neighbor_auxin(self.init_pinl, self.timestep, self.area)
        AuxinM = self.calculate_neighbor_auxin(self.init_pinm, self.timestep, self.area)
        neighbors_aux = [AuxinA, AuxinB, AuxinL, AuxinM]

        # find neighbors
        neighbors = self.find_neighbors(curr_cell)

        # update current cell
        delta_aux = self.auxin + AuxinA + AuxinB + AuxinL + AuxinM
        cell_dict = self.update_current_cell(curr_cell, cell_dict, delta_aux)

        # update neighbor cells
        cell_dict = self.update_neighbor_cell(cell_dict, neighbors, neighbors_aux)

        return cell_dict

    # Helper functions
    def calculate_auxin(self, timestep, area) -> float:
        auxin = (self.ks - self.kd * self.init_auxin * area) * timestep
        return auxin

    def calculate_arr(self, timestep, area) -> float:
        arr = (
            self.ks * 1 / (self.init_arr / self.k_ARR_ARR + 1) - self.kd * self.init_arr * area
        ) * timestep
        return arr

    def calculate_aux_lax(self, timestep, area) -> float:
        auxin = self.calculate_auxin(timestep, area)
        aux_lax = (
            self.ks * (auxin / (auxin + self.k_auxin_AUXLAX)) - self.kd * self.init_aux_lax * area
        ) * timestep
        return aux_lax

    def calculate_pin(self, timestep, area) -> float:
        auxin = self.calculate_auxin(timestep, area)
        arr = self.calculate_arr(timestep, area)
        pin = (
            self.ks * (1 / (arr / self.k_ARR_PIN + 1)) * (auxin / (auxin + self.k_auxin_PIN))
        ) * timestep
        return pin

    def calculate_neighbor_pin(self, init, timestep, area) -> float:
        pin = self.calculate_pin(timestep, area)
        neighbor_pin = (0.25 * pin - self.kd * init * area) * timestep
        return neighbor_pin

    def calculate_neighbor_auxin(self, init, timestep, area) -> float:
        aux_lax = self.calculate_aux_lax(timestep, area)
        PIN = self.calculate_neighbor_pin(init, timestep, area)
        neighbor_auxin = (self.ks * 0.25 * aux_lax - self.kd * PIN * area) * timestep
        return neighbor_auxin

    def find_neighbors(self, curr_cell):
        neighbors = [
            curr_cell.neighborA,
            curr_cell.neighborB,
            curr_cell.neighborL,
            curr_cell.neighborM,
        ]
        return neighbors

    def update_current_cell(self, curr_cell, cell_dict, delta_aux) -> dict:
        if curr_cell not in cell_dict:
            cell_dict[curr_cell] = delta_aux
        else:
            cell_dict[curr_cell] += delta_aux
        return cell_dict

    def update_neighbor_cell(self, cell_dict, neighbors, neighbors_aux) -> dict:
        for i in range(4):
            if neighbors[i] not in cell_dict:
                cell_dict[neighbors[i]] = -neighbors_aux[i]
            else:
                cell_dict[neighbors[i]] += -neighbors_aux[i]
        return cell_dict
