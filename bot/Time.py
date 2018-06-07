import time


SEC_IN_DAY = 86400
SEC_IN_15_MIN = 900
SHIFT_FROM_GTM = 10800


class Lecture:
    count = 0
    time_of_lec_ending = [33600, 39900, 46200, 53100, 59400, 65700]

    def __init__(self):
        self.current_num = self.get_cur_lec_num()

    def get_cur_lec_num(self):
        cur_time = (int(time.time()) % SEC_IN_DAY) + SHIFT_FROM_GTM
        for i in range(len(self.time_of_lec_ending)):
            if self.time_of_lec_ending[i] > cur_time:
                return i + 1
        return 1

    def is_ended(self):
        # TODO вот та точка!
        # if self.count == 0:
        #     self.count += 1
        #     return True
        # else:
        #     return False
        # TODO возможно это неправильно
        cur_time = (int(time.time()) % SEC_IN_DAY) + SHIFT_FROM_GTM
        time_after_lec = cur_time - self.time_of_lec_ending[self.current_num - 1]
        if 0 < time_after_lec < SEC_IN_15_MIN:
            return True
        return False

    def next(self):
        if self.current_num >= len(self.time_of_lec_ending):
            self.current_num = 1
        else:
            self.current_num += 1
