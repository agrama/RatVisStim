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
        uniform float x_shift;
        uniform float x_scale;
        uniform float y_scale;

        uniform float gauss_sigma;
        uniform float x_pos;
        uniform float y_pos;
        uniform float aspect_ratio;
        

        void main() {
        mat2 rotation = mat2( cos(rot_angle), sin(rot_angle),
                             -sin(rot_angle), cos(rot_angle));
          
          vec2 texcoord_scaled = vec2(texcoord.x * x_scale, texcoord.y * y_scale);
          vec2 texcoord_rotated = rotation*texcoord_scaled.xy;
          float cycles = 9;
          vec4 color0 = vec4((sign(sin(texcoord_rotated.x*2*3.14*cycles - x_shift))+1)/2, (sign(sin(texcoord_rotated.x*2*3.14*cycles - x_shift))+1)/2, (sign(sin(texcoord_rotated.x*2*3.14*cycles - x_shift))+1)/2,1);
          if (pow((texcoord.x - x_pos)*aspect_ratio,2) + pow((texcoord.y - y_pos),2) > gauss_sigma ){
                 color0 = vec4(0.5,0.5,0.5,1);
                 }
          gl_FragColor = color0;
       }
    """
]

loadPrcFileData("",
                """sync-video #t
                fullscreen #f
                win-origin 1920 0
                undecorated #t
                cursor-hidden #t
                win-size %d %d
                show-frame-rate-meter #t
                """ % (1920, 1080))


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.accept('escape', sys.exit)

        # y = (np.sign(np.sin(x)) + 1)/2 * 255
        self.stimcode = []

        # for an x shift of the centre of the disk by 10 deg, need to chance x_pos by 0.063
        # for an y shift of the centre of the disk by 10 deg, need to chance x_pos by 0.11
        # this was found empirically, and the ratio of this shift comes to 1.77 which is the aspect ratio of the monitor
        # following x and y positions presents a 4x4 grid of 10 deg disks with the grid centre at the centre of the monitor
        for x in np.arange(0.5+ 0.03150-(0.063*2),  0.5+0.0315+ 0.063 + 0.01, 0.063):
            for y in np.arange(0.5+0.055 - (0.11*2),  0.5+0.055 + 0.11 + 0.01, 0.11):
                for theta in np.arange(0, np.pi / 2 + 0.1, np.pi / 2):  # present two orientations
                    self.stimcode.append((x, y, theta))
        self.numstim = len(self.stimcode)
        self.stimcount = len(self.stimcode)

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

        self.taskMgr.add(self.frameFlipper, "frameFlipper")
        self.cardnode.hide()
        self.setBackgroundColor(0.5, 0.5, 0.5)
        self.scale = 1
        self.my_shader = Shader.make(Shader.SLGLSL, my_shader[0], my_shader[1])
        self.cardnode.setShaderInput("x_scale", self.scale * self.getAspectRatio())
        self.cardnode.setShaderInput("y_scale", self.scale)
        self.cardnode.setShaderInput("x_shift", 0)
        self.cardnode.setShaderInput("aspect_ratio", self.getAspectRatio())
        self.gabor_radius = 0.003
        # 0.04 corresponds to a disc of diameter 40 deg
        # 0.12 corresponds to a disc of diameter 20 deg when monitor is 20 cm away from animal
        # 0.003 corresponds to a disc of diameter 10 deg when monitor is 20 cm away from animal
        self.cardnode.setShaderInput("gauss_sigma", self.gabor_radius)
        self.cardnode.setShaderInput("rot_angle", 0)

        self.cardnode.setShader(self.my_shader)

    def frameFlipper(self, task):
        if self.stimcount > 0:
            if task.frame < 120:
                return task.cont
            elif (task.frame - 120) % 60 == 0:
                stimcode_dummy = self.stimcode[self.numstim - self.stimcount]
                print(stimcode_dummy)
                self.cardnode.setShaderInput("rot_angle", stimcode_dummy[2])
                self.cardnode.setShaderInput("x_pos", stimcode_dummy[0])
                self.cardnode.setShaderInput("y_pos", stimcode_dummy[1])
                self.cardnode.show()
                print(task.frame)
                self.stimcount -= 1
                return task.cont
            elif (task.frame - 140) % 60 == 0:
                self.cardnode.hide()
                return task.cont
            return task.cont
        else:
            # self.cardnode.hide()
            return task.cont

            # def TextureChanger(self, task):
            #
            #     scale = 1
            #
            #     gabor_radius = 0.003
            #
            #     #0.04 corresponds to a disc of diameter 40 deg
            #     # 0.12 corresponds to a disc of diameter 20 deg when monitor is 20 cm away from animal
            #     # 0.003 corresponds to a disc of diameter 10 deg when monitor is 20 cm away from animal
            #
            #     self.cardnode.setShaderInput("x_scale", scale*self.getAspectRatio())
            #     self.cardnode.setShaderInput("y_scale", scale)
            #     self.cardnode.setShaderInput("rot_angle", np.deg2rad(180))
            #     self.cardnode.setShaderInput("x_shift", 0)
            #     self.cardnode.setShaderInput("gauss_sigma", gabor_radius)
            #     self.cardnode.setShaderInput("aspect_ratio", self.getAspectRatio())
            #     self.cardnode.setShaderInput("x_pos",0.5)
            #     self.cardnode.setShaderInput("y_pos",0.5)
            #     return task.cont


app = MyApp()
app.run()

