"""
This unit test module requires \testdata\maya\test3dviewtransform.ma
"""

import sys
sys.path.append("D:\\Git\\git\\GLHF\\src")

import os
import unittest

from maya import cmds#@UnresolvedImport, Must be running inside maya,

from GLHF.libs.datatypes import matrix
from GLHF.libs.datatypes import vector
reload(matrix)
reload(vector)


class RefAxis(object):
    """
    Wrap the maya scene refAxis group
    """
    def __init__(self, refAxisGroupName):
        assert cmds.objExists(refAxisGroupName), "Can not find refAxis group!"
        self._orig = "viewOriginRefLocator"
        self._up = "upAxisRefLocator"
        self._right = "rightAxisRefLocator"
        self._forward = "forwardAxisRefLocator"
    
    def _getWSTranslate(self, nodeName):
        """
        cmds.xform(q=True, worldSpace=True, rotatePivot=True)
        
        @return: a list of float values representing the node rotation pivot's translate
        @rtype : list
        """
        originalSelection = cmds.ls(sl=True)
        cmds.select(nodeName, r=True)
        result = cmds.xform(q=True, worldSpace=True, rotatePivot=True)
        if originalSelection:
            cmds.select(originalSelection, r=True)
        else:
            cmds.select(cl=True)
        return result
        
    def _getUpAxis(self):
        origTrans = self._getWSTranslate("viewOriginRefLocator")
        upTrans = self._getWSTranslate("upAxisRefLocator")
        return vector.Vector4(upTrans[0]-origTrans[0],
                              upTrans[1]-origTrans[1],
                              upTrans[2]-origTrans[2],
                              0.0).normalize()
    up = property(_getUpAxis, None)
    
    def _getForwardAxis(self):
        origTrans = self._getWSTranslate("viewOriginRefLocator")
        forwardTrans = self._getWSTranslate("forwardAxisRefLocator")
        return vector.Vector4(forwardTrans[0]-origTrans[0],
                              forwardTrans[1]-origTrans[1],
                              forwardTrans[2]-origTrans[2],
                              0.0).normalize()
    forward = property(_getForwardAxis, None)
    
    def _getRightAxis(self):
        origTrans = self._getWSTranslate("viewOriginRefLocator")
        rightTrans = self._getWSTranslate("rightAxisRefLocator")
        return vector.Vector4(rightTrans[0]-origTrans[0],
                              rightTrans[1]-origTrans[1],
                              rightTrans[2]-origTrans[2],
                              0.0).normalize()
    right = property(_getRightAxis, None)
    
    def _getOrigin(self):
        origTrans = self._getWSTranslate("viewOriginRefLocator")
        return vector.Vector4(origTrans[0], origTrans[1], origTrans[2], 1.0)
    origin = property(_getOrigin, None)
    

class Test3dViewTransform(unittest.TestCase):
    
    TEST_MODULE_PATH = "GLHF.tests"
    TEST_FILE = "tests\\testdata\\maya\\test3dviewtransform.ma"
    
    def setUp(self):
        mod = __import__(self.TEST_MODULE_PATH)
        filePath = os.path.join(os.path.dirname(mod.__file__),
                                self.TEST_FILE)
        cmds.file(filePath, open=True, force=True)
        self.refAxis = RefAxis("refAxis")
    
    def test_1_worldToLocalTransformAssertPositionEqual(self):
        worldPointPos = self._getWorldPointPositionVector()
        worldPointPosTrans = self._getTransformedPosVector(worldPointPos)
        localPointPos = self._getLocalPointPositionVector()
        self._assertVectorsAlmostEqual(worldPointPosTrans, localPointPos)
        
    def _getWorldPointPositionVector(self):
        return vector.Vector4(cmds.getAttr("worldPoint.tx"),
                              cmds.getAttr("worldPoint.ty"),
                              cmds.getAttr("worldPoint.tz"),
                              1.0)
    
    def _getLocalPointPositionVector(self):
        return vector.Vector4(cmds.getAttr("localPoint.tx"),
                              cmds.getAttr("localPoint.ty"),
                              cmds.getAttr("localPoint.tz"),
                              1.0)
    
    def _getViewTransformMatrix(self):
        """
        zaxis = normal(cameraTarget - cameraPosition) --> forward
        xaxis = normal(cross(cameraUpVector, zaxis))  --> right
        yaxis = cross(zaxis, xaxis)                   --> up
        """
        up = self.refAxis.up
        right = self.refAxis.right
        forward = self.refAxis.forward
        origin = self.refAxis.origin
        mat = matrix.Matrix44()
        mat.set(0, 0, right.x); mat.set(0, 1, up.x); mat.set(0, 2, forward.x); mat.set(0, 3, 0.0)
        mat.set(1, 0, right.y); mat.set(1, 1, up.y); mat.set(1, 2, forward.y); mat.set(1, 3, 0.0)
        mat.set(2, 0, right.z); mat.set(2, 1, up.z); mat.set(2, 2, forward.z); mat.set(2, 3, 0.0)
        mat.set(3, 0, -right.dotProduct(origin))
        mat.set(3, 1, -up.dotProduct(origin))
        mat.set(3, 2, -forward.dotProduct(origin))
        mat.set(3, 3, 1.0)
        return mat
    
    def _getTransformedPosVector(self, worldPointPos):
        viewTransformMatrix = self._getViewTransformMatrix()
        worldPointPosTrans = worldPointPos.postmultTransposed(viewTransformMatrix)
        
        # righthanded system !!!!!!
        worldPointPosTrans.z *= -1
        
        return worldPointPosTrans
        
    def _assertVectorsAlmostEqual(self, vec1, vec2):
        self.assertAlmostEqual(vec1.x, vec2.x, places=8)
        self.assertAlmostEqual(vec1.y, vec2.y, places=8)
        self.assertAlmostEqual(vec1.z, vec2.z, places=8)
        self.assertAlmostEqual(vec1.w, vec2.w, places=8)

    def test_2_worldToLocalTransformWhileMoving(self):
        self._moveLocalSystem()
        self._moveWorldPoint()
        worldPointPos = self._getWorldPointPositionVector()
        worldPointPosTrans = self._getTransformedPosVector(worldPointPos)
        localPointPos = self._getLocalPointPositionVector()
        self._assertVectorsAlmostEqual(worldPointPosTrans, localPointPos)
        
    def _moveLocalSystem(self):
        cmds.setAttr("localSystem.translate", 3.843, -2.957, -1.618)
        cmds.setAttr("localSystem.rotate", 158.204, -29.985, -179.493)
        
    def _moveWorldPoint(self):
        cmds.select("localPoint", r=True)
        newPos = cmds.xform(q=True, worldSpace=True, rotatePivot=True)
        cmds.setAttr("worldPoint.translate", newPos[0], newPos[1], newPos[2])



        
"""
import sys
sys.path.append("D:\\Git\\git\\GLHF\\src\\GLHF\\tests")
import test_3dviewtransform as mm
reload(mm)
mm.runInMaya()
"""
def runInMaya():
    testSuites = [unittest.makeSuite(Test3dViewTransform),]
    runner = unittest.TextTestRunner(verbosity=2)
    for testSuite in testSuites:
        runner.run(testSuite)

    
        