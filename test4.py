from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.DirectGui import *
import numpy as np
import sys
import random as rn
import os
loadPrcFileData("",
                """sync-video #f
                fullscreen #f
                win-origin 2340 0
                undecorated #t
                cursor-hidden #t
                win-size %d %d
                show-frame-rate-meter #t
                """ % (1080, 1080))

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.accept('escape', sys.exit)
        path_to_file_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), 'aperture images'))
        onlyfiles = [os.path.join(path_to_file_dir, str(f) + ".tif") for f in range(1, 2)] # load #1-100 tiff files in that order
        self.tex =[]
        for i, file in enumerate(onlyfiles):
            pandafile = Filename.from_os_specific(file)
            print(pandafile)
            self.tex.append(loader.loadTexture(pandafile))
        print(len(self.tex))
        cm = CardMaker('card')

        self.cardnode = self.render.attachNewNode(cm.generate())

        self.lens1 = PerspectiveLens()
        self.lens1.setNearFar(0.01, 100)
        self.lens1.setFov(90, 90)
        self.cam.node().setLens(self.lens1)
        self.cardnode.setPos(-0.5, 0.5, -0.5)
        self.setBackgroundColor(0.5, 0.5, 0.5)
        self.cardnode.setTexture(self.tex[0])
        # self.cardnode.hide()
        # self.taskMgr.add(self.frameFlipper, "frameFlipper")

        self.stimcount = 0
    def frameFlipper(self,task):
        if self.stimcount < 60:
            if task.frame<120:
                return task.cont
            elif (task.frame-120) % 60 == 0:
                self.cardnode.setTexture(self.tex[self.stimcount])
                # print(self.stimcount)
                self.cardnode.show()
                self.stimcount += 1
                return task.cont
            elif (task.frame-130) % 60 == 0:
                self.cardnode.hide()
                return task.cont
            return task.cont
if __name__ == "__main__":
    app = MyApp()
    app.run()