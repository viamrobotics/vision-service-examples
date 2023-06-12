import datetime
from collections import deque


# This class helps tracks the frame per second
class Fps:
    ordered_frames = None

    def __init__(self):
        self.prev_get = datetime.datetime.now()
        self.ordered_frames = deque()
        self.cached_fps = 0

    # call record just after each GetImage request to record the time stamp
    def record(self) -> None:
        self.ordered_frames.append(datetime.datetime.now())

    # Returns the FPS. This function returns a new value at most once per second to avoid noise
    def get(self) -> int:
        # only update once a second
        if datetime.datetime.now() - self.prev_get < datetime.timedelta(seconds=1):
            return self.cached_fps

        one_sec_ago = datetime.datetime.now() - datetime.timedelta(seconds=1)
        # evict datetimes greater than one sec ago, i.e., datetimes smaller than now()-one_sec_ago
        while self.ordered_frames[0] < one_sec_ago:
            self.ordered_frames.popleft()

        self.prev_get = datetime.datetime.now()
        self.cached_fps = len(self.ordered_frames)
        return self.cached_fps
