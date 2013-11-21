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
    
    # ==========================================================
    
    if dataContainer.isInGame != 0x4000:
        return
    
    if dataContainer.viewMatrix == None:
        return
    
    # get the view properties
    globalLock.acquire()
    viewMatrix = dataContainer.viewMatrix.copy()
    viewOrigin = dataContainer.viewOrigin.copy()
    viewForwardVec = dataContainer.viewForwardVec.copy()
    fovX = dataContainer.fovX
    fovY = dataContainer.fovY
    globalLock.release()
    
    # get projection matrix
    #projM = getProjectionMatrix(0.06, 10000.0, fovX, fovY)
    
    for i in range(dataContainer.soldiers.qsize()):
        soldier = dataContainer.soldiers.get()
        if not soldier.isValid():
            continue
        #distanceToViewOrigin = viewOrigin.distanceTo(soldier.posVec4)
        hPen = win32gui.CreatePen(win32con.PS_SOLID, 2, COLOR_RED)
        win32gui.SelectObject(hDc, hPen)
        posV = viewOrigin - soldier.posVec4#.multToMat(viewMatrix)
        posV.w = 1.0
        #posVP = posV.multToMat(projM)
        
        if posV.w > 0.001:
            # =========== draw soldier minimap spot ===========
            # calculate the planar coord while compensate for the viewing angle
            dx = posV.x / posV.w
            #cosA = viewForwardVec.dotProduct(vector.Vector4(viewForwardVec.x, 0.0, viewForwardVec.z, 0.0).normalize())
            dy = posV.z / posV.w# / abs(cosA)
            # limit the drawing to the defined minimap region
            dx = int(dx / 25.0 + centerX)
            dy = int(dy / 25.0 + centerY)
            if dx < left: dx = left
            if dx > right:dx = right
            if dy < top : dy = top
            if dy > bottom:dy = bottom
            # draw spot
            hPen = win32gui.CreatePen(win32con.PS_SOLID, 2, COLOR_RED)
            win32gui.SelectObject(hDc, hPen)
            win32gui.Rectangle(hDc, dx, dy, dx+2, dy+2)
            # =================================================
    

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