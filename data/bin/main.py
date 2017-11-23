import json
import sqlite3
import sys
from pygame.locals import *
from data.src.globals import *
from data.src.Player import Player

tilemap = [ [DIRT1 for w in range(MAPWIDTH)] for h in range(MAPHEIGHT) ]
objectmap = [[None for w in range(MAPWIDTH)] for h in range(MAPHEIGHT)]

chunksGround = {}
chunksObjects = {}

global DISPLAYSURF, INVFONT, DEBUG, FSCREEN
global gen, tilemap, toolbar_selection

class Map():
    def __init__(self, x=0, y=0):
        # initial map
        self.update(x, y)

    def worldCoordinatesToChunk(self, x, y):
        if x < 0:
            xChunk = int((x-TPS+1) / TPS)
        else:
            xChunk = int(x / TPS)

        if y < 0:
            yChunk = int((y-TPS+1) / TPS)
        else:
            yChunk = int(y / TPS)

        return xChunk, yChunk

    def generateChunk(self, x, y):
        id = str(x)+","+str(y)
        App.c.execute('''SELECT id FROM map WHERE id=?''', (id,))

        if App.c.fetchone() == None:

            ground = [[DIRT1 for w in range(TPS)] for h in range(TPS)]
            objects = [ [None for w in range(TPS)] for h in range(TPS) ]
            for row in range(0,TPS):
                for column in range(0,TPS):

                    kx = (x*(TPS) + column) / MAPWIDTH# - 0.5
                    ky = (y*(TPS) + row) / MAPHEIGHT# - 0.5

                    e = self.noiseParameter(kx, ky)

                    tile = self.biome(e)

                    ground[row][column] = tile

                    if  tile not in G_WATER_ALL and \
                        tile not in [STONE1,STONE2] and \
                        tile not in G_SAND:
                            if tile in G_GRASS and random.randint(0,60) == 0:
                                objects[row][column] = TREE1+random.randint(0,1)
                            if tile in G_DGRASS and random.randint(0, 1) == 0:
                                objects[row][column] = TREE1 + random.randint(0, 1)
                            if tile in G_GRASS and random.randint(0, 30) == 0:
                                objects[row][column] = STONES1 + random.randint(0, 2)

                    elif tile in G_SAND and random.randint(0,50) == 0:
                        objects[row][column] = STONES1+random.randint(0,2)
                    else:
                        objects[row][column] = None

                    tr = self.biome(self.noiseParameter((x * (TPS) + column + 1) / MAPWIDTH, (y * (TPS) + row - 1) / MAPHEIGHT))
                    r = self.biome(self.noiseParameter((x * (TPS) + column + 1) / MAPWIDTH, (y * (TPS) + row) / MAPHEIGHT))
                    br = self.biome(self.noiseParameter((x * (TPS) + column + 1) / MAPWIDTH, (y * (TPS) + row + 1) / MAPHEIGHT))
                    tl = self.biome(self.noiseParameter((x * (TPS) + column - 1) / MAPWIDTH, (y * (TPS) + row - 1) / MAPHEIGHT))
                    l = self.biome(self.noiseParameter((x * (TPS) + column - 1) / MAPWIDTH, (y * (TPS) + row) / MAPHEIGHT))
                    bl = self.biome(self.noiseParameter((x * (TPS) + column - 1) / MAPWIDTH, (y * (TPS) + row + 1) / MAPHEIGHT))
                    t = self.biome(self.noiseParameter((x * (TPS) + column) / MAPWIDTH, (y * (TPS) + row - 1) / MAPHEIGHT))
                    b = self.biome(self.noiseParameter((x * (TPS) + column) / MAPWIDTH, (y * (TPS) + row + 1) / MAPHEIGHT))

                    if tile in G_WATER:
                        if      r in G_SAND and tl in G_WATER and l in G_WATER and \
                                bl in G_WATER and t in G_WATER and b in G_WATER:
                                    ground[row][column] = WATER_R
                        elif    tr in G_SAND and r in G_WATER and br in G_WATER and tl in G_WATER and \
                                l in G_WATER and bl in G_WATER and t in G_WATER and b in G_WATER:
                                    ground[row][column] = WATER_TR
                        elif    tr in G_SAND and r in G_SAND and l in G_WATER and \
                                bl in G_WATER and t in G_SAND and b in G_WATER:
                                    ground[row][column] = WATER_TRB
                        elif    r in G_SAND and br in G_SAND and tl in G_WATER and \
                                l in G_WATER and t in G_WATER and  b in G_SAND:
                                    ground[row][column] = WATER_BRB
                        elif    tr in G_WATER and r in G_WATER and br in G_WATER and \
                                l in G_SAND and t in G_WATER and b in G_WATER:
                                    ground[row][column] = WATER_L
                        elif    tr in G_WATER and r in G_WATER and br in G_WATER and tl in G_WATER and \
                                l in G_WATER and bl in G_SAND and t in G_WATER and b in G_WATER:
                                    ground[row][column] = WATER_BL
                        elif    tr in G_WATER and r in G_WATER and br in G_WATER and tl in G_SAND and \
                                l in G_WATER and bl in G_WATER and t in G_WATER and b in G_WATER:
                                    ground[row][column] = WATER_TL
                        elif    r in G_WATER and br in G_WATER and tl in G_SAND and \
                                l in G_SAND and t in G_SAND and b in G_WATER:
                                    ground[row][column] = WATER_TLB
                        elif    tr in G_WATER and r in G_WATER and l in G_SAND and \
                                bl in G_SAND and t in G_WATER and b in G_SAND:
                                    ground[row][column] = WATER_BLB
                        elif    tr in G_WATER and r in G_WATER and tl in G_WATER and \
                                l in G_WATER and t in G_WATER and b in G_SAND:
                                    ground[row][column] = WATER_B
                        elif    r in G_WATER and br in G_WATER and l in G_WATER and \
                                bl in G_WATER and t in G_SAND and b in G_WATER:
                                    ground[row][column] = WATER_T
                        elif    tr in G_WATER and br in G_SAND and tl in G_WATER and \
                                l in G_WATER and bl in G_WATER and t in G_WATER:
                                    ground[row][column] = WATER_BR
                    elif tile in G_SAND:
                        if      r in G_GRASS and tl in G_SAND and l in G_SAND and \
                                bl in G_SAND and t in G_SAND and b in G_SAND:
                                    ground[row][column] = GRASS_R
                        elif    tr in G_GRASS and r in G_SAND and br in G_SAND and tl in G_SAND and \
                                l in G_SAND and bl in G_SAND and t in G_SAND and b in G_SAND:
                                    ground[row][column] = GRASS_TR
                        elif    tr in G_GRASS and r in G_GRASS and l in G_SAND and \
                                bl in G_SAND and t in G_GRASS and b in G_SAND:
                                    ground[row][column] = GRASS_TRB
                        elif    r in G_GRASS and br in G_GRASS and tl in G_SAND and \
                                l in G_SAND and t in G_SAND and  b in G_GRASS:
                                    ground[row][column] = GRASS_BRB
                        elif    tr in G_SAND and r in G_SAND and br in G_SAND and \
                                l in G_GRASS and t in G_SAND and b in G_SAND:
                                    ground[row][column] = GRASS_L
                        elif    tr in G_SAND and r in G_SAND and br in G_SAND and tl in G_SAND and \
                                l in G_SAND and bl in G_GRASS and t in G_SAND and b in G_SAND:
                                    ground[row][column] = GRASS_BL
                        elif    tr in G_SAND and r in G_SAND and br in G_SAND and tl in G_GRASS and \
                                l in G_SAND and bl in G_SAND and t in G_SAND and b in G_SAND:
                                    ground[row][column] = GRASS_TL
                        elif    r in G_SAND and br in G_SAND and tl in G_GRASS and \
                                l in G_GRASS and t in G_GRASS and b in G_SAND:
                                    ground[row][column] = GRASS_TLB
                        elif    tr in G_SAND and r in G_SAND and l in G_GRASS and \
                                bl in G_GRASS and t in G_SAND and b in G_GRASS:
                                    ground[row][column] = GRASS_BLB
                        elif    tr in G_SAND and r in G_SAND and tl in G_SAND and \
                                l in G_SAND and t in G_SAND and b in G_GRASS:
                                    ground[row][column] = GRASS_B
                        elif    r in G_SAND and br in G_SAND and l in G_SAND and \
                                bl in G_SAND and t in G_GRASS and b in G_SAND:
                                    ground[row][column] = GRASS_T
                        elif    tr in G_SAND and br in G_GRASS and tl in G_SAND and \
                                l in G_SAND and bl in G_SAND and t in G_SAND:
                                    ground[row][column] = GRASS_BR


            App.c.execute('''INSERT INTO map(id, x, y, ground, objects) VALUES(?,?,?,?,?)''', (str(x)+","+str(y), x, y, json.dumps(ground), json.dumps(objects)))
            App.conn.commit()

            return ground, objects

    def loadChunk(self, x, y):
        id = str(x) + "," + str(y)
        App.c.execute('''SELECT id FROM map WHERE id=?''', (id,))
        res = App.c.fetchone()

        if res != None:

            App.c.execute('''SELECT ground FROM map WHERE id=?''', (id,))
            ground = json.loads(App.c.fetchone()[0])

            App.c.execute('''SELECT objects FROM map WHERE id=?''', (id,))
            objects = json.loads(App.c.fetchone()[0])

        else:

            ground, objects = self.generateChunk(x, y)

        chunksGround.update({str(x)+","+str(y): ground})
        chunksObjects.update({str(x)+","+str(y): objects})


        return ground, objects

    def unloadChunk(self, x, y):
        chunksGround.pop(str(x)+","+str(y), None)
        chunksObjects.pop(str(x)+","+str(y), None)

    def update(self, xPos, yPos):
        neededChunks = []

        xPos -= int(MAPWIDTH / 2)
        yPos -= int(MAPHEIGHT / 2)

        if DEBUG == True:
            INVFONT = pygame.font.Font('data/Font.ttf', 8)

        for row in range(MAPHEIGHT):
            for column in range(MAPWIDTH):
                cx, cy = self.worldCoordinatesToChunk(xPos + column, yPos + row)
                neededChunks.append(str(cx)+","+str(cy))
                if chunksGround.get(str(cx)+","+str(cy)) != None and chunksObjects.get(str(cx)+","+str(cy)) != None:
                    ground = chunksGround.get(str(cx)+","+str(cy))
                    objects = chunksObjects.get(str(cx)+","+str(cy))
                else:
                    ground, objects = self.loadChunk(cx, cy)

                chunkX = (xPos+column) % TPS
                chunkY = (yPos+row) % TPS

                tile = ground[chunkY][chunkX]
                object = objects[chunkY][chunkX]

                tilemap[row][column] = tile
                objectmap[row][column] = object

                DISPLAYSURF.blit(textures[tile], (column * TILESIZE, row * TILESIZE))
                if object != None:
                    DISPLAYSURF.blit(objectTextures[object], (column * TILESIZE, row * TILESIZE))

                if DEBUG == True:
                    textObj = INVFONT.render(str(xPos+column)+","+str(yPos+row), True, WHITE, BLACK)
                    DISPLAYSURF.blit(textObj, (column * TILESIZE, row * TILESIZE))

                    textObj = INVFONT.render(str(chunkX) + "," + str(chunkY), True, BLACK, WHITE)
                    DISPLAYSURF.blit(textObj, (column * TILESIZE, row * TILESIZE+10))

                    textObj = INVFONT.render(str(cx) + "," + str(cy), True, BLACK, GREEN)
                    DISPLAYSURF.blit(textObj, (column * TILESIZE, row * TILESIZE + 20))



    def biome(self, e):
        if e < 0.5: return WATER1+random.randint(0,3)
        if e < 0.58: return SAND1+random.randint(0,3)
        if e < 0.7: return GRASS1+random.randint(0,2)
        return DGRASS1+random.randint(0,2)

    def noiseParameter(self, kx, ky):
        # elevation
        e = 0.8 * noise(0.5 * kx, 0.5 * ky) \
            + 0.2 * noise(2 * kx, 2 * ky) #\
            #+ 0.1 * noise(2 * kx, 2 * ky)

        return e

