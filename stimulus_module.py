from multiprocessing import Process, Value, Array, Queue, sharedctypes
from gabor import MyApp


class StimulusModule(Process):
    def __init__(self, shared):
        Process.__init__(self)

        self.shared = shared

    def run(self):

        self.myapp = MyApp(self.shared)

        while self.shared.main_programm_still_running.value == 1:
                self.myapp.update_stimulus()
                self.myapp.taskMgr.step()  # main panda loop, needed for redrawing, etc.

        #self.remove_module()