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

import numpy
from gnuradio import gr
import pmt
from collections import deque

STATE_IDLE = 0
STATE_BEGIN_FRAME = 1

class ax25_deframer(gr.sync_block):
    """
    docstring for block ax25_deframer
    """

    def __init__(self):
        gr.sync_block.__init__(self,
            name="ax25_deframer",
            in_sig=[numpy.byte],
            out_sig=None)

        self.deq = deque(maxlen=8)
        self.processing_hldc = False
        self.one_count = 0
        self.hdlc_bytes = []

        self.message_port_register_out(pmt.intern('out'))

    def work(self, input_items, output_items):
        in0 = input_items[0]

        for bit in in0:
            self.process_bit(bit & 0x01)

        return len(input_items[0])

    def process_bit(self, bit):
        # Wait for flag byte (~, 0x7e)
        if not self.processing_hldc:
            self.deq.append(bit)

            if len(self.deq) == 8 and self.deque_to_byte() == 0x7e:
                self.deq.clear()
                self.processing_hldc = True
                self.one_count = 0
                self.hldc_bytes = []

            return

        # Drop stuffed bits
        if bit == 0 and self.one_count == 5:
            self.one_count = 0
            return

        self.deq.append(bit)

        # Keep track of consecutive 1's... state error if > 6
        if bit == 1:
            self.one_count += 1
            if self.one_count > 6:
                # State Error? Was expecting 0x7e, got 0x7f
                self.processing_hldc = False
        else:
            self.one_count = 0

        # We're done, unless we have 8 bits to process
        if len(self.deq) < 8:
            return

        # Grab the byte
        byte = self.deque_to_byte()

        # If we see a framing byte
        if byte == 0x7e:
            # Assume a valid message if we have between 19 and 330 bytes
            if len(self.hldc_bytes) >= 19 and len(self.hldc_bytes) <= 330:
                #print ''.join([chr(c) for c in self.hldc_bytes])
                packet = ''.join([chr(c) for c in self.hldc_bytes])
                packet = pmt.intern(packet)
                self.message_port_pub(pmt.intern('out'), packet)

            # Clear, and keep processing
            # Remember, two packets can be back to back w/ flags
            self.deq.clear()
            self.processing_hldc = True
            self.one_count = 0
            self.hldc_bytes = []

        # Assume byte is part of message, append
        else:
            self.hldc_bytes.append(self.deque_to_byte(True))

        # Clear the array of bits
        self.deq.clear()

    def deque_to_byte(self, reverse=False):
        deq = self.deq
        if reverse:
            deq.reverse()

        return (deq[0] << 7) | (deq[1] << 6) | (deq[2] << 5) | \
                (deq[3] << 4) | (deq[4] << 3) | (deq[5] << 2) | \
                (deq[6] << 1) | deq[7]

