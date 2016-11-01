from multiprocessing import Value, Array, Queue, sharedctypes
from gabor import MyApp
from FrameCounter import FrameCounter
import ctypes

class Shared():
    def __init__(self):

        self.main_programm_still_running = Value("b", 1)
        self.current_time = Value("L", 0)
        self.frameCount = Value("")

        self.frame = sharedctypes.RawArray(ctypes.c_double, 2000*2000)
        self.frame_l = Value("i", 0)


    def start_threads(self):
        submodule = FrameCounter(self)
        submodule.start()

        submodule2 = CameraModule(self)
        submodule2.start()

