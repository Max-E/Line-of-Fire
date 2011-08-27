# This is where the magic happens-- everything that "happens" is an action.
# Every action consists of a command and arguments. Each command must have
# a handler function associated with it, which will use the arguments.


from lof_game_core import *
import lof_utils as util
import lof_actionparse as parser

import sys, copy


# Handlers and formatters for basic variables

def cmd_set_string_var (gamestate, name, args):
    assert len(args) == 1, "Malformed string assignment statement "+repr(name+' '+' '.join(args))
    gamestate[name] = args[0]

def cmd_set_num_var (gamestate, name, args):
    assert len(args) == 1, "Malformed number assignment statement "+repr(name+' '+' '.join(args))
    gamestate[name] = float(args[0])

def cmd_set_bool_var (gamestate, name, args):
    assert len(args) == 1, "Malformed boolean assignment statement "+repr(name+' '+' '.join(args))
    gamestate[name] = util.string_to_bool(args[0])

def cmd_set_stringlist_var (gamestate, name, args):
    gamestate[name] = args

def cmd_set_numlist_var (gamestate, name, args):
    gamestate[name] = [float(arg) for arg in args]

def cmd_set_boollist_var (gamestate, name, args):
    gamestate[name] = [util.string_to_bool(arg) for arg in args]


def cmd_fmt_string_var (gamestate, name):
    return name+' '+gamestate[name]+'\n'

def cmd_fmt_num_var (gamestate, name):
    return name+' '+str(gamestate[name])+'\n'

def cmd_fmt_bool_var (gamestate, name):
    return name+' '+util.bool_to_string(gamestate[name])+'\n'

def cmd_fmt_stringlist_var (gamestate, name):
    return name+' '+' '.join(gamestate[name])+'\n'

def cmd_fmt_numlist_var (gamestate, name):
    return name+' '+' '.join([str(val) for val in gamestate[name]])+'\n'

def cmd_fmt_boollist_var (gamestate, name):
    return name+' '+' '.join(
            [util.bool_to_string(val) 
            for val in gamestate[name]]
        )+'\n'

def cmd_fmt_ignore (gamstate, name):
    return ''


# Handlers for other commands

def cmd_update_layer (gamestate, name, args):
    assert len(args) == 0, "Autolayer does not take arguments!"
    piecetype = gamestate["piecetype"]
    direction = gamestate["direction"]
    if piecetype == "tile":
        piecelayer = LAYER_TILE
    elif piecetype == "unit":
        piecelayer = LAYER_UNIT
    elif piecetype == "cursor":
        piecelayer = LAYER_CURSOR
    elif piecetype == "beam":
        if direction == "up":
            piecelayer = LAYER_VBEAM_UP
        elif direction == "left":
            piecelayer = LAYER_HBEAM_LEFT
        elif direction == "down":
            piecelayer = LAYER_VBEAM_DOWN
        elif direction == "right":
            piecelayer = LAYER_HBEAM_RIGHT
    gamestate["piecelayer"] = piecelayer

def cmd_quit (gamestate, name, args):
    sys.exit (0)

def cmd_place (gamestate, name, args):
    assert len(args) == 0, "Place does not take arguments!"
    cur_cell = cell_from_gamestate (gamestate)
    pieceadd = piece_from_gamestate (gamestate)
    pieceadd_layer = int(gamestate["piecelayer"])
    cur_cell.layers[pieceadd_layer] = pieceadd
    gamestate["renderer"].draw_cell (cur_cell)

