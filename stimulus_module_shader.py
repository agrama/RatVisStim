from multiprocessing import Process, Value, Array, Queue, sharedctypes
from moving_gratings_shader import MyApp
import time
import numpy as np



class StimulusModule(Process):
    def __init__(self, shared):
        Process.__init__(self)

        self.shared = shared

    def run(self):

        self.myapp = MyApp()
        self.thetas = np.arange(0, np.pi, np.pi/4)           # number of stim
        self.thetas = np.tile(self.thetas, 5)    # 3 repetitions of stimuli
        np.random.seed(1)
        self.thetas = np.random.permutation(self.thetas)
        self.numstim = len(self.thetas)
        self.stimcount = len(self.thetas)
        self.frametrig = 50*(20+1)
        self.waitframes = 50*(20+1) # wait # frames before starting stim
        while self.shared.main_programm_still_running.value == 1:
            if self.shared.frameCount.value < self.waitframes:
                self.myapp.taskMgr.step()
            else:
                if not (self.shared.frameCount.value+1-self.waitframes) % self.frametrig:    # present every 10th frame
                    self.myapp.cardnode.setShaderInput("rot_angle", self.thetas[self.numstim - self.stimcount])
                    self.stim_start_time = time.time()
                    self.last_time = time.time()
                    while self.last_time- self.stim_start_time < 5:   #present gabor for 2 sec
                        self.myapp.cardnode.setShaderInput("timer", (self.last_time-self.stim_start_time))
                        self.myapp.cardnode.show()
                        self.myapp.taskMgr.step()
                        self.last_time = time.time()
                    self.stimcount -= 1
                if self.stimcount == 0:
                    self.stim_start_time = time.time()
                    self.myapp.cardnode.hide()
                    self.last_time = time.time()
                    while self.last_time- self.stim_start_time < 10:   #present gray background for 5 s before shutting down program
                        self.myapp.taskMgr.step()
                        self.last_time = time.time()
                    self.shared.main_programm_still_running.value = 0
                self.myapp.cardnode.hide()
                self.myapp.taskMgr.step()  # main panda loop, needed for redrawing, etc.

        self.myapp.destroy()
