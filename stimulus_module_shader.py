from multiprocessing import Process, Value, Array, Queue, sharedctypes
from moving_gratings_shader import MyApp
import time
import numpy as np



class StimulusModule(Process):
    def __init__(self, shared):
        Process.__init__(self)

        self.shared = shared

    def run(self):

        self.myapp = MyApp(self.shared)
        self.thetas = np.arange(0, np.pi, np.pi/4)           # number of stim
        self.thetas = np.tile(self.thetas, 5)    #  repetitions of stimuli
        np.random.seed(9)
        self.thetas = np.random.permutation(self.thetas)
        self.numstim = len(self.thetas)
        self.stimcount = len(self.thetas)
        self.frametrig = 300
        self.waitframes = 300 # wait # frames before starting stim
        while self.shared.main_programm_still_running.value == 1:
            if self.shared.frameCount.value < self.waitframes:
                self.myapp.taskMgr.step()
            else:
                if (self.shared.frameCount.value+1-self.waitframes) % self.frametrig < 5:    # present every frametrig frame + 5 frames
                    self.myapp.cardnode.setShaderInput("rot_angle", self.thetas[self.numstim - self.stimcount])
                    self.stim_start_time = time.time()
                    self.last_time = time.time()
                    while self.last_time- self.stim_start_time < 5:   #present gabor for 5 sec
                        self.myapp.cardnode.setShaderInput("timer", (self.last_time-self.stim_start_time))
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
