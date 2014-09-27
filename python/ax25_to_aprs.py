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

import sys
import pmt
from gnuradio import gr

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

    def handle_msg(self, msg):
        msg = bytearray(str(msg))

        pmsg = ''

        # TODO: Only parse the propper length of the source/dest fields
        # TODO: Parse the SSID, get to/from sorted out
        for i in xrange(0, len(msg), 7):
            # Do we have at least 7 more bytes?
            if (i + 6) >= len(msg):
                return

            callsign = msg[i:i+6]
            ssid = msg[i+6]

            for j in xrange(6):
                callsign[j] = callsign[j] >> 1

            pmsg += str(callsign) + '\n'

            if (ssid & 0x01) == 1:
                break

        i += 7

        # We need at least 4 more bytes, control, protocol, and
        # the CRC. If we don't have that, we gotta stop
        if (i + 4) > len(msg):
            return

        control = msg[i]
        i += 1
        pmsg += 'Control: ' + bin(control) + '\n'

        protocol = msg[i]
        i += 1
        pmsg += 'Protocol: ' + bin(protocol) + '\n'

        message = msg[i:-2]
        pmsg += 'Message: ' + str(msg[i:-2]) + '\n'

        checksum = msg[-2:]
        pmsg += 'Checksum(?): ' + str(checksum).encode('hex') + '\n'

        # TODO: Actually check the checksum
        if control == 0x03 and protocol == 0xf0: 
            self.count += 1
            print pmsg
            print 'Count:', self.count
            print '-'*8
