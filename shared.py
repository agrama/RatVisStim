from multiprocessing import Value, Array, Queue, sharedctypes
from FrameCounter import FrameCounter
from stimulus_module import StimulusModule
import ctypes

class Shared():
    def __init__(self):

        self.main_programm_still_running = Value("b", 1)
        self.frameCount = Value("L", 0)
        # self.shared.stimulus_start_time = Value("d",0)
        self.theta = Value("i", 0)
    def start_threads(self):
        submodule = FrameCounter(self)
        submodule.start()

        stimulus_module = StimulusModule(self)
        stimulus_module.start()

