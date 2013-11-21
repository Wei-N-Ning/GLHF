import sys
sys.path.append("D:\Git\git\GLHF\src")

import math


class Vector2D(object):
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def multToMat(self, mat):
        newX = self.x * mat.get(0, 0) + self.y * mat.get(1, 0)
        newY = self.x * mat.get(1, 0) + self.y * mat.get(1, 1)
        return Vector2D(newX, newY)
    
    def multByMat(self, mat):
        newX = self.x * mat.get(0, 0) + self.y * mat.get(0, 1)
        newY = self.x * mat.get(1, 0) + self.y * mat.get(1, 1)
        return Vector2D(newX, newY)
    
    def __str__(self):
        return "Vec2D<%.03f, %.03f>" % (self.x, self.y)
    

class Matrix2D(object):
    
    def __init__(self):
        self._data = [0.0, 0.0, 0.0, 0.0]
        
    def get(self, row, column):
        return self._data[row * 2 + column]
    
    def set(self, row, column, value):
        self._data[row * 2 + column] = value
        
    @staticmethod
    def fromRotation(rad):
        """
        To transform a point to the new position in the system
        """
        mat = Matrix2D()
        mat.set(0, 0, math.cos(rad))
        mat.set(0, 1, -math.sin(rad))
        mat.set(1, 0, math.sin(rad))
        mat.set(1, 1, math.cos(rad))
        return mat
    
    @staticmethod
    def fromRotationInverse(rad):
        """
        To transform a point in the system back to the world system
        """
        mat = Matrix2D()
        mat.set(0, 0, math.cos(rad))
        mat.set(0, 1, math.sin(rad))
        mat.set(1, 0, -math.sin(rad))
        mat.set(1, 1, math.cos(rad))
        return mat
    
    def toString(self):
        return '\n'.join([' '.join(["%.3f"%self.get(i,j) for j in range(2)]).ljust(6) for i in range(2)]) 
    
    def __str__(self):
        return self.toString()
    

if __name__ == "__main__":
    # to transform point2D_2 to the position of point2D_1
    rad = math.radians(40.838)
    mat = Matrix2D.fromRotation(rad)
    vec2d = Vector2D(1.5, 2.0)
    newVec2d = vec2d.multByMat(mat)
    print newVec2d
    
    # to transform point2D_3 to the new position (the system does not move, the point does)
    rad = math.radians(30)
    mat = Matrix2D.fromRotationInverse(rad)
    vec2d = Vector2D(1.5, 2.0)
    newVec2d = vec2d.multByMat(mat)
    print newVec2d