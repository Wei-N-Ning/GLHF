import ctypes
import math

from GLHF.libs.datatypes import vector


class C_MATRIX(ctypes.Structure):
    
    _fields_ = [("arr", ctypes.c_float * 16)]
    
    def getColumnVector(self, idx):
        """
        If this matrix represents a view matrix, 
        the 1st column vector: right
        the 2nd column vector: up
        the 3rh column vector: forward
        """
        return vector.Vector4(self.arr[4*idx], self.arr[4*idx+1], self.arr[4*idx+2], self.arr[4*idx+3])
    
    def toPyMat4(self):
        return Matrix44(self)
    

class Matrix44(object):
    def __init__(self, cMatrix=None):
        if cMatrix:
            self.data = [element for element in cMatrix.arr]
        else:
            self.data = [0.0 for i in range(16)]
    
    def getColumnVector(self, columnIndex):
        return vector.Vector4(self.data[4*columnIndex], self.data[4*columnIndex+1], self.data[4*columnIndex+2], self.data[4*columnIndex+3])
    
    def get(self, row, column):
        return self.data[4*row+column]
    
    def set(self, row, column, value):
        self.data[4*row+column] = value
        
    def toString(self):
        return '\n'.join([' '.join(["%.3f"%self.get(i,j) for j in range(4)]).ljust(6) for i in range(4)])
    
    def __str__(self):
        return self.toString()
    
    def multTo(self, other):
        result = Matrix44()
        for rowIndex in range(4):
            for columnIndex in range(4):
                element = sum([self.get(rowIndex, k)*other.get(k, columnIndex) for k in range(4)])
                result.set(rowIndex, columnIndex, element)
        return result
    
    def copy(self):
        newMat4 = Matrix44()
        index = 0
        for element in self.data:
            newMat4.data[index] = element
            index += 1
        return newMat4


def getIdMatrix44():
    matrix44 = Matrix44()
    for index in range(4):
        matrix44.set(index, index, 1.0)
    return matrix44

def getViewMatrixFromFirstPersonTransform(firstPersonTransform):
    """
    For BF3/BF4
    
    RPM will read a "matrix" consists the view vectors and the view origin. This function will
    create a real view matrix based on it.
    
    @param firstPersonTransform: the original C_MATRIX
    @type  firstPersonTransform: L{C_MATRIX}
    """
    right = firstPersonTransform.getColumnVector(0)
    up = firstPersonTransform.getColumnVector(1)
    forward = firstPersonTransform.getColumnVector(2)
    position = firstPersonTransform.getColumnVector(3)
    
    viewMatrix = Matrix44()
    
    viewMatrix.set(0, 0, right.x)
    viewMatrix.set(0, 1, up.x)
    viewMatrix.set(0, 2, forward.x)
    viewMatrix.set(0, 3, 0.0)
    
    viewMatrix.set(1, 0, right.y)
    viewMatrix.set(1, 1, up.y)
    viewMatrix.set(1, 2, forward.y)
    viewMatrix.set(1, 3, 0.0)
    
    viewMatrix.set(2, 0, right.z)
    viewMatrix.set(2, 1, up.z)
    viewMatrix.set(2, 2, forward.z)
    viewMatrix.set(2, 3, 0.0)
    
    viewMatrix.set(3, 0, -position.dotProduct(right))
    viewMatrix.set(3, 1, -position.dotProduct(up))
    viewMatrix.set(3, 2, -position.dotProduct(forward))
    viewMatrix.set(3, 3, 1.0)
    
    return viewMatrix

def getViewMatrixFromViewAxisAndPosition(x, y, z, position):
    """
    For IW/COD series
    """
    right = x
    up = y
    forward = z

    viewMatrix = Matrix44()
    
    viewMatrix.set(0, 0, right.x)
    viewMatrix.set(0, 1, up.x)
    viewMatrix.set(0, 2, forward.x)
    viewMatrix.set(0, 3, 0.0)
    
    viewMatrix.set(1, 0, right.y)
    viewMatrix.set(1, 1, up.y)
    viewMatrix.set(1, 2, forward.y)
    viewMatrix.set(1, 3, 0.0)
    
    viewMatrix.set(2, 0, right.z)
    viewMatrix.set(2, 1, up.z)
    viewMatrix.set(2, 2, forward.z)
    viewMatrix.set(2, 3, 0.0)
    
    viewMatrix.set(3, 0, -1.0*position.dotProduct(right))
    viewMatrix.set(3, 1, -1.0*position.dotProduct(up))
    viewMatrix.set(3, 2, -1.0*position.dotProduct(forward))
    viewMatrix.set(3, 3, 1.0)
    
    return viewMatrix