class BaseCirculateModule():

    auxin = None
    ARR = None
    ARRA = None
    cell = None
    #

    def __init__(self, cell, init_vals):
        self.cell = cell
        # initialize all valuesz
        self.init_auxin = init_vals.get("auxin")
        self.init_ARR = init_vals.get("ARR")
        self.init_AUX_LAX = init_vals.get("AUX/LAX")
        self.init_PINA = init_vals.get("PINA")
        self.init_PINB = init_vals.get("PINB")
        self.init_PINL = init_vals.get("PINL")
        self.init_PINM = init_vals.get("PINM")

    def update(self):
        pass
        # calculates changes in self species and neighbor auxins
        # adds changes to self and neighbors to circulator with key=cell instance value = change in auxin
        # REMEMBER cells will be neighbors and selves multiple times

        curr_cell = self.cell
        cell_dict = curr_cell.sim.circulator.delta_auxins

        # base calculations
        auxin = 1 - 1*self.init_auxin
        ARR = 1 * (1/(self.init_ARR + 1) - 1*self.init_ARR)
        AUX_LAX = 1*(auxin/(auxin+1))*(1/(ARR/1)+1) - 1*self.init_AUX_LAX
        PIN = 1*(1/(ARR/1)+1)*(auxin/(auxin+1))
        PINA = 0.25 * PIN - 1*self.init_PINA
        PINB = 0.25 * PIN - 1*self.init_PINB
        PINL = 0.25 * PIN - 1*self.init_PINL
        PINM = 0.25 * PIN - 1*self.init_PINM
        AuxinA = 1 * 0.25 * AUX_LAX - 1 * PINA
        AuxinB = 1 * 0.25 * AUX_LAX - 1 * PINB
        AuxinL = 1 * 0.25 * AUX_LAX - 1 * PINL
        AuxinM = 1 * 0.25 * AUX_LAX - 1 * PINM
        neighbors_aux = [AuxinA, AuxinB, AuxinL, AuxinM]

        # find neighbor
        neighborA = curr_cell.neighborA
        neighborB = curr_cell.neighborB
        neighborL = curr_cell.neighborL
        neighborM = curr_cell.neighborM
        neighbors = [neighborA, neighborB, neighborL, neighborM]

        # update current cell
        delta_aux = AuxinA + AuxinB + AuxinL + AuxinM
        if curr_cell not in cell_dict:
            cell_dict[curr_cell] = delta_aux
        else:
            cell_dict[curr_cell] += delta_aux

        # update neighbor cells
        for i in range(4):
            if neighbors[i] not in cell_dict:
                cell_dict[neighbors[i]] = neighbors_aux[i]
            else:
                cell_dict[neighbors[i]] += neighbors_aux[i]


def calculate_auxin(self, ks, kd, timestep, area):
    auxin = (ks - kd*self.init_auxin*area) * timestep
    return auxin


def calculate_ARR(self, ks, kd):
    ARR = ks * (1/(self.init_ARR + 1) - kd*self.init_ARR)
    return ARR