import math

import win32api
import win32con
import win32gui

from GLHF.libs.datatypes import matrix
from GLHF.libs.datatypes import vector


COLOR_RED = win32api.RGB(255, 0, 0)
COLOR_GREEN = win32api.RGB(0, 255, 0)
COLOR_BLUE = win32api.RGB(0, 0, 255)
COLOR_YELLOW = win32api.RGB(255, 215, 10)


def drawCrossHair(hDc, centerX, centerY, size=10, lineWidth=1, color=COLOR_RED):
    hPen= win32gui.CreatePen(win32con.PS_SOLID, lineWidth, color)
    win32gui.SelectObject(hDc, hPen)
    win32gui.MoveToEx(hDc, centerX-size, centerY)
    win32gui.LineTo(hDc, centerX+size, centerY)
    win32gui.MoveToEx(hDc, centerX, centerY+size)
    win32gui.LineTo(hDc, centerX, centerY-size)


def drawSoldiers(hDc, dataContainer, globalLock):
    
    # ============== initialize the minimap ===============
    centerX, centerY = 230, 530
    boundaryX, boundaryY = 230, 230
    top, bottom = centerY - boundaryY, centerY + boundaryY
    left, right = centerX - boundaryX, centerX + boundaryX
    hPen = win32gui.CreatePen(win32con.PS_SOLID, 2, COLOR_BLUE)
    win32gui.SelectObject(hDc, hPen)
    win32gui.Rectangle(hDc, left, top, right, bottom)
    drawCrossHair(hDc, centerX, centerY, size=230, lineWidth=2, color=COLOR_BLUE)
    # =====================================================
    
    # ============== initialize the offview esp ================
    sizeX, sizeY = 230, 135
    hPenESP = win32gui.CreatePen(win32con.PS_SOLID, 1, COLOR_RED)
    hPenRect = win32gui.CreatePen(win32con.PS_SOLID, 2, COLOR_BLUE)
    win32gui.SelectObject(hDc, hPenRect)
    win32gui.Rectangle(hDc, 0, 0, 460, 270)
    drawCrossHair(hDc, 230, 135, size=5, lineWidth=2, color=COLOR_BLUE)
    # ==========================================================
    
    if dataContainer.isInGame != 0x4000:
        return
    
    # get the view properties
    globalLock.acquire()
    viewOrigin = dataContainer.viewOrigin.copy()
    viewAxisX = dataContainer.viewAxisX.copy()
    viewAxisY = dataContainer.viewAxisY.copy()
    viewAxisZ = dataContainer.viewAxisZ.copy()
    fovX = dataContainer.fovX
    fovY = dataContainer.fovY
    globalLock.release()
    
    win32gui.SelectObject(hDc, hPenESP)
    for i in range(dataContainer.soldiers.qsize()):
        soldier = dataContainer.soldiers.get()
        if not soldier.isValid():
            continue
        
        headPos = soldier.posVec4.copy()
        headPos.z += 60.0
        
        distance = (headPos - viewOrigin).length()/10
        
        feetCoords = worldToScreen(fovX, fovY, sizeX, sizeY, viewAxisX, viewAxisY, viewAxisZ, viewOrigin, soldier.posVec4)
        if not feetCoords:
            continue
        headCoords = worldToScreen(fovX, fovY, sizeX, sizeY, viewAxisX, viewAxisY, viewAxisZ, viewOrigin, headPos)
        if not headCoords:
            continue
        feetX, feetY, miniX, miniY = feetCoords
        headX, headY, _p, _q = headCoords
        height = headY - feetY
        width = height / 3
        
        # esp
        win32gui.Rectangle(hDc, headX-width/2, headY, feetX+width/2, feetY)
        
        # mini map
        dx = miniX + centerX
        dy = miniY + centerY
        if dx < left: dx = left
        if dx > right:dx = right
        if dy < top : dy = top
        if dy > bottom:dy = bottom
        win32gui.Rectangle(hDc, dx, dy, dx+4, dy+4)
        
        
        

def getProjectionMatrix(nz, fz, fovH, fovV):
    w = 1.0 / math.tan( fovH*0.5 )
    h = 1.0 / math.tan( fovV*0.5 )
    q = fz / ( fz - nz )
    mat = matrix.Matrix44()
    mat.set(0, 0, w)
    mat.set(1, 1, h)
    mat.set(2, 2, q)
    mat.set(3, 2, -1*q*nz)
    mat.set(2, 3, -1.0)
    return mat


def worldToScreenTransform(viewAxisX, viewAxisY, viewAxisZ, origin, target):
    """
    given the three view axis and two vectors, return the screen space transform 
    corresponding to target's world transform
    
    @param origin: viewport origin, ie. the player position
    @type  origin: L{EHF.libs.ehfmaths.VECTOR}
    
    @param target: the world space transform of the object of interests
    @type  target: L{EHF.libs.ehfmaths.VECTOR}
    
    @return: screen space transform
    @rtype : L{EHF.libs.ehfmaths.VECTOR}
    """
    delta = (target - origin).normalize()
    delta.w = 1.0
    scrTransform = vector.Vector4()
    scrTransform.x = delta.dotProduct(viewAxisY)
    scrTransform.y = delta.dotProduct(viewAxisZ)
    scrTransform.z = delta.dotProduct(viewAxisX)
    scrTransform.w = 1.0
    return scrTransform


def worldToScreen(fovX, fovY, scrCenterX, scrCenterY, viewAxisX, viewAxisY, viewAxisZ, origin, target):
    scrTransform = worldToScreenTransform(viewAxisX, viewAxisY, viewAxisZ, origin, target)
    if scrTransform.z < 0.1:
        return None
    x = scrCenterX * (1 - (scrTransform.x / fovX / scrTransform.z))
    y = scrCenterY * (1 - (scrTransform.y / fovY / scrTransform.z))
    return int(x), int(y), -int(scrTransform.x*100), -int(scrTransform.z*100)