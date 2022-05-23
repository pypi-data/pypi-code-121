#!/usr/bin/env python3

import unittest
import datetime as dt

from freezegun import freeze_time

from pypomodoro.pomodoro import Pomodoro

class TestPomodoro(unittest.TestCase):

    def test_init(self):
        pom = Pomodoro(work_time=10,break_time=5)
        self.assertEqual(pom.pomo_number,1)
        self.assertEqual(pom.started,False)
        self.assertEqual(pom.start_time,None)
        self.assertEqual(pom.pomo_end_time,None)
        self.assertEqual(pom.break_end_time,None)
        self.assertEqual(pom.work_time,10)
        self.assertEqual(pom.break_time,5)

    def test_start(self):
        WORK_TIME = 10
        BREAK_TIME =5

        pom = Pomodoro(work_time=WORK_TIME,break_time=BREAK_TIME)

        with freeze_time(dt.datetime.now()):
            pom.start()
            self.assertEqual(pom.start_time, dt.datetime.now())
            self.assertEqual(
                pom.pomo_end_time,
                dt.datetime.now() + dt.timedelta(seconds=WORK_TIME * 60)
            )
            self.assertEqual(
                pom.break_end_time,
                pom.pomo_end_time + dt.timedelta(seconds=BREAK_TIME * 60)
            )
            self.assertEqual(pom.started, True)

    def test_get_state(self):
        WORK_TIME = 10
        BREAK_TIME =5

        pom = Pomodoro(work_time=WORK_TIME, break_time=BREAK_TIME)
        self.assertEqual(pom.get_state(), "init")

        with freeze_time(dt.datetime.now()) as frozen_time:
            pom.start()
            self.assertEqual(pom.get_state(), "pomo")
            
            frozen_time.tick((WORK_TIME * 60) + 1)
            self.assertEqual(pom.get_state(), "break")

            frozen_time.tick((WORK_TIME * 60) + (BREAK_TIME * 60))
            self.assertEqual(pom.get_state(), "done")

    def test_restart(self):
        WORK_TIME = 10
        BREAK_TIME =5

        pom = Pomodoro(work_time=WORK_TIME, break_time=BREAK_TIME)
        self.assertEqual(pom.get_state(), "init")

        pom.start()
        self.assertEqual(pom.get_state(), "pomo")
        self.assertEqual(pom.pomo_number, 1)

        with freeze_time(dt.datetime.now()):
            pom.restart()

            self.assertEqual(pom.get_state(), "pomo")
            self.assertEqual(pom.pomo_number, 2)

            self.assertEqual(pom.start_time, dt.datetime.now())
            self.assertEqual(
                pom.pomo_end_time,
                dt.datetime.now() + dt.timedelta(seconds=WORK_TIME * 60)
            )
            self.assertEqual(
                pom.break_end_time,
                pom.pomo_end_time + dt.timedelta(seconds=BREAK_TIME * 60)
            )
            self.assertEqual(pom.started, True)

if __name__ == '__main__':
    unittest.main()
