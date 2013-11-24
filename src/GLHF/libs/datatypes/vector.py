import ctypes
import math


class C_VECTOR3(ctypes.Structure):

    _fields_ = [ 
                ("x", ctypes.c_float),
                ("y", ctypes.c_float),
                ("z", ctypes.c_float)
               ]
    
    def toPyVector4Point(self):
        return Vector4(self.x, self.y, self.z, 1.0)
    
    def toPyVector4Direction(self):
        return Vector4(self.x, self.y, self.z, 0.0)
    

class C_VECTOR4(ctypes.Structure):

    _fields_ = [ ("x", ctypes.c_float),
                 ("y", ctypes.c_float),
                 ("z", ctypes.c_float),
                 ("w", ctypes.c_float) ]
    
    def toPyVector4Point(self):
        return Vector4(self.x, self.y, self.z, 1.0)
    
    def toPyVector4Direction(self):
        return Vector4(self.x, self.y, self.z, 0.0)


class Vector4(object):
    def __init__(self, x=0.0, y=0.0, z=0.0, w=0.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w
        self._length = None
    
    def swapYZ(self):
        """
        this is a hacky patch for COD games where y and z axis appears to be swapped
        """
        temp = self.y
        self.y = self.z
        self.z = temp
    
    def __str__(self):
        return "Vec4<%.03f, %.03f, %.03f, %.03f>" % (self.x, self.y, self.z, self.w)
    
    def multToMat(self, mat):
        """
        @deprecated: use premult() -> row_vector * mat (D3D)
                         or
                         postmult() -> mat * col_vector (OpenGL)
        """
        nx = self.x*mat.get(0,0) + self.y*mat.get(1,0) + self.z*mat.get(2,0) + self.w*mat.get(3,0)
        ny = self.x*mat.get(0,1) + self.y*mat.get(1,1) + self.z*mat.get(2,1) + self.w*mat.get(3,1)
        nz = self.x*mat.get(0,2) + self.y*mat.get(1,2) + self.z*mat.get(2,2) + self.w*mat.get(3,2)
        nw = self.x*mat.get(0,3) + self.y*mat.get(1,3) + self.z*mat.get(2,3) + self.w*mat.get(3,3)
        return Vector4(nx, ny, nz, nw)
    
    def premult(self, mat):
        """
        row_vector * matrix
        
        row-column
        
        @note: be careful, some online texts and some books ignore the fact that OpenGL uses 
               column major Matrix - that is, the matrix sent to the postmult operation is actually
               the transpose of the one in the mathematical equation!
        """
        nx = self.x * mat.get(0, 0) + self.y * mat.get(1, 0) + self.z * mat.get(2, 0) + self.w * mat.get(3, 0) 
        ny = self.x * mat.get(0, 1) + self.y * mat.get(1, 1) + self.z * mat.get(2, 1) + self.w * mat.get(3, 1) 
        nz = self.x * mat.get(0, 2) + self.y * mat.get(1, 2) + self.z * mat.get(2, 2) + self.w * mat.get(3, 2) 
        nw = self.x * mat.get(0, 3) + self.y * mat.get(1, 3) + self.z * mat.get(2, 3) + self.w * mat.get(3, 3) 
        return Vector4(nx, ny, nz, nw)
    
    def premultTransposed(self, mat):
        nx = self.x * mat.get(0, 0) + self.y * mat.get(0, 1) + self.z * mat.get(0, 2) + self.w * mat.get(0, 3) 
        ny = self.x * mat.get(1, 0) + self.y * mat.get(1, 1) + self.z * mat.get(1, 2) + self.w * mat.get(1, 3) 
        nz = self.x * mat.get(2, 0) + self.y * mat.get(2, 1) + self.z * mat.get(2, 2) + self.w * mat.get(2, 3) 
        nw = self.x * mat.get(3, 0) + self.y * mat.get(3, 1) + self.z * mat.get(3, 2) + self.w * mat.get(3, 3) 
        return Vector4(nx, ny, nz, nw)
    
    def postmult(self, mat, transposed=False):
        """
        matrix * column_vector
        
        row-column
        """
        nx = mat.get(0, 0) * self.x + mat.get(0, 1) * self.y + mat.get(0, 2) * self.z + mat.get(0, 3) * self.w 
        ny = mat.get(1, 0) * self.x + mat.get(1, 1) * self.y + mat.get(1, 2) * self.z + mat.get(1, 3) * self.w 
        nz = mat.get(2, 0) * self.x + mat.get(2, 1) * self.y + mat.get(2, 2) * self.z + mat.get(2, 3) * self.w 
        nw = mat.get(3, 0) * self.x + mat.get(3, 1) * self.y + mat.get(3, 2) * self.z + mat.get(3, 3) * self.w 
        return Vector4(nx, ny, nz, nw)
    
    def postmultTransposed(self, mat):
        nx = mat.get(0, 0) * self.x + mat.get(1, 0) * self.y + mat.get(2, 0) * self.z + mat.get(3, 0) * self.w 
        ny = mat.get(0, 1) * self.x + mat.get(1, 1) * self.y + mat.get(2, 1) * self.z + mat.get(3, 1) * self.w 
        nz = mat.get(0, 2) * self.x + mat.get(1, 2) * self.y + mat.get(2, 2) * self.z + mat.get(3, 2) * self.w 
        nw = mat.get(0, 3) * self.x + mat.get(1, 3) * self.y + mat.get(2, 3) * self.z + mat.get(3, 3) * self.w 
        return Vector4(nx, ny, nz, nw)
        
    def length(self):
        if self._length == None:
            self._length = math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z + self.w*self.w)
        return self._length
        
    def dotProduct(self, dot):
        return self.x*dot.x + self.y*dot.y + self.z*dot.z + self.w*dot.w;
    
    def multScalar(self, multiplier):
        return Vector4(self.x * multiplier, self.y * multiplier, self.z * multiplier, self.w * multiplier)

    def normalize(self):
        length = self.length()
        nx = self.x/length
        ny = self.y/length
        nz = self.z/length
        nw = self.w/length
        result = Vector4(nx, ny, nz, nw)
        result._length = 1.0
        return result
    
    def __add__(self, other):
        return Vector4(self.x+other.x, self.y+other.y, self.z+other.z, self.w+other.w)
    
    def __sub__(self, other):
        return Vector4(self.x-other.x, self.y-other.y, self.z-other.z, self.w-other.w)
    
    def copy(self):
        return Vector4(self.x, self.y, self.z, self.w)

    def distanceTo(self, other):
        return (self - other).length()
        

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
    
    def __sub__(self, other):
        return Vector2D(self.x-other.x, self.y-other.y)
    
    def __str__(self):
        return "Vec2D<%.03f, %.03f>" % (self.x, self.y)