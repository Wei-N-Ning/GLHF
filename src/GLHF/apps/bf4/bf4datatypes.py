

class Soldier(object):
    
    def __init__(self):
        self.address = 0x0
        
        self.name = ''
        
        self.health = 0.0
        
        self.posVec4 = None
        self.stance = 0x0
        
        self.occluded = False # True --> isVisible!
        
        self.velVec4 = None
                
        self.isEnemy = True
        self.teamId = 0x0
    
    def __eq__(self, other):
        return self.address == other.address
    
    def __ne__(self, other):
        return self.address != other.address
    
    def isValid(self):
        return self.address != 0x0 and self.posVec4 != None and self.velVec4 != None and self.health > 0
    
    def toString(self):
        if self.address == 0x0:
            return "Soldier<invalid>"
        return "Soldier<name(%s) hp(%.03f) pos(%s) stance(%s) occl(%s)>" %\
               (self.name, self.health, self.posVec4, self.stance, self.occluded)
    
    def __str__(self):
        return self.toString()
    
class DataContainer(object):
    
    def __init__(self):
        self.inGame = False
        self.inRound = False
        self.gameTime = 0x0
        
        self.fovX = 0.0
        self.fovY = 0.0
        self.aspectRatio = 0.0
        
        self.viewMatrix = None
        self.viewOrigin = None
        self.viewForwardVec = None
        
        self.localPlayer = Soldier()
        self.soldiers = [Soldier() for i in range(64)]
        

