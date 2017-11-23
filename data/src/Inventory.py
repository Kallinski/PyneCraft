from data.src.globals import *

empty_inv = []
for key in resources:
    empty_inv.append(key)

class Inventory():

    def __init__(self, inventory=empty_inv):
        self.items = inventory

    def add(self, item, amount):
        self.items.update({str(item): self.items.get(str(item))+amount})

    def get(self, item):
        return self.items.get(str(item))

    def update(self):
        # display the inventory, starting 10 pixels in
        placePosition = 10
        for item in resources:
            # add the image
            DISPLAYSURF.blit(resourceTextures[item], (placePosition, 5))
            placePosition += 40
            # add the text showing the amount in the inventory
            textObj = INVFONT.render(str(self.items.get(str(item))), True, WHITE)
            DISPLAYSURF.blit(textObj, (placePosition, 5))
            placePosition += 50

        for item in toolbar:
            if item != None:
                barH = BOTTOM_BAR.get_height()
                barW = BOTTOM_BAR.get_width()
                itemH = objectTextures[item].get_height()
                itemW = objectTextures[item].get_width()
                offset = int((SCREENWIDTH - 10 * barW) / 2)
                DISPLAYSURF.blit(objectTextures[item],
                                 (offset + toolbar.index(item) * barH + (barH - itemH) / 2,
                                  SCREENHEIGHT - barW + (barW - itemW) / 2))
