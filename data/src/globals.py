
import os, pygame, random
from data.libs.opensimplex import OpenSimplex

RANDSEED = random.randint(0, 99999999999)
SEED = 881337

gen = OpenSimplex(seed=SEED)
def noise(nx, ny):
    # Rescale from -1.0:+1.0 to 0.0:1.0
    return gen.noise2d(nx, ny) / 2.0 + 0.5

DEBUG = False

#constants representing colours
BLACK = (0,   0,   0  )
BROWN = (153, 76,  0  )
GREEN = (0,   255, 0  )
BLUE  = (0,   0,   255)
WHITE = (255, 255, 255)

#constants representing the different resources
DIRT1   = 101
DIRT2 = 102

GRASS1  = 201
GRASS2  = 202
GRASS3  = 203
GRASS_B = 205
GRASS_BL = 206
GRASS_BR = 207
GRASS_L = 208
GRASS_R = 209
GRASS_T = 210
GRASS_TL = 211
GRASS_TR = 212
GRASS_TRB = 213
GRASS_TLB = 214
GRASS_BRB = 215
GRASS_BLB = 216

DGRASS1  = 301
DGRASS2  = 302
DGRASS3  = 303

WATER1  = 401
WATER2  = 402
WATER3  = 403
WATER4 = 404
WATER_B = 405
WATER_BL = 406
WATER_BR = 407
WATER_L = 408
WATER_R = 409
WATER_T = 410
WATER_TL = 411
WATER_TR = 412
WATER_TRB = 413
WATER_TLB = 414
WATER_BRB = 415
WATER_BLB = 416

STONE1  = 501
STONE2  = 502

SAND1 = 601
SAND2 = 602
SAND3 = 603
SAND4 = 604

TREE1 = 1001
TREE2 = 1002

STONES1 = 1101
STONES2 = 1102
STONES3 = 1103

WALL_STONE1 = 1201
WALL_STONE2 = 1202
WALL_WOOD1 = 1211

WOOD = 2001
STONE = 2002

#useful game dimensions
TILESIZE  = 32
HEIGHT_OFF = TILESIZE
SCREENWIDTH = 1920
SCREENHEIGHT = 1080
MAPWIDTH  = int(SCREENWIDTH / TILESIZE)
MAPHEIGHT = int(SCREENHEIGHT / TILESIZE)
DISPLAYSURF = None
INVFONT = None
CLOCK = None
TPS = 64 #tiles per chunk
MAX_CHUNKS = 4 + int(MAPWIDTH / TPS) * int(MAPHEIGHT / TPS)

FSCREEN = False
CRAFTING_MENU = False

if not os.path.isdir("data/savegames/"): os.makedirs("data/savegames/")
if not os.path.isdir("data/textures/"): os.makedirs("data/textures/")

terrain = pygame.image.load('data/textures/terrain.png')
character = pygame.image.load("data/textures/character.png")

resourceTextures =  {
                    WOOD: pygame.image.load("data/textures/wood_res.png"),
                    STONE: pygame.image.load("data/textures/stone_res.png"),
                    }

