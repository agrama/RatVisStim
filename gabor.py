from math import pi, sin, cos
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
import numpy as np

loadPrcFileData("",
                """sync-video #f
                fullscreen #t
                win-origin 0 0
                undecorated #t
                cursor-hidden #t
                win-size %d %d
                show-frame-rate-meter #f
                """ % (1920, 1080))
class MyApp(ShowBase):
    def __init__(self, shared):

        self.shared = shared
        ShowBase.__init__(self)
        self.disableMouse()
        # sine wave equation: y(t) = A * sin(kx +/- wt + phi) = A * sin(2*pi*x/lambda + 2*pi*f*t + phi)
        self.winsize_x = 1920             #size of the window
        self.winsize_y = 1080
        # self.lamda = 32                 #wavelength
        self.freq = 0.5
        self.sigma = 0.3                 #gaussian standard deviation

        # self.screenimage = np.zeros((1200, 1920, 4)) * 255   # this might be unnecessary , the gaussian might provide all the windowing i need
        self.img0 = np.zeros((self.winsize_y, self.winsize_x))
        self.img1 = np.ones((self.winsize_y, self.winsize_x),dtype=np.uint8)*127

        self.x0 = np.linspace(-float(self.winsize_x) / self.winsize_y, float(self.winsize_x) / self.winsize_y,
                              num=self.winsize_x)
        self.y0 = np.linspace(-1, 1, num=self.winsize_y)
        self.XX, self.YY = np.meshgrid(self.x0, self.y0)
        self.x = 0
        self.y = 0


        self.tex0 = Texture("texture")
        self.tex0.setMagfilter(Texture.FTLinear)
        self.tex0.setup2dTexture(self.img0.shape[1], self.img0.shape[0], Texture.TUnsignedByte, Texture.FLuminance)
        #memoryview(self.tex0.modify_ram_image())[:] = self.img0.tobytes()
        self.drawgrey()

        cm = CardMaker('card')
        self.cardnode = self.render.attachNewNode(cm.generate())
        self.cardnode.setPos(-0.5, 0.5, -0.5)
        self.setBackgroundColor(0.5, 0.5, 0.5, 1)

        self.lens1 = PerspectiveLens()
        self.lens1.setNearFar(0.01, 100)
        self.lens1.setFov(90, 90)
        self.cam.node().setLens(self.lens1)

        ts0 = TextureStage("mapping texture stage0")
        ts0.setSort(0)

        self.cardnode.setTexture(ts0, self.tex0)
        # self.cardnode.setTexRotate(ts0, 30)


    def update_stimulus(self):
        self.XX_theta = self.XX * np.cos(np.deg2rad(self.shared.theta.value))  # proportion of XX for given rotation
        self.YY_theta = self.YY * np.sin(np.deg2rad(self.shared.theta.value))  # proportion of YY for given rotation
        self.XY_theta = self.XX_theta + self.YY_theta  # sum the components
        self.grating = np.sin(2 * pi * self.XY_theta * 10 - 2 * np.pi * self.freq * 0)
        self.gauss = np.exp(-((self.XX - self.x) ** 2 + (self.YY - self.y) ** 2) / (2 * self.sigma ** 2))
        self.gauss = self.gauss * (self.gauss > 0.005)
        self.img0[:, :] = (self.grating * self.gauss * 127) + 127
        # self.img0[:, :, 1] = (self.grating * self.gauss * 127) + 127
        # self.img0[:, :, 2] = (self.grating * self.gauss * 127) + 127
        self.img0 = self.img0.astype(np.uint8)
        memoryview(self.tex0.modify_ram_image())[:] = self.img0.tobytes()
        self.cardnode.setPos(-0.5 + self.shared.x.value * 0.5, 0.5, -0.5 + self.shared.y.value * 0.5)

    def drawgrey(self):
        # self.camera.setHpr(180,0,0)
        memoryview(self.tex0.modify_ram_image())[:] = self.img1.tobytes()


