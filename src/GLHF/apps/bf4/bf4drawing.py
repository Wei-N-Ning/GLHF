import math

import win32api
import win32con
import win32gui

from GLHF.libs.datatypes import matrix
from GLHF.libs.datatypes import vector


COLOR_RED = win32api.RGB(255, 0, 0)
COLOR_GREEN = win32api.RGB(0, 255, 0)
COLOR_BLUE = win32api.RGB(0, 0, 255)

MAX_TEXT_WIDTH = 150
MAX_TEXT_HEIGHT = 20


def drawCrossHair(hDc, centerX, centerY, size=10, lineWidth=1, color=COLOR_RED):
    hPen= win32gui.CreatePen(win32con.PS_SOLID, lineWidth, color)
    win32gui.SelectObject(hDc, hPen)
    win32gui.MoveToEx(hDc, centerX-size, centerY)
    win32gui.LineTo(hDc, centerX+size, centerY)
    win32gui.MoveToEx(hDc, centerX, centerY+size)
    win32gui.LineTo(hDc, centerX, centerY-size)

def setTextColor(hDc, color=COLOR_RED):
    win32gui.SetTextColor(hDc, color)

def drawSimpleText(hDc, text, x, y):
    win32gui.DrawText(hDc, 
                      text, 
                      len(text), 
                      (x, y, x+MAX_TEXT_WIDTH, y+MAX_TEXT_HEIGHT), 
                      win32con.DT_TOP|win32con.DT_LEFT)
    
def drawSoldiers(hDc, dataContainer, globalLock, cX, cY, lineWidth=1):
    """
    win32gui.Rectangle(hDc, left, top, right, bottom)
    
    draw the box esp and the minimap
    """
    globalLock.acquire()
    viewTransform = dataContainer.viewMatrix
    viewOrigin = dataContainer.viewOrigin
    viewForwardVec = dataContainer.viewForwardVec
    fovY = dataContainer.fovY
    fovX = dataContainer.fovX
    
    # i'm using the old bf3 worldToScreen calculation, so do not need the aspect ratio any more
    #aspect = dataContainer.aspectRatio
    globalLock.release()
    
    projM = getProjectionMatrixBF3(0.06, 10000.0, fovX, fovY)
    
    # ============== initialize the minimap ================
    centerX, centerY = 200, 200
    boundaryX, boundaryY = 160, 160
    top, bottom = centerY - boundaryY, centerY + boundaryY
    left, right = centerX - boundaryX, centerX + boundaryX
    hPen = win32gui.CreatePen(win32con.PS_SOLID, 2, COLOR_BLUE)
    win32gui.SelectObject(hDc, hPen)
    win32gui.Rectangle(hDc, left, top, right, bottom)
    drawCrossHair(hDc, centerX, centerY, size=159, lineWidth=2, color=COLOR_BLUE)
    # ======================================================
    
    # the consumer starts up - consuming n soldier objects at a time
    # n equals to the approximate size of the queue at that point
    for i in range(dataContainer.soldiers.qsize()):
        
        soldier = dataContainer.soldiers.get()

        # strictly speaking the soldier object can not be invalid (due to the producer-consumer
        # model), but just to be on the safe side...
        if not soldier.isValid():
            continue
        
        distanceToViewOrigin = viewOrigin.distanceTo(soldier.posVec4)
        
        color = COLOR_RED if soldier.occluded else COLOR_GREEN
        
        hPen = win32gui.CreatePen(win32con.PS_SOLID, lineWidth, color)
        win32gui.SelectObject(hDc, hPen)
        
        # here is the same logic as in BF3, applies to other MVP transformation as well
        posV = soldier.posVec4.multToMat(viewTransform)
        posVP = posV.multToMat(projM)
        
        if abs(posVP.w) > 0.001 and posVP.z <= 0:
            # ============== draw soldier box esp ===============
            # important! this is different from BF3 (d3d)!!
            scrX = int(cX * (1 + posVP.x / posVP.w))
            scrY = int(cY * (1 - posVP.y / posVP.w))
            # draw text
            text = "%d(%d)" % (int(distanceToViewOrigin), int(soldier.health))
            win32gui.DrawText(hDc, text, len(text), (scrX, scrY, scrX+68, scrY+14), win32con.DT_TOP|win32con.DT_LEFT)
            # calculate the esp box size!
            
            # the reason I don't use the calculation is the scope will disturb the esp box
            w, h = 4,4#getWidthHeight(distanceToViewOrigin, soldier.stance)
            win32gui.Rectangle(hDc, scrX-w/2, scrY-h, scrX+w/2, scrY)
            # ===================================================
            
            # ============== draw soldier hp indicator ==============
            
            # =======================================================
            
            
        if posV.w > 0.001:
            # =========== draw soldier minimap spot ===========
            # calculate the planar coord while compensate for the viewing angle
            dx = posV.x / posV.w
            cosA = viewForwardVec.dotProduct(vector.Vector4(viewForwardVec.x, 0.0, viewForwardVec.z, 0.0).normalize())
            dy = posV.z / posV.w / abs(cosA)
            # limit the drawing to the defined minimap region
            dx = int(dx / 1.0 + centerX)
            dy = int(dy / 1.0 + centerY)
            if dx < left: dx = left
            if dx > right:dx = right
            if dy < top : dy = top
            if dy > bottom:dy = bottom
            # draw spot
            pColor = COLOR_RED if soldier.occluded else COLOR_GREEN
            hPen = win32gui.CreatePen(win32con.PS_SOLID, 2, pColor)
            win32gui.SelectObject(hDc, hPen)
            win32gui.Rectangle(hDc, dx, dy, dx+2, dy+2)
            # =================================================

def cot(x):
    return 1/math.tan(x)

def getProjectionMatrix(fovY, aspect, zn=0.06, zf=10000.0):
    """
    DOES NOT WORK! COMPLETELY INVERTED!!
    
    http://msdn.microsoft.com/en-us/library/windows/desktop/bb205351(v=vs.85).aspx
    
    What's cotangent (cot):
    http://mathworld.wolfram.com/Cotangent.html
    """
    projM = matrix.Matrix44()
    yScale = cot(fovY/2)
    xScale = yScale / aspect
    projM.set(0, 0, xScale)
    projM.set(1, 1, yScale)
    projM.set(2, 2, zf/(zn-zf))
    projM.set(3, 2, zn*zf/(zn-zf))
    projM.set(2, 3, -1.0)
    return projM

def getProjectionMatrixBF3(nz, fz, fovH, fovV):
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

def getWidthHeight(distant, stance):
    if stance == 0:
        width, height = 48, 64
    elif stance == 1:
        width, height = 48, 32
    elif stance == 2:
        width, height = 48, 16
    else:
        width, height = 48, 64
    _f = 20.0 / distant
    width = width * _f
    height = height * _f
    if width < 3:
        width = 3.0
    if height < 3:
        height = 3.0
    return int(width), int(height)