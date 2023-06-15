class BaseCirculateModule():

    auxin = None
    ARR = None
    AUX_LAX = None
    PINA = None
    PINB = None
    PINL = None
    PINM = None
    cell = None

    def __init__(self, cell, init_vals):
        self.cell = cell
        # initialize all values
        self.init_auxin = init_vals.get("auxin")
        self.auxin = self.init_auxin

        self.init_ARR = init_vals.get("ARR")
        self.ARR = self.init_ARR

        self.init_AUX_LAX = init_vals.get("AUX/LAX")
        self.AUX_LAX = self.init_AUX_LAX

        self.init_PINA = init_vals.get("PINA")
        self.PINA = self.init_PINA

        self.init_PINB = init_vals.get("PINB")
        self.PINB = self.init_PINB

        self.init_PINL = init_vals.get("PINL")
        self.PINL = self.init_PINL

        self.init_PINM = init_vals.get("PINM")
        self.PINM = self.init_PINM

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
        self.ARR = self.calculate_ARR(self.timestep, self.area)
        self.AUX_LAX = self.calculate_AUX_LAX(self.timestep, self.area)
        self.PIN = self.calculate_PIN(self.timestep, self.area)
        self.PINA = self.calculate_neighbor_PIN(self.init_PINA, self.timestep, self.area)
        self.PINB = self.calculate_neighbor_PIN(self.init_PINB, self.timestep, self.area)
        self.PINL = self.calculate_neighbor_PIN(self.init_PINL, self.timestep, self.area)
        self.PINM = self.calculate_neighbor_PIN(self.init_PINM, self.timestep, self.area)
        AuxinA = self.calculate_neighbor_auxin(self.init_PINA, self.timestep, self.area)
        AuxinB = self.calculate_neighbor_auxin(self.init_PINB, self.timestep, self.area)
        AuxinL = self.calculate_neighbor_auxin(self.init_PINL, self.timestep, self.area)
        AuxinM = self.calculate_neighbor_auxin(self.init_PINM, self.timestep, self.area)
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
        auxin = (self.ks - self.kd*self.init_auxin*area) * timestep
        return auxin

    def calculate_ARR(self, timestep, area) -> float:
        ARR = (self.ks * 1/(self.init_ARR/self.k_ARR_ARR + 1) - self.kd*self.init_ARR*area) * timestep
        return ARR

    def calculate_AUX_LAX(self, timestep, area) -> float:
        auxin = self.calculate_auxin(timestep, area)
        AUX_LAX = (self.ks*(auxin/(auxin+self.k_auxin_AUXLAX)) - self.kd*self.init_AUX_LAX*area) * timestep
        return AUX_LAX

    def calculate_PIN(self, timestep, area) -> float:
        auxin = self.calculate_auxin(timestep, area)
        ARR = self.calculate_ARR(timestep, area)
        PIN = (self.ks * (1/(ARR/self.k_ARR_PIN + 1)) * (auxin/(auxin+self.k_auxin_PIN))) * timestep
        return PIN

    def calculate_neighbor_PIN(self, init, timestep, area) -> float:
        PIN = self.calculate_PIN(timestep, area)
        neighbor_PIN = (0.25 * PIN - self.kd*init*area) * timestep
        return neighbor_PIN
    
    def calculate_neighbor_auxin(self, init, timestep, area) -> float:
        AUX_LAX = self.calculate_AUX_LAX(timestep, area)
        PIN = self.calculate_neighbor_PIN(init, timestep, area)
        neighbor_auxin = (self.ks * 0.25 * AUX_LAX - self.kd * PIN * area) * timestep
        return neighbor_auxin

    def find_neighbors(self, curr_cell):
        neighbors = [curr_cell.neighborA, curr_cell.neighborB, curr_cell.neighborL, curr_cell.neighborM]
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
