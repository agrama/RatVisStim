from math import pi, sin, cos
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
import numpy as np

motion_shader = [
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
                in float rot_angle;
                uniform mat2 rotation = mat2( cos(rot_angle/4.0), sin(rot_angle/4.0),
                                          -sin(rot_angle/4.0), cos(rot_angle/4.0));
                uniform sampler2D p3d_Texture0;
                uniform sampler2D p3d_Texture1;
                in vec2 texcoord;
                out vec4 gl_FragColor;

                void main() {
                  vec4 color0;
                  //if (mod(int(texcoord.y*2160)/8, 2) == 0) {
                  color0 = texture(p3d_Texture0, rotation*texcoord.xy);
                  gl_FragColor = color0;
                    //gl_FragColor.r = color0.r;
                    //gl_FragColor.g = 0;
                    //gl_FragColor.b = 0;
                    //gl_FragColor.a = 1;
                  //}
                  //else
                  //{ color0 = texture(p3d_Texture1, texcoord);
                  //gl_FragColor = color0;
                    //gl_FragColor.r = 0;
                    //gl_FragColor.g = color0.g;
                    //gl_FragColor.b = 0;
                    //gl_FragColor.a = 1;
                  //}

               }
            """
            ]

loadPrcFileData("",
                """sync-video #t
                fullscreen #f
                win-origin 500 500
                undecorated #t
                cursor-hidden #t
                show-frame-rate-meter #t
                win-size %d %d
                """ % (512, 512))
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        # sine wave equation: y(t) = A * sin(kx +/- wt + phi) = A * sin(2*pi*x/lambda + 2*pi*f*t + phi)
        self.winsize = 512             #size of the window
        self.lamda = 64                 #wavelength
        self.freq = 0.5
        self.theta = np.deg2rad(0)     #rotation angle in radians
        self.sigma = 0.1                 #gaussian standard deviation

        # self.screenimage = np.zeros((1200, 1920, 4)) * 255   # this might be unnecessary , the gaussian might provide all the windowing i need
        self.img0 = np.zeros((self.winsize, self.winsize, 3))

        t = 0
        self.x0 = np.linspace(-1, 1, num=self.winsize)
        self.XX, self.YY = np.meshgrid(self.x0, self.x0)
        self.gauss = np.exp( - ((self.XX**2) + (self.YY**2)) / (2 * self.sigma**2))
        self.img0[:, :, 0] = ((np.sin((2 * pi * self.XX * self.winsize) / self.lamda - 2 * np.pi * self.freq * t) * 127) + 127) * self.gauss
        self.img0[:, :, 1] = ((np.sin((2 * pi * self.XX * self.winsize) / self.lamda - 2 * np.pi * self.freq * t) * 127) + 127) * self.gauss
        self.img0[:, :, 2] = ((np.sin((2 * pi * self.XX * self.winsize) / self.lamda - 2 * np.pi * self.freq * t) * 127) + 127) * self.gauss
        self.img0 = self.img0.astype(np.uint8)

        self.tex0 = Texture("texture")
        self.tex0.setMagfilter(Texture.FTLinear)
        self.tex0.setup2dTexture(self.img0.shape[1], self.img0.shape[0], Texture.TUnsignedByte, Texture.FRgb)
        memoryview(self.tex0.modify_ram_image())[:] = self.img0.tobytes()


    #     # self.img1[0, :, 0] = (np.sin(x0 * 2 * np.pi / 30) + 1) * 127
    #     # self.img1[0, :, 1] = (np.sin(x0 * 2 * np.pi / 30) + 1) * 127
    #     # self.img1[0, :, 2] = (np.sin(x0 * 2 * np.pi / 30) + 1) * 127
    #     #
    #     #
    #     # self.img1 = self.img1.astype(np.uint8)
    #     # self.tex1 = Texture("texture")
    #     # self.tex1.setMagfilter(Texture.FTLinear)
    #     # self.tex1.setup2dTexture(self.img1.shape[1], self.img1.shape[0], Texture.TUnsignedByte, Texture.FRgba32)
    #     # memoryview(self.tex1.modify_ram_image())[:] = self.img1.tobytes()
    #
    #     # self.tex0 = loader.loadTexture("abhi_f.jpg")
    #     # self.tex1 = loader.loadTexture("test.jpg")
    #
    #     # memoryview(self.tex0.modify_ram_image())[:] = self.img0.tobytes()
    #
        cm = CardMaker('card')
    #
        self.cardnode = self.render.attachNewNode(cm.generate())
    #
    #
        self.lens1 = PerspectiveLens()
        self.lens1.setNearFar(0.01, 100)
        self.lens1.setFov(90, 90)
        self.cam.node().setLens(self.lens1)

        self.cardnode.setPos(-0.5, 0.5, -0.5)

    #     self.mapping_shader = Shader.make(Shader.SLGLSL, motion_shader[0], motion_shader[1])
    #
        ts0 = TextureStage("mapping texture stage0")
        ts0.setSort(0)

    #     # ts1 = TextureStage("mapping texture stage1")
    #     # ts1.setSort(1)
    #
    #
        self.cardnode.setTexture(ts0, self.tex0)
    #     # self.cardnode.setTexture(ts1, self.tex1)
    #
    #     self.cardnode.setShader(self.mapping_shader)
    #     self.cardnode.setShaderInput("rot_angle", np.pi/4)
    #
    #
    #
    #     #self.taskMgr.add(self.TextureChanger, "TextureChanger")
    #
    #
    #
    # def TextureChanger(self, task):
    #
    #     #self.cardnode0.setShaderInput("time", task.time)
    #     #self.cardnode1.setShaderInput("time", task.time)
    #
    #     return task.cont
if __name__ == "__main__":
    app = MyApp()
    app.run()