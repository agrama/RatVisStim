from math import pi, sin, cos

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.DirectGui import *
import numpy as np
import sys
import random as rn

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
        uniform float x_pos;
        uniform float y_pos;
        uniform float x_scale;
        uniform float y_scale;
        uniform float gauss_sigma;
        uniform float aspect_ratio;

        void main() {
         mat2 rotation = mat2( cos(rot_angle), sin(rot_angle),
                      -sin(rot_angle), cos(rot_angle));
         vec2 texcoord_scaled = vec2(texcoord.x * x_scale, texcoord.y * y_scale);
         vec2 texcoord_rotated = rotation*texcoord_scaled.xy;
         vec2 texcoord_spherical = 
         vec4 color0 = texture(p3d_Texture0, texcoord_rotated);
         color0 = (color0-0.5) * exp(-1* ( pow((texcoord.x - x_pos)*aspect_ratio,2) + pow((texcoord.y - y_pos),2) )/(2*pow(gauss_sigma,2)) ) + 0.5;
         gl_FragColor = color0;
       }
    """
]

loadPrcFileData("",
                """sync-video #t
                fullscreen #t
                win-origin 0 0
                undecorated #t
                cursor-hidden #t
                win-size %d %d
                show-frame-rate-meter #t
                """ % (1920, 1080))


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.accept('escape', sys.exit)
        self.stimcode = []
        for x in np.arange(0, 1.02, 0.2):
            for y in np.arange(0, 1, 0.33):
                for theta in np.arange(0, np.pi/2+0.1, np.pi/2):  # present two orientations
                    self.stimcode.append(
                        (x, y, theta))  # this generates different permutations of x and y and theta values
        rn.seed(10)
        rn.shuffle(self.stimcode)
        self.numstim = len(self.stimcode)
        self.stimcount = len(self.stimcode)

        x = np.linspace(0, 2 * np.pi, 100)
        y = (np.sign(np.sin(x)) + 1) / 2 * 255

        self.tex = Texture("texture")
        self.tex.setMagfilter(Texture.FTLinear)

        self.tex.setup2dTexture(100, 1, Texture.TUnsignedByte, Texture.FLuminance)
        memoryview(self.tex.modify_ram_image())[:] = y.astype(np.uint8).tobytes()

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
        self.scale = 12
        self.cardnode.setShaderInput("x_scale", self.scale * self.getAspectRatio())
        self.cardnode.setShaderInput("aspect_ratio", self.getAspectRatio())
        self.cardnode.setShaderInput("y_scale", self.scale)
        self.cardnode.setShaderInput("gauss_sigma", 0.08)
        # self.cardnode.setShaderInput("rot_angle", 0)
        # self.cardnode.setShaderInput("x_shift", 0)

        self.setBackgroundColor(0.5, 0.5, 0.5)

        self.taskMgr.add(self.frameFlipper, "frameFlipper")
    def frameFlipper(self,task):
        if self.stimcount > 0:
            if task.frame<120:
                return task.cont
            elif (task.frame-120) % 60 == 0:
                stimcode_dummy = self.stimcode[self.numstim - self.stimcount]
                print(stimcode_dummy)
                self.cardnode.setShaderInput("rot_angle", stimcode_dummy[2])
                self.cardnode.setShaderInput("x_pos", stimcode_dummy[0])
                self.cardnode.setShaderInput("y_pos", stimcode_dummy[1])
                self.cardnode.show()
                print(task.frame)
                self.stimcount -= 1
                return task.cont
            elif (task.frame-130) % 60 == 0:
                self.cardnode.hide()
                return task.cont
            return task.cont
        else:
            # self.cardnode.hide()
            return task.cont


if __name__ == "__main__":
    app = MyApp()
    app.run()