import time


class TimePassed:
    def __init__(self, operation):
        self.start_time = time.time()
        self.operation = operation

    def finish(self):
        print(
            f"--- {self.operation} completed in {time.time() - self.start_time} seconds ---")
