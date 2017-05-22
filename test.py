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
               uniform float timer;
               //uniform float gabor_radius;

               void main() {
               mat2 rotation = mat2( cos(rot_angle), sin(rot_angle),
                     -sin(rot_angle), cos(rot_angle));


                 //vec2 texcoord_translated = vec2(texcoord.x - x_shift, texcoord.y);
                 vec2 texcoord_scaled = vec2(texcoord.x * x_scale, texcoord.y * y_scale);
                 vec2 texcoord_rotated = rotation*texcoord_scaled.xy;

                 vec4 color0 = texture(p3d_Texture0, texcoord_rotated);
                 color0 = (color0-0.5) * sin(2 * 3.14 * timer ) + 0.5;
                 //float r;
                 //r = sqrt((texcoord.x-0.5)*(texcoord.x-0.5) + (texcoord.y-0.5)*(texcoord.y-0.5));

                 //color0.xy = color0.xy * exp(-(r*r)/(gabor_radius*gabor_radius));


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
       self.accept('escape', sys.exit)
       x = np.linspace(0, 2*np.pi, 1000)
       y = (np.sign(np.sin(x)) + 1)/2 * 255

       self.tex = Texture("texture")
       self.tex.setMagfilter(Texture.FTLinear)

       self.tex.setup2dTexture(1000, 1, Texture.TUnsignedByte, Texture.FLuminance)
       memoryview(self.tex.modify_ram_image())[:] = y.astype(np.uint8).tobytes()


       cm = CardMaker('card')

       self.cardnode = self.render.attachNewNode(cm.generate())

       self.lens1 = PerspectiveLens()
       self.lens1.setNearFar(0.01, 100)
       self.lens1.setFov(90, 90)
       self.cam.node().setLens(self.lens1)

       self.cardnode.setPos(-0.5, 0.5, -0.5)

       self.cardnode.setTexture(self.tex)

       self.taskMgr.add(self.TextureChanger, "TextureChanger")

       self.my_shader = Shader.make(Shader.SLGLSL, my_shader[0], my_shader[1])

       self.cardnode.setShader(self.my_shader)


   def TextureChanger(self, task):

       rot = task.time//3
       scale = 12

       gabor_radius = 1

       self.cardnode.setShaderInput("x_scale", scale*self.getAspectRatio())
       self.cardnode.setShaderInput("y_scale", scale)
       self.cardnode.setShaderInput("rot_angle", np.pi)
       self.cardnode.setShaderInput("x_shift", task.time)
       self.cardnode.setShaderInput("gabor_radius", gabor_radius)
       self.cardnode.setShaderInput("timer", 0.2)
       return task.cont

app = MyApp()
app.run()