class App():

    global toolbar_selection

    def __init__(self):

        # set up the display
        pygame.init()
        modes = pygame.display.list_modes(16)
        DISPLAYSURF = pygame.display.set_mode((MAPWIDTH * TILESIZE, MAPHEIGHT * TILESIZE))
        # add a font for our inventory
        INVFONT = pygame.font.Font('data/Font.ttf', 13)
        INVFONT.set_bold(True)
        CLOCK = pygame.time.Clock()

        if not os.path.isfile("data/savegames/"+str(SEED)+'.db'):
            if not os.path.isdir("data/savegames/"): os.makedirs("/savegames/")
            App.conn = sqlite3.connect("data/savegames/"+str(SEED)+'.db')
            App.c = self.conn.cursor()
            App.c.execute('''CREATE TABLE map (id string, x int, y int, ground blob, objects blob, PRIMARY KEY (id))''')
            App.c.execute('''CREATE TABLE player (id int, lastX int, lastY int, inventory blob, PRIMARY KEY (id))''')

            self.map = Map()
            self.player = Player(PLAYER)
            App.c.execute('''INSERT INTO player(id, lastX, lastY, inventory) VALUES(?,?,?,?)''',
                          (0, 0, 0, json.dumps(self.player.inventory.items)))
            App.conn.commit()

        else:
            App.conn  = sqlite3.connect("data/savegames/"+str(SEED)+'.db')
            App.c = self.conn.cursor()
            App.c.execute('''SELECT lastX, lastY, inventory FROM player WHERE id=0''')
            res = App.c.fetchall()
            x = res[0][0]
            y = res[0][1]
            inventory = json.loads(res[0][2])

            self.map = Map(x, y)
            self.player = Player(PLAYER, 0, x, y)


        toolbar[0] = WALL_WOOD1
        toolbar[1] = WALL_STONE1
        self.loop()

    def save(self):
        for key in chunksGround:
            ground = chunksGround.get(key)
            objects = chunksObjects.get(key)
            App.c.execute('''UPDATE map SET ground=?, objects=? WHERE id=?''',(json.dumps(ground), json.dumps(objects), key))
            App.c.execute('''UPDATE player SET lastX=?, lastY=?, inventory=? WHERE id=0''', (self.player.xPos, self.player.yPos, json.dumps(self.player.inventory.items)))
            App.conn.commit()

    def OnEvent(self, event):
        # if the user wants to quit
        if event.type == QUIT:
            # and the game and close the window
            self.save()
            pygame.quit()
            sys.exit()

        # if a key is pressed
        elif event.type == KEYDOWN:
            self.OnKeydownEvent(event.key)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4: toolbar_selection = (toolbar_selection - 1) % 10
            if event.button == 5: toolbar_selection = (toolbar_selection + 1) % 10

            if event.button == 1:
                x, y = self.player.getCurrentSelection()
                playerX = int(MAPWIDTH / 2)
                playerY = int(MAPHEIGHT / 2)
                offX = x - playerX
                offY = y - playerY
                currentRes = objectmap[y][x]
                cX, cY = self.map.worldCoordinatesToChunk(self.player.xPos + offX, self.player.yPos + offY)
                relX = (self.player.xPos + offX) % TPS
                relY = (self.player.yPos + offY) % TPS
                if currentRes in [TREE1, TREE2]:
                    self.player.inventory.add(WOOD, 1)
                elif currentRes in [STONES1,STONES2,STONES3]:
                    self.player.inventory.add(STONE, 1)
                objects = chunksObjects.get(str(cX) + "," + str(cY))
                objects[relY][relX] = None
                chunksObjects.update({str(cX) + "," + str(cY): objects})
            elif event.button == 3:
                x, y = self.player.getCurrentSelection()
                playerX = int(MAPWIDTH / 2)
                playerY = int(MAPHEIGHT / 2)
                offX = x - playerX
                offY = y - playerY
                cT = tilemap[y][x]
                currentObj = objectmap[y][x]
                cX, cY = self.map.worldCoordinatesToChunk(self.player.xPos + offX, self.player.yPos + offY)
                relX = (self.player.xPos + offX) % TPS
                relY = (self.player.yPos + offY) % TPS
                item = toolbar[toolbar_selection]
                res = None
                if item in [WALL_STONE1,WALL_STONE2]: res = STONE
                if item in [WALL_WOOD1]: res = WOOD
                if currentObj not in OBJECTS and \
                    currentObj not in [STONES1,STONES2,STONES3] and \
                                cT not in [WATER1, WATER2, WATER3] and \
                                cT not in [STONE1, STONE2] and \
                                self.player.inventory.get(res) > 0:
                    # player now has 1 more of this resource
                    self.player.inventory.add(res, -1)
                    objects = chunksObjects.get(str(cX) + "," + str(cY))
                    objects[relY][relX] = item
                    chunksObjects.update({str(cX) + "," + str(cY): objects})

    def OnKeysPressed(self, keys):

        # diagonal
        if (keys[K_w] and keys[K_d]) \
             and tilemap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2) + 1] not in G_WATER_ALL \
             and objectmap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2) + 1] not in OBJECTS:
            self.player.move(+1, -1)

        elif (keys[K_w] and keys[K_a]) \
             and tilemap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2) - 1] not in G_WATER_ALL \
             and objectmap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2) - 1] not in OBJECTS:
            self.player.move(-1, -1)

        elif (keys[K_s] and keys[K_d]) \
             and tilemap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2) + 1] not in G_WATER_ALL \
             and objectmap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2) + 1] not in OBJECTS:
            self.player.move(+1, +1)
        elif (keys[K_s] and keys[K_a]) \
             and tilemap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2) - 1] not in G_WATER_ALL \
             and objectmap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2) - 1] not in OBJECTS:
            self.player.move(-1, +1)

        elif (keys[K_d]) \
                and tilemap[int(MAPHEIGHT / 2)][int(MAPWIDTH / 2) + 1] not in G_WATER_ALL \
                and objectmap[int(MAPHEIGHT / 2)][int(MAPWIDTH / 2) + 1] not in OBJECTS:
            self.player.move(+1, 0)
        elif (keys[K_a]) \
                and tilemap[int(MAPHEIGHT / 2)][int(MAPWIDTH / 2) - 1] not in G_WATER_ALL \
                and objectmap[int(MAPHEIGHT / 2)][int(MAPWIDTH / 2) - 1] not in OBJECTS:
            self.player.move(-1, 0)
        elif (keys[K_w]) \
                and tilemap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2)] not in G_WATER_ALL \
                and objectmap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2)] not in OBJECTS:
            self.player.move(0, -1)
        elif (keys[K_s]) \
                and tilemap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2)] not in G_WATER_ALL \
                and objectmap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2)] not in OBJECTS:
            self.player.move(0, +1)



    def OnKeydownEvent(self, key):
        if key == K_ESCAPE:
            self.save()
            pygame.quit()
            sys.exit()

        elif key == K_e:
            CRAFTING_MENU = not CRAFTING_MENU

        elif key == K_F11:
            FSCREEN = not FSCREEN
            if FSCREEN:
                DISPLAYSURF = pygame.display.set_mode((MAPWIDTH * TILESIZE, MAPHEIGHT * TILESIZE), FULLSCREEN)
            else:
                DISPLAYSURF = pygame.display.set_mode((MAPWIDTH * TILESIZE, MAPHEIGHT * TILESIZE))

        elif key == K_F12:
            DEBUG = not DEBUG

    def OnMouseMovement(self, x, y):
        angle = self.player.rotateTo(x, y)
        self.player.selectNearestTile(x, y)

    def drawBars(self):
        for i in range(MAPWIDTH):
            DISPLAYSURF.blit(TOP_BAR, (i*TILESIZE, 0))

        offset = int((SCREENWIDTH - 10*BOTTOM_BAR.get_width()) / 2)
        for j in range(0, 10):
            DISPLAYSURF.blit(BOTTOM_BAR, (offset + j*BOTTOM_BAR.get_width(), SCREENHEIGHT - BOTTOM_BAR.get_width()))
            if toolbar_selection == j:
                DISPLAYSURF.blit(BB_SELECTION, (offset + j*BOTTOM_BAR.get_width(), SCREENHEIGHT - BOTTOM_BAR.get_width()))

    def drawCraftingMenu(self):
        DISPLAYSURF.blit(UI_FRAME_TR, ((MAPWIDTH - 11) * TILESIZE, 6 * TILESIZE))
        DISPLAYSURF.blit(UI_FRAME_TL, (11 * TILESIZE, 6 * TILESIZE))
        DISPLAYSURF.blit(UI_FRAME_BR, ((MAPWIDTH - 11) * TILESIZE, 20 * TILESIZE))
        DISPLAYSURF.blit(UI_FRAME_BL, (11 * TILESIZE, 20 * TILESIZE))

        for i in range(12, (MAPWIDTH - 11)):
            DISPLAYSURF.blit(UI_FRAME_T, (i * TILESIZE, 6 * TILESIZE))
            DISPLAYSURF.blit(UI_FRAME_B, (i * TILESIZE, 20 * TILESIZE))
        for i in range(7,20):
            DISPLAYSURF.blit(UI_FRAME_R, ((MAPWIDTH - 11) * TILESIZE, i * TILESIZE))
            DISPLAYSURF.blit(UI_FRAME_L, (11 * TILESIZE, i * TILESIZE))

        k = 0
        for i in range(7,20):
            for j in range(12, (MAPWIDTH - 11)):
                DISPLAYSURF.blit(UI_FRAME, (j * TILESIZE, i * TILESIZE))
                if k < len(CRAFTABLES):
                    DISPLAYSURF.blit(objectTextures[CRAFTABLES[k]], (j * TILESIZE, i * TILESIZE))
                    k+=1

    def loop(self):
        chunkX, chunkY = self.map.worldCoordinatesToChunk(self.player.xPos, self.player.yPos)
        self.map.loadChunk(chunkX, chunkY)

        while True:
            DISPLAYSURF.fill(BLACK)
            for event in pygame.event.get():
                self.OnEvent(event)

            self.OnKeysPressed(pygame.key.get_pressed())


            self.map.update(self.player.xPos, self.player.yPos)
            self.player.update()
            self.drawBars()
            self.player.inventory.update()

            x, y = pygame.mouse.get_pos()
            self.OnMouseMovement(x, y)

            if CRAFTING_MENU: self.drawCraftingMenu()

            # update the display
            pygame.display.update()
            CLOCK.tick(60)

if __name__ == '__main__':
    app = App()
