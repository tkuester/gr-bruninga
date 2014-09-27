#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2014 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import time

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from ax25_deframer import ax25_deframer

class qa_ax25_deframer (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        test_data = [0,1,1,0,1,0] * 10      # Garbage
        test_data += [0,1,1,1,1,1,1,0] * 3  # Hex 0x7e
        test_data += [0,1,1,0,1,0,0,0] * 19 # Hex 0x16
        test_data += [1,1,1,1,1,0,1,1,1]    # Hex 0xff
        test_data += [0,0,0,0,0,0,0,0]      # Hex 0x00
        test_data += [0,1,1,1,1,1,1,0] * 2  # Hex 0x7e

        src = blocks.vector_source_b(test_data)
        uut = ax25_deframer()
        sink = blocks.message_debug()

        self.tb.connect(src, uut)
        self.tb.msg_connect(uut, 'out', sink, 'store')

        self.tb.start()
        time.sleep(0.1)
        self.tb.stop()
        self.tb.wait()

        # check data
        self.assertEqual(sink.num_messages(), 1)
        self.assertEqual(str(sink.get_message(0)), '\x16'*19 + '\xff\x00')

    def test_002_t (self):
        test_data = [0,1,1,0,1,0] * 10      # Garbage
        test_data += [0,1,1,1,1,1,1,0] * 3  # Hex 0x7e
        test_data += [0,1,1,0,1,0,0,0] * 19 # Hex 0x16
        test_data += [0,1,1,1,1,1,1,1]      # State error
        test_data += [0,1,1,0,1,0] * 10     # Garbage
        test_data += [0,1,1,1,1,1,1,0] * 3  # Hex 0x7e
        test_data += [0,1,1,0,1,0,0,0] * 19 # Hex 0x16
        test_data += [1,1,1,1,1,0,1,1,1]      # State error
        test_data += [0,0,0,0,0,0,0,0]      # Hex 0x00
        test_data += [0,1,1,1,1,1,1,0] * 2  # Hex 0x7e

        src = blocks.vector_source_b(test_data)
        uut = ax25_deframer()
        sink = blocks.message_debug()

        self.tb.connect(src, uut)
        self.tb.msg_connect(uut, 'out', sink, 'store')

        self.tb.start()
        time.sleep(0.1)
        self.tb.stop()
        self.tb.wait()

        # check data
        self.assertEqual(sink.num_messages(), 1)
        self.assertEqual(str(sink.get_message(0)), '\x16'*19 + '\xff\x00')

if __name__ == '__main__':
    gr_unittest.run(qa_ax25_deframer, "qa_ax25_deframer.xml")
