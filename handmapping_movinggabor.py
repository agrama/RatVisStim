from math import pi, sin, cos
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.showbase import DirectObject
from direct.task import Task
import numpy as np
from scipy import signal

loadPrcFileData("",
                """sync-video #t
                fullscreen #t
                win-origin 0 0
                undecorated #t
                cursor-hidden #f
                win-size %d %d
                show-frame-rate-meter #t
                """ % (1920, 1200))
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.accept('mouse1', self.mouseLeftClick)  #event handler for left mouse click
        self.accept('mouse3', self.mouseRightClick) #event handler for right mouse click
        self.accept('escape', self.escapeAction)
        self.disableMouse()
        # sine wave equation: y(t) = A * sin(kx +/- wt + phi) = A * sin(2*pi*x/lambda + 2*pi*f*t + phi)
        self.winsize_x = 1920  # size of the window
        self.winsize_y = 1200
        self.lamda = 32                 #wavelength
        self.freq = 0.5
        self.theta = np.deg2rad(0)     #rotation angle in radians
        self.sigma = 0.3                 #gaussian standard deviation

        # self.screenimage = np.zeros((1200, 1920, 4)) * 255   # this might be unnecessary , the gaussian might provide all the windowing i need
        self.img0 = np.zeros((self.winsize_y, self.winsize_x))
        self.img1 = np.ones((self.winsize_y, self.winsize_x), dtype=np.uint8) * 127
        self.img2 = np.zeros((self.winsize_y, self.winsize_x)).astype(np.uint8)
        self.drawGreyFlag = 0


        t = 0
        self.x0 = np.linspace(-float(self.winsize_x)/self.winsize_y, float(self.winsize_x)/self.winsize_y, num=self.winsize_x)
        self.y0 = np.linspace(-1, 1, num=self.winsize_y)
        self.XX, self.YY = np.meshgrid(self.x0, self.y0)
        self.XX_theta = self.XX * np.cos(self.theta)  # proportion of XX for given rotation
        self.YY_theta = self.YY * np.sin(self.theta)  # proportion of YY for given rotation
        self.XY_theta = self.XX_theta + self.YY_theta  # sum the components
        self.gauss = np.exp(- ((self.XX ** 2) + (self.YY ** 2)) / (2 * self.sigma ** 2))
        self.gauss = self.gauss * (self.gauss > 0.005)
        self.grating = signal.square(2 * pi * self.XY_theta * 10 - 2 * np.pi * self.freq * t)
        self.gaussgrating = self.grating * self.gauss
        self.img0[:, :] = (self.gaussgrating * 127) + 127

        # self.img0[:, :, 1] = (self.grating * self.gauss * 127) + 127
        # self.img0[:, :, 2] = (self.grating * self.gauss * 127) + 127
        self.img0 = self.img0.astype(np.uint8)

        self.tex0 = Texture("texture")
        self.tex0.setMagfilter(Texture.FTLinear)
        self.tex0.setup2dTexture(self.img0.shape[1], self.img0.shape[0], Texture.TUnsignedByte, Texture.FLuminance)
        memoryview(self.tex0.modify_ram_image())[:] = self.img0.tobytes()

        cm = CardMaker('card')
        self.cardnode = self.render.attachNewNode(cm.generate())
        self.cardnode.setPos(-0.5, 0.5, -0.5)

        self.lens1 = PerspectiveLens()
        self.lens1.setNearFar(0.01, 100)
        self.lens1.setFov(90, 90)
        self.cam.node().setLens(self.lens1)

        ts0 = TextureStage("mapping texture stage0")
        ts0.setSort(0)

        self.cardnode.setTexture(ts0, self.tex0)
        self.setBackgroundColor(0.5, 0.5, 0.5, 1)

        self.taskMgr.add(self.MouseWatcher, "MouseWatcher")
        self.taskMgr.add(self.contrastReversal, "contrastReversal")

    # change the centre of the Gabor by tracking mouse position
    def MouseWatcher(self, task):
        if self.mouseWatcherNode.hasMouse():
            self.x = self.mouseWatcherNode.getMouseX()
            self.y = self.mouseWatcherNode.getMouseY()
            self.cardnode.setPos(-0.5+self.x*0.5, 0.5, -0.5+self.y*0.5)

            # self.gauss = np.exp(-((self.XX-self.x)**2 + (self.YY-self.y)**2) / (2 * self.sigma**2))
            # self.gauss = self.gauss * (self.gauss > 0.005)
            # self.img0[:, :, 0] = (self.grating * self.gauss * 127) + 127
            # self.img0[:, :, 1] = (self.grating * self.gauss * 127) + 127
            # self.img0[:, :, 2] = (self.grating * self.gauss * 127) + 127
            # self.img0 = self.img0.astype(np.uint8)
            # memoryview(self.tex0.modify_ram_image())[:] = self.img0.tobytes()
        return task.cont
    # change contrast of gratings
    def contrastReversal(self, task):
        if not self.drawGreyFlag:
            self.img0[:, :] = (self.gaussgrating * 127 * np.cos(2* np.pi* task.time/4)) + 127
            memoryview(self.tex0.modify_ram_image())[:] = self.img0.tobytes()
        return task.cont
    #print mouse position in the window upon left mouse click
    def mouseLeftClick(self):
        if self.drawGreyFlag:
            # memoryview(self.tex0.modify_ram_image())[:] = self.img0.tobytes()
            self.drawGreyFlag = 0
        else:
            memoryview(self.tex0.modify_ram_image())[:] = self.img1.tobytes()
            self.drawGreyFlag = 1
    def mouseRightClick(self):
        print (self.x, self.y)
    def escapeAction(self):
        self.destroy()
        self.taskMgr.stop()

if __name__ == "__main__":
    app = MyApp()
    app.run()
