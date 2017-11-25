import json
import sqlite3
import sys
import random
import pygame
import os
from pygame.locals import *
import data.src.globals as glob
from data.src.Player import Player

tilemap = [ [glob.DIRT1 for w in range(glob.MAPWIDTH)] for h in range(glob.MAPHEIGHT) ]
objectmap = [[None for w in range(glob.MAPWIDTH)] for h in range(glob.MAPHEIGHT)]

chunksGround = {}
chunksObjects = {}

class Map():
    def __init__(self, x=0, y=0):
        # initial map
        self.update(x, y)

    def worldCoordinatesToChunk(self, x, y):
        if x < 0:
            xChunk = int((x-glob.TPS+1) / glob.TPS)
        else:
            xChunk = int(x / glob.TPS)

        if y < 0:
            yChunk = int((y-glob.TPS+1) / glob.TPS)
        else:
            yChunk = int(y / glob.TPS)

        return xChunk, yChunk

    def generateChunk(self, x, y):
        id = str(x)+","+str(y)
        App.c.execute('''SELECT id FROM map WHERE id=?''', (id,))

        if App.c.fetchone() == None:

            ground = [[glob.DIRT1 for w in range(glob.TPS)] for h in range(glob.TPS)]
            objects = [ [None for w in range(glob.TPS)] for h in range(glob.TPS) ]
            for row in range(0,glob.TPS):
                for column in range(0,glob.TPS):

                    kx = (x*(glob.TPS) + column) / glob.MAPWIDTH# - 0.5
                    ky = (y*(glob.TPS) + row) / glob.MAPHEIGHT# - 0.5

                    e = self.noiseParameter(kx, ky)

                    tile = self.biome(e)

                    ground[row][column] = tile

                    if  tile not in glob.G_WATER_ALL and \
                        tile not in glob.G_STONE and \
                        tile not in glob.G_SAND:
                            if tile in glob.G_GRASS and random.randint(0,60) == 0:
                                objects[row][column] = glob.TREE1+random.randint(0,1)
                            if tile in glob.G_DGRASS and random.randint(0, 1) == 0:
                                objects[row][column] = glob.TREE1 + random.randint(0, 1)
                            if tile in glob.G_GRASS and random.randint(0, 30) == 0:
                                objects[row][column] = glob.STONES1 + random.randint(0, 2)

                    elif tile in glob.G_SAND and random.randint(0,50) == 0:
                        objects[row][column] = glob.STONES1+random.randint(0,2)
                    else:
                        objects[row][column] = None

                    tr = self.biome(self.noiseParameter((x * (glob.TPS) + column + 1) / glob.MAPWIDTH, (y * (glob.TPS) + row - 1) / glob.MAPHEIGHT))
                    r = self.biome(self.noiseParameter((x * (glob.TPS) + column + 1) / glob.MAPWIDTH, (y * (glob.TPS) + row) / glob.MAPHEIGHT))
                    br = self.biome(self.noiseParameter((x * (glob.TPS) + column + 1) / glob.MAPWIDTH, (y * (glob.TPS) + row + 1) / glob.MAPHEIGHT))
                    tl = self.biome(self.noiseParameter((x * (glob.TPS) + column - 1) / glob.MAPWIDTH, (y * (glob.TPS) + row - 1) / glob.MAPHEIGHT))
                    l = self.biome(self.noiseParameter((x * (glob.TPS) + column - 1) / glob.MAPWIDTH, (y * (glob.TPS) + row) / glob.MAPHEIGHT))
                    bl = self.biome(self.noiseParameter((x * (glob.TPS) + column - 1) / glob.MAPWIDTH, (y * (glob.TPS) + row + 1) / glob.MAPHEIGHT))
                    t = self.biome(self.noiseParameter((x * (glob.TPS) + column) / glob.MAPWIDTH, (y * (glob.TPS) + row - 1) / glob.MAPHEIGHT))
                    b = self.biome(self.noiseParameter((x * (glob.TPS) + column) / glob.MAPWIDTH, (y * (glob.TPS) + row + 1) / glob.MAPHEIGHT))

                    if tile in glob.G_WATER:
                        if      r in glob.G_SAND and tl in glob.G_WATER and l in glob.G_WATER and \
                                bl in glob.G_WATER and t in glob.G_WATER and b in glob.G_WATER:
                                    ground[row][column] = glob.WATER_R
                        elif    tr in glob.G_SAND and r in glob.G_WATER and br in glob.G_WATER and tl in glob.G_WATER and \
                                l in glob.G_WATER and bl in glob.G_WATER and t in glob.G_WATER and b in glob.G_WATER:
                                    ground[row][column] = glob.WATER_TR
                        elif    tr in glob.G_SAND and r in glob.G_SAND and l in glob.G_WATER and \
                                bl in glob.G_WATER and t in glob.G_SAND and b in glob.G_WATER:
                                    ground[row][column] = glob.WATER_TRB
                        elif    r in glob.G_SAND and br in glob.G_SAND and tl in glob.G_WATER and \
                                l in glob.G_WATER and t in glob.G_WATER and  b in glob.G_SAND:
                                    ground[row][column] = glob.WATER_BRB
                        elif    tr in glob.G_WATER and r in glob.G_WATER and br in glob.G_WATER and \
                                l in glob.G_SAND and t in glob.G_WATER and b in glob.G_WATER:
                                    ground[row][column] = glob.WATER_L
                        elif    tr in glob.G_WATER and r in glob.G_WATER and br in glob.G_WATER and tl in glob.G_WATER and \
                                l in glob.G_WATER and bl in glob.G_SAND and t in glob.G_WATER and b in glob.G_WATER:
                                    ground[row][column] = glob.WATER_BL
                        elif    tr in glob.G_WATER and r in glob.G_WATER and br in glob.G_WATER and tl in glob.G_SAND and \
                                l in glob.G_WATER and bl in glob.G_WATER and t in glob.G_WATER and b in glob.G_WATER:
                                    ground[row][column] = glob.WATER_TL
                        elif    r in glob.G_WATER and br in glob.G_WATER and tl in glob.G_SAND and \
                                l in glob.G_SAND and t in glob.G_SAND and b in glob.G_WATER:
                                    ground[row][column] = glob.WATER_TLB
                        elif    tr in glob.G_WATER and r in glob.G_WATER and l in glob.G_SAND and \
                                bl in glob.G_SAND and t in glob.G_WATER and b in glob.G_SAND:
                                    ground[row][column] = glob.WATER_BLB
                        elif    tr in glob.G_WATER and r in glob.G_WATER and tl in glob.G_WATER and \
                                l in glob.G_WATER and t in glob.G_WATER and b in glob.G_SAND:
                                    ground[row][column] = glob.WATER_B
                        elif    r in glob.G_WATER and br in glob.G_WATER and l in glob.G_WATER and \
                                bl in glob.G_WATER and t in glob.G_SAND and b in glob.G_WATER:
                                    ground[row][column] = glob.WATER_T
                        elif    tr in glob.G_WATER and br in glob.G_SAND and tl in glob.G_WATER and \
                                l in glob.G_WATER and bl in glob.G_WATER and t in glob.G_WATER:
                                    ground[row][column] = glob.WATER_BR
                    elif tile in glob.G_SAND:
                        if      r in  glob.G_GRASS and tl in glob.G_SAND and l in glob.G_SAND and \
                                bl in glob.G_SAND and t in glob.G_SAND and b in glob.G_SAND:
                                    ground[row][column] = glob.GRASS_R
                        elif    tr in  glob.G_GRASS and r in glob.G_SAND and br in glob.G_SAND and tl in glob.G_SAND and \
                                l in glob.G_SAND and bl in glob.G_SAND and t in glob.G_SAND and b in glob.G_SAND:
                                    ground[row][column] = glob.GRASS_TR
                        elif    tr in  glob.G_GRASS and r in  glob.G_GRASS and l in glob.G_SAND and \
                                bl in glob.G_SAND and t in  glob.G_GRASS and b in glob.G_SAND:
                                    ground[row][column] = glob.GRASS_TRB
                        elif    r in  glob.G_GRASS and br in  glob.G_GRASS and tl in glob.G_SAND and \
                                l in glob.G_SAND and t in glob.G_SAND and  b in  glob.G_GRASS:
                                    ground[row][column] = glob.GRASS_BRB
                        elif    tr in glob.G_SAND and r in glob.G_SAND and br in glob.G_SAND and \
                                l in  glob.G_GRASS and t in glob.G_SAND and b in glob.G_SAND:
                                    ground[row][column] = glob.GRASS_L
                        elif    tr in glob.G_SAND and r in glob.G_SAND and br in glob.G_SAND and tl in glob.G_SAND and \
                                l in glob.G_SAND and bl in  glob.G_GRASS and t in glob.G_SAND and b in glob.G_SAND:
                                    ground[row][column] = glob.GRASS_BL
                        elif    tr in glob.G_SAND and r in glob.G_SAND and br in glob.G_SAND and tl in  glob.G_GRASS and \
                                l in glob.G_SAND and bl in glob.G_SAND and t in glob.G_SAND and b in glob.G_SAND:
                                    ground[row][column] = glob.GRASS_TL
                        elif    r in glob.G_SAND and br in glob.G_SAND and tl in  glob.G_GRASS and \
                                l in  glob.G_GRASS and t in  glob.G_GRASS and b in glob.G_SAND:
                                    ground[row][column] = glob.GRASS_TLB
                        elif    tr in glob.G_SAND and r in glob.G_SAND and l in  glob.G_GRASS and \
                                bl in  glob.G_GRASS and t in glob.G_SAND and b in  glob.G_GRASS:
                                    ground[row][column] = glob.GRASS_BLB
                        elif    tr in glob.G_SAND and r in glob.G_SAND and tl in glob.G_SAND and \
                                l in glob.G_SAND and t in glob.G_SAND and b in  glob.G_GRASS:
                                    ground[row][column] = glob.GRASS_B
                        elif    r in glob.G_SAND and br in glob.G_SAND and l in glob.G_SAND and \
                                bl in glob.G_SAND and t in  glob.G_GRASS and b in glob.G_SAND:
                                    ground[row][column] = glob.GRASS_T
                        elif    tr in glob.G_SAND and br in  glob.G_GRASS and tl in glob.G_SAND and \
                                l in glob.G_SAND and bl in glob.G_SAND and t in glob.G_SAND:
                                    ground[row][column] = glob.GRASS_BR


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

        xPos -= int(glob.MAPWIDTH / 2)
        yPos -= int(glob.MAPHEIGHT / 2)

        if glob.DEBUG == True:
            glob.INVFONT = pygame.font.Font('data/Font.ttf', 8)

        for row in range(glob.MAPHEIGHT):
            for column in range(glob.MAPWIDTH):
                cx, cy = self.worldCoordinatesToChunk(xPos + column, yPos + row)
                neededChunks.append(str(cx)+","+str(cy))
                if chunksGround.get(str(cx)+","+str(cy)) != None and chunksObjects.get(str(cx)+","+str(cy)) != None:
                    ground = chunksGround.get(str(cx)+","+str(cy))
                    objects = chunksObjects.get(str(cx)+","+str(cy))
                else:
                    ground, objects = self.loadChunk(cx, cy)

                chunkX = (xPos+column) % glob.TPS
                chunkY = (yPos+row) % glob.TPS

                tile = ground[chunkY][chunkX]
                object = objects[chunkY][chunkX]

                tilemap[row][column] = tile
                objectmap[row][column] = object

                glob.DISPLAYSURF.blit(glob.terrain, (column * glob.TILESIZE, row * glob.TILESIZE), glob.textures[tile])
                if object != None:
                    if object == glob.TREE1 or object == glob.TREE2:
                        glob.DISPLAYSURF.blit(glob.terrain, (column * glob.TILESIZE - glob.TILESIZE/2, row * glob.TILESIZE - 4*glob.TILESIZE),glob.objectTextures[object])
                    else:
                        glob.DISPLAYSURF.blit(glob.terrain, (column * glob.TILESIZE, row * glob.TILESIZE), glob.objectTextures[object])

                if glob.DEBUG == True:
                    textObj = glob.INVFONT.render(str(xPos+column)+","+str(yPos+row), True, glob.WHITE, glob.BLACK)
                    glob.DISPLAYSURF.blit(textObj, (column * glob.TILESIZE, row * glob.TILESIZE))

                    textObj = glob.INVFONT.render(str(chunkX) + "," + str(chunkY), True, glob.BLACK, glob.WHITE)
                    glob.DISPLAYSURF.blit(textObj, (column * glob.TILESIZE, row * glob.TILESIZE+10))

                    textObj = glob.INVFONT.render(str(cx) + "," + str(cy), True, glob.BLACK, glob.GREEN)
                    glob.DISPLAYSURF.blit(textObj, (column * glob.TILESIZE, row * glob.TILESIZE + 20))



    def biome(self, e):
        if e < 0.5: return glob.WATER1+random.randint(0,3)
        if e < 0.58: return glob.SAND1+random.randint(0,3)
        if e < 0.7: return glob.GRASS1+random.randint(0,2)
        return glob.DGRASS1+random.randint(0,2)

    def noiseParameter(self, kx, ky):
        # elevation
        e = 0.8 * glob.noise(0.5 * kx, 0.5 * ky) \
            + 0.2 * glob.noise(2 * kx, 2 * ky) #\
            #+ 0.1 * noise(2 * kx, 2 * ky)

        return e

