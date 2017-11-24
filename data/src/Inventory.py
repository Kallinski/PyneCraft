import data.src.globals as glob

empty_inv = dict()
for key in glob.resources:
    empty_inv.update({str(key): 0})

class Inventory():

    def __init__(self, inventory=empty_inv):
        self.items = inventory

    def add(self, item, amount):
        self.items.update({str(item): self.items.get(str(item))+amount})

    def get(self, item):
        return self.items[str(item)]

    def update(self):
        # display the inventory, starting 10 pixels in
        placePosition = 10
        for item in glob.resources:
            # add the image
            glob.DISPLAYSURF.blit(glob.resourceTextures[item], (placePosition, 5))
            placePosition += 40
            # add the text showing the amount in the inventory
            textObj = glob.INVFONT.render(str(self.get(item)), True, glob.WHITE)
            glob.DISPLAYSURF.blit(textObj, (placePosition, 5))
            placePosition += 50

        for item in glob.toolbar:
            if item != None:
                barH = glob.BOTTOM_BAR.get_height()
                barW = glob.BOTTOM_BAR.get_width()
                itemH = glob.objectTextures[item].get_height()
                itemW = glob.objectTextures[item].get_width()
                offset = int((glob.SCREENWIDTH - 10 * barW) / 2)
                glob.DISPLAYSURF.blit(glob.objectTextures[item],
                                 (offset + glob.toolbar.index(item) * barH + (barH - itemH) / 2,
                                  glob.SCREENHEIGHT - barW + (barW - itemW) / 2))