def cmd_gameplace (gamestate, name, args):
    assert len(args) == 0, "Gplace does not take arguments!"
    r = gamestate["renderer"]
    if gamestate["editor"]:
        cur_cell = cell_from_gamestate (gamestate)
        pieceadd = piece_from_gamestate (gamestate)
        pieceadd_layer = int(gamestate["piecelayer"])
        cur_cell.layers[pieceadd_layer] = pieceadd
        r.draw_cell (cur_cell)
        for bcell in beam_check (cur_cell, gamestate["field"]):
            for layer in [LAYER_VBEAM_UP, LAYER_VBEAM_DOWN, LAYER_HBEAM_LEFT, LAYER_HBEAM_RIGHT]:
                if bcell.layers[layer] != None and bcell.layers[LAYER_UNIT] != None:
                    bcell.layers[LAYER_UNIT] = None
                    for bcell2 in beam_check (bcell, gamestate["field"]):
                        r.draw_cell (bcell2)
            r.draw_cell (bcell)
    else:
        assert "selection" in gamestate, "Gplace called with nothing selected!"
        cur_selection = gamestate["selection"]
        cur_cell = cell_from_gamestate (gamestate)
        if cur_cell.layers[LAYER_SHADE] == None:
            print "Invalid move!"
            return
        old_cell = cur_selection.cur_cell
        old_cell.layers[LAYER_UNIT_PLACE] = None
        r.draw_cell (old_cell)
        for bcell in beam_check (old_cell, gamestate["field"], True):
            r.draw_cell (bcell)
        cur_selection.cur_cell = cur_cell
        pieceadd = cur_selection.cur_unit
        pieceadd.unittype = cur_selection.original_unit.unittype
        cur_cell.layers[LAYER_UNIT_PLACE] = pieceadd
        r.draw_cell (cur_cell)
        for bcell in beam_check (cur_cell, gamestate["field"], True):
            r.draw_cell (bcell)

def cmd_delete (gamestate, name, args):
    assert len(args) == 0, "Delete does not take arguments!"
    cur_cell = cell_from_gamestate (gamestate)
    layer = int(gamestate["piecelayer"])
    cur_cell.layers[layer] = None
    gamestate["renderer"].draw_cell (cur_cell)

def cmd_gamedelete (gamestate, name, args):
    assert len(args) == 0, "Gdelete does not take arguments!"
    cur_cell = cell_from_gamestate (gamestate)
    layer = int(gamestate["piecelayer"])
    cur_cell.layers[layer] = None
    gamestate["renderer"].draw_cell (cur_cell)
    for bcell in beam_check (cur_cell, gamestate["field"]):
        gamestate["renderer"].draw_cell (bcell)

def cmd_save (gamestate, name, args):
    if len(args) == 1:
        gamestate["filename"] = args[0]
    elif len(args) > 1:
        assert False, "Too many arguments to save!"
    elif "filename" not in gamestate:
        gamestate["filename"] = raw_input ("Please enter a name for the new scenario: ")
    outfile = open (gamestate["fs"].locate_resource("scenario", gamestate["filename"]), "wb")
    for (k, v) in gamestate.items():
        outfile.write (formatters[k](gamestate, k))
    outfile.close()

def cmd_open (gamestate, name, args):
    if len(args) == 1:
        gamestate["filename"] = args[0]
    elif len(args) > 1:
        assert False, "Too many arguments to open!"
    elif "filename" not in gamestate:
        gamestate["filename"] = raw_input ("Please enter a scenario name: ")
    infile = open (gamestate["fs"].locate_resource("scenario", gamestate["filename"]), "rb")
    for action in parser.parse_file (infile):
        run_cmd (gamestate, action[0], action[1])
    for action in gamestate["defaults"]:
        cmd, args = parser.parse_statement (action)
        run_cmd (gamestate, cmd, args)
    if not gamestate["editor"]:
        del gamestate["filename"]

