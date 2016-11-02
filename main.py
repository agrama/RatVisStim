if __name__ == "__main__":

    from shared import Shared
    import time
    shared = Shared()
    shared.start_threads()
    for i in range(100):
        print("Beautiful girl, i slept with #{:05d} - {}".format(i, shared.frameCount.value))

        if i > 80:
            shared.theta.value = 30
        time.sleep(0.1)


    shared.main_programm_still_running.value = 0