from plantem.sim.circulator import Circulator
from plantem.agent.cell import GrowingCell


class BaseCirculateModule():

    auxin = None
    ARR = None
    ARRA = None
    cell = None
    #

    def __init__(self, cell, init_aux):
        self.cell = cell
        # initialize all values
        self.auxin_c = 1
        self.ARR_c = 1
        self.AUX_LAX_c = 1
        self.PINA_c = 1
        self.PINB_c = 1
        self.PINL_c = 1
        self.PINM_c = 1

    def update(self):
        pass
        # calculates changes in self species and neighbor auxins
        # adds changes to self and neighbors to circulator with key=cell instance value = change in auxin
        # REMEMBER cells will be neighbors and selves multiple times

        curr_cell = self.cell
        cell_dict = curr_cell.sim.circulator.delta_auxins

        # based calculations
        auxin = 1 - 1*self.auxin_c
        ARR = 1 * (1/(self.ARR_c + 1) - 1*self.ARR_c)
        AUX_LAX = 1*(auxin/(auxin+1))*(1/(ARR/1)+1) - 1*self.AUX_LAX_c
        PIN = 1*(1/(ARR/1)+1)*(auxin/(auxin+1))
        PINA = 0.25 * PIN - 1*self.PINA_c
        PINB = 0.25 * PIN - 1*self.PINB_c
        PINL = 0.25 * PIN - 1*self.PINL_c
        PINM = 0.25 * PIN - 1*self.PINM_c
        AuxinA = 1 * 0.25 * AUX_LAX - 1 * PINA
        AuxinB = 1 * 0.25 * AUX_LAX - 1 * PINB
        AuxinL = 1 * 0.25 * AUX_LAX - 1 * PINL
        AuxinM = 1 * 0.25 * AUX_LAX - 1 * PINM

        # find neighbor
        neighbors = curr_cell.neighbor
        neighbors_aux = [AuxinA, AuxinB, AuxinL, AuxinM]

        # update current cell
        delta_aux = sum(neighbors_aux)
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
