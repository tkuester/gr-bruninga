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

import struct

import pmt
from gnuradio import gr
from datetime import datetime

import json
from . import packet
from pprint import pprint

class ax25_to_aprs(gr.sync_block):
    """
    docstring for block ax25_to_aprs
    """
    def __init__(self):
        gr.sync_block.__init__(self,
                               name="ax25_to_aprs",
                               in_sig=None,
                               out_sig=None)

        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)
        self.count = 0
        self.dropped = 0

    def handle_msg(self, msg_pmt):
        msg_pmt = pmt.pmt_to_python.pmt_to_python(msg_pmt)
        if not isinstance(msg_pmt, tuple):
            return
        if len(msg_pmt) != 2:
            return

        msg = bytearray(msg_pmt[1])

        try:
            pkt = packet.from_bytes(msg)
            packet.dump(pkt)

            if pkt.control == 0x03 and pkt.protocol_id == 0xf0:
                self.count += 1
        except ValueError as e:
            print e
            self.dropped += 1

        print 'Count:', self.count
        print 'Dropped:', self.dropped
        print '-'*8
