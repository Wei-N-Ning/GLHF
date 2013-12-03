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
import time

from GLHF.libs.memory import rpm
from GLHF.libs.datatypes import matrix

import bf4datatypes

import logging
logger = logging.getLogger(__name__)


class BF4DataFeeder(object):
    
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
               The code must convert this transform into a real view matrix. 
        """
        fovY = self.rpm.readFloat(self.cfg.RenderViewAddress + 0xB4)
        fovX = self.rpm.readFloat(self.cfg.RenderViewAddress + 0x250)
        
        # i'm using the old bf3 worldToScreen calculation, so do not need the aspect ratio any more
        #aspectRatio = self.rpm.readFloat(self.cfg.RenderViewAddress + 0xC4)
        firstPersonTransform = self.rpm.readMat4(self.cfg.RenderViewAddress + 0x40)
        viewMatrix = matrix.getViewMatrixFromFirstPersonTransform(firstPersonTransform)
        viewOrigin = firstPersonTransform.getColumnVector(3)
        viewForwardVec = firstPersonTransform.getColumnVector(2)
        viewOrigin.w = 1.0
        
        self.lock.acquire()
        self.ctn.fovY = fovY
        self.ctn.fovX = fovX
        
        # i'm using the old bf3 worldToScreen calculation, so do not need the aspect ratio any more
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
            
            # check if the controllable is a vehicle
            vehicleDataBlock = self.rpm.readUInt64(soldierAddress + 0xDB0)
            if vehicleDataBlock != 0x0:
                soldier = self._readVehicle(soldierAddress, vehicleDataBlock)
            else:
                soldier = self._readSoldier(soldierAddress)

            if soldier == None:
                continue
                
            # set values
            if soldierAddress == self.cfg.LocalPlayerAddress:
                # use thread lock
                self.lock.acquire()
                self.ctn.localPlayer = soldier
                self.lock.release()
            else:
                # Queue object has the "blocking" ability
                self.ctn.soldiers.put(soldier)
        
    def _readSoldier(self, soldierAddress):
        """
        The logic of this method is similar to that of ehf-bf3's
        
        @param soldierAddress: a.k.a ClientPlayerEntity, PlayerEntity, SoliderEntity....
        @type  soldierAddress: int
        """
        # ClientSoldierEntity, same concept as in BF3, ensure it is a valid pointer
        cse = self.rpm.readUInt64(soldierAddress + 0xDC0)
        if cse == 0x0:
            return None
        
        # ========= populating Soldier structure ==========
        soldier = bf4datatypes.Soldier()
        # replicated controller, same concept as in BF3
        repCon = self.rpm.readUInt64(cse + 0x490)
        
        #@TODO: figure out why this could happen??!!
        if repCon > 0xF0000000:
            return None
        
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
        
        # a sort of hack here, use the stance to offset the position y value
        if soldier.stance == 0:
            soldier.posVec4.y += 1.3
        elif soldier.stance == 1:
            soldier.posVec4.y += 0.8
        
        # =================================================        
        # test weapon no recoil and no spread addresses
#        soldierWeaponComponent = self.rpm.readUInt64(cse + 0x550)
#        activeSlot = self.rpm.readByte(soldierWeaponComponent + 0x09A8)
#        weaponArrayBase = self.rpm.readUInt64(soldierWeaponComponent + 0x07A0)
#        weaponAddress = weaponArrayBase + activeSlot * 8
#        clientSoldierWeapon = self.rpm.readUInt64(weaponAddress)
#        weaponFiring = self.rpm.readUInt64(clientSoldierWeapon + 0x49C8)
#        sway = self.rpm.readUInt64(weaponFiring + 0x0078)
#        print "0x%X" % sway
#        if sway and sway > 0x10000000 and sway < 0xF0000000:
#            """
#            float m_deviationPitch; //0x0130 
#            float m_deviationYaw; //0x0134 
#            float m_deviationRoll; //0x0138 
#            """
#            print "sway: 0x%X" % sway
#            print self.rpm.readFloat(sway + 0x130)
#            print self.rpm.readFloat(sway + 0x134)
#            print self.rpm.readFloat(sway + 0x138)
        # =================================================
            
        return soldier
    
    def _readVehicle(self, soldierAddress, vehicleDataBlock):
        """
        @param vehicleDataBlock: (don't know what it is supposed to be called) this represents 
                                 the object contains the vehicle controllable entity (again, not
                                 sure how to call that) 
        @type  vehicleDataBlock: int
        """
        # the block contains the vehicle position etc.
        vehicleControl = self.rpm.readUInt64(vehicleDataBlock + 0x238)
        vehicleSoldierBlock = self.rpm.readUInt64(vehicleControl + 0xA0)
        soldier = bf4datatypes.Soldier()
        soldier.address = soldierAddress
        soldier.name = "_veh_" #@TODO: rpm the vehicle id then the mapped type
        soldier.isVehicle = True
        
        #########
        cse = self.rpm.readUInt64(soldierAddress + 0xDC0)
        if cse == 0x0:
            return None
        healthCompoundAddress = self.rpm.readUInt64(cse + 0x140)
        #########
        
        soldier.health = self.rpm.readFloat(healthCompoundAddress + 0x38)
        soldier.posVec4 = self.rpm.readVec4Point(vehicleSoldierBlock + 0x30)
        soldier.velVec4 = self.rpm.readVec4Direction(vehicleControl + 0x280)
        return soldier
        
        