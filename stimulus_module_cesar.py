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
        counter = 0;
        self.stimcode = np.arange(1,31) #number of stim files
        numtrials = 3
        self.stimcode = np.tile(self.stimcode, numtrials) # repeat stim
        # should i randomise the presentation?
        self.numstim = len(self.stimcode)
        self.stimcount = len(self.stimcode)
        self.waitframes = 30 * (20 + 1)  # wait frames before starting stim
        self.frametrig = 30 * (20 + 1)  # trigger visual stim at these frame intervals after waitframes
        while self.shared.main_programm_still_running.value == 1:
            if self.shared.frameCount.value < self.waitframes:
                self.myapp.taskMgr.step()
            else:
                if not (self.shared.frameCount.value+1 - self.waitframes) % self.frametrig:    # present every frametrig frame
                    # need to pass values of position and rotation angle to the shader
                    self.myapp.cardnode.setTexture(self.myapp.tex[self.stimcode[self.numstim-self.stimcount]])
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
