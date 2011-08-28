# This file is what you edit to change your keyboard controls. You can also
# add new menu items!

import lof_game as game


def add_buttons (gamestate, buttons):
    r = gamestate["renderer"]
    buttonrows = [[]]
    rownum = 0
    startx = 0
    max_x = 640
    for (text, actionlist) in buttons.items():
        resource, width = r.get_button_resource ("  "+text+"  ")
        selected_version, selected_version_width = \
            r.get_button_resource (" ["+text+"] ")
        width = max (width, selected_version_width)
        if startx+width >= max_x:
            rownum += 1
            startx = 0
            buttonrows += [[]]
        cur_button = game.button (
                resource, selected_version, actionlist, startx, width, rownum
            )
        buttonrows[rownum] += [cur_button]
        r.draw_button (cur_button, False)
        startx += width
    gamestate["buttons"] = buttonrows


# For the map editor
editor_menuselect = ["MOUSE1"]
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

editor_buttons = {
#       button text:        actionlist
        "red triangle":     ["teamname red", "piecetype unit", "unittype triangle", "autolayer"],
        "blue triangle":    ["teamname blue", "piecetype unit", "unittype triangle", "autolayer"],
        "red diamond":      ["teamname red", "piecetype unit", "unittype diamond", "autolayer"],
        "blue diamond":     ["teamname blue", "piecetype unit", "unittype diamond", "autolayer"],
        "goal tile":        ["teamname all", "piecetype tile", "tiletype goal", "autolayer"],
        "save":             ["savemap"],
        "open":             ["openmap"],
        "new":              ["clearfilename", "newfield"],
        "quit":             ["quit"]
}

def editor_add_buttons (gamestate):
    add_buttons (gamestate, editor_buttons)

def editor_transform_controls (instate, gamestate):
    actions = [ "pos "+
                str(min(instate.cursor_x, 39))+" "+
                str(min(instate.cursor_y, 24)) ]
    
    if instate.cursor_y > 24:
        x, y = instate.cursor_x*16, min(instate.cursor_y-25, len(gamestate["buttons"])-1)
        buttonrow = gamestate["buttons"][y]
        for button in buttonrow:
            if x < button.startx:
                continue
            gamestate["selected_button"] = button
    elif "selected_button" in gamestate:
        del gamestate["selected_button"]
    
    for button in instate.buttons:
        if button in editor_menuselect and "selected_button" in gamestate:
            actions += gamestate["selected_button"].actionlist
            continue
        
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
game_menuselect = ["MOUSE1"]
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
game_quit = ["q", "EXIT"]

game_buttons = {
#       button text:    actionlist
        "finalize":     ["gfinalize"],
        "save":         ["savemap"],
        "open":         ["openmap"],
        "quit":         ["quit"]
}

def game_add_buttons (gamestate):
    add_buttons (gamestate, game_buttons)

def game_transform_controls (instate, gamestate):
    actions = [ "pos "+
                str(min(instate.cursor_x, 39))+" "+
                str(min(instate.cursor_y, 24)) ]
    
    if instate.cursor_y > 24:
        x, y = instate.cursor_x*16, min(instate.cursor_y-25, len(gamestate["buttons"])-1)
        buttonrow = gamestate["buttons"][y]
        for button in buttonrow:
            if x < button.startx:
                continue
            gamestate["selected_button"] = button
    elif "selected_button" in gamestate:
        del gamestate["selected_button"]
    
    for button in instate.buttons:
        if button in game_menuselect and "selected_button" in gamestate:
            actions += gamestate["selected_button"].actionlist
            continue
        
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