def cmd_newfield (gamestate, name, args):
    assert len(args) == 0, "Newfield does not take arguments!"
    cells = [   [   cell (x, y, [None]*LAYER_COUNT) 
                for x in range (40)
            ] for y in range (25)
        ]
    gamestate["field"] = cells
    for row in cells:
        for cur_cell in row:
            for i in range (1, TRIANGLE_BEAM_LENGTH+1):
                direction_coordinates = {
                        "up": (cur_cell.x, cur_cell.y-i),
                        "left": (cur_cell.x-i, cur_cell.y),
                        "down": (cur_cell.x, cur_cell.y+i),
                        "right": (cur_cell.x+i, cur_cell.y)
                    }
                for cur_direct in ["up", "left", "down", "right"]:
                    (x, y) = direction_coordinates[cur_direct]
                    if x < 0 or y < 0 or y >= len(cells) or x >= len(row):
                        continue
                    cur_cell.beam_reachable[cur_direct] += [cells[y][x]]
            gamestate["renderer"].draw_cell (cur_cell)

def cmd_gamedirection (gamestate, name, args):
    assert len(args) == 1, "Malformed gdirection statement!"
    if "selection" not in gamestate:
        print "No unit selected for rotation!"
        return
    cur_selection = gamestate["selection"]
    selected_cell = cur_selection.cur_cell
    selected_unit = cur_selection.cur_unit
    if args[0] in ["up", "left", "down", "right"]:
        direction = args[0]
    elif args[0] == "auto":
        next_direction = {"up": "left", "left": "down", "down": "right", "right": "up"}
        direction = next_direction[selected_unit.direction]
        cursor_pos = gamestate["pos"]
        cursor_x, cursor_y = int(cursor_pos[0]), int(cursor_pos[1])
        ofs_x, ofs_y = cursor_x - selected_cell.x, cursor_y - selected_cell.y
        if abs(ofs_x) >= abs(ofs_y):
            if ofs_x > 0:
                direction = "right"
            elif ofs_x < 0:
                direction = "left"
        else:
            if ofs_y > 0:
                direction = "down"
            elif ofs_y < 0:
                direction = "up"
    else:
        assert False, "Invalid direction "+str(args[0])
    selected_unit.unittype = cur_selection.original_unit.unittype
    selected_unit.direction = direction
    gamestate["renderer"].draw_cell (selected_cell)
    for bcell in beam_check (selected_cell, gamestate["field"], True):
        gamestate["renderer"].draw_cell (bcell)

def cmd_drawcursor (gamestate, name, args):
    assert len(args) == 0, "Drawcursor does not take arguments!"
    r = gamestate["renderer"]
    cur_cell = cell_from_gamestate (gamestate)
    cur_cell.layers[LAYER_CURSOR] = cursor ("std")
    if gamestate["editor"]:
        if gamestate["piecetype"] == "unit":
            pieceadd_layer = LAYER_UNIT_PLACE
        elif gamestate["piecetype"] == "tile":
            pieceadd_layer = LAYER_TILE_PLACE
        else:
            assert False, "Drawcursor: don't know how to preview "+str(gamestate["piecetype"])
        cur_cell.layers[pieceadd_layer] = piece_from_gamestate (gamestate)
        for bcell in beam_check (cur_cell, gamestate["field"], True):
            r.draw_cell (bcell)
    r.draw_cell (cur_cell)

def cmd_clearcursor (gamestate, name, args):
    assert len(args) == 0, "Clearcursor does not take arguments!"
    r = gamestate["renderer"]
    cur_cell = cell_from_gamestate (gamestate)
    cur_cell.layers[LAYER_CURSOR] = None
    if gamestate["editor"]:
        if gamestate["piecetype"] == "unit":
            pieceadd_layer = LAYER_UNIT_PLACE
        elif gamestate["piecetype"] == "tile":
            pieceadd_layer = LAYER_TILE_PLACE
        else:
            assert False, "Clearcursor: don't know how to clear preview for "+str(gamestate["piecetype"])
        cur_cell.layers[pieceadd_layer] = None
        for bcell in beam_check (cur_cell, gamestate["field"], True):
            r.draw_cell (bcell)
    r.draw_cell (cur_cell)

def cmd_refresh (gamestate, name, args):
    assert len(args) == 0, "Refresh does not take arguments!"
    gamestate["renderer"].refresh()

