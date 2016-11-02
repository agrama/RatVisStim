from multiprocessing import Process, Value, Array, Queue, sharedctypes
import sys
import numpy as np
import time
import os
import importlib
import time

class StimulusModule(Process):
    def __init__(self, shared):
        Process.__init__(self)

        self.shared = shared

    def remove_module(self):
        if self.stimulus_widget is not None:
            try:
                self.stimulus_widget.destroy()

                del self.stimulus_widget
                del self.module
                self.stimulus_widget = None

            except Exception as e:
                print("Stimulus file error", e)

            self.shared.stimulus_script_active.value = 0
            self.shared.stimulus_name_l.value = 0
            self.shared.stimulus_number_of_stimuli.value = 0
            self.shared.stimulus_time_per_stimulus.value = 0
            self.shared.stimulus_current_index.value = -1

    def run(self):

        self.stimulus_widget = None

        while self.shared.running.value == 1:

            if self.shared.stimulus_script_update_requested.value == 1:
                self.shared.stimulus_script_update_requested.value = 0
                full_path_to_module = bytearray(self.shared.stimulus_script_path[:self.shared.stimulus_script_path_l.value]).decode()

                self.remove_module()

                try:

                    module_dir, module_file = os.path.split(full_path_to_module)
                    module_name, module_ext = os.path.splitext(module_file)

                    spec = importlib.util.spec_from_file_location(module_name, full_path_to_module)

                    self.module = spec.loader.load_module()

                    self.stimulus_widget = self.module.MyApp(self.shared)

                    stimulus_name = self.stimulus_widget.stimulus_name.encode()

                    self.shared.stimulus_name[:len(stimulus_name)] = stimulus_name
                    self.shared.stimulus_name_l.value = len(stimulus_name)
                    self.shared.stimulus_number_of_stimuli.value = self.stimulus_widget.stimulus_number_of_stimuli
                    self.shared.stimulus_time_per_stimulus.value = self.stimulus_widget.stimulus_time_per_stimulus
                    self.shared.stimulus_script_active.value = 1

                except Exception as e:
                    print("Stimulus file error", e)

            if self.stimulus_widget is not None:
                if self.shared.stimulus_start_stimulus_requested.value == 1:
                    self.shared.stimulus_start_stimulus_requested.value = 0

                    for fish_index in range(4):
                        self.stimulus_widget.init_stimulus(fish_index, self.shared.stimulus_current_index.value)

                    # reset the global timer and start the stimulus updating routine
                    self.shared.stimulus_currently_running.value = 1
                    self.shared.stimulus_start_time.value = time.time()
                    self.shared.current_stimulus_time.value = 0

                    self.last_time = time.time()

                if self.shared.stimulus_currently_running.value == 1:
                    self.new_time = time.time()
                    dt = self.last_time - self.new_time
                    self.last_time = self.new_time

                    stimulus_time = self.new_time - self.shared.stimulus_start_time.value # time releative to stimulus start

                    self.shared.current_stimulus_time.value = stimulus_time

                    for fish_index in range(4):
                        self.stimulus_widget.update_stimulus(fish_index, self.shared.stimulus_current_index.value, stimulus_time, dt)


                    if stimulus_time >= self.shared.stimulus_time_per_stimulus.value:
                        self.shared.stimulus_currently_running.value = 0 # stop the stimulus updating

                if self.shared.stimulus_calibration_update_requested.value == 1:
                    self.shared.stimulus_calibration_update_requested.value = 0
                    self.stimulus_widget.update_fish_positions()

                self.stimulus_widget.taskMgr.step()  # main panda loop, needed for redrawing, etc.

        self.remove_module()