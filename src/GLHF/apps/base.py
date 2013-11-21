import time

from ctypes import windll
kernel32 = windll.kernel32

import win32api
import win32con
import win32gui 

from GLHF import config

import logging
logger = logging.getLogger(__name__)


class OpenProcessError(Exception):
    def __init__(self, pid, flag, errorCode):
        message = "Can not open process, pid[%d] flag[0x%X] ErrorCode[%d]" % (pid, flag, errorCode)
        super(OpenProcessError, self).__init__(message)


class BaseApplication(object):
    
    CONFIG_FILE = ''
    
    EX_WINDOW_STYLE = win32con.WS_EX_TOPMOST|win32con.WS_EX_TRANSPARENT|win32con.WS_EX_LAYERED|win32con.WS_EX_COMPOSITED
    
    WINDOW_STYLE = win32con.WS_POPUP|win32con.WS_VISIBLE
    
    FPS = 60
    
    PROCESS_ALL_ACCESS = 0x0010
        
    def __init__(self, name='', dataContainer=None, globalLock=None):
        self.appName = name
        self.ctn = dataContainer
        self.lock = globalLock
        self.cfg = config.Config.fromFile(self.CONFIG_FILE)
        self.addUserConfig()
        self.renderInterval = 1.0/(self.FPS*2.0)
    
    def addUserConfig(self):
        """
        Client code can implement this method to customize the config structure
        """
        pass
    
    def openProcess(self):
        hProcess = kernel32.OpenProcess(self.PROCESS_ALL_ACCESS, False, self.cfg.pid)
        if not hProcess:
            lastErrorCode = kernel32.GetLastError()
            raise OpenProcessError(self.cfg.pid, self.PROCESS_ALL_ACCESS, lastErrorCode)
        return hProcess
        
    def createWindowClass(self, wndproc, bgColorBrush=win32con.COLOR_WINDOW+1):
        """
        Create and register the window class structure, returning the class atom.
        
        @param wndproc: a dictionary containing the <message: routine> mapping.
                        see scripts\win32gui_demo.py for an example
        @type  wndproc: dict
        
        @return: the class atom
        @rtype : 
        """
        wc = win32gui.WNDCLASS()
        wc.lpszClassName = self.appName
        wc.style = win32con.CS_GLOBALCLASS|win32con.CS_VREDRAW | win32con.CS_HREDRAW
        wc.hbrBackground = bgColorBrush
        wc.lpfnWndProc = wndproc
        classAtom=win32gui.RegisterClass(wc)       
        return classAtom
    
    def createWindow(self, classAtom):
        """
        Create the window, returning the window handle.
        
        @note:
        the most important part is win32gui.SetLayeredWindowAttributes() which keys out the 
        white background leaving only the color pixels
        
        @return: the window handle
        @rtype :
        """       
        hwnd = win32gui.CreateWindowEx(self.EX_WINDOW_STYLE,
                                       classAtom,
                                       self.appName,
                                       self.WINDOW_STYLE,
                                       self.cfg.windowLeft,
                                       self.cfg.windowTop,
                                       self.cfg.windowRight,
                                       self.cfg.windowBottom,
                                       0,
                                       0,
                                       0,
                                       None)

        win32gui.SetLayeredWindowAttributes(hwnd, 
                                            win32api.RGB(255, 255, 255), 
                                            255, 
                                            win32con.LWA_COLORKEY)
        return hwnd
    
    def createWindowClassic(self, classAtom):
        hwnd = win32gui.CreateWindow(classAtom,
                                     "QQ2013 Xmas",
                                     self.WINDOW_STYLE,
                                     self.cfg.windowX,
                                     self.cfg.windowY,
                                     self.cfg.windowWidth,
                                     self.cfg.windowHeight,
                                     0,
                                     0,
                                     0,
                                     None)
        return hwnd
    
    def render(self, hwnd, classAtom):
        try:
            while True:
                win32gui.InvalidateRect(hwnd, None, True)
                win32gui.PumpWaitingMessages()
                time.sleep(self.renderInterval)
        except KeyboardInterrupt:
            logger.info("User has stopped the execution! Closing window and cleaning up.")
        except Exception, e:
            logger.exception(e)
        win32gui.DestroyWindow(hwnd)
        win32gui.UnregisterClass(classAtom, None)