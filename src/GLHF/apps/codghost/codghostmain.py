import threading

import win32api
import win32con
import win32gui

from GLHF.apps import base

import codghostdatafeeder
import codghostdatatypes
import codghostdrawing

import logging
logger = logging.getLogger(__name__)


class CODGhostApplication(base.BaseApplication):
    CONFIG_FILE = "D:\\temp\\codghost_appinfo_dump.cfg"
    def addUserConfig(self):
        # for classic window
        self.cfg.windowX = 1460
        self.cfg.windowY = 0
        self.cfg.windowWidth = 460
        self.cfg.windowHeight = 900
        # for ex window
        self.cfg.windowLeft = 1460
        self.cfg.windowRight = 460
        self.cfg.windowTop = 0
        self.cfg.windowBottom = 900

        
globalLock = threading.Lock()
container = codghostdatatypes.DataContainer()
app = CODGhostApplication("QQ2013 Plus", container, globalLock)
feeder = codghostdatafeeder.CODGhostDataFeeder(app)


def onPaint(hwnd, msg, wp, lp):
    hDc, ps=win32gui.BeginPaint(hwnd)
    win32gui.SetGraphicsMode(hDc, win32con.GM_ADVANCED)
    
    codghostdrawing.drawSoldiers(hDc, container, globalLock)
    
    win32gui.EndPaint(hwnd, ps)
    return 0
wndproc = {win32con.WM_PAINT:onPaint}


def main():
    hProcess = app.openProcess()
    feeder.initializeRPM(hProcess)
    feederThread = threading.Thread(target=feeder.run)
    feederThread.start()
    
    # 1 for grey, 2 for black, 7 for dark grey (better)
    classAtom = app.createWindowClass(wndproc, 6)
    hwnd = app.createWindow(classAtom)
    app.render(hwnd, classAtom)

    globalLock.acquire()
    app.cfg.killed = True
    globalLock.release()

    # clean up
    logger.info("Waiting for the feeder thread to close...")
    feederThread.join()
    logger.info("Application terminates.")


if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.DEBUG)
    main()