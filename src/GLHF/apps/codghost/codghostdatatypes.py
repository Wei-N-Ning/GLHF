import Queue
import ctypes

from GLHF.libs.datatypes import vector
from GLHF.libs.datatypes import common

MAX_ENTITY_COUNT = 32


class RefDef(ctypes.Structure):
    """
    struct refdef_t
    {
        char _0x0000[8];
        int width;
        int height;
        float fov_x;
        float fov_y;
        vec3_t viewOrigin;
        vec3_t viewAxis[3];
    }
    """
    _fields_ = [
                ("_padding0", ctypes.c_char * 8),
                ("width", ctypes.c_int),
                ("height", ctypes.c_int),
                ("fov_x", ctypes.c_float),
                ("fov_y", ctypes.c_float),
                ("viewOrigin", vector.C_VECTOR3),
                ("viewAxis", vector.C_VECTOR3 * 3)
               ]
    def debugPrint(self):
        print "dimension:", self.width, self.height
        print "fov:", self.fov_x, self.fov_y
        print "orig:", self.viewOrigin.x, self.viewOrigin.y, self.viewOrigin.z
        print "x axis:", self.viewAxis[0].x, self.viewAxis[0].y, self.viewAxis[0].z
        print "y axis:", self.viewAxis[1].x, self.viewAxis[1].y, self.viewAxis[1].z
        print "z axis:", self.viewAxis[2].x, self.viewAxis[2].y, self.viewAxis[2].z
    def getSize(self):
        return ctypes.sizeof(self)
    

class Entity(ctypes.Structure):
    """
    typedef struct
    {
        char _0x0000[0x18];                                                         
        Vector lerpOrigin;                                                          
        char _0x00A0[0x7C];                                                         
        Vector oldOrigin;                                                           
        char _0x00F8[0x4C];                                                         
        __int32 clientNum;                                                          
        __int32 eType;                                                              
        __int32 eFlags;                                                             
        char _0x0150[0x4C];                                                         
        Vector newOrigin;                                                           
        char _0x0200[0xA4];                                                         
        __int32 isAlive;                                                            
        char _0x204[0x34];                                                          
    }entity_t; //Size=0x0238
    """
    _fields_ = [
                ("_padding0", ctypes.c_char * 0x18),
                ("lerpOrigin", vector.C_VECTOR3),
                ("_padding1", ctypes.c_char * 0x7C),
                ("oldOrigin", vector.C_VECTOR3),
                ("_padding2", ctypes.c_char * 0x4C),
                ("clientNum", ctypes.c_int),
                ("eType", ctypes.c_int),
                ("eFlags", ctypes.c_int),
                ("_padding3", ctypes.c_char * 0x4C),
                ("newOrigin", vector.C_VECTOR3),
                ("_padding4", ctypes.c_char * 0xA4),
                ("isAlive", ctypes.c_int),
                ("_padding5", ctypes.c_char * 0x34)
               ]
    size = 0x238
    def debugPring(self):
        print "oOrig:", self.oldOrigin.x, self.oldOrigin.y, self.oldOrigin.z
        print "eType:", self.eType
        print "eFlags:", self.eFlags
        print "isAlive:", self.isAlive
class EntityArray(ctypes.Structure):
    _fields_ = [("entities", Entity * MAX_ENTITY_COUNT)]
    def getSize(self):
        return Entity.size * MAX_ENTITY_COUNT


class EntityName(ctypes.Structure):
    _fields_ = [("name", ctypes.c_char * 0x70)]
    size = 0x70
class EntityNameArray(ctypes.Structure):
    _fields_ = [("entityNames", EntityName * MAX_ENTITY_COUNT)]
    def getSize(self):
        return EntityName.size * MAX_ENTITY_COUNT


class ViewAngles(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float),
                ("y", ctypes.c_float),
                ("z", ctypes.c_float)]
    def getSize(self):
        return 0x4 * 3
    def debugPrint(self):
        print "I:%.03f, II:%.03f, III:%.04f" % (self.x, self.y, self.z)
    

class Soldier(object):
    """
    ClientEntity + ClientInfo
    """
    def __init__(self):
        self.clientEntityAddress = 0
        
        self.name = ''
        self.health = 0.0
        
        self.posVec4 = None
        self.stance = 0x0
        
        self.velVec4 = None
        
        self.teamId = 0x0
        
    def __eq__(self, other):
        if isinstance(other, Soldier):
            return self.clientEntityAddress == other.clientEntityAddress
        return False
    
    def __ne__(self, other):
        if isinstance(other, Soldier):
            return self.clientEntityAddress != other.clientEntityAddress
        return True
    
    def isValid(self):
        """
        Don't check health for now...
        """
        return self.clientEntityAddress != 0 and self.posVec4 != None
    
    def toString(self):
        if self.clientEntityAddress != 0:
            return "Soldier<team(%s), name(%s), HP(%.03f), POS(%s)>" % (self.teamId, self.name, self.health, self.posVec4)
        return "Soldier<invalid>"
    
    def __str__(self):
        return self.toString()
    

class DataContainer(object):
    
    def __init__(self):
        self.isInGame = False
        
        self.fovX = 0.0
        self.fovY = 0.0
        
        self.viewMatrix = None
        self.minimapRotationMatrix = None
        
        self.viewAxisX = None
        self.viewAxisY = None
        self.viewAxisZ = None
        
        self.viewOrigin = None
        self.viewForwardVec = None
        
        # corresponding to viewAngles[0-2]
        # yaw being the important one for minimap
        self.yaw = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        
        self.localPlayer = Soldier()
        
        self.soldiers = Queue.Queue(maxsize=64)
        
        

