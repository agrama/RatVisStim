if __name__ == "__main__":

    from shared import Shared
    import time
    shared = Shared()
    shared.start_threads()
    while shared.main_programm_still_running.value:
        time.sleep(0.1)
        None



    shared.main_programm_still_running.value = 0