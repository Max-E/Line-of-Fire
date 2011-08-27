#! /usr/bin/python

import lof_gfx_pygame as gfx
import lof_game as game
import lof_bindings as bindings
import lof_actionparse as parser
import lof_fs as fs

r = gfx.renderer()

instate = game.input_state()
gamestate = {
        "renderer": r,
        "fs":       fs.fs ("lof_data"),
        "defaults": [   "teamname red",
                        "editor false", 
                        "direction up", 
                        "piecetype unit", 
                        "unittype triangle", 
                        "autolayer",
                        "tiletype goal",
                        "pos 0 0"       ],
        "eachframe": [  "drawcursor",
                        "refresh",
                        "clearcursor"   ]
    }
gamestate["fs"].add_resource_type ("scenario", "scenarios", "lof")
for action in gamestate["defaults"]+["filename std", "openmap"]:
    cmd, args = parser.parse_statement(action)
    game.run_cmd (gamestate, cmd, args)

while True:
    r.update_inputstate (instate)
    actions = bindings.game_transform_controls(instate, gamestate)
    
    for action in actions:
        cmd, args = parser.parse_statement (action)
        game.run_cmd (gamestate, cmd, args)
    
    for action in gamestate["eachframe"]:
        cmd, args = parser.parse_statement (action)
        game.run_cmd (gamestate, cmd, args)
    

