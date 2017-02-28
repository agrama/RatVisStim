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
        self.thetas = np.arange(0, 2*np.pi, np.pi/4)           # number of stim
        self.thetas = np.tile(self.thetas, 1)    # 3 repetitions of stimuli
        np.random.seed(1)
        self.thetas = np.random.permutation(self.thetas)
        self.numstim = len(self.thetas)
        self.stimcount = len(self.thetas)
        self.frametrig = 477
        while self.shared.main_programm_still_running.value == 1:
            self.myapp.cardnode.hide()
            if not (self.shared.frameCount.value+1) % self.frametrig:    # present every 10th frame
                self.myapp.cardnode.setShaderInput("rot_angle", self.thetas[self.numstim - self.stimcount])
                self.stim_start_time = time.time()
                self.last_time = time.time()
                while self.last_time- self.stim_start_time < 2:   #present gabor for 2 sec
                    self.myapp.cardnode.setShaderInput("x_shift", self.last_time-self.stim_start_time/self.myapp.scale)
                    self.myapp.cardnode.show()
                    self.myapp.taskMgr.step()
                    self.last_time = time.time()
                self.myapp.cardnode.hide()
                self.stimcount -= 1
            if self.stimcount == 0:
                self.stim_start_time = time.time()
                self.myapp.drawgrey()
                self.last_time = time.time()
                while self.last_time- self.stim_start_time < 5:   #present gray background for 5 s before shutting down program
                    self.myapp.taskMgr.step()
                    self.last_time = time.time()
                self.shared.main_programm_still_running.value = 0

            self.myapp.taskMgr.step()  # main panda loop, needed for redrawing, etc.

        self.myapp.destroy()
