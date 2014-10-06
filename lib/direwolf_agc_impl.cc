/* -*- c++ -*- */
/* 
 * Copyright 2014 <+YOU OR YOUR COMPANY+>.
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "direwolf_agc_impl.h"

namespace gr {
  namespace bruninga {

    direwolf_agc::sptr
    direwolf_agc::make(float attack, float decay)
    {
      return gnuradio::get_initial_sptr
        (new direwolf_agc_impl(attack, decay));
    }

    /*
     * The private constructor
     */
    direwolf_agc_impl::direwolf_agc_impl(float attack, float decay)
      : gr::sync_block("direwolf_agc",
              gr::io_signature::make(1, 1, sizeof(float)),
              gr::io_signature::make(1, 3, sizeof(float))),
        d_attack(attack), d_decay(decay),
        d_peak(1), d_valley(0)
    {
    }

    /*
     * Our virtual destructor.
     */
    direwolf_agc_impl::~direwolf_agc_impl()
    {
    }

    int
    direwolf_agc_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        const float *in = (const float*) input_items[0];
        float *out = (float*) output_items[0];
        float *peak_out = NULL;
        float *valley_out = NULL;

        if(output_items.size() == 3)
        {
            peak_out = (float*)output_items[1];
            valley_out = (float*)output_items[2];
        }

        // Taken from WB2OSZ's Direwolf demodulator
        for(int i = 0; i < noutput_items; i++)
        {
            if(in[i] >= d_peak)
            {
                d_peak = in[i] * d_attack + d_peak * (1.0 - d_attack);
            }
            else
            {
                d_peak = in[i] * d_decay + d_peak * (1.0 - d_decay);
            }
            if(peak_out != NULL)
            {
                peak_out[i] = d_peak;
            }

            if(in[i] < d_valley)
            {
                d_valley = in[i] * d_attack + d_valley * (1.0 - d_attack);
            }
            else
            {
                d_valley = in[i] * d_decay + d_valley * (1.0 - d_decay);
            }
            if(valley_out != NULL)
            {  
                valley_out[i] = d_valley;
            }

            if(d_peak > d_valley)
            {
                out[i] = (in[i] - 0.5 * (d_peak + d_valley)) / (d_peak - d_valley);
                if(out[i] > 5)
                {
                    out[i] = 5;
                }
                else if(out[i] < -5)
                {
                    out[i] = -5;
                }
            }
            else
            {
                out[i] = 0;
            }
        }

        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace bruninga */
} /* namespace gr */

