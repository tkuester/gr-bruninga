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

from gnuradio import gr
from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from scipy import signal
import math
import bruninga

class fsk_demod(gr.hier_block2):
    """
    Tidied up version of the demodulator found in examples/aprs-rx.grc

    samp_rate should be the incoming audio sample rate.
    """
    def __init__(self, inc_samp_rate):
        gr.hier_block2.__init__(self,
            "fsk_demod",
            gr.io_signature(1, 1, gr.sizeof_float),  # Input signature
            gr.io_signature(1, 1, gr.sizeof_char) # Output signature
        )

        self.inc_samp_rate = inc_samp_rate

        self.sps = sps = 4
        self.baud_rate = baud_rate = 1200
        self.samp_rate = samp_rate = sps * baud_rate * 4
        self.mark = mark = 2200
        self.space = space = 1200
        self.center = center = int((mark + space) / 2)

        ##################################################
        # Blocks
        ##################################################
        # Stage 1: Force resampling to 19.2ksps
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=samp_rate,
                decimation=self.inc_samp_rate,
                taps=None,
                fractional_bw=None,
        )

        # Stage 2: Bandpass Filter
        self.bpf_width = bpf_width = 800
        self.bpf_trans = bpf_trans = 200

        self.band_pass_filter_0 = filter.fir_filter_fff(1, firdes.band_pass(
            1, samp_rate, 1700-bpf_width, 1700+bpf_width, bpf_trans, firdes.WIN_RECTANGULAR, 6.76))

        # Stage 3: Tone Detection
        self.window_len = window_len = self.samp_rate/self.baud_rate*2
        self.window = window = signal.windows.cosine(window_len)

        self.freq_xlating_fir_filter_xxx_0_0 = filter.freq_xlating_fir_filter_fcf(4, (window), mark, samp_rate)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_fcf(4, (window), space, samp_rate)
        self.blocks_complex_to_mag_0_0 = blocks.complex_to_mag(1)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)

        # Stage 4: AGC
        self.decay = decay = 0.00022
        self.attack = attack = 0.8
        self.bruninga_direwolf_agc_0_0 = bruninga.direwolf_agc(attack, decay)
        self.bruninga_direwolf_agc_0 = bruninga.direwolf_agc(attack, decay)
        self.blocks_sub_xx_1 = blocks.sub_ff(1)

        # Stage 5: Clock Recovery
        self.gain_mu = gain_mu = 0.45

        self.digital_clock_recovery_mm_xx_0 = digital.clock_recovery_mm_ff(self.sps*(1+0.0), 0.25*gain_mu*gain_mu, 0.5, gain_mu, 0.05)

        # Stage 6: Differential Decoding
        self.digital_diff_decoder_bb_0 = digital.diff_decoder_bb(2)
        self.blocks_not_xx_0 = blocks.not_bb()
        self.blocks_and_const_xx_0 = blocks.and_const_bb(1)

        # Stage 7: Output
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()

        ##################################################
        # Connections
        ##################################################
        self.connect((self, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.band_pass_filter_0, 0))

        self.connect((self.band_pass_filter_0, 0), (self.freq_xlating_fir_filter_xxx_0_0, 0))
        self.connect((self.band_pass_filter_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))

        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0_0, 0), (self.blocks_complex_to_mag_0_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.bruninga_direwolf_agc_0, 0))
        self.connect((self.blocks_complex_to_mag_0_0, 0), (self.bruninga_direwolf_agc_0_0, 0))

        self.connect((self.bruninga_direwolf_agc_0_0, 0), (self.blocks_sub_xx_1, 1))
        self.connect((self.bruninga_direwolf_agc_0, 0), (self.blocks_sub_xx_1, 0))
        self.connect((self.blocks_sub_xx_1, 0), (self.digital_clock_recovery_mm_xx_0, 0))

        self.connect((self.digital_clock_recovery_mm_xx_0, 0), (self.digital_binary_slicer_fb_0, 0))

        self.connect((self.digital_diff_decoder_bb_0, 0), (self.blocks_not_xx_0, 0))
        self.connect((self.blocks_not_xx_0, 0), (self.blocks_and_const_xx_0, 0))
        self.connect((self.blocks_and_const_xx_0, 0), (self, 0))

        self.connect((self.digital_binary_slicer_fb_0, 0), (self.digital_diff_decoder_bb_0, 0))
