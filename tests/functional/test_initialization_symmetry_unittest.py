import unittest
import pyglet
import os
from src.plantem.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Starting Template"


class TestInitializationSymmetry(unittest.TestCase):
    """
    Tests the symmetry of the default simulation initialization.
    """

    @classmethod
    def setUpClass(cls):
        print("Running headless")
        # for mac
        pyglet.options["headless"] = True
        # for PC
        os.environ["ARCADE_HEADLESS"] = "true"

    def test_initial_symmetry(self):
        timestep = 1
        root_midpoint_x = 71
        vis = False
        cell_val_file = "src/plantem/sim/input/default_init_vals.csv"
        v_file = "src/plantem/sim/input/default_vs.csv"
        gparam_series = None
        simulation = GrowingSim(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_TITLE,
            timestep,
            root_midpoint_x,
            vis,
            cell_val_file,
            v_file,
            gparam_series,
            geometry="default",
        )
        keys = [
            0,
            6,
            13,
            22,
            30,
            40,
            55,
            2,
            8,
            12,
            21,
            29,
            39,
            54,
            4,
            10,
            17,
            26,
            28,
            38,
            46,
            53,
            16,
            20,
            34,
            44,
            50,
            36,
            48,
            52,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            76,
            77,
            78,
            79,
            80,
            81,
            82,
            90,
            91,
            92,
            93,
            94,
            95,
            96,
            97,
            106,
            107,
            108,
            109,
            110,
            111,
            112,
            120,
            121,
            122,
            123,
            124,
            125,
            126,
            127,
            136,
            137,
            138,
            139,
            140,
            141,
            142,
            143,
            152,
            153,
            154,
            155,
            156,
            157,
            158,
            166,
            167,
            168,
            169,
            170,
            171,
            172,
            173,
            182,
            183,
            184,
            185,
            186,
            187,
            188,
            196,
            197,
            198,
            199,
            200,
            201,
            202,
            210,
            211,
            212,
            213,
            214,
            215,
            216,
            217,
            226,
            227,
            228,
            229,
            230,
            231,
            232,
            240,
            241,
            242,
            243,
            244,
            245,
            246,
            254,
            255,
            256,
            257,
            258,
            259,
            260,
            268,
            269,
            270,
            271,
            272,
            273,
            274,
            282,
            283,
            284,
            285,
            286,
            287,
            288,
            296,
            297,
            298,
            299,
            300,
            301,
            302,
            303,
            312,
            313,
            314,
            315,
            316,
            317,
            318,
            326,
            327,
            328,
            329,
            330,
            331,
            332,
            340,
            341,
            342,
            343,
            344,
            345,
            346,
            354,
            355,
            356,
            357,
            358,
            359,
            360,
            368,
            369,
            370,
            371,
            372,
            373,
            374,
            382,
            383,
            384,
            385,
            386,
            387,
            388,
            396,
            397,
            398,
            399,
            400,
            401,
            402,
            410,
            411,
            412,
            413,
            414,
            415,
            416,
            424,
            425,
            426,
            427,
            428,
            429,
            430,
            438,
            439,
            440,
            441,
            442,
            443,
            444,
            452,
            453,
            454,
            455,
            456,
            457,
            458,
            466,
            467,
            468,
            469,
            470,
            471,
            472,
            480,
            481,
            482,
            483,
            484,
            485,
            486,
            494,
            495,
            496,
            497,
            498,
            499,
            500,
            508,
            509,
            510,
            511,
            512,
            513,
            514,
            522,
            523,
            524,
            525,
            526,
            527,
            528,
            536,
            537,
            538,
            539,
            540,
            541,
            542,
            550,
            551,
            552,
            553,
            554,
            555,
            556,
            564,
            565,
            566,
            567,
            568,
            569,
            570,
            578,
            579,
            580,
            581,
            582,
            583,
            584,
            592,
            593,
            594,
            595,
            596,
            597,
            598,
            606,
            607,
            608,
            609,
            610,
            611,
            612,
            620,
            621,
            622,
            623,
            624,
            625,
            626,
            634,
            635,
            636,
            637,
            638,
            639,
            640,
            648,
            649,
            650,
            651,
            652,
            653,
            654,
            662,
            663,
            664,
            665,
            666,
            667,
            668,
            676,
            677,
            678,
            679,
            680,
            681,
            682,
            690,
            691,
            692,
            693,
            694,
            695,
            696,
            704,
            705,
            706,
            707,
            708,
            709,
            710,
            718,
            719,
            720,
            721,
            722,
            723,
            724,
            732,
            733,
            734,
            735,
            736,
            737,
            738,
            746,
            747,
            748,
            749,
            750,
            751,
            752,
            760,
            761,
            762,
            763,
            764,
            765,
            766,
            774,
            775,
            776,
            777,
            778,
            779,
            780,
            788,
            789,
            790,
            791,
            792,
            793,
            794,
            802,
            803,
            804,
            805,
            806,
            807,
            808,
            816,
            817,
            818,
            819,
            820,
            821,
            822,
        ]
        value = [
            1,
            7,
            14,
            23,
            31,
            41,
            56,
            3,
            9,
            15,
            24,
            32,
            42,
            57,
            5,
            11,
            18,
            27,
            33,
            43,
            47,
            58,
            19,
            25,
            35,
            45,
            51,
            37,
            49,
            59,
            75,
            74,
            73,
            72,
            71,
            70,
            69,
            68,
            89,
            88,
            87,
            86,
            85,
            84,
            83,
            105,
            104,
            103,
            102,
            101,
            100,
            99,
            98,
            119,
            118,
            117,
            116,
            115,
            114,
            113,
            135,
            134,
            133,
            132,
            131,
            130,
            129,
            128,
            151,
            150,
            149,
            148,
            147,
            146,
            145,
            144,
            165,
            164,
            163,
            162,
            161,
            160,
            159,
            181,
            180,
            179,
            178,
            177,
            176,
            175,
            174,
            195,
            194,
            193,
            192,
            191,
            190,
            189,
            209,
            208,
            207,
            206,
            205,
            204,
            203,
            225,
            224,
            223,
            222,
            221,
            220,
            219,
            218,
            239,
            238,
            237,
            236,
            235,
            234,
            233,
            253,
            252,
            251,
            250,
            249,
            248,
            247,
            267,
            266,
            265,
            264,
            263,
            262,
            261,
            281,
            280,
            279,
            278,
            277,
            276,
            275,
            295,
            294,
            293,
            292,
            291,
            290,
            289,
            311,
            310,
            309,
            308,
            307,
            306,
            305,
            304,
            325,
            324,
            323,
            322,
            321,
            320,
            319,
            339,
            338,
            337,
            336,
            335,
            334,
            333,
            353,
            352,
            351,
            350,
            349,
            348,
            347,
            367,
            366,
            365,
            364,
            363,
            362,
            361,
            381,
            380,
            379,
            378,
            377,
            376,
            375,
            395,
            394,
            393,
            392,
            391,
            390,
            389,
            409,
            408,
            407,
            406,
            405,
            404,
            403,
            423,
            422,
            421,
            420,
            419,
            418,
            417,
            437,
            436,
            435,
            434,
            433,
            432,
            431,
            451,
            450,
            449,
            448,
            447,
            446,
            445,
            465,
            464,
            463,
            462,
            461,
            460,
            459,
            479,
            478,
            477,
            476,
            475,
            474,
            473,
            493,
            492,
            491,
            490,
            489,
            488,
            487,
            507,
            506,
            505,
            504,
            503,
            502,
            501,
            521,
            520,
            519,
            518,
            517,
            516,
            515,
            535,
            534,
            533,
            532,
            531,
            530,
            529,
            549,
            548,
            547,
            546,
            545,
            544,
            543,
            563,
            562,
            561,
            560,
            559,
            558,
            557,
            577,
            576,
            575,
            574,
            573,
            572,
            571,
            591,
            590,
            589,
            588,
            587,
            586,
            585,
            605,
            604,
            603,
            602,
            601,
            600,
            599,
            619,
            618,
            617,
            616,
            615,
            614,
            613,
            633,
            632,
            631,
            630,
            629,
            628,
            627,
            647,
            646,
            645,
            644,
            643,
            642,
            641,
            661,
            660,
            659,
            658,
            657,
            656,
            655,
            675,
            674,
            673,
            672,
            671,
            670,
            669,
            689,
            688,
            687,
            686,
            685,
            684,
            683,
            703,
            702,
            701,
            700,
            699,
            698,
            697,
            717,
            716,
            715,
            714,
            713,
            712,
            711,
            731,
            730,
            729,
            728,
            727,
            726,
            725,
            745,
            744,
            743,
            742,
            741,
            740,
            739,
            759,
            758,
            757,
            756,
            755,
            754,
            753,
            773,
            772,
            771,
            770,
            769,
            768,
            767,
            787,
            786,
            785,
            784,
            783,
            782,
            781,
            801,
            800,
            799,
            798,
            797,
            796,
            795,
            815,
            814,
            813,
            812,
            811,
            810,
            809,
            829,
            828,
            827,
            826,
            825,
            824,
            823,
        ]
        equal_dict = dict(zip(keys, value))
        for id in keys:
            assert (
                simulation.get_cell_by_ID(id).get_circ_mod().get_state()
                == simulation.get_cell_by_ID(equal_dict[id]).get_circ_mod().get_state()
            )

    def test_symmetry_after_updates(self):
        timestep = 1
        root_midpoint_x = 71
        vis = False
        cell_val_file = "src/plantem/sim/input/default_init_vals.csv"
        v_file = "src/plantem/sim/input/default_vs.csv"
        gparam_series = None
        simulation = GrowingSim(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_TITLE,
            timestep,
            root_midpoint_x,
            vis,
            cell_val_file,
            v_file,
            gparam_series,
            geometry="default",
        )
        keys = [
            0,
            6,
            13,
            22,
            30,
            40,
            55,
            2,
            8,
            12,
            21,
            29,
            39,
            54,
            4,
            10,
            17,
            26,
            28,
            38,
            46,
            53,
            16,
            20,
            34,
            44,
            50,
            36,
            48,
            52,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            76,
            77,
            78,
            79,
            80,
            81,
            82,
            90,
            91,
            92,
            93,
            94,
            95,
            96,
            97,
            106,
            107,
            108,
            109,
            110,
            111,
            112,
            120,
            121,
            122,
            123,
            124,
            125,
            126,
            127,
            136,
            137,
            138,
            139,
            140,
            141,
            142,
            143,
            152,
            153,
            154,
            155,
            156,
            157,
            158,
            166,
            167,
            168,
            169,
            170,
            171,
            172,
            173,
            182,
            183,
            184,
            185,
            186,
            187,
            188,
            196,
            197,
            198,
            199,
            200,
            201,
            202,
            210,
            211,
            212,
            213,
            214,
            215,
            216,
            217,
            226,
            227,
            228,
            229,
            230,
            231,
            232,
            240,
            241,
            242,
            243,
            244,
            245,
            246,
            254,
            255,
            256,
            257,
            258,
            259,
            260,
            268,
            269,
            270,
            271,
            272,
            273,
            274,
            282,
            283,
            284,
            285,
            286,
            287,
            288,
            296,
            297,
            298,
            299,
            300,
            301,
            302,
            303,
            312,
            313,
            314,
            315,
            316,
            317,
            318,
            326,
            327,
            328,
            329,
            330,
            331,
            332,
            340,
            341,
            342,
            343,
            344,
            345,
            346,
            354,
            355,
            356,
            357,
            358,
            359,
            360,
            368,
            369,
            370,
            371,
            372,
            373,
            374,
            382,
            383,
            384,
            385,
            386,
            387,
            388,
            396,
            397,
            398,
            399,
            400,
            401,
            402,
            410,
            411,
            412,
            413,
            414,
            415,
            416,
            424,
            425,
            426,
            427,
            428,
            429,
            430,
            438,
            439,
            440,
            441,
            442,
            443,
            444,
            452,
            453,
            454,
            455,
            456,
            457,
            458,
            466,
            467,
            468,
            469,
            470,
            471,
            472,
            480,
            481,
            482,
            483,
            484,
            485,
            486,
            494,
            495,
            496,
            497,
            498,
            499,
            500,
            508,
            509,
            510,
            511,
            512,
            513,
            514,
            522,
            523,
            524,
            525,
            526,
            527,
            528,
            536,
            537,
            538,
            539,
            540,
            541,
            542,
            550,
            551,
            552,
            553,
            554,
            555,
            556,
            564,
            565,
            566,
            567,
            568,
            569,
            570,
            578,
            579,
            580,
            581,
            582,
            583,
            584,
            592,
            593,
            594,
            595,
            596,
            597,
            598,
            606,
            607,
            608,
            609,
            610,
            611,
            612,
            620,
            621,
            622,
            623,
            624,
            625,
            626,
            634,
            635,
            636,
            637,
            638,
            639,
            640,
            648,
            649,
            650,
            651,
            652,
            653,
            654,
            662,
            663,
            664,
            665,
            666,
            667,
            668,
            676,
            677,
            678,
            679,
            680,
            681,
            682,
            690,
            691,
            692,
            693,
            694,
            695,
            696,
            704,
            705,
            706,
            707,
            708,
            709,
            710,
            718,
            719,
            720,
            721,
            722,
            723,
            724,
            732,
            733,
            734,
            735,
            736,
            737,
            738,
            746,
            747,
            748,
            749,
            750,
            751,
            752,
            760,
            761,
            762,
            763,
            764,
            765,
            766,
            774,
            775,
            776,
            777,
            778,
            779,
            780,
            788,
            789,
            790,
            791,
            792,
            793,
            794,
            802,
            803,
            804,
            805,
            806,
            807,
            808,
            816,
            817,
            818,
            819,
            820,
            821,
            822,
        ]
        value = [
            1,
            7,
            14,
            23,
            31,
            41,
            56,
            3,
            9,
            15,
            24,
            32,
            42,
            57,
            5,
            11,
            18,
            27,
            33,
            43,
            47,
            58,
            19,
            25,
            35,
            45,
            51,
            37,
            49,
            59,
            75,
            74,
            73,
            72,
            71,
            70,
            69,
            68,
            89,
            88,
            87,
            86,
            85,
            84,
            83,
            105,
            104,
            103,
            102,
            101,
            100,
            99,
            98,
            119,
            118,
            117,
            116,
            115,
            114,
            113,
            135,
            134,
            133,
            132,
            131,
            130,
            129,
            128,
            151,
            150,
            149,
            148,
            147,
            146,
            145,
            144,
            165,
            164,
            163,
            162,
            161,
            160,
            159,
            181,
            180,
            179,
            178,
            177,
            176,
            175,
            174,
            195,
            194,
            193,
            192,
            191,
            190,
            189,
            209,
            208,
            207,
            206,
            205,
            204,
            203,
            225,
            224,
            223,
            222,
            221,
            220,
            219,
            218,
            239,
            238,
            237,
            236,
            235,
            234,
            233,
            253,
            252,
            251,
            250,
            249,
            248,
            247,
            267,
            266,
            265,
            264,
            263,
            262,
            261,
            281,
            280,
            279,
            278,
            277,
            276,
            275,
            295,
            294,
            293,
            292,
            291,
            290,
            289,
            311,
            310,
            309,
            308,
            307,
            306,
            305,
            304,
            325,
            324,
            323,
            322,
            321,
            320,
            319,
            339,
            338,
            337,
            336,
            335,
            334,
            333,
            353,
            352,
            351,
            350,
            349,
            348,
            347,
            367,
            366,
            365,
            364,
            363,
            362,
            361,
            381,
            380,
            379,
            378,
            377,
            376,
            375,
            395,
            394,
            393,
            392,
            391,
            390,
            389,
            409,
            408,
            407,
            406,
            405,
            404,
            403,
            423,
            422,
            421,
            420,
            419,
            418,
            417,
            437,
            436,
            435,
            434,
            433,
            432,
            431,
            451,
            450,
            449,
            448,
            447,
            446,
            445,
            465,
            464,
            463,
            462,
            461,
            460,
            459,
            479,
            478,
            477,
            476,
            475,
            474,
            473,
            493,
            492,
            491,
            490,
            489,
            488,
            487,
            507,
            506,
            505,
            504,
            503,
            502,
            501,
            521,
            520,
            519,
            518,
            517,
            516,
            515,
            535,
            534,
            533,
            532,
            531,
            530,
            529,
            549,
            548,
            547,
            546,
            545,
            544,
            543,
            563,
            562,
            561,
            560,
            559,
            558,
            557,
            577,
            576,
            575,
            574,
            573,
            572,
            571,
            591,
            590,
            589,
            588,
            587,
            586,
            585,
            605,
            604,
            603,
            602,
            601,
            600,
            599,
            619,
            618,
            617,
            616,
            615,
            614,
            613,
            633,
            632,
            631,
            630,
            629,
            628,
            627,
            647,
            646,
            645,
            644,
            643,
            642,
            641,
            661,
            660,
            659,
            658,
            657,
            656,
            655,
            675,
            674,
            673,
            672,
            671,
            670,
            669,
            689,
            688,
            687,
            686,
            685,
            684,
            683,
            703,
            702,
            701,
            700,
            699,
            698,
            697,
            717,
            716,
            715,
            714,
            713,
            712,
            711,
            731,
            730,
            729,
            728,
            727,
            726,
            725,
            745,
            744,
            743,
            742,
            741,
            740,
            739,
            759,
            758,
            757,
            756,
            755,
            754,
            753,
            773,
            772,
            771,
            770,
            769,
            768,
            767,
            787,
            786,
            785,
            784,
            783,
            782,
            781,
            801,
            800,
            799,
            798,
            797,
            796,
            795,
            815,
            814,
            813,
            812,
            811,
            810,
            809,
            829,
            828,
            827,
            826,
            825,
            824,
            823,
        ]
        equal_dict = dict(zip(keys, value))
        while simulation.get_tick() < 100:
            print(f"tick {simulation.get_tick()}")
            for id in keys:
                try:
                    assert (
                        simulation.get_cell_by_ID(id).get_circ_mod().get_state()
                        == simulation.get_cell_by_ID(equal_dict[id]).get_circ_mod().get_state()
                    )
                except AssertionError:
                    print(f"cell {id} and cell {equal_dict[id]} are not equal")
                    print(
                        f"cell {id} state: {simulation.get_cell_by_ID(id).get_circ_mod().get_state()}"
                    )
                    print(
                        f"cell {equal_dict[id]} state: {simulation.get_cell_by_ID(equal_dict[id]).get_circ_mod().get_state()}"
                    )
                    raise AssertionError
            simulation.cell_list.update()
            simulation.vertex_mover.update()
            simulation.circulator.update()
            simulation.divider.update()
            simulation.root_tip_y = simulation.get_root_tip_y()
            simulation.tick += 1
