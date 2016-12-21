from multiprocessing import Process, Value, Array, Queue, sharedctypes
from gabor import MyApp
import time
import numpy as np



class StimulusModule(Process):
    def __init__(self, shared):
        Process.__init__(self)

        self.shared = shared

    def run(self):

        self.myapp = MyApp(self.shared)
        self.thetas = np.arange(0, 360, 45)           # number of stim
        self.thetas = np.tile(self.thetas, 3)    # 3 repetitions of stimuli
        np.random.seed(1)
        self.thetas = np.random.permutation(self.thetas)
        self.numstim = len(self.thetas)
        self.stimcount = len(self.thetas)
        self.last_time = time.time()
        while self.shared.main_programm_still_running.value == 1:
            self.new_time = time.time()
            self.dt = self.new_time - self.last_time
            self.last_time = self.new_time
            if not (self.shared.frameCount.value+1) % 15:    # present every 10th frame
                self.shared.theta.value = self.thetas[self.numstim - self.stimcount]
                self.stim_start_time = time.time()
                self.myapp.update_stimulus()
                self.last_time = time.time()
                while self.last_time- self.stim_start_time < 2:   #present gabor for 2 sec
                    self.myapp.taskMgr.step()
                    self.last_time = time.time()
                self.myapp.drawgrey()
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
