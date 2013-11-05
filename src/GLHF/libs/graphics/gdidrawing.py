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
    """
    globalLock.acquire()
    viewTransform = dataContainer.viewMatrix
    viewOrigin = dataContainer.viewOrigin
    fovY = dataContainer.fovY
    fovX = dataContainer.fovX
    aspect = dataContainer.aspectRatio
    globalLock.release()
    
    #viewTransform.set(3, 3, 1.0)
    projM = getProjectionMatrixBF3(0.06, 10000.0, fovX, fovY)
    viewProjM = viewTransform.multTo(projM)

    for soldier in dataContainer.soldiers:
        globalLock.acquire()
        isValid = soldier.isValid()
        posVec4 = soldier.posVec4
        isOccluded = soldier.occluded
        stance = soldier.stance
        hp = soldier.health
        globalLock.release()
        
        if not isValid:
            continue
        
        distanceToViewOrigin = viewOrigin.distanceTo(posVec4)
        
        color = COLOR_RED if isOccluded else COLOR_GREEN
        
        hPen = win32gui.CreatePen(win32con.PS_SOLID, lineWidth, color)
        win32gui.SelectObject(hDc, hPen)
        
        posVP = posVec4.multToMat(viewProjM)
        if abs(posVP.w) < 0.001 or posVP.z > 0:
            continue
        
        scrX = int(cX * (1 + posVP.x / posVP.w))
        scrY = int(cY * (1 - posVP.y / posVP.w))
        
        text = "%d H%d" % (int(distanceToViewOrigin), int(hp))
        textLength = len(text)
        win32gui.DrawText(hDc, 
                          text,
                          textLength,
                          (scrX, scrY, scrX+150, scrY+20),
                          win32con.DT_TOP | win32con.DT_LEFT
                          )
        
        w, h = getWidthHeight(distanceToViewOrigin, stance)
        
        win32gui.Rectangle(hDc, scrX, scrY, scrX-w, scrY-h)


def drawMiniMapBoundary(hDc, lineWidth=2):
    centerX, centerY = 200, 200
    boundaryX, boundaryY = 160, 160
    top, bottom = centerY - boundaryY, centerY + boundaryY
    left, right = centerX - boundaryX, centerX + boundaryX
    hPen = win32gui.CreatePen(win32con.PS_SOLID, lineWidth, COLOR_BLUE)
    win32gui.SelectObject(hDc, hPen)
    win32gui.Rectangle(hDc, left, top, right, bottom)
    drawCrossHair(hDc, centerX, centerY, size=159, lineWidth=2, color=COLOR_BLUE)
    
def drawSoldiersMiniMap(hDc, dataContainer, globalLock, lineWidth=2):
    centerX, centerY = 200, 200
    boundaryX, boundaryY = 160, 160
    top, bottom = centerY - boundaryY, centerY + boundaryY
    left, right = centerX - boundaryX, centerX + boundaryX
    
    globalLock.acquire()
    viewTransform = dataContainer.viewMatrix
    viewForwardVec = dataContainer.viewForwardVec
    globalLock.release()

    for soldier in dataContainer.soldiers:
        globalLock.acquire()
        posVec4 = soldier.posVec4
        isValid = soldier.isValid()
        occl = soldier.occluded
        globalLock.release()

        if not isValid:
            continue
        
        posV = posVec4.multToMat(viewTransform)
        #posV.x *= -1
        if posV.w < 0.001:
            continue
        
        dx = posV.x / posV.w
        cosA = viewForwardVec.dotProduct(vector.Vector4(viewForwardVec.x, 0.0, viewForwardVec.z, 0.0).normalize())
        dy = posV.z / posV.w / abs(cosA)
        
        dx = int(dx / 1.0 + centerX)
        dy = int(dy / 1.0 + centerY)
        
        if dx < left: dx = left
        if dx > right:dx = right
        if dy < top : dy = top
        if dy > bottom:dy = bottom
        
        pColor = COLOR_RED if occl else COLOR_GREEN
        hPen = win32gui.CreatePen(win32con.PS_SOLID, lineWidth, pColor)
        win32gui.SelectObject(hDc, hPen)

        win32gui.Rectangle(hDc, dx, dy, dx+2, dy+2)
         
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
        width, height = 24.0, 32.0
    elif stance == 1:
        width, height = 24.0, 16.0
    elif stance == 2:
        width, height = 24.0, 4.0
    else:
        width, height = 24.0, 32.0
    _f = 20.0 / distant
    width = width * _f
    height = height * _f
    if width < 3:
        width = 3.0
    if height < 3:
        height = 3.0
    return int(width), int(height)