def cmd_select (gamestate, name, args):
    assert len(args) == 0, "Select does not take arguments!"
    cur_cell = cell_from_gamestate (gamestate)
    cur_selection = selection (cur_cell)
    cur_unit = cur_selection.cur_unit
    if cur_unit.team != gamestate["teamname"]:
        print "Cannot select other team's units!"
        return
    gamestate["selection"] = cur_selection 
    cur_selection.shade_cells += [cur_cell]
    shadeadd = shade (cur_unit.team)
    cur_cell.layers[LAYER_SHADE] = shadeadd
    cur_cell.layers[LAYER_UNIT_PLACE] = cur_unit
    cur_cell.layers[LAYER_UNIT] = None
    gamestate["renderer"].draw_cell (cur_cell)
    directions_enabled = {
            "up": True, "left": True, "down": True, "right": True
        }
    field = gamestate["field"]
    for i in range (1, TRIANGLE_BEAM_LENGTH+1):
        direction_coordinates = {
                "up": (cur_cell.x, cur_cell.y-i),
                "left": (cur_cell.x-i, cur_cell.y),
                "down": (cur_cell.x, cur_cell.y+i),
                "right": (cur_cell.x+i, cur_cell.y)
            }
        for cur_direct in ["up", "left", "down", "right"]:
            (x, y) = direction_coordinates[cur_direct]
            if x < 0 or y < 0 or y >= len(field) or x >= len(field[0]):
                continue
            if directions_enabled[cur_direct]:
                cur_shaded_cell = field[y][x]
                if cur_shaded_cell.layers[LAYER_UNIT] != None:
                    directions_enabled[cur_direct] = False
                    continue
                for j in [LAYER_VBEAM_UP, LAYER_HBEAM_LEFT, LAYER_VBEAM_DOWN, LAYER_HBEAM_RIGHT, LAYER_VBEAM_UP]:
                    existing_beam = cur_shaded_cell.layers[j]
                    if existing_beam != None and existing_beam.team != cur_unit.team:
                        directions_enabled[cur_direct] = False
                        break
                if not directions_enabled[cur_direct]:
                    continue
                cur_tile = cur_shaded_cell.layers[LAYER_TILE]
                if cur_tile != None and cur_tile.tiletype == "goal":
                    directions_enabled[cur_direct] = False
                    if cur_unit.unittype == "diamond":
                        cur_shaded_cell.layers[LAYER_SHADE] = shadeadd
                        gamestate["renderer"].draw_cell (cur_shaded_cell)
                        cur_selection.shade_cells += [cur_shaded_cell]
                    continue
                cur_shaded_cell.layers[LAYER_SHADE] = shadeadd
                gamestate["renderer"].draw_cell (cur_shaded_cell)
                cur_selection.shade_cells += [cur_shaded_cell]

def cmd_deselect (gamestate, name, args):
    assert len(args) == 0, "Deselect does not take arguments!"
    assert "selection" in gamestate, "Deselect called with no selection!"
    r = gamestate["renderer"]
    cur_selection = gamestate["selection"]
    cur_cell = cur_selection.cur_cell
    cur_cell.layers[LAYER_UNIT_PLACE] = None
    for bcell in beam_check (cur_cell, gamestate["field"], True):
        r.draw_cell (bcell)
    r.draw_cell (cur_cell)
    origin_cell = cur_selection.origin_cell
    origin_cell.layers[LAYER_UNIT] = cur_selection.original_unit
    for bcell in beam_check (origin_cell, gamestate["field"]):
        r.draw_cell (bcell)
    for scell in cur_selection.shade_cells:
        scell.layers[LAYER_SHADE] = None
        r.draw_cell (scell)
    del gamestate["selection"]

