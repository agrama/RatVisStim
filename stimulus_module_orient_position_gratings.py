from multiprocessing import Process, Value, Array, Queue, sharedctypes
from gabor_mapping_shader import MyApp
import time
import numpy as np
import random as rn

# this module will flash gabors of different orientations in different parts of the screen in a randomised way

class StimulusModule(Process):
    def __init__(self, shared):
        Process.__init__(self)

        self.shared = shared

    def run(self):

        self.myapp = MyApp(self.shared)
        # self.myapp.drawgrey()
        # self.myapp.taskMgr.step()

        self.stimcode = []
        # for an x shift of the centre of the disk by 10 deg, need to chance x_pos by 0.063
        # for an y shift of the centre of the disk by 10 deg, need to chance x_pos by 0.11
        # this was found empirically, and the ratio of this shift comes to 1.77 which is the aspect ratio of the monitor
        for x in np.arange(0.5+ 0.03150-(0.063*2),  0.5+0.0315+ 0.063 + 0.01, 0.063):
            for y in np.arange(0.5+0.055 - (0.11*2),  0.5+0.055 + 0.11 + 0.01, 0.11):
                for theta in np.arange(0, np.pi/2 + 0.1, np.pi/2):   # present two orientations
                    self.stimcode.append((x, y, theta))     #this generates different permutations of x and y and theta values
        rn.seed(1)
        rn.shuffle(self.stimcode)
        stimcode1 = self.stimcode[:]
        numtrials = 5
        for trial in range(numtrials-1):
            self.stimcode.extend(stimcode1)   #repeat the randomized stim block
        self.numstim = len(self.stimcode)
        self.stimcount = len(self.stimcode)
        self.waitframes = 120  # wait frames before starting stim
        self.frametrig = 60  # trigger visual stim at these frame intervals after waitframes
        while self.shared.main_programm_still_running.value == 1:
            if self.shared.frameCount.value < self.waitframes:
                self.myapp.taskMgr.step()
            else:
                if (self.shared.frameCount.value-self.waitframes) % self.frametrig < 5:    # present every frametrig frame
                    # need to pass values of position and rotation angle to the shader
                    stimcode_dummy = self.stimcode[self.numstim - self.stimcount]
                    self.myapp.cardnode.setShaderInput("rot_angle", stimcode_dummy[2])
                    self.myapp.cardnode.setShaderInput("x_pos", stimcode_dummy[0])
                    self.myapp.cardnode.setShaderInput("y_pos", stimcode_dummy[1])
                    self.stim_start_time = time.time()
                    self.last_time = time.time()
                    while self.last_time- self.stim_start_time < 0.5:   #present gabor for 500 msec
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
