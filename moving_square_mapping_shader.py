from math import pi, sin, cos
import random as rn
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.DirectGui import *
import numpy as np
import sys

my_shader = [
    """#version 140

            uniform mat4 p3d_ModelViewProjectionMatrix;
            in vec4 p3d_Vertex;
            in vec2 p3d_MultiTexCoord;
            out vec2 texcoord;

            void main() {
              gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
              texcoord = p3d_MultiTexCoord;
            }
    """,

    """#version 140

        uniform sampler2D p3d_Texture0;
        in vec2 texcoord;
        out vec4 gl_FragColor;

        uniform float x_shift;
        //uniform float y_shift;


        void main() {

          vec2 texcoord_translated = vec2(texcoord.x-x_shift , texcoord.y);
          vec4 color0 = texture(p3d_Texture0, texcoord_translated);
          gl_FragColor = color0;
       }
    """
]

loadPrcFileData("",
                """sync-video #f
                fullscreen #f
                win-origin 2760 0
                undecorated #t
                cursor-hidden #t
                win-size %d %d
                show-frame-rate-meter #f
                """ % (1080, 1080))


class MyApp(ShowBase):
    def __init__(self,shared):
        ShowBase.__init__(self)
        self.accept('escape', self.escapeAction)
        self.shared = shared
        self.winsize = 100
        self.x = np.zeros((self.winsize, self.winsize), dtype=np.uint8)
        self.barwidth = 20  # this corresponds to about a 2 deg bar when scale is 0.125
        self.scale = 0.125  # this corresponds to 11.8 deg when monitor is 20 cm from animal but this will divide the 80 deg screen into 10 chunks
        self.tex = Texture("texture")
        self.tex.setMagfilter(Texture.FTLinear)
        self.tex.setup2dTexture(self.winsize, self.winsize, Texture.TUnsignedByte, Texture.FLuminance)
        self.x[:, 0:self.barwidth] = 255
        memoryview(self.tex.modify_ram_image())[:] = self.x.astype(np.uint8).tobytes()


        cm = CardMaker('card')

        self.cardnode = self.render.attachNewNode(cm.generate())

        self.lens1 = PerspectiveLens()
        self.lens1.setNearFar(0.01, 100)
        self.lens1.setFov(90,90)
        self.cam.node().setLens(self.lens1)

        self.cardnode.setR(270)
        self.cardnode.setPos(0, 0.5, 0)
        self.cardnode.setScale(self.scale)
        self.cardnode.setTexture(self.tex)
        # this is important to rotate the cardnode from its midpoint and not the edge
        self.pivotNode = render.attachNewNode("environ-pivot")
        self.pivotNode.setPos(-self.scale/2 , 0.5, self.scale/2 )
        self.cardnode.wrtReparentTo(self.pivotNode)
        self.cardnode.hide()

        self.setBackgroundColor(0, 0, 0)

        self.my_shader = Shader.make(Shader.SLGLSL, my_shader[0], my_shader[1])

        self.cardnode.setShader(self.my_shader)
        self.win.getGsg().setGamma(1.0)

    def escapeAction(self):
        self.shared.main_programm_still_running.value = 0