from PyDAQmx import *
from multiprocessing import Process
import time

class FrameCounter(Process):
    def __init__(self, shared):

        self.taskHandle = TaskHandle()
        self.frameCount = uInt32()
        self.shared = shared
    def run(self):
        try:
            # DAQmx Configure Code
            DAQmxCreateTask("",byref(self.taskHandle))
            DAQmxCreateCICountEdgesChan(taskHandle,"Dev1/ctr0","", DAQmx_Val_Rising, 0, DAQmx_Val_CountUp)

            # DAQmx Start Code
            DAQmxStartTask(taskHandle)
            while self.shared.main_program_still_running.value == 1:
                DAQmxReadCounterScalarU32(taskHandle, 10.0, byref(self.frameCount), None)
                self.shared.frameCount.value = self.frameCount.value
                time.sleep(0.005)

        except DAQError as err:
                print("DAQmx Error: %s"%err)
        finally:
            if self.taskHandle:
                DAQmxStopTask(self.taskHandle)
                DAQmxClearTask(self.taskHandle)

