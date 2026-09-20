import config
class Wall:

    def __init__(self, x1, y1, x2, y2, durability, strength, color, Ricochet_Chance, Ricochet_Treshold=30, Ricochet_Loss=0.5, Ricochet_Loss_Variation=2, Detected=False, heat=0):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.durability = durability
        self.strength = strength
        self.color = color
        self.Ricochet_Chance = Ricochet_Chance
        self.Ricochet_Treshold = Ricochet_Treshold
        self.Ricochet_Loss = Ricochet_Loss
        self.Ricochet_Loss_Variation = Ricochet_Loss_Variation
        self.detected = Detected
        self.heat = heat
        self.midpoints = self.get_midpoints()
        self.center = ((x1 + x2)/2, (y1 + y2)/2)
    
    def get_midpoints(self):
        return [
            (((self.x1 + self.x2) / 2), self.y1), #bottom 
            (self.x1, ((self.y1 + self.y2) / 2)), #left
            (((self.x1 + self.x2) / 2), self.y2), #top
            (self.x2, ((self.y1 + self.y2) / 2)), #right
        ]