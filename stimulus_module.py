from multiprocessing import Process, Value, Array, Queue, sharedctypes
from fullscreen_gratings import MyApp
import time
import numpy as np



class StimulusModule(Process):
    def __init__(self, shared):
        Process.__init__(self)

        self.shared = shared

    def run(self):

        self.myapp = MyApp(self.shared)
        self.thetas = np.arange(0, 180, 45)           # number of stim
        self.thetas = np.tile(self.thetas, 5)    # 3 repetitions of stimuli
        np.random.seed(1)
        self.thetas = np.random.permutation(self.thetas)
        self.numstim = len(self.thetas)
        self.stimcount = len(self.thetas)
        self.frametrig = 447  # present after every frametrig frame
        self.last_time = time.time()
        while self.shared.main_programm_still_running.value == 1:

            if not (self.shared.frameCount.value+1) % self.frametrig:    # present every 10th frame
                self.shared.theta.value = self.thetas[self.numstim - self.stimcount]
                self.myapp.update_theta()
                self.stim_start_time = time.time()
                self.myapp.update_stimulus()
                self.last_time = time.time()
                while self.last_time- self.stim_start_time < 1:   #present gabor for 1 sec
                    self.myapp.taskMgr.step()
                    self.last_time = time.time()
                self.myapp.drawgrey()
                self.stimcount -= 1
            if self.stimcount == 0:
                self.stim_start_time = time.time()
                self.myapp.drawgrey()
                self.last_time = time.time()
                while self.last_time- self.stim_start_time < 10:   #present gray background for 10 s before shutting down program
                    self.myapp.taskMgr.step()
                    self.last_time = time.time()
                self.shared.main_programm_still_running.value = 0

            self.myapp.taskMgr.step()  # main panda loop, needed for redrawing, etc.

        self.myapp.destroy()