def cmd_finalizemove (gamestate, name, args):
    assert len(args) == 0, "Deselect does not take arguments!"
    if "selection" not in gamestate:
        if gamestate["teamname"] == "red":
            print "red forfeits"
            gamestate["teamname"] = "blue"
        else:
            print "blue forfeits"
            gamestate["teamname"] = "red"
        return
    r = gamestate["renderer"]
    cur_selection = gamestate["selection"]
    cur_cell = cur_selection.cur_cell
    cur_cell.layers[LAYER_UNIT_PLACE] = None
    for bcell in beam_check (cur_cell, gamestate["field"], True):
        r.draw_cell (bcell)
    cur_cell.layers[LAYER_UNIT] = cur_selection.cur_unit
    for bcell in beam_check (cur_cell, gamestate["field"]):
        for layer in [LAYER_VBEAM_UP, LAYER_VBEAM_DOWN, LAYER_HBEAM_LEFT, LAYER_HBEAM_RIGHT]:
            if bcell.layers[layer] != None and bcell.layers[LAYER_UNIT] != None:
                bcell.layers[LAYER_UNIT] = None
                for bcell2 in beam_check (bcell, gamestate["field"]):
                    r.draw_cell (bcell2)
        r.draw_cell (bcell)
    for scell in cur_selection.shade_cells:
        scell.layers[LAYER_SHADE] = None
        r.draw_cell (scell)
    dest_tile = cur_cell.layers[LAYER_TILE]
    if dest_tile != None and dest_tile.tiletype == "goal":
        assert cur_selection.cur_unit.unittype == "diamond", "Only diamonds can score!"
        gamestate[gamestate["teamname"]+"score"] += 1
        print gamestate["teamname"]+" scores! Total score "+str(gamestate[gamestate["teamname"]+"score"])
        cur_cell.layers[LAYER_UNIT] = None
    r.draw_cell (cur_cell)
    del gamestate["selection"]
    if gamestate["teamname"] == "red":
        gamestate["teamname"] = "blue"
    else:
        gamestate["teamname"] = "red"

def cmd_transformunit (gamestate, name, args):
    assert len(args) == 1, "Transformunit takes exactly one argument!"
    assert "selection" in gamestate, "Transformunit called with nothing selected!"
    if args[0] in ["triangle", "diamond"]:
        new_unittype = args[0]
    elif args[0] == "next":
        if gamestate["selection"].cur_unit.unittype == "triangle":
            new_unittype = "diamond"
        else:
            new_unittype = "triangle"
    else:
        assert False, "Transformunit: unknown unit type "+str(args[0])+"!"
    r = gamestate["renderer"]
    gamestate["unittype"] == new_unittype
    cur_selection = gamestate["selection"]
    cur_selection.cur_unit = copy.deepcopy (cur_selection.original_unit)
    cur_selection.cur_unit.unittype = new_unittype
    cur_selection.cur_cell.layers[LAYER_UNIT_PLACE] = None
    for bcell in beam_check (cur_selection.cur_cell, gamestate["field"], True):
        r.draw_cell (bcell)
    r.draw_cell (cur_selection.cur_cell)
    cur_selection.cur_cell = cur_selection.origin_cell
    cur_selection.cur_cell.layers[LAYER_UNIT_PLACE] = cur_selection.cur_unit
    for bcell in beam_check (cur_selection.cur_cell, gamestate["field"], True):
        r.draw_cell (bcell)
    r.draw_cell (cur_selection.cur_cell)


# Specialized formatters

