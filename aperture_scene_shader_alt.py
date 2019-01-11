from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
import sys
import os

# this aperture shader leaves a gray zone between the centre and surround. also presents the natural images in a square
# area which can be moved to the most anterior part of the screen
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
                uniform float width;
                uniform float aperture_toggle;
                float gap_width = 0; //0.125;
                
                void main() {
                 vec4 color0 = vec4(0.5,0.5,0.5,1);
                 // toggle 0 is for presentation in aperture
                if (aperture_toggle == 0){
                    if ( (float(abs(texcoord.x-x_pos)) < width) && (float(abs(texcoord.y - y_pos)) < width) ){
                        color0 = texture(p3d_Texture0, texcoord);
                        }
                    else{
                        color0 = vec4(0.5,0.5,0.5,1);
                        }        
                    }
                // toggle 1 is for presentation over the whole screen
                if (aperture_toggle == 1){
                    if ( (float(abs(texcoord.x-x_pos)) < width) && (float(abs(texcoord.y - y_pos)) < width) ){
                        color0 = texture(p3d_Texture0, texcoord);
                        }
                    
                    if ( (float(abs(texcoord.y - y_pos)) > (width+ gap_width)) && (float(abs(texcoord.x-x_pos)) > width)){
                        color0 = texture(p3d_Texture0, texcoord);
                        }
                    if ( (float(abs(texcoord.y - y_pos)) > (width)) && (float(abs(texcoord.x-x_pos)) > width+gap_width )){
                        color0 = texture(p3d_Texture0, texcoord);
                        }
                    if ( (float(abs(texcoord.y - y_pos)) < (width)) && (float(abs(texcoord.x-x_pos)) > width+ gap_width )){
                        color0 = texture(p3d_Texture0, texcoord);
                        }
                    if ( (float(abs(texcoord.y - y_pos)) > (width+gap_width)) && (float(abs(texcoord.x-x_pos)) < width)){
                        color0 = texture(p3d_Texture0, texcoord);
                        }
                    
                    }
                // toggle 2 is for presentation in couter-aperture
                if (aperture_toggle == 2){
                     if ( (float(abs(texcoord.x-x_pos)) < (width+gap_width)) && (float(abs(texcoord.y - y_pos)) < (width+gap_width)) ){
                        color0 = vec4(0.5,0.5,0.5,1);
                        }
                    else{
                        color0 = texture(p3d_Texture0, texcoord);
                        }        
                    }
                 gl_FragColor = color0;
               }
            """
            ]
loadPrcFileData("",
                """sync-video #f
                fullscreen #f
                win-origin 2760 0
                undecorated #t
                cursor-hidden #t
                win-size %d %d
                show-frame-rate-meter #f
                """ % (1080, 1080))

class MyApp(ShowBase):
    def __init__(self, shared):
        ShowBase.__init__(self)
        self.disableMouse()

        self.shared = shared
        self.accept('escape', self.escapeAction)
        path_to_file_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), 'new aperture images'))
        onlyfiles = [os.path.join(path_to_file_dir, str(f) + ".tif") for f in range(1, 4)] # load #1-3 tiff files in that order
        self.tex =[]
        for i, file in enumerate(onlyfiles):
            pandafile = Filename.from_os_specific(file)
            self.tex.append(loader.loadTexture(pandafile))
        print(len(self.tex))
        cm = CardMaker('card')

        self.cardnode = self.render.attachNewNode(cm.generate())

        self.lens1 = PerspectiveLens()
        self.lens1.setNearFar(0.01, 100)
        self.lens1.setFov(90, 90)
        self.cam.node().setLens(self.lens1)
        self.cardnode.setPos(-0.5, 0.5, -0.5)
        self.my_shader = Shader.make(Shader.SLGLSL, my_shader[0], my_shader[1])
        self.cardnode.setShader(self.my_shader)
        self.setBackgroundColor(0.5, 0.5, 0.5)
        self.gabor_radius = 0.04  # this would correspond to 40 deg diameter patch if the benq monitor was 20 cm from animal
        self.cardnode.setShaderInput("gabor_radius", self.gabor_radius)
        self.cardnode.setShaderInput("aspect_ratio", self.getAspectRatio())  # accounts for aspect ratio of screen
        self.cardnode.setShaderInput("aperture_toggle", 0)
        # self.cardnode.setTexture(self.tex[0])
        self.cardnode.hide()
        self.win.getGsg().setGamma(2.0)
    def escapeAction(self):
        self.shared.main_programm_still_running.value = 0
