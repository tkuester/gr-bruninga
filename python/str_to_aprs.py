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
import pickle

class str_to_aprs(gr.sync_block):
    """
    A block which turns messages (or short strings) into packets.

    Connect to the "Socket PDU" to transmit strings received over a TCP port.

    src - The callsign originating the packet ie: "KB3VOZ-1"
    dest - Same as above
    via - The list of digipeaters as a python array. ie: ['WIDE1-1', 'WIDE2-1']
    """
    def __init__(self, src, dest, via):
        gr.sync_block.__init__(self,
            name="str_to_aprs",
            in_sig=None,
            out_sig=None)

        self.src = packet.string_to_address(src)
        self.dest = packet.string_to_address(dest)
        self.via = []

        if isinstance(via, str):
            self.via.append(packet.string_to_address(via))
        else:
            for v in via:
                self.via.append(packet.string_to_address(v))

        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)

        self.message_port_register_out(pmt.intern('out'))

    def handle_msg(self, msg_pmt):
        msg = pmt.to_python(msg_pmt)
        if not (isinstance(msg, tuple) and len(msg) == 2):
            print 'Expected tuple of (None, str)'
            return

        msg = str(bytearray(msg[1]))[:-1]

        p = packet.AX25Packet()
        p.src = self.src
        p.dest = self.dest
        p.digipeaters = self.via
        p.control = 0x03
        p.protocol_id = 0xf0
        p.info = msg

        out = (None, pickle.dumps(p))
        self.message_port_pub(pmt.intern('out'), pmt.to_pmt(out))

    def work(self, input_items, output_items):
        print 'No call'
        return 0
