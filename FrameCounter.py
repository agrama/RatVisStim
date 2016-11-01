import PyDAQmx as PyDAQ
from multiprocessing import Process
import time

class FrameCounter(Process):
    def __init__(self, shared):
        Process.__init__(self)
        self.shared = shared
    def run(self):
        taskHandle = PyDAQ.TaskHandle()
        frameCount = PyDAQ.uInt32()
        try:
            # DAQmx Configure Code
            PyDAQ.DAQmxCreateTask("", PyDAQ.byref(taskHandle))
            PyDAQ.DAQmxCreateCICountEdgesChan(taskHandle,"Dev1/ctr0","", PyDAQ.DAQmx_Val_Rising, 0, PyDAQ.DAQmx_Val_CountUp)

            # DAQmx Start Code
            PyDAQ.DAQmxStartTask(taskHandle)
            while self.shared.main_programm_still_running.value:
                PyDAQ.DAQmxReadCounterScalarU32(taskHandle, 10.0, PyDAQ.byref(frameCount), None)
                # print(frameCount.value)
                self.shared.frameCount.value = frameCount.value
                time.sleep(0.005) # this prevents this loop from over exerting the processor

        except PyDAQ.DAQError as err:
                print("DAQmx Error: %s" % err)
        finally:
            if taskHandle:
                PyDAQ.DAQmxStopTask(taskHandle)
                PyDAQ.DAQmxClearTask(taskHandle)
                print('DAQ Task Deleted')
#
# if __name__ == "__main__":
#     fc = FrameCounter()
#     fc.run()
