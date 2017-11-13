from multiprocessing import Process, Value, Array, Queue, sharedctypes
from moving_bar_shader import MyApp
import time
import numpy as np



class StimulusModule(Process):
    def __init__(self, shared):
        Process.__init__(self)

        self.shared = shared

    def run(self):

        self.myapp = MyApp(self.shared)
        self.thetas = np.arange(0, np.pi, np.pi/4)           # number of stim
        self.thetas = np.tile(self.thetas, 5)    # 3 repetitions of stimuli
        np.random.seed(1)
        self.thetas = np.random.permutation(self.thetas)
        self.numstim = len(self.thetas)
        self.stimcount = len(self.thetas)
        self.waitframes = 300 # wait # frames before starting stim
        self.stimcode = 'left'
        self.stimtime = 100
        while self.shared.main_programm_still_running.value == 1:
            if self.shared.frameCount.value < self.waitframes:
                self.myapp.taskMgr.step()

            else:
                if self.stimcode == 'right':
                    self.myapp.x[:,0:self.myapp.barwidth] = 255
                    memoryview(self.myapp.tex.modify_ram_image())[:] = self.myapp.x.astype(np.uint8).tobytes()
                    self.stim_start_time = time.time()
                    self.last_time = time.time()
                    self.myapp.cardnode.show()
                    while self.last_time - self.stim_start_time < self.stimtime: # present for 200 sec
                        self.myapp.cardnode.setShaderInput("y_shift", 0)
                        self.myapp.cardnode.setShaderInput("x_shift", (self.last_time - self.stim_start_time) * 0.1) # shift bar at 0.1 Hz
                        self.myapp.taskMgr.step()
                        self.last_time = time.time()
                    self.shared.main_programm_still_running.value = 0
                elif self.stimcode == 'left':
                    self.myapp.x[:,-self.myapp.barwidth:-1] = 255
                    memoryview(self.myapp.tex.modify_ram_image())[:] = self.myapp.x.astype(np.uint8).tobytes()
                    self.stim_start_time = time.time()
                    self.last_time = time.time()
                    self.myapp.cardnode.show()
                    while self.last_time - self.stim_start_time < self.stimtime:  # present for 200 sec
                        self.myapp.cardnode.setShaderInput("y_shift", 0)
                        self.myapp.cardnode.setShaderInput("x_shift", -(self.last_time - self.stim_start_time) * 0.1)  # shift bar at 0.1 Hz
                        self.myapp.taskMgr.step()
                        self.last_time = time.time()
                    self.shared.main_programm_still_running.value = 0
                elif self.stimcode == 'up':
                    self.myapp.x[0:self.myapp.barwidth, :] = 255
                    memoryview(self.myapp.tex.modify_ram_image())[:] = self.myapp.x.astype(np.uint8).tobytes()
                    self.stim_start_time = time.time()
                    self.last_time = time.time()
                    self.myapp.cardnode.show()
                    while self.last_time - self.stim_start_time < self.stimtime:  # present for 200 sec
                        self.myapp.cardnode.setShaderInput("y_shift", (self.last_time - self.stim_start_time) * 0.1)  # shift bar at 0.1 Hz
                        self.myapp.cardnode.setShaderInput("x_shift", 0)
                        self.myapp.taskMgr.step()
                        self.last_time = time.time()
                    self.shared.main_programm_still_running.value = 0
                elif self.stimcode == 'down':
                    self.myapp.x[-self.myapp.barwidth:-1, :] = 255
                    memoryview(self.myapp.tex.modify_ram_image())[:] = self.myapp.x.astype(np.uint8).tobytes()
                    self.stim_start_time = time.time()
                    self.last_time = time.time()
                    self.myapp.cardnode.show()
                    while self.last_time - self.stim_start_time < self.stimtime:  # present for 200 sec
                        self.myapp.cardnode.setShaderInput("y_shift", -(self.last_time - self.stim_start_time) * 0.1) # shift bar at 0.1 Hz
                        self.myapp.cardnode.setShaderInput("x_shift", 0)
                        self.myapp.taskMgr.step()
                        self.last_time = time.time()
                    self.shared.main_programm_still_running.value = 0
                self.myapp.cardnode.hide()
                self.myapp.taskMgr.step()  # main panda loop, needed for redrawing, etc.

        self.myapp.destroy()
