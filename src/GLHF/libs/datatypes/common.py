import ctypes


class STR16(ctypes.Structure):
    _fields_ = [ ("str", ctypes.c_char * 16)]
    
    
class STR32(ctypes.Structure):
    _fields_ = [ ("str", ctypes.c_char * 32)]


class STR64(ctypes.Structure):
    _fields_ = [ ("str", ctypes.c_char * 64)]


class STR256(ctypes.Structure):
    _fields_ = [ ("str", ctypes.c_byte * 256)]