from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
import sys
import os
loadPrcFileData("",
                """sync-video #t
                fullscreen #t
                win-origin 0 0
                undecorated #t
                cursor-hidden #t
                win-size %d %d
                show-frame-rate-meter #t
                """ % (1024, 768))

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.accept('escape', sys.exit)
        path_to_file_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), 'lowPass'))
        onlyfiles = [os.path.join(path_to_file_dir, str(f) + ".tif") for f in range(1, 100)] # load #1-100 tiff files in that order
        self.tex =[]
        for i, file in enumerate(onlyfiles):
            pandafile = Filename.from_os_specific(file)
            self.tex.append(loader.loadTexture(pandafile))

        cm = CardMaker('card')

        self.cardnode = self.render.attachNewNode(cm.generate())

        self.lens1 = PerspectiveLens()
        self.lens1.setNearFar(0.01, 100)
        self.lens1.setFov(90, 90)
        self.cam.node().setLens(self.lens1)
        self.cardnode.setPos(-0.5, 0.5, -0.5)
        self.setBackgroundColor(0.5, 0.5, 0.5)
        # self.cardnode.setTexture(self.tex[0])
        self.cardnode.hide()
