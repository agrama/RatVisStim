from multiprocessing import Process, Value, Array, Queue, sharedctypes
from cesar_natural_scenes import MyApp
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
        self.stimcode = np.arange(1,61) #number of stim files
        numtrials = 2
        self.stimcode = np.tile(self.stimcode, numtrials) # repeat stim
        rn.seed(1)
        rn.shuffle(self.stimcode)
        # should i randomise the presentation?
        self.numstim = len(self.stimcode)
        self.stimcount = len(self.stimcode)
        self.waitframes = 50 * (41 + 10)  # wait frames before starting stim
        self.frametrig = 15 * (41 + 10)  # trigger visual stim at these frame intervals after waitframes
        while self.shared.main_programm_still_running.value == 1:
            if self.shared.frameCount.value < self.waitframes:
                self.myapp.taskMgr.step()
            else:
                if (self.shared.frameCount.value+1-self.waitframes) % self.frametrig < 5:    # present every frametrig frame + 5 frames
                    # need to pass values of position and rotation angle to the shader
                    self.myapp.cardnode.setTexture(self.myapp.tex[self.stimcode[self.numstim-self.stimcount]])
                    self.stim_start_time = time.time()
                    self.last_time = time.time()
                    while self.last_time- self.stim_start_time < 0.5:   #present natural scene for 500 msec
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
