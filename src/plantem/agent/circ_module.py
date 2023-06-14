from plantem.sim.circulator import Circulator
from plantem.agent.cell import GrowingCell


class BaseCirculateModule():

    auxin = None
    ARR = None
    ARRA = None
    cell = None
    #

    def __init__(self, cell):
        self.cell = cell
        # initialize all values

    def update(self):
        pass
        # calculates changes in self species and neighbor auxins
        # adds changes to self and neighbors to circulator with key=cell instance value = change in auxin
        # REMEMBER cells will be neighbors and selves multiple times