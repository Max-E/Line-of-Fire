# This file is what you edit to change your keyboard controls
# Easy: just edit the lists of globals
# Hard: create new types of controls, including sophisticated context-
# sensitive ones

import lof_game as game


# For the map editor
editor_place = ["MOUSE1"]
editor_delete = ["MOUSE2"]
editor_redteam = ["r"]
editor_blueteam = ["b"]
editor_triangle = ["t"]
editor_diamond = ["d"]
editor_goaltile = ["g"]
editor_savemap = ["s"]
editor_openmap = ["o"]
editor_newmap = ["n"]
editor_quit = ["q", "EXIT"]
editor_faceup = ["UPARROW"]
editor_faceleft = ["LEFTARROW"]
editor_facedown = ["DOWNARROW"]
editor_faceright = ["RIGHTARROW"]

def editor_transform_controls (instate, gamestate):
    actions = ["pos "+str(instate.cursor_x)+" "+str(instate.cursor_y)]
    for button in instate.buttons:
        if button in editor_place:
            actions += ["gplace"]
        elif button in editor_delete:
            actions += ["gdelete"]
        elif button in editor_redteam:
            actions += ["teamname red"]
        elif button in editor_blueteam:
            actions += ["teamname blue"]
        elif button in editor_triangle:
            if gamestate["teamname"] == "all":
                actions += ["teamname red"]
            actions += ["piecetype unit", "unittype triangle", "autolayer"]
        elif button in editor_diamond:
            if gamestate["teamname"] == "all":
                actions += ["teamname red"]
            actions += ["piecetype unit", "unittype diamond", "autolayer"]
        elif button in editor_goaltile:
            actions += ["teamname all", "piecetype tile", "tiletype goal", "autolayer"]
        elif button in editor_savemap:
            actions += ["savemap"]
        elif button in editor_openmap:
            actions += ["openmap"]
        elif button in editor_newmap:
            if "filename" in gamestate:
                del gamestate["filename"]
            actions += ["newfield"]
        elif button in editor_quit:
            actions += ["quit"]
        elif button in editor_faceup:
            actions += ["direction up", "autolayer"]
        elif button in editor_faceleft:
            actions += ["direction left", "autolayer"]
        elif button in editor_facedown:
            actions += ["direction down", "autolayer"]
        elif button in editor_faceright:
            actions += ["direction right", "autolayer"]
        else:
            print "unbound button "+button
    instate.buttons = []
    return actions


#For the game
game_select = ["MOUSE1"]
game_deselect = ["ESC"]
game_place = ["MOUSE1"]
game_rotate = ["MOUSE2"]
game_faceup = ["UPARROW"]
game_faceleft = ["LEFTARROW"]
game_facedown = ["DOWNARROW"]
game_faceright = ["RIGHTARROW"]
game_totriangle = ["t"]
game_todiamond = ["d"]
game_cycleunit = ["MOUSE3"]
game_finalizemove = ["ENTER"]
game_saveprogress = ["s"]
game_openprogress = ["o"]
game_newgame = ["n"]
game_quit = ["q", "EXIT"]

def game_transform_controls (instate, gamestate):
    actions = ["pos "+str(instate.cursor_x)+" "+str(instate.cursor_y)]
    for button in instate.buttons:
        if button in game_select:
            cur_cell = game.cell_from_gamestate (gamestate)
            if cur_cell.layers[game.LAYER_UNIT] != None:    
                if "selection" in gamestate:
                    if gamestate["selection"].cur_cell != cur_cell:
                        actions += ["deselect", "select"]
                else:
                    actions += ["select"]
                continue
            
        if button in game_place and "selection" in gamestate:
            actions += ["gplace"]
        elif button in game_finalizemove:
            actions += ["gfinalize"]
        elif button in game_deselect and "selection" in gamestate:
            actions += ["deselect"]
        elif button in game_totriangle and "selection" in gamestate:
            actions += ["gtransform triangle"]
        elif button in game_todiamond and "selection" in gamestate:
            actions += ["gtransform diamond"]
        elif button in game_cycleunit and "selection" in gamestate:
            actions += ["gtransform next"]
        elif button in game_saveprogress:
            actions += ["savemap"]
        elif button in game_openprogress:
            actions += ["openmap"]
        elif button in game_newgame:
            if "filename" in gamestate:
                del gamestate["filename"]
            actions += ["newfield"]
        elif button in game_quit:
            actions += ["quit"]
        elif button in game_faceup:
            actions += ["gdirection up"]
        elif button in game_faceleft:
            actions += ["gdirection left"]
        elif button in game_facedown:
            actions += ["gdirection down"]
        elif button in game_faceright:
            actions += ["gdirection right"]
        elif button in game_rotate:
            actions += ["gdirection auto"]
        else:
            print "unbound button "+button
    instate.buttons = []
    return actions
