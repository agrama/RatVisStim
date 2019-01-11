from math import pi, sin, cos

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

        uniform float x_pos;
        uniform float y_pos;
        uniform float polarity;


        void main() {

          float width = 0.025; // this corresponds to ~ 5 deg square on the BenQ monitor when positioned 20 cm from animal
          vec4 color0 = vec4(0.5,0.5,0.5,1);
          if ( (float(abs(texcoord.x-x_pos)) < width) && (float(abs(texcoord.y - y_pos)) < width) ){

                 color0 = vec4(polarity,polarity,polarity,1);

            }
          else{
          vec4 color0 = vec4(0.5,0.5,0.5,1);
          }
          gl_FragColor = color0;
       }
    """
]

loadPrcFileData("",
                """sync-video #f
                fullscreen #f
                win-origin 2340 0
                undecorated #t
                cursor-hidden #t
                win-size %d %d
                show-frame-rate-meter #f
                """ % (1080, 1080))

class MyApp(ShowBase):
    def __init__(self,shared):

        ShowBase.__init__(self)
        self.shared = shared
        self.disableMouse()
        self.accept('escape', self.escapeAction)
        self.tex = Texture("texture")
        self.tex.setMagfilter(Texture.FTLinear)
        x = np.linspace(0, 1, 1000)
        self.tex.setup2dTexture(1000, 1, Texture.TUnsignedByte, Texture.FLuminance)
        memoryview(self.tex.modify_ram_image())[:] = x.astype(np.uint8).tobytes()
        cm = CardMaker('card')

        self.cardnode = self.render.attachNewNode(cm.generate())

        self.lens1 = PerspectiveLens()
        self.lens1.setNearFar(0.01, 100)
        self.lens1.setFov(90, 90)
        self.cam.node().setLens(self.lens1)

        self.cardnode.setPos(-0.5, 0.5, -0.5)

        self.cardnode.setTexture(self.tex)

        self.cardnode.hide()
        self.setBackgroundColor(0.5, 0.5, 0.5)

        self.my_shader = Shader.make(Shader.SLGLSL, my_shader[0], my_shader[1])

        self.cardnode.setShader(self.my_shader)
        self.cardnode.hide()
    def escapeAction(self):
        self.shared.main_programm_still_running.value = 0