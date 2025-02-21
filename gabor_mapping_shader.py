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
                uniform float rot_angle;
                uniform float x_scale;
                uniform float y_scale;
                uniform float cycles;
                uniform float gauss_sigma;
                uniform float x_pos;
                uniform float y_pos;
                uniform float aspect_ratio;
        
                void main() {
                mat2 rotation = mat2( cos(rot_angle), sin(rot_angle),
                                     -sin(rot_angle), cos(rot_angle));
                  
                  vec2 texcoord_scaled = vec2(texcoord.x * x_scale, texcoord.y * y_scale);
                  vec2 texcoord_rotated = rotation*texcoord_scaled.xy;
                  
                  vec4 color0 = vec4((sign(sin(texcoord_rotated.x*2*3.14*cycles))+1)/2, (sign(sin(texcoord_rotated.x*2*3.14*cycles))+1)/2, (sign(sin(texcoord_rotated.x*2*3.14*cycles))+1)/2,1);
                  if (pow((texcoord.x - x_pos)*aspect_ratio,2) + pow((texcoord.y - y_pos),2) > gauss_sigma ){
                         color0 = vec4(0.5,0.5,0.5,1);
                         }
                  gl_FragColor = color0;
               }
            """
            ]

loadPrcFileData("",
                """sync-video #f
                fullscreen #f
                win-origin 1920 0
                undecorated #t
                cursor-hidden #t
                win-size %d %d
                show-frame-rate-meter #t
                """ % (1920, 1080))

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
        # x = np.linspace(0, 2*np.pi, 100)
        # y = (np.sign(np.sin(x)) + 1)/2 * 255
        #
        # self.tex = Texture("texture")
        # self.tex.setMagfilter(Texture.FTLinear)
        #
        # self.tex.setup2dTexture(100, 1, Texture.TUnsignedByte, Texture.FLuminance)
        # memoryview(self.tex.modify_ram_image())[:] = y.astype(np.uint8).tobytes()


        cm = CardMaker('card')

        self.cardnode = self.render.attachNewNode(cm.generate())

        self.lens1 = PerspectiveLens()
        self.lens1.setNearFar(0.01, 100)
        self.lens1.setFov(90, 90)
        self.cam.node().setLens(self.lens1)

        self.cardnode.setPos(-0.5, 0.5, -0.5)

        self.cardnode.setTexture(self.tex)

        self.my_shader = Shader.make(Shader.SLGLSL, my_shader[0], my_shader[1])

        self.cardnode.setShader(self.my_shader)
        self.cardnode.hide()
        self.scale = 1
        self.cardnode.setShaderInput("x_scale", self.scale * self.getAspectRatio())
        self.cardnode.setShaderInput("y_scale", self.scale)
        self.cardnode.setShaderInput("aspect_ratio", self.getAspectRatio())
        self.gabor_radius = 0.003   # this corresponds to a disc of radius 10 deg
        self.cardnode.setShaderInput("gauss_sigma", self.gabor_radius)
        self.cardnode.setShaderInput("cycles",9)    #this corresponds to 0.1 cpd on benq monitor 20 cm from animal
        self.cardnode.setShaderInput("rot_angle", 0)
        # self.cardnode.setShaderInput("x_shift", 0)

        self.setBackgroundColor(0.5, 0.5, 0.5)

    def escapeAction(self):
        self.shared.main_programm_still_running.value = 0

