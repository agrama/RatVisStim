from multiprocessing import Value, Array, Queue, sharedctypes
from FrameCounter import FrameCounter
# from stimulus_module_orient_position_gratings import StimulusModule
import ctypes
# from stimulus_module_shader import StimulusModule
# from stimulus_module_movingbar import StimulusModule
# from stimulus_module_orient_position_gratings import StimulusModule
# from stimulus_module_cesar import StimulusModule
# from stimulus_module_moving_grating_circularpatch import StimulusModule
# from stimulus_module_aperture import StimulusModule
# from stimulus_module_ON_OFF_square_RFmapping import StimulusModule
from stimulus_module_moving_square_RFmapping import StimulusModule
# from stimulus_module_moving_square_RFmapping_4x4 import StimulusModule
# from stimulus_module_aperture_grating import StimulusModule
# from stimulus_module_aperture_scene import StimulusModule
class Shared():
    def __init__(self):

        self.main_programm_still_running = Value("b", 1)
        self.frameCount = Value("L", 0)
        # self.shared.stimulus_start_time = Value("d",0)
        self.theta = Value("i", 0)
        self.x = Value("d", 0)
        self.y = Value("d", 0)

    def start_threads(self):
        submodule = FrameCounter(self)
        submodule.start()

        stimulus_module = StimulusModule(self)
        stimulus_module.start()

