from math import pi, sin, cos
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
import numpy as np

loadPrcFileData("",
                """sync-video #t
                fullscreen #f
                win-origin 500 500
                undecorated #t
                cursor-hidden #f
                show-frame-rate-meter #t
                win-size %d %d
                """ % (512, 512))
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        # self.disableMouse()
        # sine wave equation: y(t) = A * sin(kx +/- wt + phi) = A * sin(2*pi*x/lambda + 2*pi*f*t + phi)
        self.winsize = 512             #size of the window
        self.img0 = 127*np.ones((self.winsize, self.winsize), dtype=np.uint8)
        self.img1 = 127*np.ones((self.winsize, self.winsize), dtype=np.uint8)
        # self.img0 = self.img0.astype(np.uint8)
        self.x = 0
        self.y = 0
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

        self.taskMgr.add(self.MouseWatcher, "MouseWatcher")

    def MouseWatcher(self, task):
        if self.mouseWatcherNode.hasMouse():
            self.x = int((self.winsize/2)*self.mouseWatcherNode.getMouseY() + (self.winsize/2))
            self.y = int((self.winsize/2)*self.mouseWatcherNode.getMouseX() + (self.winsize/2))
            self.img0[:] = self.img1[:]
            self.img0[self.x:(self.x+10), self.y:(self.y+10)]=0
            memoryview(self.tex0.modify_ram_image())[:] = self.img0.tobytes()

            #
        #self.cardnode0.setShaderInput("time", task.time)
        #self.cardnode1.setShaderInput("time", task.time)

        return task.cont
if __name__ == "__main__":
    app = MyApp()
    app.run()