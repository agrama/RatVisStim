from multiprocessing import Process, Value, Array, Queue, sharedctypes
from moving_gabor_shader import MyApp
import time
import numpy as np



class StimulusModule(Process):
    def __init__(self, shared):
        Process.__init__(self)

        self.shared = shared

    def run(self):

        self.myapp = MyApp(self.shared)
        self.thetas = np.arange(0, 2*np.pi, np.pi/4)           # number of stim

        #######JULEEEE
        num_repetitions = 5
        self.frametrig = 300
        self.waitframes = 300  # wait # frames before starting stim
        self.temporal_frequency = 4 #of grating in Hz; the value of 4 was chosen by looking at girman et al
        #######
        self.thetas = np.tile(self.thetas, num_repetitions)    #  repetitions of stimuli
        np.random.seed(9)
        self.thetas = np.random.permutation(self.thetas)
        self.numstim = len(self.thetas)
        self.stimcount = len(self.thetas)

        while self.shared.main_programm_still_running.value == 1:
            if self.shared.frameCount.value < self.waitframes:
                self.myapp.taskMgr.step()
            else:
                if (self.shared.frameCount.value-self.waitframes) % self.frametrig < 5:    # present every frametrig frame + 5 frames
                    self.myapp.cardnode.setShaderInput("rot_angle", self.thetas[self.numstim - self.stimcount])
                    self.stim_start_time = time.time()
                    self.last_time = time.time()
                    while self.last_time- self.stim_start_time < 5:   #present gabor for 5 sec
                        self.myapp.cardnode.setShaderInput("phi", 2*np.pi*self.temporal_frequency*(self.last_time-self.stim_start_time))
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
