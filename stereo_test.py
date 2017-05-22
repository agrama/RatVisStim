from math import pi, sin, cos

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.DirectGui import *
import numpy as np
import sys

loadPrcFileData("",
               """sync-video #t
               fullscreen #t
               win-origin 0 0
               undecorated #t
               cursor-hidden #t
               win-size %d %d
               show-frame-rate-meter #t
               framebuffer-stereo 1
               """ % (1920, 1080))

class MyApp(ShowBase):
   def __init__(self):
       ShowBase.__init__(self)
       self.window = self.openWindow()
       print(self.window.isStereo())
       self.displayRegion = self.window.makeDisplayRegion()
       self.displayRegion.setCamera(self.camera)
       
       # Load the environment model.
       # self.displayRegion = self.window.makeDisplayRegion()
       # self.camNode = Camera('cam')
       # self.camNP = NodePath(self.camNode)
       # self.displayRegion.setCamera(self.camNP)
       # self.camNP.reparentTo(self.camera)


app = MyApp()
app.run()