def cmd_fmt_field (gamestate, name):
    res = 'newfield\n'
    cur_piecetype = None
    cur_teamname = None
    cur_unittype = None
    cur_tiletype = None
    cur_direction = None
    cur_beamtype = None
    cur_beamorg = None
    for layer in range (LAYER_SAVED_COUNT):
        res += 'piecelayer '+str(layer)+'\n'
        for rownum in range(len(gamestate[name])):
            row = gamestate[name][rownum]
            for cellnum in range(len(row)):
                cell = row[cellnum]
                cur_piece = cell.layers[layer]
                if cur_piece != None:
                    res += 'pos '+str(cellnum)+' '+str(rownum)+'\n'
                    if cur_piece.piecetype != cur_piecetype:
                        cur_piecetype = cur_piece.piecetype
                        res += 'piecetype '+cur_piecetype+'\n'
                    if cur_piece.team != cur_teamname:
                        cur_teamname = cur_piece.team
                        res += 'teamname '+cur_teamname+'\n'
                    if cur_piecetype == "tile":
                        if cur_piece.tiletype != cur_tiletype:
                            cur_tiletype = cur_piece.tiletype
                            res += 'tiletype '+cur_tiletype+'\n'
                    else:
                        if cur_piece.direction != cur_direction:
                            cur_direction = cur_piece.direction
                            res += 'direction '+cur_direction+'\n'
                        if cur_piecetype == "unit":
                            if cur_piece.unittype != cur_unittype:
                                cur_unittype = cur_piece.unittype
                                res += 'unittype '+cur_unittype+'\n'
                        elif cur_piecetype == "beam":
                            if cur_piece.beamtype != cur_beamtype:
                                cur_beamtype = cur_piece.beamtype
                                res += 'beamtype '+cur_beamtype+'\n'
                            if cur_piece.origin != cur_beamorg:
                                cur_beamorg = cur_piece.origin
                                res += 'beamorg '
                                res += str(cur_beamorg[0])+' '
                                res += str(cur_beamorg[1])+'\n'
                    res += 'place\n'
    return res


handlers = {
    "pos":              cmd_set_numlist_var,
    "teamname":         cmd_set_string_var,
    "direction":        cmd_set_string_var,
    "piecelayer":       cmd_set_num_var,
    "piecetype":        cmd_set_string_var,
    "unittype":         cmd_set_string_var,
    "tiletype":         cmd_set_string_var,
    "beamtype":         cmd_set_string_var,
    "beamorg":          cmd_set_numlist_var,
    "editor":           cmd_set_bool_var,
    "filename":         cmd_set_string_var,
    "redscore":         cmd_set_num_var,
    "bluescore":        cmd_set_num_var,
    
    "autolayer":        cmd_update_layer,
    "quit":             cmd_quit,
    "place":            cmd_place,
    "gplace":           cmd_gameplace,
    "delete":           cmd_delete,
    "gdelete":          cmd_gamedelete,
    "savemap":          cmd_save,
    "openmap":          cmd_open,
    "newfield":         cmd_newfield,
    "gdirection":       cmd_gamedirection,
    "drawcursor":       cmd_drawcursor,
    "clearcursor":      cmd_clearcursor,
    "refresh":          cmd_refresh,
    "select":           cmd_select,
    "deselect":         cmd_deselect,
    "gfinalize":        cmd_finalizemove,
    "gtransform":       cmd_transformunit
}


formatters = {
    "pos":              cmd_fmt_numlist_var,
    "teamname":         cmd_fmt_string_var,
    "direction":        cmd_fmt_string_var,
    "piecelayer":       cmd_fmt_num_var,
    "piecetype":        cmd_fmt_string_var,
    "unittype":         cmd_fmt_string_var,
    "tiletype":         cmd_fmt_string_var,
    "beamtype":         cmd_fmt_string_var,
    "beamorg":          cmd_fmt_numlist_var,
    "redscore":         cmd_fmt_num_var,
    "bluescore":        cmd_fmt_num_var,
    
    "editor":           cmd_fmt_ignore,
    "renderer":         cmd_fmt_ignore,
    "filename":         cmd_fmt_ignore,
    "defaults":         cmd_fmt_ignore,
    "eachframe":        cmd_fmt_ignore,
    "selection":        cmd_fmt_ignore,
    "fs":               cmd_fmt_ignore,
    
    "field":            cmd_fmt_field
}


def run_cmd (gamestate, cmd, args):
    cmd = cmd.lower()
    assert cmd in handlers, "Invalid variable or command "+str(cmd)
    handlers[cmd](gamestate, cmd, args)

