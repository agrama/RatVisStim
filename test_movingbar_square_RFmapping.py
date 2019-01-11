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
                """sync-video #t
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

        self.winsize = 100
        self.x = np.zeros((self.winsize, self.winsize), dtype=np.uint8)
        self.barwidth = 20  # this corresponds to about a 2 deg bar when scale is 0.125
        self.scale = 0.125  # this corresponds to 11.8 deg when monitor is 20 cm from animal but this will divide the 80 deg screen into 10 chunks
        stimcode = []
        for x in np.arange((-0.5 + self.scale/2), (0.5 - self.scale/2 + 0.05), self.scale):
            for y in np.arange((-0.5 + self.scale/2), (0.5 - self.scale/2 + 0.05), self.scale):
                stimcode.append((x, y))
        numtrials = 1
        # self.stimcode = stimcode
        stimcode_ = [item for item in stimcode for i in range(numtrials)]
        # stimcode_ = []
        # rn.seed(2)
        # # self.stimcode = []
        # stim_ind = rn.randint(0, len(stimcode))
        # stimcode_.append(stimcode[stim_ind])
        # stimcode.pop(stim_ind)
        # while len(stimcode) > 1:
        #     stim_ind = rn.randint(0, len(stimcode) - 1)
        #     old_point = stimcode_[-1]
        #     new_point = stimcode[stim_ind]
        #     dist = ((new_point[0] - old_point[0]) ** 2 + (new_point[1] - old_point[1]) ** 2) ** 0.5
        #     while dist < 0.35:
        #         stim_ind = rn.randint(0, len(stimcode) - 1)
        #         new_point = stimcode[stim_ind]
        #         dist = ((new_point[0] - old_point[0]) ** 2 + (new_point[1] - old_point[1]) ** 2) ** 0.5
        #     stimcode_.append(stimcode[stim_ind])
        #     # print(len(stimcode_))
        #     stimcode.pop(stim_ind)
        # stimcode_.append(stimcode[-1])
        self.stimcode = []
        for indx in range(numtrials):
            self.stimcode.extend(stimcode)
        self.numstim = len(self.stimcode)
        self.stimcount = len(self.stimcode)
        print(self.numstim)
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

        self.pivotNode = render.attachNewNode("environ-pivot")
        self.pivotNode.setPos(-self.scale/2 , 0.5, self.scale/2 )
        self.cardnode.wrtReparentTo(self.pivotNode)
        self.cardnode.hide()

        self.taskMgr.add(self.frameFlipper, "frameFlipper")
        # self.cardnode.show()
        self.setBackgroundColor(0.5, 0.5, 0.5)

        self.my_shader = Shader.make(Shader.SLGLSL, my_shader[0], my_shader[1])
        self.randorder = np.arange(0,4)
        rn.shuffle(self.randorder)
        self.cardnode.setShader(self.my_shader)

    def frameFlipper(self, task):
        if task.time % 5 < 1:
            stimcode_dummy = self.stimcode[self.numstim - self.stimcount]
            print(stimcode_dummy)
            # print(np.floor((task.time%5)/0.25))
            # self.cardnode.setPos(0.5-stimcode_dummy[0], 0.5, 0.5-stimcode_dummy[1])
            self.pivotNode.setPos( stimcode_dummy[0], 0.5, stimcode_dummy[1])
            # self.pivotNode.setPos(-self.scale/2 + (stimcode_dummy[0]-0.5), 0.5, self.scale/2 + (stimcode_dummy[1]-0.5) )
            self.pivotNode.setR(self.randorder[int(np.floor((task.time%5)/0.25))]*90)
            self.cardnode.setShaderInput('x_shift', (task.time%5)*4)
            self.cardnode.show()
        if task.time % 6 < 0.005:
            # stimcode_dummy = self.stimcode[self.numstim - self.stimcount]
            # print(stimcode_dummy)
            # print(self.stimcount)
            self.cardnode.hide()
            self.stimcount -= 1
        # else:
        #     # self.cardnode.hide()
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

