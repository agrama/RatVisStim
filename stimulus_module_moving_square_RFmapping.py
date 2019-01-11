from multiprocessing import Process, Value, Array, Queue, sharedctypes
from moving_square_mapping_shader import MyApp
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
        stimcode = []

        for x in np.arange((-0.5 + self.myapp.scale/2), (0.5 - self.myapp.scale/2 + 0.05), self.myapp.scale):
            for y in np.arange((-0.5 + self.myapp.scale/2), (0.5 - self.myapp.scale/2 + 0.05), self.myapp.scale):
                stimcode.append((x, y))


        numtrials = 10
        rn.seed(2)
        self.waitframes = 600  # wait frames before starting stim
        self.frametrig = 120  # trigger visual stim at these frame intervals after waitframes

        stimcode_ = []
        # self.stimcode = []
        stim_ind = rn.randint(0, len(stimcode))
        stimcode_.append(stimcode[stim_ind])
        stimcode.pop(stim_ind)
        while len(stimcode) > 1:
            stim_ind = rn.randint(0, len(stimcode) - 1)
            old_point = stimcode_[-1]
            new_point = stimcode[stim_ind]
            dist = ((new_point[0] - old_point[0]) ** 2 + (new_point[1] - old_point[1]) ** 2) ** 0.5
            while dist < 0.35:
                stim_ind = rn.randint(0, len(stimcode) - 1)
                new_point = stimcode[stim_ind]
                dist = ((new_point[0] - old_point[0]) ** 2 + (new_point[1] - old_point[1]) ** 2) ** 0.5
            stimcode_.append(stimcode[stim_ind])
            # print(len(stimcode_))
            stimcode.pop(stim_ind)
        stimcode_.append(stimcode[-1])
        self.stimcode = []
        for indx in range(numtrials):
            self.stimcode.extend(stimcode_)
        self.numstim = len(self.stimcode)
        self.stimcount = len(self.stimcode)

        rn.seed(2)
        self.randorder =  np.tile(np.arange(0,4),(self.numstim,1))
        for ind in range(self.numstim):
            rn.shuffle(self.randorder[ind, :])

        while self.shared.main_programm_still_running.value == 1:

            if self.shared.frameCount.value < self.waitframes:

                self.myapp.taskMgr.step()
                time.sleep(0.001)
            else:
                if (self.shared.frameCount.value-self.waitframes) % self.frametrig < 5:    # present every frametrig frame
                    # need to pass values of position and rotation angle to the shader

                    stimcode_dummy = self.stimcode[self.numstim - self.stimcount]
                    print(self.shared.frameCount.value, stimcode_dummy[0], stimcode_dummy[1])
                    self.myapp.pivotNode.setPos(stimcode_dummy[0], 0.5, stimcode_dummy[1])
                    self.stim_start_time = time.time()
                    self.last_time = time.time()
                    while self.last_time- self.stim_start_time < 1:   #present the moving bars for 1 sec
                        self.myapp.cardnode.show()
                        self.myapp.pivotNode.setR(self.randorder[self.numstim - self.stimcount, int(np.floor((self.last_time - self.stim_start_time) / 0.25))] * 90) # this changes the direction of the moving bar randomly every 250 ms across the 4 cardinal directions
                        self.myapp.cardnode.setShaderInput('x_shift', (self.last_time - self.stim_start_time) * 4)
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
        self.myapp.win.getGsg().setGamma(1.0)
        self.myapp.destroy()
