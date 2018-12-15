import time

from datetime import date, datetime, timedelta
from calendar import Calendar, monthrange, day_name, month_name
import numpy as np
from geopy.geocoders import Nominatim
from tabulate import tabulate

MINUTE_IN_HOUR = 60
HOUR_IN_DAY = 24
DAY_IN_WEEK = 7
WEEK_IN_MONTH = 4
MONTH_IN_YEAR = 12


DATE = datetime.now()
TIMEZONE = time.tzname
CALENDAR = "GREGORIAN"

START = DATE.year
# Year 2038 problem
# https://en.wikipedia.org/wiki/Year_2038_problem
END = 2038

DEFAULT_INTERVAL = 30
U_INTERVAL = "min"

GEO = Nominatim(user_agent="FreeTime")


class Space(object):
    """

    """
    def __init__(self, num, state=False, title=" ", description=" ", *args, **kwargs):

        self._num = num
        self._state = state

        if state:
            self._title = title
            self._description = description
        else:
            self._title = None
            self._description = None

    @property
    def num(self):
        return self._num

    @num.setter
    def num(self, n):
        self._num = n

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, t):
        self._title = t

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, desc):
        self._description = desc

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, opt):
        self._state = opt

    def is_free(self):
        if self._state:
            return True
        return False


class TimeSpace(Space):
    """

    """

    def __init__(self, start, location='', interval=DEFAULT_INTERVAL, *args, **kwargs):
        super(TimeSpace, self).__init__(*args, **kwargs)

        self._interval = interval
        self._start = start
        self._end = start + interval
        self._location = location

    @property
    def location(self):
        return GEO.geocode(self._location)

    @location.getter
    def location(self):
        return self._location

    @location.setter
    def location(self, geo):
        self._location = geo

    @property
    def start(self):
        return self._start

    @property
    def hours_start(self):
        if self.start >= 1440:
            hours_start = str(timedelta(minutes=self.start))[7:11]
        else:
            hours_start = str(timedelta(minutes=self.start))[:-3]

        return hours_start

    @start.setter
    def start(self, begin):
        self._start = begin

    @property
    def end(self):
        return self._end

    def str(self, visible=False):
        if self.state or visible:

            hours_start = str(timedelta(minutes=self.start))[:-3]
            hours_end = str(timedelta(minutes=self.end))[:-3]

            if self.start >= 1440:
                hours_start = str(timedelta(minutes=self.start))[7:11]
            elif self.end >= 1440:
                hours_end = str(timedelta(minutes=self.end))[7:11]

            return tabulate([["Start:", hours_start],
                             ["End:", hours_end]], tablefmt="plain")
        else:
            return " "


class DaySpace(Space):
    """

    """

    def __init__(self, day, *args, **kwargs):
        super(DaySpace, self).__init__(*args, **kwargs)

        self._day = day

        if U_INTERVAL == 'min':
            self._n_space = int((HOUR_IN_DAY * MINUTE_IN_HOUR) / DEFAULT_INTERVAL)
        elif U_INTERVAL == 'h':
            self._n_space = int(HOUR_IN_DAY / DEFAULT_INTERVAL)

        self._list = np.empty(self._n_space, dtype=object)

        self.init()

    def init(self):
        for i in range(self._n_space):
            self._list[i] = TimeSpace(num=int(i), start=i * DEFAULT_INTERVAL)

    @property
    def list(self):
        return self._list

    @property
    def num_space(self):
        return self._n_space

    @property
    def day(self):
        return self._day

    @day.setter
    def day(self, d):
        self._day = d

    def get_space(self, index):
        return self._list[index]

    def fill_gap(self, start, end):
        for i in range(start, end):
            self.get_space(i).state = True

    def auto_fill(self):
        edge = []
        loop_iter = 0
        for i in range(self._n_space):
            if self.get_space(i).state and self.get_space(i+1).state is False:
                edge.append(i)

        print(edge)
        for j in range(int(len(edge)/2)):
                self.fill_gap(edge[j + loop_iter], edge[j + loop_iter + 1])
                loop_iter = loop_iter + 1

    def str(self, visible=False):
        day_grid = []
        for i in range(self._n_space):
            if self.list[i].state or visible:
                day_grid.append([self.list[i].num, self.list[i].str()])

            elif visible is False:
                day_grid.append([self.list[i].num, " "])
            else:
                day_grid.append([" "])
        return tabulate(day_grid, tablefmt="grid")


class WeekSpace(Space):
    """

    """

    def __init__(self, week, *args, **kwargs):
        super(WeekSpace, self).__init__(*args, **kwargs)

        self._week = week
        self._list = np.empty(DAY_IN_WEEK, dtype=object)

        self.init()

    def init(self):
        for i in range(DAY_IN_WEEK):
            self._list[i] = DaySpace(num=i, day=day_name[i])

    @property
    def list(self):
        return self._list

    @property
    def week(self):
        return self._week

    @week.setter
    def week(self, w):
        self._week = w

    def get_day(self, index):
        return self._list[index]

    def get_space(self, day, space):
        return self._list[day].list[space]

    def cmp_week(self, week):
        free_time = [[0 for x in range(self.list[0].num_space)] for x in range(DAY_IN_WEEK)]
        for i in range(DAY_IN_WEEK):
            for j in range(self.list[0].num_space):
                if self.list[i].list[j].state == week.list[i].list[j].state:
                    free_time[i][j] = True
                else:
                    free_time[i][j] = False
        return free_time

    def str(self, visible=True):
        week_header = []
        week_grid = [[]]
        for i in range(DAY_IN_WEEK):
            weekday = self.list[i].str()
            week_header.append(self.list[i].day)
            week_grid[0].append(weekday)
        if visible:
            return tabulate(week_grid, headers=week_header, tablefmt="grid")


class MonthSpace(Space):
    """

    """
    def __init__(self, month, *args, **kwargs):
        super(MonthSpace, self).__init__(*args, **kwargs)

        self._month = month

        self._list = np.empty(WEEK_IN_MONTH, dtype=object)

        self.init()

    def init(self):
        for i in range(WEEK_IN_MONTH):
            self._list[i] = WeekSpace(num=i, week=i)

    @property
    def list(self):
        return self._list

    @property
    def month(self):
        return self._month

    @month.setter
    def month(self, m):
        self._month = m


class YearSpace(Space):
    """

    """

    def __init__(self, year, *args, **kwargs):
        super(YearSpace, self).__init__(*args, **kwargs)

        self._year = year

        if self.leap_year(year):
            self._n_day = 366
        self._n_day = 365

        self._list = np.empty(MONTH_IN_YEAR, dtype=object)

        self.init()

    def init(self):
        for i in range(MONTH_IN_YEAR):
            self._list[i] = MonthSpace(num=i, month=month_name[i])
    
    @property
    def list(self):
        return self._list
    
    def leap_year(self, y):
        """
        The method leapyear returns True if the parameter year
        is a leap year, False otherwise
        """
        if not y % 4 == 0:
            return False
        elif not y % 100 == 0:
            return True
        elif not y % 400 == 0:
            return False
        else:
            return True

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, y):
        self._year = y


if __name__ == '__main__':

    Week = WeekSpace(0, 0)

    Week.list[0].list[0].state = True
    Week.list[0].list[9].state = True

    Week.list[0].list[11].state = True
    Week.list[0].list[14].state = True

    Week.list[0].list[16].state = True
    Week.list[0].list[19].state = True

    Week.list[1].list[44].state = True
    Week.list[1].list[46].state = True

    Week.get_day(0).auto_fill()
    print(Week.str(True))

