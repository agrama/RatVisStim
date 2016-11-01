from PyDAQmx import *# Declaration of variable passed by referencetaskHandle = TaskHandle()read = uInt32()try:    # DAQmx Configure Code    DAQmxCreateTask("",byref(taskHandle))    DAQmxCreateCICountEdgesChan(taskHandle,"Dev1/ctr0","", DAQmx_Val_Rising, 0, DAQmx_Val_CountUp)    # DAQmx Start Code    DAQmxStartTask(taskHandle)    # DAQmx Read Code    while True:        DAQmxReadCounterScalarU32(taskHandle, 10.0, byref(read), None)        print(read)except DAQError as err:    print("DAQmx Error: %s"%err)finally:    if taskHandle:        # DAQmx Stop Code        DAQmxStopTask(taskHandle)        DAQmxClearTask(taskHandle)