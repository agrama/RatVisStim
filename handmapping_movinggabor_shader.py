from math import pi, sin, cos
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.showbase import DirectObject
from direct.task import Task
import numpy as np
from scipy import signal

my_shader = [
            """#version 140

                    uniform mat4 p3d_ModelViewProjectionMatrix;
                    in vec4 p3d_Vertex;
                    in vec2 p3d_MultiTexCoord0;
                    out vec2 texcoord;

                    void main() {
                      gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
                      texcoord = p3d_MultiTexCoord0;
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
                 vec4 color0 = texture(p3d_Texture0, texcoord_rotated);
                 color0 = (color0-0.5) * exp(-1* ( pow((texcoord.x - x_pos)*aspect_ratio,2) + pow((texcoord.y - y_pos),2) )/(2*pow(gauss_sigma,2)) ) + 0.5;
                 gl_FragColor = color0;
                 }
            """
            ]

loadPrcFileData("",
                """sync-video #f
                fullscreen #f
                win-origin 1920 0
                undecorated #t
                cursor-hidden #f
                win-size %d %d
                show-frame-rate-meter #t
                """ % (1920, 1920))
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.accept('mouse1', self.mouseLeftClick)  #event handler for left mouse click
        self.accept('mouse3', self.mouseRightClick) #event handler for right mouse click
        self.accept('escape', self.escapeAction)
        self.accept('arrow_right', self.ThetaIncrease)
        self.accept('arrow_left', self.ThetaDecrease)
        # self.accept('wheel_up', self.GaborIncrease)
        # self.accept('wheel_down', self.GaborDecrease)
        self.disableMouse()
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
        self.scale = 16 #on the benq monitor at 20 cm from animal, this corresponds to 0.1 cpd
        self.cardnode.setShaderInput("x_scale", self.scale * self.getAspectRatio())
        self.cardnode.setShaderInput("aspect_ratio", self.getAspectRatio())
        self.cardnode.setShaderInput("y_scale", self.scale)
        self.gabor_radius = 0.0588
        self.cardnode.setShaderInput("gauss_sigma", self.gabor_radius)
        self.theta = 0
        self.cardnode.setShaderInput("rot_angle", self.theta)
        # self.cardnode.setShaderInput("rot_angle", 0)
        # self.cardnode.setShaderInput("x_shift", 0)
        self.x = 0
        self.y = 0
        self.setBackgroundColor(0.5, 0.5, 0.5)
        self.drawGreyFlag = 1
        self.taskMgr.add(self.MouseWatcher, "MouseWatcher")
        # self.taskMgr.add(self.contrastReversal, "contrastReversal")


    # change the centre of the Gabor by tracking mouse position
    def MouseWatcher(self, task):
        if self.mouseWatcherNode.hasMouse():
            self.x = self.mouseWatcherNode.getMouseX()
            self.y = self.mouseWatcherNode.getMouseY()
            self.cardnode.setShaderInput("x_pos", 0.5+self.x*0.5)
            self.cardnode.setShaderInput("y_pos", 0.5+self.y*0.5)
        return task.cont
    # change contrast of gratings
    def contrastReversal(self, task):
        if not self.drawGreyFlag:
            self.img0[:, :, 0] = (self.gaussgrating * 127 * signal.square(2* np.pi* task.time)) + 127
            memoryview(self.tex0.modify_ram_image())[:] = self.img0.tobytes()
        return task.cont
    #print mouse position in the window upon left mouse click
    def mouseLeftClick(self):
        if self.drawGreyFlag:
            self.cardnode.show()
            self.drawGreyFlag = 0
        else:
            self.cardnode.hide()
            self.drawGreyFlag = 1
    def mouseRightClick(self):
        print (0.5+self.x*0.5, 0.5+self.y*0.5)
    def escapeAction(self):
        self.destroy()
        self.taskMgr.stop()
    def ThetaIncrease(self):

        self.theta += np.deg2rad(10.0)
        self.cardnode.setShaderInput("rot_angle", self.theta)

    def ThetaDecrease(self):
        self.theta -= np.deg2rad(10)
        self.cardnode.setShaderInput("rot_angle", self.theta)
    def GaborIncrease(self):
        if self.gabor_radius<0.6:
            self.gabor_radius += 0.05
            self.cardnode.setShaderInput("gauss_sigma",self.gabor_radius)
    def GaborDecrease(self):
        if self.gabor_radius>0.1:
            self.gabor_radius -= 0.05
            self.cardnode.setShaderInput("gauss_sigma", self.gabor_radius)


if __name__ == "__main__":
    app = MyApp()
    app.run()
