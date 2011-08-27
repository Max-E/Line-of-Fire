from lof_gfx import renderer as base_renderer
from lof_fs import fs
import lof_game as game

import os
import pygame
from pygame.locals import *

TILE_WIDTH = 16
TILE_HEIGHT = TILE_WIDTH


rotation = {"up": 0, "left": 90, "down": 180, "right": 270}

keys = {
	pygame.K_a: "a",
	pygame.K_b: "b",
	pygame.K_c: "c",
	pygame.K_d: "d",
	pygame.K_e: "e",
	pygame.K_f: "f",
	pygame.K_g: "g",
	pygame.K_h: "h",
	pygame.K_i: "i",
	pygame.K_j: "j",
	pygame.K_k: "k",
	pygame.K_l: "l",
	pygame.K_m: "m",
	pygame.K_n: "n",
	pygame.K_o: "o",
	pygame.K_p: "p",
	pygame.K_q: "q",
	pygame.K_r: "r",
	pygame.K_s: "s",
	pygame.K_t: "t",
	pygame.K_u: "u",
	pygame.K_v: "v",
	pygame.K_w: "w",
	pygame.K_x: "x",
	pygame.K_y: "y",
	pygame.K_z: "z",
	pygame.K_UP: "UPARROW",
	pygame.K_LEFT: "LEFTARROW",
	pygame.K_DOWN: "DOWNARROW",
	pygame.K_RIGHT: "RIGHTARROW",
	pygame.K_ESCAPE: "ESC",
	pygame.K_RETURN: "ENTER"
}


class renderer (base_renderer):

    def _init_dpy (self):
        self.dpy = pygame.display.set_mode((640, 480))
    
    def _init_res (self):
        self.sprites = {"tiles": {}, 
                        "units": {"red": {}, "blue": {}}, 
                        "beams": {"red": {}, "blue": {}}, 
                        "cursors": {},
                        "shades": {}
                        }
        self.fs.add_resource_type ("sprite", "sprites", "png")
        for tilename in ["blank", "goal"]:
            resfile = self.fs.locate_resource ("sprite", tilename+"_tile")
            self.sprites["tiles"][tilename] = self.load_sprite (resfile)
        for unitname in ["triangle", "diamond"]: 
            for teamname in ["red", "blue"]:
                resname = teamname + "_" + unitname
                resfile = self.fs.locate_resource ("sprite", resname)
                ressurf = self.load_sprite (resfile)
                self.sprites["units"][teamname][unitname] = ressurf
        for beamname in ["beam", "beam_end"]: 
            for teamname in ["red", "blue"]:
                resname = teamname + "_" + beamname
                resfile = self.fs.locate_resource ("sprite", resname)
                ressurf = self.load_sprite (resfile)
                self.sprites["beams"][teamname][beamname] = ressurf
        for cursorname in ["selected", "target", "std"]:
            resfile = self.fs.locate_resource ("sprite", cursorname+"_cursor")
            self.sprites["cursors"][cursorname] = self.load_sprite (resfile)
        for shadename in ["red", "blue"]:
            resfile = self.fs.locate_resource ("sprite", shadename+"_shaded")
            self.sprites["shades"][shadename] = self.load_sprite (resfile)
    
    def load_sprite (self, filename):
        res = pygame.image.load (filename).convert_alpha()
        assert res.get_width() == TILE_WIDTH, \
                filename+" is the wrong width!"
        assert res.get_height() == TILE_HEIGHT, \
                filename+" is the wrong height!"
        return res
    
    def get_resource (self, piece):
        try:
            if piece.piecetype == "tile":
                assert  piece.tiletype in self.sprites["tiles"], \
                        "No such tile type "+piece.tiletype
                return self.sprites["tiles"][piece.tiletype]
            elif piece.piecetype == "shade":
                assert  piece.team in self.sprites["shades"], \
                        "No such team "+piece.team
                return self.sprites["shades"][piece.team]
            elif piece.piecetype == "cursor":
                assert  piece.cursortype in self.sprites["cursors"], \
                        "No such cursor "+piece.cursortype
                return self.sprites["cursors"][piece.cursortype]
            elif piece.piecetype == "unit":
                assert  piece.team in self.sprites["units"], \
                        "No such team "+piece.team
                unittypes = self.sprites["units"][piece.team]
                assert  piece.unittype in unittypes, \
                        "No such unit type "+piece.unittype
                assert  piece.direction in rotation, \
                        "No such direction "+piece.direction
                if piece.unittype == "diamond":
                    return unittypes[piece.unittype] #diamonds aren't rotated
                return pygame.transform.rotate (unittypes[piece.unittype], 
                                                rotation[piece.direction])
            elif piece.piecetype == "beam":
                assert  piece.team in self.sprites["beams"], \
                        "No such team "+piece.team
                beamtypes = self.sprites["beams"][piece.team]
                assert  piece.beamtype in beamtypes, \
                        "No such beam type "+piece.beamtype
                assert  piece.direction in rotation, \
                        "No such direction "+piece.direction
                return pygame.transform.rotate (beamtypes[piece.beamtype], 
                                                rotation[piece.direction])
            else:
                assert False, "No such piece type "+piece.piecetype
        except:
            print "Malformed piece object!"
            raise
    
    def refresh (self):
        pygame.display.update()
    
    def draw_cell (self, cell):
        pos = (cell.x*TILE_WIDTH, cell.y*TILE_HEIGHT)
        if cell.layers[game.LAYER_TILE] == None:
            self.dpy.blit (self.get_resource (game.tile ("blank")), pos)
        for piece in cell.layers:
            if piece != None:
                spr = self.get_resource (piece)
                self.dpy.blit (spr, pos)

    def update_inputstate (self, input_state):
        for event in pygame.event.get():
            evtype = event.type
            if evtype == pygame.MOUSEMOTION:
                (mouse_x, mouse_y) = pygame.mouse.get_pos()
                input_state.cursor_x = min(mouse_x/TILE_WIDTH, 39)
                input_state.cursor_y = min(mouse_y/TILE_HEIGHT, 24)
            elif evtype == pygame.KEYUP:
                if event.key in keys:
                    input_state.buttons = [keys[event.key]] + input_state.buttons
                else:
                    print "Unknown key type", event.key
            elif evtype == pygame.MOUSEBUTTONUP:
                if event.button == 1: #left click
                    input_state.buttons = ["MOUSE1"] + input_state.buttons
                elif event.button == 2: #middle click
                    input_state.buttons = ["MOUSE3"] + input_state.buttons
                elif event.button == 3: #right click
                    input_state.buttons = ["MOUSE2"] + input_state.buttons
    
