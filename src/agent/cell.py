from arcade import Sprite
from arcade import draw_polygon_filled, draw_polygon_outline
from typing import TYPE_CHECKING, Any, cast, Union, Dict
from src.arora_enums import PinLocalizationRulesetEnum, CircModEnum
from src.agent.circ_module_universal_syndeg import CirculateModuleUniversalSynDeg
from src.agent.circ_module_indep_syn_deg import CirculateModuleIndSynDeg
from src.agent.circ_module_aux_syn_deg_only import CirculateModuleAuxinSynDegOnly
from src.agent.circ_module_aux_syn_deg_export import CirculateModuleAuxinSynDegExport
from src.agent.circ_module_imposed_pin_arr_activity import (
    CirculateModuleImposedPinArrActivity,
)
from src.agent.circ_module_imposed_pin_no_arr import CirculateModuleImposedPinNoArr
from src.loc.quad_perimeter.quad_perimeter import QuadPerimeter
from src.agent.default_geo_neighbor_helpers import NeighborHelpers
from src.agent.circ_module import CirculateModule

if TYPE_CHECKING:
    from src.sim.simulation.sim import GrowingSim
    from src.loc.vertex.vertex import Vertex

# Growth rate of cells in meristematic zone in um per um per hour from Van den Berg et al. 2018
MERISTEMATIC_GROWTH_RATE: float = -0.0179

# Growth rate cells in transition zone in um per um per hour from Van den Berg et al. 2018
TRANSITION_GROWTH_RATE: float = -0.0179

# Growth rate cells in elongation zone in um per um per hour from Van den Berg et al. 2018
ELONGATION_GROWTH_RATE: float = -0.00112

# Growth rate cells in differentiation zone in um per um per hour from Van den Berg et al. 2018
DIFFERENTIATION_GROWTH_RATE: float = -0.00112


# um Y distance from tip at which cells pass from root tip to meristematic zone
# Inferred from Van dn Berg et al. 2018
ROOT_TIP_DIST_FROM_TIP: int = 74

# um Y distance from tip at which cells pass from meristemtic to transition zone
# from Van den Berg et al. 2018
MERISTEMATIC_MAX_DIST_FROM_TIP: int = ROOT_TIP_DIST_FROM_TIP + 160

# um Y distance from tip at which cells pass from transition to elongation zone
# from Van den Berg et al. 2018
TRANSITION_MAX_DIST_FROM_TIP: int = MERISTEMATIC_MAX_DIST_FROM_TIP + 180

# um Y distance from tip at which cells pass from elongation to differentiation zone
# from Van den Berg et al. 2018
ELONGATION_MAX_DIST_FROM_TIP: int = TRANSITION_MAX_DIST_FROM_TIP + 600

# um Y distance from tip at which cells leave differentiation zone
# from Van den Berg et al. 2018
DIFFERENTIATION_MAX_DIST_FROM_TIP: int = ELONGATION_MAX_DIST_FROM_TIP + 500

# max um X distance vasc cells can be from self.sim.get_root_midpointx()
# from Salvi et al. 2020
VASC_CELL_DIST_FROM_ROOT_MIDPOINTX: int = 12

# max um X distance peri cells can be from self.sim.get_root_midpointx()
# from Salvi et al. 2020
PERI_CELL_DIST_FROM_ROOT_MIDPOINTX: int = 17

# max um X distance endo cells can be from self.sim.get_root_midpointx()
# from Salvi et al. 2020
ENDO_CELL_DIST_FROM_ROOT_MIDPOINTX: int = 24

# max um X distance cortex cells can be from self.sim.get_root_midpointx()
# from Salvi et al. 2020
CORTEX_CELL_DIST_FROM_ROOT_MIDPOINTX: int = 35

# max um X distance epidermis cells can be from self.sim.get_root_midpointx()
# from Salvi et al. 2020
EPIDERMIS_CELL_DIST_FROM_ROOT_MIDPOINTX: int = 45

MERISTEM_FIRST_ROW_CENTER_Y = 75.5  # μm distance from tip for first meristematic band
MERISTEM_ROW_STEP = 5.0  # μm between successive meristematic bands
MERISTEM_MAX_ROW_INDEX = 16  # last observed meristematic band index

TRANSITION_FIRST_ROW_CENTER_Y = 160.5  # μm distance from tip for first transition band
TRANSITION_ROW_STEP = 5.0
TRANSITION_MAX_ROW_INDEX = 33  # highest observed transition band index


