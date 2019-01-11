from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
import numpy as np
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
                
                uniform float aperture_toggle;
                uniform float rot_angle;
                uniform float x_pos;
                uniform float y_pos;
                uniform float width;
                uniform float cycles;

                void main() {
                mat2 rotation = mat2( cos(rot_angle), sin(rot_angle),
                             -sin(rot_angle), cos(rot_angle));
                mat2 rotation_ortho = mat2( cos(rot_angle + 1.57), sin(rot_angle + 1.57),
                             -sin(rot_angle + 1.57), cos(rot_angle + 1.57));
                vec2 texcoord_rotated = rotation*texcoord.xy;
                vec2 texcoord_rotated_ortho = rotation_ortho*texcoord.xy;
                vec4 color0 = vec4(0.5,0.5,0.5,1);
                
                // toggle 0 is for presentation in aperture
                if (aperture_toggle == 0){
                    if ( (float(abs(texcoord.x-x_pos)) < width) && (float(abs(texcoord.y - y_pos)) < width) ){
                        color0 = vec4((sign(sin(texcoord_rotated.x*2*3.14*cycles))+1)/2, (sign(sin(texcoord_rotated.x*2*3.14*cycles))+1)/2, (sign(sin(texcoord_rotated.x*2*3.14*cycles))+1)/2,1);
                        }
                    else{
                        color0 = vec4(0.5,0.5,0.5,1);
                        }        
                    }
                // toggle 1 is for presentation over the whole screen
                if (aperture_toggle == 1){
                    color0 = vec4((sign(sin(texcoord_rotated.x*2*3.14*cycles))+1)/2, (sign(sin(texcoord_rotated.x*2*3.14*cycles))+1)/2, (sign(sin(texcoord_rotated.x*2*3.14*cycles))+1)/2,1);
                    }
                // toggle 2 is for presentation in couter-aperture
                if (aperture_toggle == 2){
                     if ( (float(abs(texcoord.x-x_pos)) < width) && (float(abs(texcoord.y - y_pos)) < width) ){
                        color0 = vec4(0.5,0.5,0.5,1);
                        }
                    else{
                        color0 = vec4((sign(sin(texcoord_rotated.x*2*3.14*cycles))+1)/2, (sign(sin(texcoord_rotated.x*2*3.14*cycles))+1)/2, (sign(sin(texcoord_rotated.x*2*3.14*cycles))+1)/2,1);
                        }        
                    }
                // toggle 3 is for mismatch presentation    
                if(aperture_toggle == 3){
                    if ( (float(abs(texcoord.x-x_pos)) < width) && (float(abs(texcoord.y - y_pos)) < width) ){
                        color0 = vec4((sign(sin(texcoord_rotated.x*2*3.14*cycles))+1)/2, (sign(sin(texcoord_rotated.x*2*3.14*cycles))+1)/2, (sign(sin(texcoord_rotated.x*2*3.14*cycles))+1)/2,1);
                        }
                    else{
                        color0 = vec4((sign(sin(texcoord_rotated_ortho.x*2*3.14*cycles))+1)/2, (sign(sin(texcoord_rotated_ortho.x*2*3.14*cycles))+1)/2, (sign(sin(texcoord_rotated_ortho.x*2*3.14*cycles))+1)/2,1);
                        }        
                    }
                 gl_FragColor = color0;
               }
            """
            ]
loadPrcFileData("",
                """sync-video #f
                fullscreen #f
                win-origin 2460 0
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
        x = np.linspace(0, 1, 1000)

        self.tex = Texture("texture")
        self.tex.setMagfilter(Texture.FTLinear)

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
        self.my_shader = Shader.make(Shader.SLGLSL, my_shader[0], my_shader[1])
        self.cardnode.setShader(self.my_shader)
        self.setBackgroundColor(0.5, 0.5, 0.5)
        self.cardnode.setShaderInput("cycles", 9)  # this would be a 0.1 cpd grating if the benq monitor was 20 cm from animal
        self.cardnode.setShaderInput("rot_angle", 0)
        self.cardnode.setShaderInput("x_pos", 0.5)  # present gabor in the centre of the screen
        self.cardnode.setShaderInput("y_pos", 0.5)
        self.cardnode.setShaderInput('width', 0.25)
        self.cardnode.setShaderInput("aperture_toggle", 0)
        # self.cardnode.setTexture(self.tex[0])
        self.cardnode.hide()
        # added gamma correction on 102318
        self.win.getGsg().setGamma(2.0)

    def escapeAction(self):
        self.shared.main_programm_still_running.value = 0
