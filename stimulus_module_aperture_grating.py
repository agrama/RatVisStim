from multiprocessing import Process, Value, Array, Queue, sharedctypes
from aperture_grating_shader_alt import MyApp
import time
import numpy as np
import random as rn

# this module will flash gratings of two orthogonal orientations in whole screen, in aperture and counter aperture, and mismatch conditions


class StimulusModule(Process):
    def __init__(self, shared):
        Process.__init__(self)

        self.shared = shared

    def run(self):

        self.myapp = MyApp(self.shared)
        # self.myapp.drawgrey()
        # self.myapp.taskMgr.step()

        self.stimcode = []
        for theta in np.arange(0, np.pi, np.pi/2):
            for aperture in np.arange(0, 4, 1):
                self.stimcode.append((theta, aperture))     #this generates different permutations of x and y and theta values



        #######

        numtrials = 20
        self.waitframes = 600  # wait frames before starting stim
        self.frametrig = 300  # trigger visual stim at these frame intervals after waitframes
        # need to define the boundaries of the aperture here
        self.aperture_center = (0.5,0.5)
        self.aperture_width = 0.25 # half the side length of the square
        self.myapp.cardnode.setShaderInput('x_pos', self.aperture_center[0])
        self.myapp.cardnode.setShaderInput('y_pos', self.aperture_center[1])
        self.myapp.cardnode.setShaderInput('width', self.aperture_width)
        #########
        stimcode1 = self.stimcode[:]
        for trial in range(numtrials-1):
            self.stimcode.extend(stimcode1)   #repeat the randomized stim block
        rn.seed(1)
        rn.shuffle(self.stimcode)       # shuffle the stimulus presentation
        self.numstim = len(self.stimcode)
        self.stimcount = len(self.stimcode)

        while self.shared.main_programm_still_running.value == 1:
            if self.shared.frameCount.value < self.waitframes:
                self.myapp.taskMgr.step()
            else:
                if not (self.shared.frameCount.value - self.waitframes) % self.frametrig:    # present every frametrig frame
                    # need to pass values of position and rotation angle to the shader
                    stimcode_dummy = self.stimcode[self.numstim - self.stimcount]
                    print(stimcode_dummy)
                    self.myapp.cardnode.setShaderInput("rot_angle", stimcode_dummy[0])
                    self.myapp.cardnode.setShaderInput("aperture_toggle", stimcode_dummy[1])
                    self.stim_start_time = time.time()
                    self.last_time = time.time()
                    while self.last_time- self.stim_start_time < 0.5:   #present image for 500 msec
                        self.myapp.cardnode.show()
                        self.myapp.taskMgr.step()
                        self.last_time = time.time()

                    self.stimcount -= 1
                if self.stimcount == 0:
                    self.stim_start_time = time.time()
                    self.myapp.cardnode.hide()
                    self.last_time = time.time()
                    while self.last_time- self.stim_start_time < 10:   #present gray background for 10 s before shutting down program
                        self.myapp.taskMgr.step()
                        self.last_time = time.time()
                    self.shared.main_programm_still_running.value = 0
                self.myapp.cardnode.hide()
                self.myapp.taskMgr.step()  # main panda loop, needed for redrawing, etc.

        self.myapp.destroy()