textures =  {
            DIRT1: (19*TILESIZE, 5*TILESIZE, TILESIZE, TILESIZE),
            DIRT2: (20*TILESIZE, 5*TILESIZE, TILESIZE, TILESIZE),

            GRASS1: (21*TILESIZE, 5*TILESIZE, TILESIZE, TILESIZE),
            GRASS2: (22*TILESIZE, 5*TILESIZE, TILESIZE, TILESIZE),
            GRASS3: (23*TILESIZE, 5*TILESIZE, TILESIZE, TILESIZE),
            GRASS_B: (33*TILESIZE, 2*TILESIZE, TILESIZE, TILESIZE),
            GRASS_BL: (34*TILESIZE, 2*TILESIZE, TILESIZE, TILESIZE),
            GRASS_BR: (32*TILESIZE, 2*TILESIZE, TILESIZE, TILESIZE),
            GRASS_L: (34*TILESIZE, 3*TILESIZE, TILESIZE, TILESIZE),
            GRASS_R: (32*TILESIZE, 3*TILESIZE, TILESIZE, TILESIZE),
            GRASS_T: (33*TILESIZE, 4*TILESIZE, TILESIZE, TILESIZE),
            GRASS_TL: (34*TILESIZE, 4*TILESIZE, TILESIZE, TILESIZE),
            GRASS_TR: (32*TILESIZE, 4*TILESIZE, TILESIZE, TILESIZE),
            GRASS_TRB: (34*TILESIZE, 0*TILESIZE, TILESIZE, TILESIZE),
            GRASS_TLB: (33*TILESIZE, 0*TILESIZE, TILESIZE, TILESIZE),
            GRASS_BRB: (34*TILESIZE, 1*TILESIZE, TILESIZE, TILESIZE),
            GRASS_BLB: (33*TILESIZE, 1*TILESIZE, TILESIZE, TILESIZE),

            DGRASS1: (21*TILESIZE, 11*TILESIZE, TILESIZE, TILESIZE),
            DGRASS2: (22*TILESIZE, 11*TILESIZE, TILESIZE, TILESIZE),
            DGRASS3: (23*TILESIZE, 11*TILESIZE, TILESIZE, TILESIZE),

            WATER1: (3*TILESIZE, 14*TILESIZE, TILESIZE, TILESIZE),
            WATER2: (5*TILESIZE, 14*TILESIZE, TILESIZE, TILESIZE),
            WATER3: (8*TILESIZE, 14*TILESIZE, TILESIZE, TILESIZE),
            WATER4: (8*TILESIZE, 14*TILESIZE, TILESIZE, TILESIZE),
            WATER_B: (4*TILESIZE, 11*TILESIZE, TILESIZE, TILESIZE),
            WATER_BL: (5*TILESIZE, 11*TILESIZE, TILESIZE, TILESIZE),
            WATER_BR: (3*TILESIZE, 11*TILESIZE, TILESIZE, TILESIZE),
            WATER_L: (5*TILESIZE, 12*TILESIZE, TILESIZE, TILESIZE),
            WATER_R: (3*TILESIZE, 12*TILESIZE, TILESIZE, TILESIZE),
            WATER_T: (4*TILESIZE, 13*TILESIZE, TILESIZE, TILESIZE),
            WATER_TL: (5*TILESIZE, 13*TILESIZE, TILESIZE, TILESIZE),
            WATER_TR: (3*TILESIZE, 13*TILESIZE, TILESIZE, TILESIZE),
            WATER_TRB: (5*TILESIZE, 9*TILESIZE, TILESIZE, TILESIZE),
            WATER_TLB: (4*TILESIZE, 9*TILESIZE, TILESIZE, TILESIZE),
            WATER_BRB: (5*TILESIZE, 10*TILESIZE, TILESIZE, TILESIZE),
            WATER_BLB: (4*TILESIZE, 10*TILESIZE, TILESIZE, TILESIZE),

            STONE1: pygame.image.load('data/textures/stone1.png'),
            STONE2: pygame.image.load('data/textures/stone2.png'),

            SAND1: (4*TILESIZE, 12*TILESIZE, TILESIZE, TILESIZE),
            SAND2: (0*TILESIZE, 14*TILESIZE, TILESIZE, TILESIZE),
            SAND3: (1*TILESIZE, 14*TILESIZE, TILESIZE, TILESIZE),
            SAND4: (2*TILESIZE, 14*TILESIZE, TILESIZE, TILESIZE),
            }

objectTextures =    {
                    TREE1: (26*TILESIZE, 31*TILESIZE, TILESIZE, TILESIZE),
                    TREE2: (27*TILESIZE, 28*TILESIZE, 2*TILESIZE, 6*TILESIZE),

                    STONES1: (26*TILESIZE, 25*TILESIZE, TILESIZE, TILESIZE),
                    STONES2: (27*TILESIZE, 25*TILESIZE, TILESIZE, TILESIZE),
                    STONES3: (28*TILESIZE, 25*TILESIZE, TILESIZE, TILESIZE),

                    WALL_STONE1: pygame.image.load('data/textures/wall_stone1.png'),
                    WALL_STONE2: pygame.image.load('data/textures/wall_stone2.png'),
                    WALL_WOOD1: pygame.image.load('data/textures/wall_wood1.png'),
                    }

G_WATER = [WATER1,WATER2,WATER3,WATER4]
G_WATER_ALL = [WATER1,WATER2,WATER3,WATER4,WATER_B,WATER_BL,WATER_BR,WATER_T,WATER_TL,WATER_TR,WATER_R,WATER_L,
               WATER_TRB,WATER_BRB,WATER_TLB,WATER_BLB]
G_SAND = [SAND1,SAND2,SAND3,SAND4]
G_GRASS = [GRASS1,GRASS2,GRASS3]
G_DGRASS = [DGRASS1,DGRASS2,DGRASS3]

G_STONE = [STONE1,STONE2]

CRAFTABLES = [WALL_STONE1,WALL_WOOD1]

OBJECTS = []
for key in objectTextures:
    OBJECTS.append(key)



resources = [WOOD,STONE]


PLAYER_ORIG = pygame.image.load('data/textures/player.png')
PLAYER = PLAYER_ORIG
SELECTION = pygame.image.load('data/textures/selection.png')
BB_SELECTION = pygame.image.load('data/textures/bottom_bar_selection.png')
TOP_BAR = pygame.image.load('data/textures/top_bar.png')
BOTTOM_BAR = pygame.image.load('data/textures/bottom_bar.png')
UI_FRAME = pygame.image.load('data/textures/ui_frame.png')
UI_FRAME_T = pygame.image.load('data/textures/ui_frame_t.png')
UI_FRAME_B = pygame.image.load('data/textures/ui_frame_b.png')
UI_FRAME_L = pygame.image.load('data/textures/ui_frame_l.png')
UI_FRAME_R = pygame.image.load('data/textures/ui_frame_r.png')
UI_FRAME_TL = pygame.image.load('data/textures/ui_frame_tl.png')
UI_FRAME_TR = pygame.image.load('data/textures/ui_frame_tr.png')
UI_FRAME_BL = pygame.image.load('data/textures/ui_frame_bl.png')
UI_FRAME_BR = pygame.image.load('data/textures/ui_frame_br.png')

toolbar = [ None for i in range(10)]
toolbar_selection = 0