class App():

    global toolbar_selection

    def __init__(self):

        # set up the display
        pygame.init()
        glob.modes = pygame.display.list_modes(16)
        glob.DISPLAYSURF = pygame.display.set_mode((glob.MAPWIDTH * glob.TILESIZE, glob.MAPHEIGHT * glob.TILESIZE))
        # add a font for our inventory
        glob.INVFONT = pygame.font.Font('data/Font.ttf', 13)
        glob.INVFONT.set_bold(True)
        glob.CLOCK = pygame.time.Clock()

        if not os.path.isfile("data/savegames/"+str(glob.SEED)+'.db'):
            if not os.path.isdir("data/savegames/"): os.makedirs("/savegames/")
            App.conn = sqlite3.connect("data/savegames/"+str(glob.SEED)+'.db')
            App.c = self.conn.cursor()
            App.c.execute('''CREATE TABLE map (id string, x int, y int, ground blob, objects blob, PRIMARY KEY (id))''')
            App.c.execute('''CREATE TABLE player (id int, lastX int, lastY int, inventory blob, PRIMARY KEY (id))''')

            self.map = Map()
            self.player = Player(glob.PLAYER)
            App.c.execute('''INSERT INTO player(id, lastX, lastY, inventory) VALUES(?,?,?,?)''',
                          (0, 0, 0, json.dumps(self.player.inventory.items)))
            App.conn.commit()

        else:
            App.conn  = sqlite3.connect("data/savegames/"+str(glob.SEED)+'.db')
            App.c = self.conn.cursor()
            App.c.execute('''SELECT lastX, lastY, inventory FROM player WHERE id=0''')
            res = App.c.fetchall()
            x = res[0][0]
            y = res[0][1]
            inventory = json.loads(res[0][2])

            self.map = Map(x, y)
            self.player = Player(glob.PLAYER, 0, x, y, inventory)

        glob.toolbar[0] = glob.WALL_WOOD1
        glob.toolbar[1] = glob.WALL_STONE1
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
            if event.button == 4: glob.toolbar_selection = (glob.toolbar_selection - 1) % 10
            if event.button == 5: glob.toolbar_selection = (glob.toolbar_selection + 1) % 10

            if event.button == 1:
                x, y = self.player.getCurrentSelection()
                playerX = int(glob.MAPWIDTH / 2)
                playerY = int(glob.MAPHEIGHT / 2)
                offX = x - playerX
                offY = y - playerY
                currentRes = objectmap[y][x]
                cX, cY = self.map.worldCoordinatesToChunk(self.player.xPos + offX, self.player.yPos + offY)
                relX = (self.player.xPos + offX) % glob.TPS
                relY = (self.player.yPos + offY) % glob.TPS
                if currentRes in [glob.TREE1, glob.TREE2]:
                    self.player.inventory.add(glob.WOOD, 1)
                elif currentRes in [glob.STONES1,glob.STONES2,glob.STONES3]:
                    self.player.inventory.add(glob.STONE, 1)
                objects = chunksObjects.get(str(cX) + "," + str(cY))
                objects[relY][relX] = None
                chunksObjects.update({str(cX) + "," + str(cY): objects})
            elif event.button == 3:
                x, y = self.player.getCurrentSelection()
                playerX = int(glob.MAPWIDTH / 2)
                playerY = int(glob.MAPHEIGHT / 2)
                offX = x - playerX
                offY = y - playerY
                cT = tilemap[y][x]
                currentObj = objectmap[y][x]
                cX, cY = self.map.worldCoordinatesToChunk(self.player.xPos + offX, self.player.yPos + offY)
                relX = (self.player.xPos + offX) % glob.TPS
                relY = (self.player.yPos + offY) % glob.TPS
                item = glob.toolbar[glob.toolbar_selection]
                res = None
                if item in [glob.WALL_STONE1,glob.WALL_STONE2]: res = glob.STONE
                if item in [glob.WALL_WOOD1]: res = glob.WOOD
                if currentObj not in glob.OBJECTS and \
                    currentObj not in [glob.STONES1,glob.STONES2,glob.STONES3] and \
                                cT not in [glob.WATER1, glob.WATER2, glob.WATER3] and \
                                cT not in [glob.STONE1, glob.STONE2] and \
                                self.player.inventory.get(res) > 0:
                    # player now has 1 more of this resource
                    self.player.inventory.add(res, -1)
                    objects = chunksObjects.get(str(cX) + "," + str(cY))
                    objects[relY][relX] = item
                    chunksObjects.update({str(cX) + "," + str(cY): objects})

    def OnKeysPressed(self, keys):

        # diagonal
        if (keys[K_w] and keys[K_d]) \
             and tilemap[int(glob.MAPHEIGHT / 2) - 1][int(glob.MAPWIDTH / 2) + 1] not in glob.G_WATER_ALL \
             and objectmap[int(glob.MAPHEIGHT / 2) - 1][int(glob.MAPWIDTH / 2) + 1] not in glob.OBJECTS:
            self.player.move(+1, -1)

        elif (keys[K_w] and keys[K_a]) \
             and tilemap[int(glob.MAPHEIGHT / 2) - 1][int(glob.MAPWIDTH / 2) - 1] not in glob.G_WATER_ALL \
             and objectmap[int(glob.MAPHEIGHT / 2) - 1][int(glob.MAPWIDTH / 2) - 1] not in glob.OBJECTS:
            self.player.move(-1, -1)

        elif (keys[K_s] and keys[K_d]) \
             and tilemap[int(glob.MAPHEIGHT / 2) + 1][int(glob.MAPWIDTH / 2) + 1] not in glob.G_WATER_ALL \
             and objectmap[int(glob.MAPHEIGHT / 2) + 1][int(glob.MAPWIDTH / 2) + 1] not in glob.OBJECTS:
            self.player.move(+1, +1)
        elif (keys[K_s] and keys[K_a]) \
             and tilemap[int(glob.MAPHEIGHT / 2) + 1][int(glob.MAPWIDTH / 2) - 1] not in glob.G_WATER_ALL \
             and objectmap[int(glob.MAPHEIGHT / 2) + 1][int(glob.MAPWIDTH / 2) - 1] not in glob.OBJECTS:
            self.player.move(-1, +1)

        elif (keys[K_d]) \
                and tilemap[int(glob.MAPHEIGHT / 2)][int(glob.MAPWIDTH / 2) + 1] not in glob.G_WATER_ALL \
                and objectmap[int(glob.MAPHEIGHT / 2)][int(glob.MAPWIDTH / 2) + 1] not in glob.OBJECTS:
            self.player.move(+1, 0)
        elif (keys[K_a]) \
                and tilemap[int(glob.MAPHEIGHT / 2)][int(glob.MAPWIDTH / 2) - 1] not in glob.G_WATER_ALL \
                and objectmap[int(glob.MAPHEIGHT / 2)][int(glob.MAPWIDTH / 2) - 1] not in glob.OBJECTS:
            self.player.move(-1, 0)
        elif (keys[K_w]) \
                and tilemap[int(glob.MAPHEIGHT / 2) - 1][int(glob.MAPWIDTH / 2)] not in glob.G_WATER_ALL \
                and objectmap[int(glob.MAPHEIGHT / 2) - 1][int(glob.MAPWIDTH / 2)] not in glob.OBJECTS:
            self.player.move(0, -1)
        elif (keys[K_s]) \
                and tilemap[int(glob.MAPHEIGHT / 2) + 1][int(glob.MAPWIDTH / 2)] not in glob.G_WATER_ALL \
                and objectmap[int(glob.MAPHEIGHT / 2) + 1][int(glob.MAPWIDTH / 2)] not in glob.OBJECTS:
            self.player.move(0, +1)



    def OnKeydownEvent(self, key):
        if key == K_ESCAPE:
            self.save()
            pygame.quit()
            sys.exit()

        elif key == K_e:
            glob.CRAFTING_MENU = not glob.CRAFTING_MENU

        elif key == K_F11:
            glob.FSCREEN = not glob.FSCREEN
            if glob.FSCREEN:
                glob.DISPLAYSURF = pygame.display.set_mode((glob.MAPWIDTH * glob.TILESIZE, glob.MAPHEIGHT * glob.TILESIZE), FULLSCREEN | DOUBLEBUF)
            else:
                glob.DISPLAYSURF = pygame.display.set_mode((glob.glob.MAPWIDTH * glob.TILESIZE, glob.MAPHEIGHT * glob.TILESIZE), DOUBLEBUF)

        elif key == K_F12:
            glob.DEBUG = not glob.DEBUG

        elif key == K_SPACE:
            self.player.attack()

    def OnMouseMovement(self, x, y):
        self.player.rotateTo(x, y)
        self.player.selectNearestTile(x, y)

    def drawBars(self):
        for i in range(glob.MAPWIDTH):
            glob.DISPLAYSURF.blit(glob.TOP_BAR, (i*glob.TILESIZE, 0))

        offset = int((glob.SCREENWIDTH - 10*glob.BOTTOM_BAR.get_width()) / 2)
        for j in range(0, 10):
            glob.DISPLAYSURF.blit(glob.BOTTOM_BAR, (offset + j*glob.BOTTOM_BAR.get_width(), glob.SCREENHEIGHT - glob.BOTTOM_BAR.get_width()))
            if glob.toolbar_selection == j:
                glob.DISPLAYSURF.blit(glob.BB_SELECTION, (offset + j*glob.BOTTOM_BAR.get_width(), glob.SCREENHEIGHT - glob.BOTTOM_BAR.get_width()))

    def drawCraftingMenu(self):
        glob.DISPLAYSURF.blit(glob.UI_FRAME_TR, ((glob.MAPWIDTH - 11) * glob.TILESIZE, 6 * glob.TILESIZE))
        glob.DISPLAYSURF.blit(glob.UI_FRAME_TL, (11 * glob.TILESIZE, 6 * glob.TILESIZE))
        glob.DISPLAYSURF.blit(glob.UI_FRAME_BR, ((glob.MAPWIDTH - 11) * glob.TILESIZE, 20 * glob.TILESIZE))
        glob.DISPLAYSURF.blit(glob.UI_FRAME_BL, (11 * glob.TILESIZE, 20 * glob.TILESIZE))

        for i in range(12, (glob.MAPWIDTH - 11)):
            glob.DISPLAYSURF.blit(glob.UI_FRAME_T, (i * glob.TILESIZE, 6 * glob.TILESIZE))
            glob.DISPLAYSURF.blit(glob.UI_FRAME_B, (i * glob.TILESIZE, 20 * glob.TILESIZE))
        for i in range(7,20):
            glob.DISPLAYSURF.blit(glob.UI_FRAME_R, ((glob.MAPWIDTH - 11) * glob.TILESIZE, i * glob.TILESIZE))
            glob.DISPLAYSURF.blit(glob.UI_FRAME_L, (11 * glob.TILESIZE, i * glob.TILESIZE))

        k = 0
        for i in range(7,20):
            for j in range(12, (glob.MAPWIDTH - 11)):
                glob.DISPLAYSURF.blit(glob.UI_FRAME, (j * glob.TILESIZE, i * glob.TILESIZE))
                if k < len(glob.CRAFTABLES):
                    glob.DISPLAYSURF.blit(glob.objectTextures[glob.CRAFTABLES[k]], (j * glob.TILESIZE, i * glob.TILESIZE))
                    k+=1

    def loop(self):
        chunkX, chunkY = self.map.worldCoordinatesToChunk(self.player.xPos, self.player.yPos)
        self.map.loadChunk(chunkX, chunkY)

        while True:
            glob.DISPLAYSURF.fill(glob.BLACK)
            for event in pygame.event.get():
                self.OnEvent(event)

            self.OnKeysPressed(pygame.key.get_pressed())


            self.map.update(self.player.xPos, self.player.yPos)
            x, y = pygame.mouse.get_pos()
            self.OnMouseMovement(x, y)
            self.player.update()
            self.drawBars()
            self.player.inventory.update()

            if glob.CRAFTING_MENU: self.drawCraftingMenu()

            # update the display
            pygame.display.update()
            glob.CLOCK.tick(60)

if __name__ == '__main__':
    app = App()
