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
        stimcode = []
        for x in np.arange(0.0625,1, 0.125):
            for y in np.arange(0.0625,1, 0.125):
                for polarity in np.arange(0, 2):
                    stimcode.append((x, y, 255*polarity))
        # for numtrials = 2 use seed 5
        # for numtrials = 5 use seed 2
        # for numtrials = 10 use seed 2
        numtrials = 5

        # stimcode_ = [item for item in stimcode for i in range(numtrials)]
        stimcode_ = []
        rn.seed(2)
        # self.stimcode = []
        stim_ind = rn.randint(0, len(stimcode))
        stimcode_.append(stimcode[stim_ind])
        stimcode.pop(stim_ind)
        while len(stimcode) > 1:
            stim_ind = rn.randint(0, len(stimcode) - 1)
            old_point = stimcode_[-1]
            new_point = stimcode[stim_ind]
            dist = ((new_point[0] - old_point[0]) ** 2 + (new_point[1] - old_point[1]) ** 2) ** 0.5
            while dist < 0.35:
                stim_ind = rn.randint(0, len(stimcode)-1)
                new_point = stimcode[stim_ind]
                dist = ((new_point[0] - old_point[0]) ** 2 + (new_point[1] - old_point[1]) ** 2) ** 0.5
            stimcode_.append(stimcode[stim_ind])
            # print(len(stimcode_))
            stimcode.pop(stim_ind)
        stimcode_.append(stimcode[-1])
        self.stimcode = []
        for indx in range(numtrials):
            self.stimcode.extend(stimcode_)
        self.numstim = len(self.stimcode)
        self.stimcount = 2#len(self.stimcode)
        print(self.numstim)
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

        self.my_shader = Shader.make(Shader.SLGLSL, my_shader[0], my_shader[1])

        self.cardnode.setShader(self.my_shader)

    def frameFlipper(self, task):
        if self.stimcount > 0:
            if task.frame < 120:
                return task.cont
            elif (task.frame - 120) % 60 == 0:
                stimcode_dummy = self.stimcode[self.numstim - self.stimcount]
                print(stimcode_dummy)
                self.cardnode.setShaderInput("polarity", stimcode_dummy[2])
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

