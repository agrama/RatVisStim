from multiprocessing import Process, Value, Array, Queue, sharedctypes
from gabor import MyApp
import time
import numpy as np
import random as rn



class StimulusModule(Process):
    def __init__(self, shared):
        Process.__init__(self)

        self.shared = shared

    def run(self):

        self.myapp = MyApp(self.shared)
        # self.myapp.drawgrey()
        # self.myapp.taskMgr.step()
        counter = 0;
        self.stimcode = []
        for x in np.arange(-0.66, 0.7, 0.33):
            for y in [-0.5, 0.5]:
                for theta in np.arange(0, 180, 90):
                    self.stimcode.append((x, y, theta))     #this generates different permutations of x and y and theta values
        rn.seed(1)
        rn.shuffle(self.stimcode)
        stimcode1 = self.stimcode[:]
        numtrials = 3
        self.frametrig = 15 * (30 + 8) #present stim every 15th frame or volume
        for trial in range(numtrials-1):
            self.stimcode.extend(stimcode1) #repeat the randomized stim block

        # self.thetas = np.arange(0, 360, 180)           # number of stim
        # self.thetas = np.tile(self.thetas, 3)    # 3 repetitions of stimuli
        # np.random.seed(1)
        # self.thetas = np.random.permutation(self.thetas)
        self.numstim = len(self.stimcode)
        self.stimcount = len(self.stimcode)
        self.last_time = time.time()
        # self.new_time = time.time()
        while self.shared.main_programm_still_running.value == 1:
            # self.new_time = time.time()
            # self.dt = self.new_time - self.last_time
            # print self.dt
            # self.last_time = self.new_time
            if not (self.shared.frameCount.value+1) % self.frametrig:    # present every 15th frame
                print(self.shared.frameCount.value)
                self.shared.x.value = self.stimcode[self.numstim - self.stimcount][0]
                self.shared.y.value = self.stimcode[self.numstim - self.stimcount][1]
                self.shared.theta.value = self.stimcode[self.numstim - self.stimcount][2]
                print self.shared.x.value, self.shared.y.value, self.shared.theta.value
                self.stim_start_time = time.time()
                self.myapp.update_stimulus()
                self.last_time = time.time()
                while self.last_time- self.stim_start_time < 2:   #present gabor for 2 sec
                    self.myapp.taskMgr.step()
                    self.last_time = time.time()
                self.myapp.drawgrey()
                self.myapp.taskMgr.step()
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
