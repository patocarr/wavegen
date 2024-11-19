#!/usr/bin/env python
# -*- coding: utf-8 -*-

# From:
# https://stackoverflow.com/questions/4083796/how-do-i-run-unittest-on-a-tkinter-app

import unittest
import tkinter as tk
from src.wavegen.wavegen import Wavegen


class WavegenTestCase(unittest.TestCase):
    """These methods are going to be the same for every GUI test,
    so refactored them into a separate class
    """
    def setUp(self):
        self.root=tk.Tk()
        self.pump_events()

    def tearDown(self):
        if self.root:
            self.root.destroy()
            self.pump_events()

    def pump_events(self):
        while self.root.dooneevent(tk._tkinter.ALL_EVENTS | tk._tkinter.DONT_WAIT):
            pass

class TestViewAskText(WavegenTestCase):
    def test_enter(self):
        v = Wavegen(self.root)
        self.pump_events()
        v.sampling.focus_set()
        v.sampling.insert(tk.END,u'2')
        v.sampling.event_generate('<FocusOut>')
        self.pump_events()

        #self.assertRaises(tk.TclError, lambda: v.frame.winfo_viewable())
        self.assertEqual(v.sampling.get(),u'6400.02')
        self.assertEqual(v.fname.get(),u'real_6400.02MHz_2.0MHz_8x_0.707a')


if __name__ == '__main__':
    import unittest
    unittest.main()

