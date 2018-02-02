from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
import sys
import os

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
                uniform float gabor_radius;
                uniform float aspect_ratio;
                uniform int aperture_toggle;

                void main() {
                 vec4 color0 = texture(p3d_Texture0, texcoord);
                 if (aperture_toggle == 1){
                     if (pow((texcoord.x - x_pos)*aspect_ratio,2) + pow((texcoord.y - y_pos),2) > gabor_radius ){
                            color0 = vec4(0.5,0.5,0.5,1);
                            }
                 }
                 if(aperture_toggle == 2){
                    if (pow((texcoord.x - x_pos)*aspect_ratio,2) + pow((texcoord.y - y_pos),2) < gabor_radius ){
                            color0 = vec4(0.5,0.5,0.5,1);
                            }
                 }
                 gl_FragColor = color0;
               }
            """
            ]
loadPrcFileData("",
                """sync-video #f
                fullscreen #t
                win-origin 0 0
                undecorated #t
                cursor-hidden #t
                win-size %d %d
                show-frame-rate-meter #f
                """ % (1920, 1080))

class MyApp(ShowBase):
    def __init__(self, shared):
        ShowBase.__init__(self)
        self.shared = shared
        self.accept('escape', self.escapeAction)
        path_to_file_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), 'aperture images'))
        onlyfiles = [os.path.join(path_to_file_dir, str(f) + ".tif") for f in range(1, 3)] # load #1-3 tiff files in that order
        self.tex =[]
        for i, file in enumerate(onlyfiles):
            pandafile = Filename.from_os_specific(file)
            self.tex.append(loader.loadTexture(pandafile))
        cm = CardMaker('card')

        self.cardnode = self.render.attachNewNode(cm.generate())

        self.lens1 = PerspectiveLens()
        self.lens1.setNearFar(0.01, 100)
        self.lens1.setFov(90, 90)
        self.cam.node().setLens(self.lens1)
        self.cardnode.setPos(-0.5, 0.5, -0.5)
        self.setBackgroundColor(0.5, 0.5, 0.5)
        self.gabor_radius = 0.04  # this would correspond to 40 deg diameter patch if the benq monitor was 20 cm from animal
        self.cardnode.setShaderInput("gabor_radius", self.gabor_radius)
        self.cardnode.setShaderInput("aspect_ratio", self.getAspectRatio())  # accounts for aspect ratio of screen
        # self.cardnode.setTexture(self.tex[0])
        self.cardnode.hide()

    def escapeAction(self):
        self.shared.main_programm_still_running.value = 0
