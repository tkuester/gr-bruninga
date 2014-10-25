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
from bruninga import packet
import pmt
import Queue

class aprs_gen(gr.sync_block):
    """
    docstring for block aprs_gen
    """
    def __init__(self, src, dest, via, preamble_len_ms):
        gr.sync_block.__init__(self,
            name="aprs_gen",
            in_sig=None,
            out_sig=[numpy.byte])

        self.src = packet.string_to_address(src)
        self.dest = packet.string_to_address(dest)
        self.via = []

        if isinstance(via, str):
            self.via.append(packet.string_to_address(via))
        else:
            for v in via:
                self.via.append(packet.string_to_address(v))

        self.preamble_cnt = int(numpy.ceil(preamble_len_ms / (8.0 / 1200 *
            1000))) + 1

        self.outbox = Queue.Queue()
        self.active_msg = None
        self.active_idx = 0

        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)

    def handle_msg(self, msg_pmt):
        msg = pmt.to_python(msg_pmt)
        if isinstance(msg, tuple) and len(msg) == 2:
            msg = str(bytearray(msg[1]))[:-1]

            p = packet.AX25Packet()
            p.src = self.src
            p.dest = self.dest
            p.digipeaters = self.via
            p.control = 0x03
            p.protocol_id = 0xf0
            p.info = msg

            self.outbox.put(p)
            print 'Recv', p

    def work(self, input_items, output_items):
        out = output_items[0]

        if self.active_msg is None:
            if self.outbox.empty():
                return 0

            self.active_msg = self.outbox.get()
            self.active_idx = 0
            self.active_msg = self.active_msg.hdlc_wrap(self.preamble_cnt, 10)

        out_idx = 0
        while (
                out_idx < len(out) and
                self.active_idx < len(self.active_msg)
              ):
            out[out_idx] = self.active_msg[self.active_idx]
            self.active_idx += 1
            out_idx += 1
        
        if self.active_idx >= len(self.active_msg):
            self.active_msg = None

        return out_idx
