import copy


# A tile can either be a blank tile or a goal tile. Later, team-specific goal
# tiles and obstacle tiles might be introduced as well.
LAYER_TILE = 0
LAYER_TILE_PLACE = 1
# Shading is used to show the reachable area for the currently selected piece.
LAYER_SHADE = 2
# Units are the game pieces.
LAYER_UNIT = 3
# Markers show which unit is selected, and which units are targeted for
# destruction should the current planned move be finalized.
LAYER_MARKER = 4
# Multiple beams may cross the same tile. For both beam orientations
# (left/right and up/down,) there can be up to three beam sources: one from
# either direction from placed units, and a third "preview" beam from the unit
# which is currently being moved.
LAYER_VBEAM_DOWN = 5
LAYER_VBEAM_UP = 6
LAYER_VBEAM_PLACE = 7
LAYER_HBEAM_RIGHT = 8
LAYER_HBEAM_LEFT = 9
LAYER_HBEAM_PLACE = 10
# Total number of layers that get saved in maps or sent via network
LAYER_SAVED_COUNT = 11
# Preview for the unit being placed
LAYER_UNIT_PLACE = 11
# The cursor follows the mouse around and may be used to select, move, and aim
# units.
LAYER_CURSOR = 12
# Total number of layers.
LAYER_COUNT = 13


TRIANGLE_BEAM_LENGTH = 6


class piece:

    pass

class unit (piece):
    
    def __init__ (self, team, unittype):
        assert type(team) == str, "team must be a string!"
        assert type(unittype) == str, "unittype must be a string!"
        self.piecetype = "unit"
        self.team = team
        self.unittype = unittype
        self.direction = "up"


class beam (piece):
    
    def __init__ (self, team, beamtype, direction, origin):
        assert type(team) == str, "team must be a string!"
        assert type(beamtype) == str, "beamtype must be a string!"
        self.piecetype = "beam"
        self.team = team
        self.beamtype = beamtype
        self.direction = direction
        self.origin = origin


class tile (piece):
    
    def __init__ (self, tiletype):
        assert type(tiletype) == str, "tiletype must be a string!"
        self.piecetype = "tile"
        self.team = "all"
        self.tiletype = tiletype


class cursor (piece):
    
    def __init__ (self, cursortype):
        assert type(cursortype) == str, "cursortype must be a string!"
        self.piecetype = "cursor"
        self.cursortype = cursortype


class shade (piece):
    
    def __init__ (self, team):
        assert type(team) == str, "team must be a string!"
        self.piecetype = "shade"
        self.team = team


class cell:
    
    def __init__ (self, x, y, layers):
        self.x = x
        self.y = y
        self.layers = layers
        self.beam_reachable = {"up": [], "left": [], "down": [], "right": []}


class input_state:

    def __init__ (self):
        self.cursor_x = 0
        self.cursor_y = 0
        self.buttons = []


class selection:

    def __init__ (self, cur_cell):
        cur_unit = cur_cell.layers[LAYER_UNIT]
        assert cur_unit != None, \
                "Invalid selection at "+ \
                str(cur_cell.x)+","+str(cur_cell.y)+ \
                ": has no unit!"
        self.shade_cells = []
        self.original_unit = copy.deepcopy (cur_unit)
        self.cur_cell = cur_cell
        self.cur_unit = cur_unit
        self.origin_cell = cur_cell


currently_checking = {}

