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

# TODO: Pickle -> JSON
import pickle
import numpy as np
import Queue
import time

from gnuradio import gr
from bruninga import packet
import pmt


class ax25_fsk_mod(gr.sync_block):
    """
    A continuous phase FSK modulator for AX25 packets.
    
    When given an AX25 Packet, this block converts it to an audio stream with
    the given configured parameters. Two in question:

    - Flag Count: How many flags to put before and after the packet
    - Preamble Len (ms): How long to transmit a clock signal (01010101)

    The default values for the mark, space, and baud rate are configurable to
    allow for further experimentation. v.23 modems, for example, use 1300/2100
    tones to generate 1200 baud signals.
    """
    def __init__(self, samp_rate, preamble_len_ms, flag_count, mark_freq,
            space_freq, baud_rate):

        gr.sync_block.__init__(self,
            name="ax25_fsk_mod",
            in_sig=None,
            out_sig=[np.float32])

        self.samp_rate = samp_rate
        self.flag_count = flag_count
        self.mark_freq = mark_freq
        self.space_freq = space_freq
        self.baud_rate = baud_rate

        self.preamble_len_bits = int((preamble_len_ms / 1000.0) * baud_rate / 2)
        self.sps = int(1.0 * self.samp_rate / self.baud_rate)

        self.outbox = Queue.Queue()
        self.output_buffer = None
        self.opb_idx = 0

        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)

    def handle_msg(self, msg_pmt):
        msg = pmt.to_python(msg_pmt)
        if not (isinstance(msg, tuple) and len(msg) == 2):
            print 'Invalid Message: Expected tuple of len 2'
            print 'Dropping msg of type %s' % type(msg)
            return
        
        try:
            msg = pickle.loads(msg[1])
        except StandardError as e:
            print 'Bad format: Expected pickled AX25Packet'
            print str(e)
            return

        # TODO: Take list of AX25 packets VVVV
        if not isinstance(msg, packet.AX25Packet):
            print 'Expected AX25Packet, got %s' % type(msg)
            return

        self.outbox.put(msg)

    def ax25_to_fsk(self, msg):
        # TODO: Allow multiple messages to be strung together with
        #       one preamble

        # Generate message
        msg_bits = [0, 1] * self.preamble_len_bits
        msg_bits += msg.hdlc_wrap(self.flag_count, self.flag_count)

        # Calculate phase increments
        mark_pinc = 2 * np.pi * self.mark_freq / self.samp_rate
        space_pinc = 2 * np.pi * self.space_freq / self.samp_rate
        
        phase = 0
        opb = np.empty(len(msg_bits) * self.sps)
        for i, bit in enumerate(msg_bits):
            pinc = (mark_pinc if bit is 1 else space_pinc)
            phase += pinc

            tmp = np.arange(self.sps) * pinc + phase
            opb[i*self.sps:(i+1)*self.sps] = np.sin(tmp)

            phase = tmp[-1]

        return opb

    def work(self, input_items, output_items):
        out = output_items[0]
        idx = 0

        # TODO: Transmit cooldown period
        if self.output_buffer is None:
            if self.outbox.empty():
                # TODO: This is a bit of a hack to work around the ALSA Audio
                #       Sink being unhappy with underflows
                out[0:] = 0
                return len(out)

            self.output_buffer = self.ax25_to_fsk(self.outbox.get())
            self.opb_idx = 0

        # How many samples do we have left for each buffer?
        opb_left = len(self.output_buffer) - self.opb_idx
        out_left = len(out) - idx

        # Take the minimum, and copy them to out
        cnt = min(opb_left, out_left)
        out[idx:idx+cnt] = self.output_buffer[self.opb_idx:self.opb_idx+cnt]

        # Update counters
        idx += cnt
        self.opb_idx += cnt

        # If we run out of samples in the output buffer, we're done
        if self.opb_idx >= len(self.output_buffer):
            self.output_buffer = None

        # Fill the remaining buffer with zeros. Hack to help the ALSA audio sink
        # be happy.
        if idx < len(out):
            out[idx:] = 0

        return len(out)

