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
        aspectRatio = self.rpm.readFloat(self.cfg.RenderViewAddress + 0xC4)
        firstPersonTransform = self.rpm.readMat4(self.cfg.RenderViewAddress + 0x40)
        viewMatrix = matrix.getViewMatrixFromFirstPersonTransform(firstPersonTransform)
        viewOrigin = firstPersonTransform.getColumnVector(3)
        viewForwardVec = firstPersonTransform.getColumnVector(2)
        viewOrigin.w = 1.0
        
        self.lock.acquire()
        self.ctn.fovY = fovY
        self.ctn.fovX = fovX
        self.ctn.aspectRatio = aspectRatio
        self.ctn.viewMatrix = viewMatrix
        self.ctn.viewOrigin = viewOrigin
        self.ctn.viewForwardVec = viewForwardVec
        self.ctn
        self.lock.release()
        
    def _populateSoldierArray(self):
        arrayAddress = self.cfg.PlayerPtrArrayAddress
        myTeamId = self.rpm.readUInt(self.cfg.LocalPlayerAddress + 0xCBC)
        for index in range(64):
            entryAddress = arrayAddress+index*8
            # address & teamId (isEnemy) & vehicle & CSE
            soldierAddress = self.rpm.readUInt64(entryAddress)   
            if soldierAddress == 0x0:
                continue
            teamId = self.rpm.readUInt(soldierAddress + 0xCBC)
            if teamId == myTeamId:
                continue
            vehicle = self.rpm.readUInt64(soldierAddress + 0xDB0)
            if vehicle != 0x0:
                continue
            cse = self.rpm.readUInt64(soldierAddress + 0xDC0)
            if cse == 0x0:
                continue
            # replicated controller
            repCon = self.rpm.readUInt64(cse + 0x490)
            # name
            name = self.rpm.readStr64(soldierAddress + 0x40)
            # health
            healthCompoundAddress = self.rpm.readUInt64(cse + 0x140)
            health = self.rpm.readFloat(healthCompoundAddress + 0x38)
            # occl
            occluded = bool(self.rpm.readByte(cse + 0x591))
            # pos vector
            posVec4 = self.rpm.readVec4Position(repCon + 0x30)
            posVec4.w = 1.0
            # vel vector
            velVec4 = self.rpm.readVec4Direction(repCon + 0x50)
            # stance
            stance = self.rpm.readUInt(repCon + 0x80)
            
            # set values
            self.lock.acquire()
            if soldierAddress == self.cfg.LocalPlayerAddress:
                self.ctn.localPlayer.address = soldierAddress
                self.ctn.localPlayer.teamId = teamId
                self.ctn.localPlayer.name = name
                self.ctn.localPlayer.health = health
                self.ctn.localPlayer.posVec4 = posVec4
                self.ctn.localPlayer.velVec4 = velVec4
                self.ctn.localPlayer.stance = stance
            else:
                self.ctn.soldiers[index].address = soldierAddress
                self.ctn.soldiers[index].teamId = teamId
                self.ctn.soldiers[index].isEnemy = True
                self.ctn.soldiers[index].name = name
                self.ctn.soldiers[index].health = health
                self.ctn.soldiers[index].posVec4 = posVec4
                self.ctn.soldiers[index].velVec4 = velVec4
                self.ctn.soldiers[index].occluded = occluded
                self.ctn.soldiers[index].stance = stance
            self.lock.release()