def beam_check (checked_cell, field, preview = False):
    global currently_checking
    if checked_cell in currently_checking:
        return []
    currently_checking[checked_cell] = True
    cells_to_refresh = []
    directions_enabled = {
            "up": False, "left": False, "down": False, "right": False
        }
    direction_layers = {
            "up": LAYER_VBEAM_UP, "left": LAYER_HBEAM_LEFT,
            "down": LAYER_VBEAM_DOWN, "right": LAYER_HBEAM_RIGHT
        }
    alt_direction_layers = {
            "up": LAYER_VBEAM_PLACE, "left": LAYER_HBEAM_PLACE,
            "down": LAYER_VBEAM_PLACE, "right": LAYER_HBEAM_PLACE
        }
    checked_unit = checked_cell.layers[LAYER_UNIT]
    if checked_unit == None:
        checked_unit = checked_cell.layers[LAYER_UNIT_PLACE]
    if preview:
        direction_layers, alt_direction_layers = \
                alt_direction_layers, direction_layers
    
    if checked_unit != None and checked_unit.unittype != "triangle":
        checked_unit = None
    if checked_unit != None:
        assert  checked_unit.direction in directions_enabled, \
                "No such direction "+repr(checked_unit.direction)
        directions_enabled[checked_unit.direction] = True
    for layer in [LAYER_VBEAM_UP, LAYER_VBEAM_DOWN, LAYER_HBEAM_LEFT, LAYER_HBEAM_RIGHT]:
        if checked_cell.layers[layer] != None:
            (x, y) = checked_cell.layers[layer].origin
            cells_to_refresh += beam_check (field[y][x], field)
            checked_cell.layers[layer] = None
    last_beam = {
            "up": None, "left": None, "down": None, "right": None
        }
    for cur_direct in ["up", "left", "down", "right"]:
        cur_reachable = checked_cell.beam_reachable[cur_direct]
        if directions_enabled[cur_direct] == True:
            for cur_cell in cur_reachable:
                cells_to_refresh += [cur_cell]
                cur_unit = cur_cell.layers[LAYER_UNIT]
                if cur_unit == None:
                    cur_unit = cur_cell.layers[LAYER_UNIT_PLACE]
                if cur_unit != None:
                    if cur_unit.team == checked_unit.team:
                        break
                cur_cell.layers[direction_layers[cur_direct]] = \
                last_beam[cur_direct] = \
                        beam (  checked_unit.team, "beam", cur_direct, 
                                (checked_cell.x, checked_cell.y))
        else:
            for cur_cell in cur_reachable:
                cells_to_refresh += [cur_cell]
                if cur_cell.layers[LAYER_UNIT] != None:
                    cells_to_refresh += beam_check (cur_cell, field)
                    break
                if cur_cell.layers [LAYER_UNIT_PLACE] != None:
                    cells_to_refresh += beam_check (cur_cell, field, True)
                    break
                existing_beam = cur_cell.layers[direction_layers[cur_direct]]
                alt_existing_beam = cur_cell.layers[alt_direction_layers[cur_direct]]
                if existing_beam == None and alt_existing_beam == None: 
                    continue
                assert alt_existing_beam != existing_beam, "Preview and placed on same cell!"
                cur_cell.layers[direction_layers[cur_direct]] = None
                cur_cell.layers[alt_direction_layers[cur_direct]] = None
                if alt_existing_beam != None:
                    (x, y) = alt_existing_beam.origin
                else:
                    (x, y) = existing_beam.origin
                cells_to_refresh += beam_check (field[y][x], field)
    for (k, v) in last_beam.items():
        if v != None:
            v.beamtype = "beam_end"
    del currently_checking[checked_cell]
    return cells_to_refresh


def piece_from_gamestate (gamestate):
    piecetype = gamestate["piecetype"]
    if piecetype == "unit":
        newpiece = unit (gamestate["teamname"], gamestate["unittype"])
        newpiece.direction = gamestate["direction"]
        return newpiece
    elif piecetype == "tile":
        return tile (gamestate["tiletype"])
    elif piecetype == "beam":
        beamorg = gamestate["beamorg"]
        beamorg = (int(beamorg[0]), int(beamorg[1]))
        return beam (
                gamestate["teamname"], gamestate["beamtype"], 
                gamestate["direction"], beamorg
            )


def cell_from_gamestate (gamestate):
    pos = gamestate["pos"]
    x, y = int(pos[0]), int(pos[1])
    return gamestate["field"][y][x]
