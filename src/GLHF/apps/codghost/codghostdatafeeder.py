import sys
import time

from GLHF.libs.memory import rpm
from GLHF.libs.datatypes import matrix

import codghostdatatypes

import logging
logger = logging.getLogger(__name__)


class CODGhostDataFeeder(object):
    
    def __init__(self, app):
        self.ctn = app.ctn
        self.cfg = app.cfg
        self.lock = app.lock
        self.feedingInterval = app.renderInterval
        self.rpm = None
        
        # some buffer objects
        self.bufferRefDef = codghostdatatypes.RefDef() 
        self.bufferRefDefSize = self.bufferRefDef.getSize()
        self.bufferEntityArray = codghostdatatypes.EntityArray()
        self.bufferEntityArraySize = self.bufferEntityArray.getSize()
        self.bufferEntityNameArray = codghostdatatypes.EntityNameArray()
        self.bufferEntityNameArraySize = self.bufferEntityNameArray.getSize()
        
    def initializeRPM(self, hProcess):
        self.rpm = rpm.RPM(hProcess)
    
    def run(self):
        while True:

            self.lock.acquire()
            killed = self.cfg.killed
            self.lock.release()
            if killed:
                break

            self._populateGameProperties()
            
            if self.ctn.isInGame == 0x4000:
                self._populateViewProperties()
                self._populateSoldiers()
            
            time.sleep(self.feedingInterval)
    
    def _populateGameProperties(self):
        """
        IsInGame equals to 0 if not in game, but will be set to various non-zero flags depending
        on the stage of the gaming
        
        0x4000 -> in a round
        """
        self.ctn.isInGame = self.rpm.readInt(self.cfg.IsInGame)
                
    def _populateViewProperties(self):
        """
        Be careful! The three component of RefDef.viewAxis are:
        1st: pointing to positive Y
        2nd: pointing to negative X
        3rd: pointing to positive Z
        
        axisX(right) = -1 * 2nd
        axisY(up) = 1st
        axisZ(forward) = 3rd
        
        Be careful #2:
        y,z in COD appears to be swapped!
        y: forward
        z: up
        """
        self.rpm.read(self.cfg.RefdefAddress, self.bufferRefDef, self.bufferRefDefSize)
        self.ctn.fovX = self.bufferRefDef.fov_x
        self.ctn.fovY = self.bufferRefDef.fov_y
        
        self.ctn.viewOrigin = self.bufferRefDef.viewOrigin.toPyVector4Point()
        self.ctn.viewOrigin.swapYZ()
        
        axisX = self.bufferRefDef.viewAxis[1].toPyVector4Direction().multScalar(-1.0)
        axisY = self.bufferRefDef.viewAxis[0].toPyVector4Direction()
        axisZ = self.bufferRefDef.viewAxis[2].toPyVector4Direction()
        
        self.ctn.viewMatrix = matrix.getViewMatrixFromViewAxisAndPosition(axisX, axisY, axisZ, self.ctn.viewOrigin)
        self.ctn.viewForwardVec = axisZ
        
        # debug print-----------------------------
        #self.bufferRefDef.debugPrint()
        #print "x:", axisX
        #print "y:", axisY
        #print "z:", axisZ
        #print self.ctn.viewOrigin
        # ----------------------------------------
        
    def _populateSoldiers(self):
        # get the entity count 
        entityCount = self.rpm.readInt(self.cfg.PlayerCount)
        if entityCount == 0:
            return
        
        # get the entity name array (see the datatype module for how the array is defined)
        # char** names[0x70]
        # [self.bufferEntityNameArray.entityNames[i].name for i in range(entityCount)]
        self.rpm.read(self.cfg.PlayerNames, self.bufferEntityNameArray, self.bufferEntityNameArraySize)
        
        # get the local client number (the player itself)
        localClientNum = self.rpm.readInt(self.cfg.LocalClientNum)
        localPlayerTeamId = 0x0
        
        # get the entities
        self.rpm.read(self.cfg.EntityAddress, self.bufferEntityArray, self.bufferEntityArraySize)
        
        tempSoldierList = []
        # create soldier objects!!
        for i in range(entityCount):
            
            # ignore the dead soldier
            if self.bufferEntityArray.entities[i].isAlive & 0x1 == 0:
                continue

            # populate the structure
            soldier = codghostdatatypes.Soldier()
            soldier.clientEntityAddress = self.cfg.EntityAddress + codghostdatatypes.Entity.size * i
            soldier.name = self.bufferEntityNameArray.entityNames[i].name
            soldier.posVec4 = self.bufferEntityArray.entities[i].lerpOrigin.toPyVector4Point()
            soldier.posVec4.swapYZ()
            soldier.teamId = self.rpm.readInt(self.cfg.ClientInfo + 0x5D8 * i + 0xC)
            
            # debug print-----------------------
            #print soldier
            # ----------------------------------
            
            # check if the current soldier is the local player (ignore local player)
            if self.bufferEntityArray.entities[i].clientNum == localClientNum:
                localPlayerTeamId = soldier.teamId
            else:
                tempSoldierList.append(soldier)
        
        # populate the queue (ignoring the friendly soldiers)
        for soldier in tempSoldierList:
            if soldier.teamId == localPlayerTeamId:
                continue
            self.ctn.soldiers.put(soldier)
        