class Cell(Sprite):
    """
    A class to represent a cell in the simulation.

    Parameters
    ----------
    simulation : GrowingSim
        The simulation object.
    corners : list of Vertex
        The Vertex corners of the cell.
    init_vals : dict of str to Any
        Initial values for cell Circ Mod.
    id : int
        The ID of the cell.

    Attributes
    ----------
    c_id : int
        The ID of the cell.
    a_neighbors : list
        List of apical neighbors.
    b_neighbors : list
        List of basal neighbors.get_pin
    l_neighbors : list
        List of lateral neighbors.
    m_neighbors : list
        List of medial neighbors.
    sim : GrowingSim
        The simulation object that calls this cell.
    quad_perimeter : QuadPerimeter
        The quad perimeter object defining this cell's location.
    circ_mod : BaseCirculateModule
        The circ module object that will manage hormone circulation for this cell.
    growing : bool
        Indicates if the cell is growing.
    dev_zone : float
        The development zone of the cell.
    cell_type : str
        The type of the cell.
    pin_loc_ruleset : PinLocalizationRules
        The rules the cell is following to determine its PIN localization
    color : str
        The color of the cell.
    """

    dev_zone: str
    cell_type: str
    growing: bool
    pin_loc_ruleset: PinLocalizationRulesetEnum

    def __init__(
        self,
        simulation: "GrowingSim",
        corners: list["Vertex"],
        init_vals: dict[str, Any],
        c_id: int,
        from_division: bool = False,
    ):
        """
        Initializes a new instance of the Cell class.

        Parameters
        ----------
        simulation : GrowingSim
            The simulation object.
        corners : list of Vertex
            The Vertex corners of the cell.
        init_vals : dict of str to Any
            Initial values for cell Circ Mod.
        id : int
            The ID of the cell.
        """
        self.c_id = c_id
        super().__init__()
        self.a_neighbors: list["Cell"] = []
        self.b_neighbors: list["Cell"] = []
        self.l_neighbors: list["Cell"] = []
        self.m_neighbors: list["Cell"] = []
        self.sim: "GrowingSim" = simulation
        simulation.increment_next_cell_id()
        self.quad_perimeter = QuadPerimeter(corners)

        h = self.quad_perimeter.get_height()
        if from_division:
            # daughter cell: h is the true birth height, divide at 2× that
            self.birth_height = h
        else:
            # file-loaded cell: h is the midpoint of the growth cycle (= 1.5× birth)
            self.birth_height = h / 1.5
        self.division_height = 2.0 * self.birth_height

        # Type hint circ_mod to accept any class that implements the CirculateModule protocol
        self.circ_mod: CirculateModule
        circ_mod_name = simulation.get_circ_mod()
        match circ_mod_name:
            case CircModEnum.UNIVERSAL_SYN_DEG:
                self.circ_mod = CirculateModuleUniversalSynDeg(self, init_vals)
            case CircModEnum.INDEP_SYN_DEG:
                self.circ_mod = CirculateModuleIndSynDeg(self, init_vals)
            case CircModEnum.AUX_SYN_DEG_ONLY:
                self.circ_mod = CirculateModuleAuxinSynDegOnly(self, init_vals)
            case CircModEnum.AUX_SYN_DEG_EXP:
                self.circ_mod = CirculateModuleAuxinSynDegExport(self, init_vals)
            case CircModEnum.IMPOSED_PIN_ARR_ACTIVITY:
                self.circ_mod = CirculateModuleImposedPinArrActivity(self, init_vals)
            case CircModEnum.IMPOSED_PIN_NO_ARR:
                self.circ_mod = CirculateModuleImposedPinNoArr(self, init_vals)
            case _:
                raise SyntaxError(f"Unknown circ mod '{circ_mod_name}'")

        if self.sim.geometry != "default":
            self.dev_zone = ""
            self.cell_type = ""
            self.growing = False
        else:
            dist = self.get_distance_from_tip()
            self.dev_zone = self.calculate_dev_zone(dist)
            self.cell_type = self.calculate_cell_type()
            self.growing = cast(bool, init_vals.get("growing"))

        self.pin_loc_ruleset = self.get_sim().get_pin_loc_rules()
        self.pin_weights: Dict[str, float] = self.calculate_pin_weights()
        self.color: tuple[int, int, int, int] = self.calculate_color()
        self.sim.add_to_cell_list(self)

    def calculate_cell_type(self) -> str:
        """
        Calculates the type of cell based on its x location in relation to center of root.
        Note: This only works for the default geometry.

        Returns
        -------
        str
            Type of cell.
        """
        root_tip_midpoint_x = self.sim.get_root_midpointx()
        cell_midpoint_x = self.quad_perimeter.get_midpointx()
        dist_from_root_midpoint = abs(root_tip_midpoint_x - cell_midpoint_x)
        cell_type = None
        if self.dev_zone == "roottip":
            cell_type = "roottip"
        elif dist_from_root_midpoint < VASC_CELL_DIST_FROM_ROOT_MIDPOINTX:
            cell_type = "vasc"
        elif dist_from_root_midpoint < PERI_CELL_DIST_FROM_ROOT_MIDPOINTX:
            cell_type = "peri"
        elif dist_from_root_midpoint < ENDO_CELL_DIST_FROM_ROOT_MIDPOINTX:
            cell_type = "endo"
        elif dist_from_root_midpoint < CORTEX_CELL_DIST_FROM_ROOT_MIDPOINTX:
            cell_type = "cortex"
        elif dist_from_root_midpoint < EPIDERMIS_CELL_DIST_FROM_ROOT_MIDPOINTX:
            cell_type = "epidermis"
        if cell_type is None:
            raise ValueError("Cell type not recognized")
        return cell_type

    def get_cell_type(self) -> str:
        """
        Returns the type of cell.

        Returns
        -------
        str
            The type of cell.
        """
        return self.cell_type

    def calculate_color(self) -> tuple[int, int, int, int]:
        """
        Calculates the color of the cell based on the auxin concentration and sim's cmap.

        Returns
        -------
        tuple[int, int, int, int]
            A tuple containing the RGBA values of the calculated color.
        """
        auxin = self.circ_mod.get_auxin()
        max_auxin = 2000  # TODO make this not hard coded
        normalized_auxin = (auxin) / (max_auxin)
        rgba = self.sim.cmap(normalized_auxin)
        # Scale and round the RGB values
        red, green, blue = (
            int(rgba[0] * 255 + 0.5),
            int(rgba[1] * 255 + 0.5),
            int(rgba[2] * 255 + 0.5),
        )
        alpha = 255
        return (red, green, blue, alpha)

    def get_quad_perimeter(self) -> "QuadPerimeter":
        """
        Returns the quad perimeter object defining the cell's location.

        Returns
        -------
        QuadPerimeter
            The quad perimeter object defining the cell's location.
        """
        return self.quad_perimeter

    def get_c_id(self) -> int:
        """
        Returns the ID of the cell.

        Returns
        -------
        int
            The ID of the cell.
        """
        return self.c_id

    def get_dev_zone(self) -> str:
        """
        Returns the development zone of the cell.

        Returns
        -------
        str
            The development zone of the cell.
        """
        return self.dev_zone

    def set_dev_zone(self, zone: str) -> None:
        """
        Sets the development zone of the cell.

        Parameters
        ----------
        zone : str
            The development zone to set for the cell.
        """
        self.dev_zone = zone

    def set_growing(self, growing: bool) -> None:
        """
        Sets the growing status of the cell.

        Parameters
        ----------
        growing : bool
            The growing status to set for the cell.
        """
        self.growing = growing

    def get_growing(self) -> bool:
        """
        Returns the growing status of the cell.

        Returns
        -------
        bool
            The growing status of the cell.
        """
        return self.growing

    def add_neighbor(self, neighbor: "Cell") -> None:
        """
        Adds a neighbor to the cell's correct neighbor list.

        Parameters
        ----------
        neighbor : Cell
            The neighbor to add to the cell's neighbor list.
        """
        if not self.check_if_neighbor(neighbor):
            neighbor_location = self.find_new_neighbor_relative_location(neighbor)
            if neighbor_location == "a":
                self.a_neighbors.append(neighbor)
            elif neighbor_location == "b":
                self.b_neighbors.append(neighbor)
            elif neighbor_location == "l":
                self.l_neighbors.append(neighbor)
            elif neighbor_location == "m":
                self.m_neighbors.append(neighbor)
            elif neighbor_location == "cell no longer root cap cell neighbor":
                pass
            elif neighbor_location is None:
                print(f"cell {self.c_id} is not neighbors with cell {neighbor.get_c_id()}")
                raise ValueError("Non-neighbor added as neighbor")
            else:
                raise ValueError("Non-neighbor added as neighbor")
        else:
            raise ValueError("Neighbor being added twice")

    def find_new_neighbor_relative_location(self, neighbor: "Cell") -> str:
        """
        Finds the relative location of a new neighbor to the cell.

        Parameters
        ----------
        neighbor : Cell
            The neighbor to find the relative location of.

        Returns
        -------
        str
            The relative location of the neighbor to the cell.

        Raises
        ------
        ValueError
            If the neighbor is not recognized.
        """
        self_vs = self.get_quad_perimeter().get_vs()
        neighbor_vs = neighbor.get_quad_perimeter().get_vs()
        neighbor_dir = ""
        if len(set(self_vs).intersection(set(neighbor_vs))) == 1 and self.sim.geometry == "default":
            neighbor_dir = NeighborHelpers.get_neighbor_dir_neighbor_shares_one_v_default_geo(
                self, neighbor
            )
        if len(set(self_vs).intersection(set(neighbor_vs))) == 0 and self.sim.geometry == "default":
            neighbor_dir = NeighborHelpers.get_neighbor_dir_neighbor_shares_no_vs_default_geo(
                self, neighbor
            )
        if len(set(self_vs).intersection(set(neighbor_vs))) == 2 and neighbor_dir == "":
            neighbor_dir = self.get_neighbor_di_neighbor_shares_two_vs_std(neighbor)
        if len(set(self_vs).intersection(set(neighbor_vs))) == 1 and neighbor_dir == "":
            neighbor_dir = self.get_neighbor_dir_neighbor_shares_one_v_std(neighbor)
        if neighbor_dir not in [
            "a",
            "b",
            "l",
            "m",
            "cell no longer root cap cell neighbor",
        ]:
            raise ValueError("Neighbor not recognized")
        return neighbor_dir

    def get_a_neighbors(self) -> list["Cell"]:
        """
        Returns the list of apical neighbors.

        Returns
        -------
        list
            The list of apical neighbors.
        """
        return self.a_neighbors

    def get_b_neighbors(self) -> list["Cell"]:
        """
        Returns the list of basal neighbors.

        Returns
        -------
        list
            The list of basal neighbors.
        """
        return self.b_neighbors

    def get_m_neighbors(self) -> list["Cell"]:
        """
        Returns the list of medial neighbors.

        Returns
        -------
        list
            The list of medial neighbors.
        """
        return self.m_neighbors

    def get_l_neighbors(self) -> list["Cell"]:
        """
        Returns the list of lateral neighbors.

        Returns
        -------
        list
            The list of lateral neighbors.
        """
        return self.l_neighbors

    def get_all_neighbors(self) -> list["Cell"]:
        """
        Returns the list of all neighbors.

        Returns
        -------
        list of Cell
            The list of all neighbors.
        """
        return (
            self.get_a_neighbors()
            + self.get_b_neighbors()
            + self.get_m_neighbors()
            + self.get_l_neighbors()
        )

    def get_sim(self) -> "GrowingSim":
        """
        Returns the simulation object that calls this cell.

        Returns
        -------
        GrowingSim
            The simulation object that calls this cell.
        """
        return self.sim

    def get_circ_mod(self) -> "CirculateModule":
        """
        Returns the circ module object that manages hormone circulation for this cell.

        Returns
        -------
        BaseCirculateModule
            The circ module object that manages hormone circulation for this cell.
        """
        return self.circ_mod

    def add_l_neighbor(self, neighbor: "Cell") -> None:
        """
        Adds a lateral neighbor to the cell's lateral neighbor list.

        Note this is ONLY used to directly add LRC cells to the medial neighbor list of growing cells
        when running under default conditions.

        Parameters
        ----------
        neighbor : Cell
            The lateral neighbor to add to the cell's lateral neighbor list.
        """
        assert self.get_sim().geometry == "default"
        assert neighbor.get_c_id() in NeighborHelpers.ROOTCAP_CELL_IDs
        self.l_neighbors.append(neighbor)

    def add_m_neighbor(self, neighbor: "Cell") -> None:
        """
        Adds a medial neighbor to the cell's medial neighbor list.

        Note this is ONLY used to directly add growing cells to the lateral neighbor list of LRC cells
        when running under default conditions.

        Parameters
        ----------
        neighbor : Cell
            The medial neighbor to add to the cell's medial neighbor list.
        """
        assert self.get_sim().geometry == "default"
        assert self.get_c_id() in NeighborHelpers.ROOTCAP_CELL_IDs
        self.m_neighbors.append(neighbor)

    def remove_m_neighbor(self, neighbor: "Cell") -> None:
        """
        Removes a medial neighbor from the cell's medial neighbor list.

        Note this is ONLY used to directly remove growing cells from the lateral neighbor list of LRC cells
        when running under default conditions.

        Parameters
        ----------
        neighbr : Cell
            The medial neighbor to remove from the cell's medial neighbor list.
        """
        assert self.get_sim().geometry == "default"
        assert self.get_c_id() in NeighborHelpers.ROOTCAP_CELL_IDs
        self.m_neighbors.remove(neighbor)

    def remove_l_neighbor(self, neighbor: "Cell") -> None:
        """
        Removes a lateral neighbor from the cell's lateral neighbor list.

        Note this is ONLY used to directly remove LRC cells from the medial neighbor list of growing cells
        when running under default conditions.

        Parameters
        ----------
        neighbor : Cell
            The lateral neighbor to remove from the cell's lateral neighbor list.
        """
        assert self.get_sim().geometry == "default"
        assert neighbor.get_c_id() in NeighborHelpers.ROOTCAP_CELL_IDs
        self.l_neighbors.remove(neighbor)

    def remove_neighbor(self, cell: "Cell") -> None:
        """
        Removes a neighbor from the cell's neighbor list.

        Parameters
        ----------
        cell : Cell
            The neighbor to remove from the cell's neighbor list.
        """
        if cell in self.a_neighbors:
            self.a_neighbors.remove(cell)
        elif cell in self.b_neighbors:
            self.b_neighbors.remove(cell)
        elif cell in self.l_neighbors:
            self.l_neighbors.remove(cell)
        elif cell in self.m_neighbors:
            self.m_neighbors.remove(cell)
        else:
            raise ValueError("Non neighbor cell being removed from neighbor list")

    def check_if_neighbor(self, cell: "Cell") -> bool:
        """
        Check if a cell is a neighbor of the current cell.

        Parameters
        ----------
        cell : Cell
            The cell to check if it is a neighbor.

        Returns
        -------
        bool
            True if the cell is a neighbor (in the neighbor lists), False if not.
        """
        if cell in self.a_neighbors:
            return True
        if cell in self.b_neighbors:
            return True
        if cell in self.l_neighbors:
            return True
        if cell in self.m_neighbors:
            return True
        return False

    def get_area(self) -> float:
        """
        Returns the area of the cell.

        Returns
        -------
        float
            The area of the cell.
        """
        return self.quad_perimeter.get_area()

    def draw(
        self, *, filter: Any = None, pixelated: Any = None, blend_function: Any = None
    ) -> None:
        """
        Draws the cell on the screen.

        Parameters
        ----------
        filter : Any, optional
            The filter to be applied during drawing, by default None.
        pixelated : Any, optional
            The pixelation level to be applied during drawing, by default None.
        blend_function : Any, optional
            The blend function to be used during drawing, by default None.
        """

        super().draw(filter=filter, pixelated=pixelated, blend_function=blend_function)
        self.color = self.calculate_color()
        point_list = self.quad_perimeter.get_corners_for_disp()
        point_list_for_draw_functions = []
        for point in point_list:
            pt_tuple = (point[0], point[1])
            point_list_for_draw_functions.append(pt_tuple)
        draw_polygon_filled(point_list=point_list_for_draw_functions, color=self.color)
        draw_polygon_outline(
            point_list=point_list_for_draw_functions, color=(0, 0, 0, 255), line_width=1
        )

    def grow(self) -> None:
        """
        Grows the cell by adding the cell and calculated delta to the sim's vertex mover.
        """
        self.sim.get_vertex_mover().add_cell_delta_val(self, self.calculate_delta())

    def get_distance_from_tip(self) -> float:
        """
        Returns the distance of the cell from the root tip.

        Returns
        -------
        float
            The distance of the cell from the root tip.
        """
        root_tip_y = self.sim.get_root_tip_y()
        self_y = self.quad_perimeter.get_midpointy()
        return abs(self_y - root_tip_y)

    def calculate_dev_zone(self, dist_to_root_tip: float) -> str:
        """
        Calculates the development zone of the cell based on its distance from the root tip.

        Parameters
        ----------
        dist_to_root_tip : float
            The distance of the cell from the root tip.

        Returns
        -------
        str
            The development zone of the cell.

        Notes
        -----
        This method only works for the default geometry.

        The development zones are defined as follows:
        - 'roottip': If the cell ID is in the root_cap_cells list or the distance to the root tip is less than ROOT_TIP_DIST_FROM_TIP.
        - 'meristematic': If the distance to the root tip is less than MERISTEMATIC_MAX_DIST_FROM_TIP.
        - 'transition': If the distance to the root tip is less than TRANSITION_MAX_DIST_FROM_TIP.
        - 'elongation': If the distance to the root tip is less than ELONGATION_MAX_DIST_FROM_TIP.
        - 'differentiation': Otherwise.
        """
        root_cap_cells = NeighborHelpers.ROOTCAP_CELL_IDs
        if self.c_id in root_cap_cells:
            return "roottip"
        if dist_to_root_tip < ROOT_TIP_DIST_FROM_TIP:
            return "roottip"
        if dist_to_root_tip < MERISTEMATIC_MAX_DIST_FROM_TIP:
            return "meristematic"
        if dist_to_root_tip < TRANSITION_MAX_DIST_FROM_TIP:
            return "transition"
        if dist_to_root_tip < ELONGATION_MAX_DIST_FROM_TIP:
            return "elongation"
        return "differentiation"

    def get_growth_rate(self) -> float:
        """
        Returns the growth rate of the cell based on its development zone.

        Returns:
        ----------
        float:
            The growth rate of the cell.

        Raises:
        ----------
        ValueError:
            If the cell has no recognizable development zone.
        """
        if self.get_quad_perimeter().get_height() >= 250:
            self.growing = False
            return 0
        if self.dev_zone == "roottip":
            return 0
        if self.dev_zone == "meristematic":
            return MERISTEMATIC_GROWTH_RATE
        if self.dev_zone == "transition":
            return TRANSITION_GROWTH_RATE
        if self.dev_zone == "elongation":
            return ELONGATION_GROWTH_RATE
        if self.dev_zone == "differentiation":
            return DIFFERENTIATION_GROWTH_RATE
        raise ValueError("Cell has no recognizable dev zone")

    def calculate_delta(self) -> float:
        """
        Calculate the growth delta of the cell for a single simulation tick.

        Returns
        -------
        float
            The growth delta (in μm) for this tick.

        Note
        ----
        VDB super-exponential growth: dh/dt = r * h², so
        Δh ≈ r * h² * Δt.
        """
        dist_to_root_tip = self.get_distance_from_tip()
        self.dev_zone = self.calculate_dev_zone(dist_to_root_tip)

        # Relative growth rate (1/h/µm, VDB Table 1 units)
        rate = self.get_growth_rate()
        if rate == 0.0:
            return 0.0

        # Current cell height in μm
        height = self.get_quad_perimeter().get_height()

        # Biological time for one tick (hours)
        dt_hours = self.get_sim().get_timestep_hours()

        # VDB growth step: Δh = r * h² * Δt
        return rate * height * height * dt_hours

    def calculate_pin_weights(self) -> dict:
        """
        Calculates the pin weights of each membrane of the cell.
        For SIMPLE_INHERITANCE, uses circ_mod's dynamic PIN.
        For IMPOSED, uses the VdB-style imposed PIN pattern and
        converts it to fractions that sum to 1.
        """
        if self.pin_loc_ruleset == PinLocalizationRulesetEnum.SIMPLE_INHERITANCE:
            # circ_mod holds the current PIN levels per membrane
            return self.circ_mod.get_pin_weights()

        elif self.pin_loc_ruleset == PinLocalizationRulesetEnum.IMPOSED:
            # use imposed spatial pattern (VdB) as "absolute PIN"
            pins = self.get_imposed_pin_distribution()  # {"a": ..., "b": ..., "l": ..., "m": ...}
            total = pins["a"] + pins["b"] + pins["l"] + pins["m"]
            if total == 0:
                return {"a": 0.0, "b": 0.0, "l": 0.0, "m": 0.0}
            return {key: val / total for key, val in pins.items()}

        else:
            raise NotImplementedError("Unknown PIN localization ruleset")

    def get_imposed_pin_distribution(self) -> Dict[str, float]:
        """
        Assign PIN weights according to a cell's global location, maintaining the
        PIN distributions established in the initial conditions.

        Returns
        -------
        dict
            The PIN weights for each membrane of the cell.
            Keys are "a", "b", "l", and "m".
            Returns current pin_weights for roottip cells.
        """
        dev_zone = self.get_dev_zone()
        cell_type = self.get_cell_type()

        # Root tip cells: use whatever the ODE module's initial PIN distribution is.
        if dev_zone == "roottip" or cell_type == "roottip":
            return self.circ_mod.get_pin_weights()

        dist_to_root_tip = self.get_distance_from_tip()

        if dev_zone == "meristematic":
            pins = self._pin_meristematic(cell_type, dist_to_root_tip)
        elif dev_zone == "transition":
            pins = self._pin_transition(cell_type, dist_to_root_tip)
        elif dev_zone == "elongation":
            pins = self._pin_elongation(cell_type)
        elif dev_zone == "differentiation":
            pins = self._pin_differentiation(cell_type)
        else:
            raise SyntaxError("Dev zone error cannot get imposed PIN pattern")

        return pins

    def _meristem_row_index(self, dist_to_root_tip: float) -> int:
        """
        Map distance from tip to a discrete 'row' index in the meristematic zone,
        using 5 μm bands centered at MERISTEM_FIRST_ROW_CENTER_Y.
        """
        row = int(round((dist_to_root_tip - MERISTEM_FIRST_ROW_CENTER_Y) / MERISTEM_ROW_STEP))
        if row < 0:
            row = 0
        if row > MERISTEM_MAX_ROW_INDEX:
            row = MERISTEM_MAX_ROW_INDEX
        return row

    def _transition_row_index(self, dist_to_root_tip: float) -> int:
        """
        Map distance from tip to a discrete 'row' index in the transition zone,
        using 5 μm bands centered at TRANSITION_FIRST_ROW_CENTER_Y.
        """
        row = int(round((dist_to_root_tip - TRANSITION_FIRST_ROW_CENTER_Y) / TRANSITION_ROW_STEP))
        if row < 0:
            row = 0
        if row > TRANSITION_MAX_ROW_INDEX:
            row = TRANSITION_MAX_ROW_INDEX
        return row

    def _pin_meristematic(self, cell_type: str, dist_to_root_tip: float) -> Dict[str, float]:
        """
        Meristematic zone PIN patterns, banded along y.
        """
        row = self._meristem_row_index(dist_to_root_tip)

        if cell_type == "vasc":
            if row == 0:
                return {"a": 0.0, "b": 1.0, "l": 0.4, "m": 0.4}
            # rows 1–16: alternate stripes
            if row % 2 == 1:
                return {"a": 0.0, "b": 1.0, "l": 0.0, "m": 0.0}
            else:
                return {"a": 0.0, "b": 1.0, "l": 0.025, "m": 0.025}

        elif cell_type == "peri":
            return {"a": 0.0, "b": 1.0, "l": 0.0, "m": 0.0}

        elif cell_type == "endo":
            if row == 0:
                return {"a": 0.0, "b": 1.0, "l": 0.35, "m": 0.5}
            if row % 2 == 1:
                return {"a": 0.0, "b": 1.0, "l": 0.0, "m": 0.0}
            else:
                return {"a": 0.0, "b": 1.0, "l": 0.1, "m": 0.35}

        elif cell_type == "cortex":
            if row == 0:
                return {"a": 0.0, "b": 1.0, "l": 0.1, "m": 0.1}
            if row % 2 == 1:
                return {"a": 0.0, "b": 1.0, "l": 0.0, "m": 0.0}
            else:
                return {"a": 0.0, "b": 1.0, "l": 0.0, "m": 0.1}

        elif cell_type == "epidermis":
            # row 0: low lateral PIN
            if row == 0:
                return {"a": 1.0, "b": 0.0, "l": 0.1, "m": 0.1}
            # rows 1–9: alternate (high lateral) vs (higher shootward)
            if 1 <= row <= 9:
                if row % 2 == 1:
                    return {"a": 1.0, "b": 0.0, "l": 1.0, "m": 1.0}
                else:
                    return {"a": 1.0, "b": 0.0, "l": 0.3, "m": 0.1}
            # rows 10–16: alternate between low lateral and high lateral
            if row % 2 == 0:
                return {"a": 1.0, "b": 0.0, "l": 0.1, "m": 0.1}
            else:
                return {"a": 1.0, "b": 0.0, "l": 1.0, "m": 1.0}

        # unknown types: raise exception
        raise SyntaxError(
            "Meristematic cell not within meristamatic PIN bands. Check for growth errros."
        )

    def _pin_transition(self, cell_type: str, dist_to_root_tip: float) -> Dict[str, float]:
        """
        Transition zone PIN patterns, banded along y.
        """
        row = self._transition_row_index(dist_to_root_tip)

        if cell_type == "vasc":
            # rows 0–22: alternate weak vs stronger shootward
            if row <= 22:
                if row % 2 == 0:
                    return {"a": 0.0, "b": 1.0, "l": 0.0, "m": 0.0}
                else:
                    return {"a": 0.0, "b": 1.0, "l": 0.025, "m": 0.025}
            # upper transition: match elongation/diff vasc profile
            return {"a": 0.0, "b": 1.0, "l": 0.0525, "m": 0.0525}

        elif cell_type == "peri":
            return {"a": 0.0, "b": 1.0, "l": 0.0, "m": 0.0}

        elif cell_type == "endo":
            # rows 0–14: alternate (0,0) vs (0.1,0.35)
            if row <= 14:
                if row % 2 == 0:
                    return {"a": 0.0, "b": 1.0, "l": 0.0, "m": 0.0}
                else:
                    return {"a": 0.0, "b": 1.0, "l": 0.1, "m": 0.35}
            # rows 15–22: alternate (0,0) vs (0,0.35)
            if row <= 22:
                if row % 2 == 0:
                    return {"a": 0.0, "b": 1.0, "l": 0.0, "m": 0.0}
                else:
                    return {"a": 0.0, "b": 1.0, "l": 0.0, "m": 0.35}
            # upper transition: fixed 0.35 on m
            return {"a": 0.0, "b": 1.0, "l": 0.0, "m": 0.35}

        elif cell_type == "cortex":
            if row <= 22:
                if row % 2 == 0:
                    return {"a": 0.0, "b": 1.0, "l": 0.0, "m": 0.0}
                else:
                    return {"a": 0.0, "b": 1.0, "l": 0.0, "m": 0.1}
            # upper transition cortex matches elongation cortex
            return {"a": 1.0, "b": 0.0, "l": 0.0, "m": 0.1}

        elif cell_type == "epidermis":
            if row <= 22:
                if row % 2 == 0:
                    return {"a": 1.0, "b": 0.0, "l": 1.0, "m": 1.0}
                else:
                    return {"a": 1.0, "b": 0.0, "l": 0.1, "m": 0.1}
            # upper transition epidermis matches elongation epidermis
            return {"a": 1.0, "b": 0.0, "l": 0.0, "m": 0.5}

        # unknown types: raise exception
        raise SyntaxError(
            "Transition cell not within transition PIN bands. Check for growth errros."
        )

    def _pin_elongation(self, cell_type: str) -> Dict[str, float]:
        """
        Elongation zone PIN patterns, constant within each cell type.
        """
        if cell_type == "vasc":
            return {"a": 0.0, "b": 1.0, "l": 0.0525, "m": 0.0525}
        if cell_type == "peri":
            return {"a": 0.0, "b": 1.0, "l": 0.0, "m": 0.0}
        if cell_type == "endo":
            return {"a": 0.0, "b": 1.0, "l": 0.0, "m": 0.35}
        if cell_type == "cortex":
            return {"a": 1.0, "b": 0.0, "l": 0.0, "m": 0.1}
        if cell_type == "epidermis":
            return {"a": 1.0, "b": 0.0, "l": 0.0, "m": 0.5}
        raise SyntaxError("Vascular cell type unrecognized.")

    def _pin_differentiation(self, cell_type: str) -> Dict[str, float]:
        """
        Differentiation zone PIN patterns, constant within each cell type.
        """
        if cell_type == "vasc":
            return {"a": 0.0, "b": 1.0, "l": 0.0525, "m": 0.0525}
        if cell_type == "peri":
            return {"a": 0.0, "b": 1.0, "l": 0.0, "m": 0.0}
        if cell_type == "endo":
            return {"a": 0.0, "b": 1.0, "l": 0.0, "m": 0.35}
        if cell_type == "cortex":
            return {"a": 0.35, "b": 0.0, "l": 0.0, "m": 0.1}
        if cell_type == "epidermis":
            return {"a": 0.35, "b": 0.0, "l": 0.0, "m": 0.1}
        raise SyntaxError("Differentiation cell type unrecognized.")

    def get_pin_weights(self) -> dict:
        """
        Returns the pin weights of each membrane the cell.

        Returns
        -------
        dict
            The pin weights for each membrane of the cell.
            Keys are "a", "b", "l", and "m".
        """
        return self.pin_weights

    def update(self) -> None:
        if self.growing:
            self.grow()

        self.dev_zone = self.calculate_dev_zone(self.get_distance_from_tip())

        rules = self.get_sim().get_pin_loc_rules()

        # Recompute pin_weights every tick so imposed patterns can change with zone / position
        if rules in (
            PinLocalizationRulesetEnum.SIMPLE_INHERITANCE,
            PinLocalizationRulesetEnum.IMPOSED,
        ):
            self.pin_weights = self.calculate_pin_weights()

        self.circ_mod.update()

    def get_neighbor_di_neighbor_shares_two_vs_std(self, neighbor: "Cell") -> str:
        """
        Returns the direction of a neighbor when the neighbor shares two vertices with the cell
        assuming regular geometry.

        Parameters
        ----------
        neighbor : Cell
            The neighbor to find the direction of.

        Returns
        -------
        str
            The direction of the neighbor.
        """
        # standard case, check which vertices neighbor shares with self
        # if neighbor shares top left and bottom left, neighbor is to the left
        if (self.quad_perimeter.get_top_left() in neighbor.get_quad_perimeter().get_vs()) and (
            self.quad_perimeter.get_bottom_left() in neighbor.get_quad_perimeter().get_vs()
        ):
            if (
                self.quad_perimeter.get_left_lateral_or_medial(self.sim.get_root_midpointx())
                == "lateral"
            ):
                neighbor_direction = "l"
            else:
                neighbor_direction = "m"
        # if neighbor shares top right and bottom right, neighbor is to the right
        elif (self.quad_perimeter.get_top_right() in neighbor.get_quad_perimeter().get_vs()) and (
            self.quad_perimeter.get_bottom_right() in neighbor.get_quad_perimeter().get_vs()
        ):
            if (
                self.quad_perimeter.get_right_lateral_or_medial(self.sim.get_root_midpointx())
                == "lateral"
            ):
                neighbor_direction = "l"
            else:
                neighbor_direction = "m"
        elif (self.quad_perimeter.get_top_left() in neighbor.get_quad_perimeter().get_vs()) and (
            self.quad_perimeter.get_top_right() in neighbor.get_quad_perimeter().get_vs()
        ):
            neighbor_direction = "a"
        elif (self.quad_perimeter.get_bottom_left() in neighbor.get_quad_perimeter().get_vs()) and (
            self.quad_perimeter.get_bottom_right() in neighbor.get_quad_perimeter().get_vs()
        ):
            neighbor_direction = "b"
        return neighbor_direction

    def get_neighbor_dir_neighbor_shares_one_v_std(self, neighbor: "Cell") -> str:
        """
        Returns the direction of a neighbor when the neighbor shares one vertex with the cell
        assuming regular geometry.

        Parameters
        ----------
        neighbor : Cell
            The neighbor to find the direction of.

        Returns
        -------
        str
            The direction of the neighbor.
        """
        if (
            self.get_quad_perimeter().get_top_left()
            == neighbor.get_quad_perimeter().get_top_right()
        ):
            if (
                self.get_quad_perimeter().get_left_lateral_or_medial(self.sim.get_root_midpointx())
                == "lateral"
            ):
                neighbor_direction = "l"
            elif (
                self.get_quad_perimeter().get_left_lateral_or_medial(self.sim.get_root_midpointx())
                == "medial"
            ):
                neighbor_direction = "m"

        elif (
            self.get_quad_perimeter().get_top_right()
            == neighbor.get_quad_perimeter().get_top_left()
        ):
            if (
                self.get_quad_perimeter().get_right_lateral_or_medial(self.sim.get_root_midpointx())
                == "lateral"
            ):
                neighbor_direction = "l"
            elif (
                self.get_quad_perimeter().get_right_lateral_or_medial(self.sim.get_root_midpointx())
                == "medial"
            ):
                neighbor_direction = "m"

        elif (
            self.get_quad_perimeter().get_bottom_left()
            == neighbor.get_quad_perimeter().get_bottom_right()
        ):
            if (
                self.get_quad_perimeter().get_left_lateral_or_medial(self.sim.get_root_midpointx())
                == "lateral"
            ):
                neighbor_direction = "l"
            elif (
                self.get_quad_perimeter().get_left_lateral_or_medial(self.sim.get_root_midpointx())
                == "medial"
            ):
                neighbor_direction = "m"

        elif (
            self.get_quad_perimeter().get_bottom_right()
            == neighbor.get_quad_perimeter().get_bottom_left()
        ):
            if (
                self.get_quad_perimeter().get_right_lateral_or_medial(self.sim.get_root_midpointx())
                == "lateral"
            ):
                neighbor_direction = "l"
            elif (
                self.get_quad_perimeter().get_right_lateral_or_medial(self.sim.get_root_midpointx())
                == "medial"
            ):
                neighbor_direction = "m"
        elif (
            self.get_quad_perimeter().get_top_left()
            == neighbor.get_quad_perimeter().get_bottom_left()
        ):
            neighbor_direction = "a"
        elif (
            self.get_quad_perimeter().get_top_right()
            == neighbor.get_quad_perimeter().get_bottom_right()
        ):
            neighbor_direction = "a"
        elif (
            self.get_quad_perimeter().get_bottom_left()
            == neighbor.get_quad_perimeter().get_top_left()
        ):
            neighbor_direction = "b"
        elif (
            self.get_quad_perimeter().get_bottom_right()
            == neighbor.get_quad_perimeter().get_top_right()
        ):
            neighbor_direction = "b"
        return neighbor_direction
