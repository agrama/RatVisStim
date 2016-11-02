from math import pi, sin, cos
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.showbase import DirectObject
from direct.task import Task
import numpy as np

loadPrcFileData("",
                """sync-video #t
                fullscreen #f
                win-origin 500 500
                undecorated #t
                cursor-hidden #f
                win-size %d %d
                """ % (1024, 1024))
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.accept('mouse1', self.mouseClick)  #event handler for left mouse click
        self.disableMouse()
        # sine wave equation: y(t) = A * sin(kx +/- wt + phi) = A * sin(2*pi*x/lambda + 2*pi*f*t + phi)
        self.winsize = 1024             #size of the window
        self.lamda = 32                 #wavelength
        self.freq = 0.5
        self.theta = np.deg2rad(0)     #rotation angle in radians
        self.sigma = 0.1                 #gaussian standard deviation

        # self.screenimage = np.zeros((1200, 1920, 4)) * 255   # this might be unnecessary , the gaussian might provide all the windowing i need
        self.img0 = np.zeros((self.winsize, self.winsize, 3))

        t = 0
        self.x0 = np.linspace(-1, 1, num=self.winsize)
        self.XX, self.YY = np.meshgrid(self.x0, self.x0)
        self.XX_theta = self.XX * np.cos(self.theta)  # proportion of XX for given rotation
        self.YY_theta = self.YY * np.sin(self.theta)  # proportion of YY for given rotation
        self.XY_theta = self.XX + self.YY  # sum the components
        self.gauss = np.exp(- ((self.XX ** 2) + (self.YY ** 2)) / (2 * self.sigma ** 2))
        self.gauss = self.gauss * (self.gauss > 0.005)
        self.grating = np.sin((2 * pi * self.XY_theta * self.winsize) / self.lamda - 2 * np.pi * self.freq * t)
        self.img0[:, :, 0] = (self.grating * self.gauss * 127) + 127
        self.img0[:, :, 1] = (self.grating * self.gauss * 127) + 127
        self.img0[:, :, 2] = (self.grating * self.gauss * 127) + 127
        self.img0 = self.img0.astype(np.uint8)

        self.tex0 = Texture("texture")
        self.tex0.setMagfilter(Texture.FTLinear)
        self.tex0.setup2dTexture(self.img0.shape[1], self.img0.shape[0], Texture.TUnsignedByte, Texture.FRgb)
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
    #print mouse position in the window upon left mouse click
    def mouseClick(self):
        print (self.x, self.y)


if __name__ == "__main__":
    app = MyApp()
    app.run()