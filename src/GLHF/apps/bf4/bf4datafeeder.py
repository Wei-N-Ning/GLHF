"""
Example of how to parse the player block
while True:
time.sleep(self.feedingInterval)
pl = self.cfg.LocalPlayerAddress

# name
name = self.rpm.readStr64(pl + 0x40)

# team id
teamId = self.rpm.readUInt(pl + 0xCBC)

# client soldier entity
cse = self.rpm.readUInt64(pl + 0xDC0)
self.prthex(cse, "clientSoldierEntity: ")

# health
health = self.rpm.readUInt64(cse + 0x140)
self.prthex(health, "healthcomp: ")
hp = self.rpm.readFloat(health + 0x38)
print "health: ", hp

# vehicle data block!!
veh = self.rpm.readUInt64(pl + 0xDB0)
self.prthex(veh, "vehicle: ")

if not veh:
    rp = self.rpm.readUInt64(cse + 0x490)
    self.prthex(rp, "replicatedController: ")
    
    # occl
    occl = self.rpm.readByte(cse + 0x591)
    self.prthex(occl, "occl: ")
     
    # pos
    print "pos:", self.rpm.readVec4Point(rp + 0x30)
    # surf vel
    print "surf-vel:", self.rpm.readVec4Direction(rp + 0x40)
    # vel
    print "vel:", self.rpm.readVec4Direction(rp + 0x50)
    # stance
    print "stance:", self.rpm.readUInt(rp + 0x80)
else:
    veh_vel = self.rpm.readVec4Direction(veh + 0x280)
    print "vehicle vel:", veh_vel
"""

import sys
import threading
import time

from GLHF.libs.memory import rpm
from GLHF.libs.datatypes import matrix

import bf4datatypes

import logging
logger = logging.getLogger(__name__)


class BF4DataFeeder(object):
    
    vehicleIdNameMap = {
        32: "MRAP",
        35: "UH-1Y VENOM",
        75: "PWC",
        78: "RCB",
        81: "Z-9 HAITUN",
        82: "Tank",
        90: "LAV-25",
        120:"Z-10W",
        143:"ZBO-09",
        148:"AH-1Z VIPER",
        154:"ZFB-05"
    }
        
    def __init__(self, app):
        self.ctn = app.ctn
        self.cfg = app.cfg
        self.lock = app.lock
        self.feedingInterval = app.renderInterval
        self.rpm = None
    
    def initializeRPM(self, hProcess):
        self.rpm = rpm.RPM(hProcess)
    
    def run(self):
        while True:
            self.lock.acquire()
            killed = self.cfg.killed
            self.lock.release()
            if killed:
                break
            self._populateViewProperties()
            self._populateSoldierArray()
            time.sleep(self.feedingInterval)
        sys.exit(0)
        
    def _populateViewProperties(self):
        """
        @note: the address RenderViewAddress + 0x40 is in fact FirstPersonTransform, same as 
               BF3. It is a compound structure holding the view vectors and the view location
               but NOT a view matrix!!
               The code must convert this transform into a legit view matrix. 
        """
        fovY = self.rpm.readFloat(self.cfg.RenderViewAddress + 0xB4)
        fovX = self.rpm.readFloat(self.cfg.RenderViewAddress + 0x250)
        #aspectRatio = self.rpm.readFloat(self.cfg.RenderViewAddress + 0xC4)
        firstPersonTransform = self.rpm.readMat4(self.cfg.RenderViewAddress + 0x40)
        viewMatrix = matrix.getViewMatrixFromFirstPersonTransform(firstPersonTransform)
        viewOrigin = firstPersonTransform.getColumnVector(3)
        viewForwardVec = firstPersonTransform.getColumnVector(2)
        viewOrigin.w = 1.0
        
        self.lock.acquire()
        self.ctn.fovY = fovY
        self.ctn.fovX = fovX
        #self.ctn.aspectRatio = aspectRatio
        self.ctn.viewMatrix = viewMatrix
        self.ctn.viewOrigin = viewOrigin
        self.ctn.viewForwardVec = viewForwardVec
        self.lock.release()
        
    def _populateSoldierArray(self):
        
        # the producer starts up...
        arrayAddress = self.cfg.PlayerPtrArrayAddress
        myTeamId = self.rpm.readUInt(self.cfg.LocalPlayerAddress + 0xCBC)
        
        # there are maximum 64 players in a round
        for index in range(64):
            
            # get the player address (ClientSoldier)
            entryAddress = arrayAddress+index*8
            
            # not all the ptr is valid, be careful
            # as soon as a player dies, its pointer is NULL-ed
            soldierAddress = self.rpm.readUInt64(entryAddress)   
            if soldierAddress == 0x0:
                continue
            
            # teamId (isEnemy) & vehicle & CSE
            # to save performance, do not handle friendly players
            teamId = self.rpm.readUInt(soldierAddress + 0xCBC)
            if teamId == myTeamId:
                continue
            
            # check if the controllable is a vehicle,
            # there is currently no way to handle vehicle....
            vehicle = self.rpm.readUInt64(soldierAddress + 0xDB0)
            if vehicle != 0x0:
                continue
            
            # ClientSoldierEntity, same concept as in BF3, ensure it is a valid pointer
            cse = self.rpm.readUInt64(soldierAddress + 0xDC0)
            if cse == 0x0:
                continue
            
            # ========= populating Soldier structure ==========
            soldier = bf4datatypes.Soldier()
            # replicated controller, same concept as in BF3
            repCon = self.rpm.readUInt64(cse + 0x490)
            # name
            soldier.address = soldierAddress
            soldier.name = self.rpm.readStr64(soldierAddress + 0x40)
            # health
            healthCompoundAddress = self.rpm.readUInt64(cse + 0x140)
            soldier.health = self.rpm.readFloat(healthCompoundAddress + 0x38)
            # occl
            soldier.occluded = bool(self.rpm.readByte(cse + 0x591))
            # pos vector, make sure its w element is 1.0, required by d3d convention
            soldier.posVec4 = self.rpm.readVec4Position(repCon + 0x30)
            soldier.posVec4.w = 1.0
            # vel vector
            soldier.velVec4 = self.rpm.readVec4Direction(repCon + 0x50)
            # stance: 0-stand, 1-nail, 2-crouch
            soldier.stance = self.rpm.readUInt(repCon + 0x80)
            # =================================================
            
            # set values
            if soldierAddress == self.cfg.LocalPlayerAddress:
                # use thread lock
                self.lock.acquire()
                self.ctn.localPlayer = soldier
                self.lock.release()
            else:
                # Queue object has the "blocking" ability
                self.ctn.soldiers.put(soldier)
