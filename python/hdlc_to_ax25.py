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

import os, pty
import struct

import pmt
from gnuradio import gr
from datetime import datetime

from . import packet

class hdlc_to_ax25(gr.sync_block):
    """
    Converts an array of bytes into a AX25Packet object.

    Connect to the "HDLC Deframer", or a block which emits a PMT tuple of
    (None, bytearray)

    This module maintains statistics of packets seen in .count and .dropped

    .dropped counts the packets that failed do unpack due to state machine
    violations. Since the HDLC Deframer block silently drops packets that fail
    to match the checksum, we are unable to know how many packets failed.

    .count counts the number of APRS packets received. (For now, this library
    is only focusing on APRS)
    """
    def __init__(self):
        gr.sync_block.__init__(self,
                               name="hdlc_to_ax25",
                               in_sig=None,
                               out_sig=None)

        (self.pty_master, self.pty_slave) = pty.openpty()
        tty = os.ttyname(self.pty_slave)

        if os.path.islink('/tmp/kiss_pty'):
            os.unlink('/tmp/kiss_pty')
        os.symlink(tty, '/tmp/kiss_pty')

        print 'KISS PTY is: /tmp/kiss_pty (%s)' % os.ttyname(self.pty_slave)

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
            # TODO: Forward this packet on to other modules
            print packet.dump(pkt)

            if pkt.control == 0x03 and pkt.protocol_id == 0xf0:
                os.write(self.pty_master, packet.kiss_wrap_bytes(msg))
                self.count += 1
        except ValueError as e:
            print e
            self.dropped += 1

        print 'Count:', self.count
        print 'Dropped:', self.dropped
        print '-'*8

    def stop(self):
        print 'Closing PTYs'
        os.close(self.pty_master)
        os.close(self.pty_slave)
        try:
            os.unlink('/tmp/kiss_pty')
        except OSError:
            pass

        gr.sync_block.stop(self)
