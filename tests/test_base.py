import unittest
import pytest

from base import *

def test_Space():
    pass


def test_TimeSpace():
    pass


def test_DaySpace():
    pass


def test_WeekSpace():
    Week = WeekSpace(0, 0)

    Week_fill = WeekSpace(0, 0)

    Week_fill.get_space(0, 0).state = True
    Week_fill.get_space(0, 9).state = True
    Week_fill.get_space(0, 11).state = True
    Week_fill.get_space(0, 14).state = True

    Week_cmp = WeekSpace(0, 0)
    Week_cmp.get_space(0, 1).state = True

    test_cmp = [[True for x in range(Week_cmp.get_day(0).num_space)] for x in range(DAY_IN_WEEK)]
    test_cmp[0][1] = False

    assert Week.cmp_week(Week_cmp)[0] == test_cmp[0]


def test_MonthSpace():
    pass


def test_YearSpace():
    test_year = YearSpace(DATE.year, DATE.year, state=True)
    assert test_year.list[0].list[0].list[0].list[0].num == 0

