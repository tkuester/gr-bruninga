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
        msg_pmt = pmt.pmt_to_python.pmt_to_python(msg)
        if not isinstance(msg_pmt, tuple):
            return
        if len(msg) != 2:
            return

        msg = bytearray(msg_pmt[1])

        packet = {}
        packet['raw_bytes'] = msg
        packet['digipeaters'] = []

        # TODO: Only parse the propper length of the source/dest fields
        # TODO: Parse the SSID, get to/from sorted out
        address_count = 0
        for i in xrange(0, len(msg), 7):
            # Do we have at least 7 more bytes?
            if (i + 6) >= len(msg):
                self.dropped += 1
                return

            callsign = msg[i:i+6]
            ssid = msg[i+6]

            for j in xrange(6):
                # We're going to treat the LSB as a don't care.
                # Protocol does not specify what to do if this is a 1
                callsign[j] = callsign[j] >> 1

            if address_count == 0:
                packet['destination'] = {
                        'callsign': str(callsign).strip(),
                        'ssid': (ssid >> 1) & 0x0f,
                        'repeated': (ssid & 0x80) == 0x80
                        }
            elif address_count == 1:
                packet['source'] = {
                        'callsign': str(callsign).strip(),
                        'ssid': (ssid >> 1) & 0x0f,
                        'repeated': (ssid & 0x80) == 0x80
                        }
            elif address_count < 10:
                packet['digipeaters'].append({
                        'callsign': str(callsign).strip(),
                        'ssid': (ssid >> 1) & 0x0f,
                        'repeated': (ssid & 0x80) == 0x80
                        })
            else:
                # More than 10 addresses means we probably
                # have an invalid packet, a bit got flipped somewhere
                self.dropped += 1
                return

            address_count += 1

            if (ssid & 0x01) == 1:
                break

        if address_count < 2:
            self.dropped += 1
            return

        i += 7

        # We need at least 2 more bytes, control, and protocol
        # If we don't have that, we gotta stop
        if (i + 2) > len(msg):
            return

        packet['control'] = msg[i]
        i += 1

        packet['protocol'] = msg[i]
        i += 1

        packet['message'] = str(msg[i:])
        packet['timestamp'] = datetime.now()

        if (packet['control'] & 0x03) == 0x03 and packet['protocol'] == 0xf0: 
            dump_packet(packet)
            self.count += 1
            print 'Count:', self.count
            print 'Dropped:', self.dropped
            print '-'*8
        else:
            self.dropped += 1

def dump_packet(packet):
    ret = '%s-%d>' % (packet['source']['callsign'], packet['source']['ssid'])

    for station in packet['digipeaters']:
        ret += '%s-%d>' % (station['callsign'], station['ssid'])

    ret += '%s-%d:' % (packet['destination']['callsign'], packet['destination']['ssid'])
    ret += str(packet['message'])

    print ret
