from ctypes import byref

from ctypes import windll
kernel32 = windll.kernel32

import ctypes
from ctypes import POINTER

from GLHF.libs.datatypes import common
from GLHF.libs.datatypes import matrix
from GLHF.libs.datatypes import vector


class RPMError(Exception):
    def __init__(self, hProcess, address, length, errorCode):
        message = "RPM error: hProcess[%s] addr[0x%X] length[0x%X]. ErrorCode[%s]" % (hProcess, address, length, errorCode)
        super(RPMError, self).__init__(message)


class RPM(object):

    def __init__(self, hProcess, is64Bit=True):
        self.hProcess = hProcess
        self.addressTypeConv = ctypes.c_ulonglong if is64Bit else ctypes.c_uint
        
        self.intBuffer = ctypes.c_int() 
        self.intBufferSize = ctypes.sizeof(self.intBuffer)
        
        self.uintBuffer = ctypes.c_uint()
        self.uintBufferSize = ctypes.sizeof(self.uintBuffer)
        
        self.int64Buffer = ctypes.c_longlong()
        self.int64BufferSize = ctypes.sizeof(self.int64Buffer)
        
        self.uint64Buffer = ctypes.c_ulonglong()
        self.uint64BufferSize = ctypes.sizeof(self.uint64Buffer)
        
        self.floatBuffer = ctypes.c_float()
        self.floatBufferSize = ctypes.sizeof(self.floatBuffer)
        
        self.vec4Buffer = vector.C_VECTOR4()
        self.vec4BufferSize = ctypes.sizeof(self.vec4Buffer)
        
        self.mat4Buffer = matrix.C_MATRIX()
        self.mat4BufferSize = ctypes.sizeof(self.mat4Buffer)
        
        self.str64Buffer = common.STR64()
        self.str64BufferSize = ctypes.sizeof(self.str64Buffer)
        
        self.byteBuffer = ctypes.c_byte()
        self.byteBufferSize = ctypes.sizeof(self.byteBuffer)
        
    def read(self, address, buf, length):
        if not kernel32.ReadProcessMemory(self.hProcess, 
                                          self.addressTypeConv(address),
                                          byref(buf),
                                          length,
                                          None):
            lastErrorCode = kernel32.GetLastError()
            raise RPMError(self.hProcess, address, length, lastErrorCode)
    
    def readInt(self, address):
        self.read(address, self.intBuffer, self.intBufferSize)
        return self.intBuffer.value
    
    def readUInt(self, address):
        self.read(address, self.uintBuffer, self.uintBufferSize)
        return self.uintBuffer.value
    
    def readInt64(self, address):
        self.read(address, self.int64Buffer, self.int64BufferSize)
        return self.int64Buffer.value
    
    def readUInt64(self, address):
        self.read(address, self.uint64Buffer, self.uint64BufferSize)
        return self.uint64Buffer.value
    
    def readFloat(self, address):
        self.read(address, self.floatBuffer, self.floatBufferSize)
        return self.floatBuffer.value
    
    def readVec4Point(self, address):
        self.read(address, self.vec4Buffer, self.vec4BufferSize)
        return self.vec4Buffer.toPyVector4Point()
    
    def readVec4Direction(self, address):
        self.read(address, self.vec4Buffer, self.vec4BufferSize)
        return self.vec4Buffer.toPyVector4Direction()
    
    def readVec4Position(self, address):
        self.read(address, self.vec4Buffer, self.vec4BufferSize)
        return self.vec4Buffer.toPyVector4Point()
        
    def readMat4(self, address):
        self.read(address, self.mat4Buffer, self.mat4BufferSize)
        return self.mat4Buffer.toPyMat4()

    def readStr64(self, address):
        self.read(address, self.str64Buffer, self.str64BufferSize)
        return self.str64Buffer.str
    
    def readByte(self, address):
        self.read(address, self.byteBuffer, self.byteBufferSize)
        return self.byteBuffer.value
    

if __name__ == "__main__":
    hProcess = kernel32.OpenProcess(0x10, False, 5620)
    rrr = RPM(hProcess)
    print rrr.readStr64(0x74BF4030+0x40)
