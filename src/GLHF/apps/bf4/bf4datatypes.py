import Queue


class Soldier(object):

    vehicleIdNameMap = {
        32: "MRAP",
        35: "UH-1Y VENOM",
        75: "PWC",
        78: "RCB",
        81: "Z-9 HAITUN",
        82: "Tank",
        117:"Tank", # ++
        90: "LAV-25",
        120:"Z-10W",
        143:"ZBO-09",
        148:"AH-1Z VIPER",
        154:"ZFB-05"
    }
    
    def __init__(self):
        self.address = 0x0
        
        self.name = ''
        
        self.health = 0.0
        
        self.posVec4 = None
        self.stance = 0x0
        
        self.occluded = False # False --> isVisible! True --> notVisible!
        
        self.velVec4 = None
                
        self.isEnemy = True
        self.teamId = 0x0
        
        self.isVehicle = False
    
    def vehicleIdToName(self, vehicleId):

        return ''
    
    def __eq__(self, other):
        if isinstance(other, Soldier):
            return self.address == other.address
        return False
    
    def __ne__(self, other):
        if isinstance(other, Soldier): 
            return self.address != other.address
        return True
        
    def isValid(self):
        # do not check velocity for now (since people can camp around)
        return self.address != 0x0 and self.posVec4 != None and self.health > 0.1
    
    def toString(self):
        if self.address == 0x0:
            return "Soldier<invalid>"
        tag = "[VEL]" if self.isVehicle else "[-_-]"
        return "Soldier%s<name(%s) HP(%.03f) POS(%s) stance(%s) occl(%s)>" %\
               (tag, self.name, self.health, self.posVec4, self.stance, self.occluded)
    
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
        
        # maxsize is an integer that sets the upperbound limit on the number of items that can 
        # be placed in the queue. Insertion will block once this size has been reached
        self.soldiers = Queue.Queue(maxsize=64)
        

