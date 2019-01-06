import sys
import csv
from calendar import day_name
from datetime import timedelta
import numpy as np

from base import WeekSpace, DAY_IN_WEEK

class ImportFile(object):
    """

    """
    def __init__(self, fname):
        self._fname = fname

    def base(self):
        pass

    def csv(self, debug=False):
        """

        """
        reader = csv.reader(open(self._fname, newline=''), delimiter=',', quotechar='|')

        raw = []
        data = []

        for line in reader:
            raw.append(line)
            if debug:
                print(','.join(line))

        for line in raw:
            data.append(line)

        return data


class ExportFile(object):
    """

    """

    def __init__(self, week, fname):
        self.week = week
        self._fname = fname

    def base(self):
        pass

    def csv(self, debug=False):
        with open(self._fname, 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

            index = []
            sub_index = []

            num = []
            title = []
            description = []
            state = []
            start = []
            end = []

            loop_iter = 0

            for j in range(self.week.get_day(0).num_space):
                for i in range(DAY_IN_WEEK):

                    sub_index.append(loop_iter)

                    if i % 7 == 6:
                        index.append(sub_index)
                        sub_index = []

                    num.append(str(self.week.get_space(i, j).num))
                    title.append(self.week.get_space(i, j).title)
                    description.append(self.week.get_space(i, j).description)
                    state.append(str(self.week.get_space(i, j).state))

                    min_start = self.week.get_space(i, j).start
                    min_end = self.week.get_space(i, j).end

                    hours_start = str(timedelta(minutes=min_start))[:-3]
                    hours_end = str(timedelta(minutes=min_end))[:-3]

                    if min_start >= 1440:
                        hours_start = str(timedelta(minutes=min_start))[7:11]
                    elif min_end >= 1440:
                        hours_end = str(timedelta(minutes=min_end))[7:11]

                    start.append(str(hours_start))
                    end.append(str(hours_end))

                    loop_iter = loop_iter + 1

            for l in range(DAY_IN_WEEK):
                for k in range(self.week.get_day(0).num_space):
                    writer.writerow(np.take(num, index[k]))
                    writer.writerow(np.take(title, index[k]))
                    writer.writerow(np.take(description, index[k]))
                    writer.writerow(np.take(state, index[k]))
                    writer.writerow(np.take(start, index[k]))
                    writer.writerow(np.take(end, index[k]))


if __name__ == '__main__':

    ImportFile("FreeTime.csv").csv()
    # ExportFile(WeekSpace(0, 0), 'FreeTime.csv').csv()

