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


#ifndef INCLUDED_BRUNINGA_DIREWOLF_AGC_H
#define INCLUDED_BRUNINGA_DIREWOLF_AGC_H

#include <bruninga/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace bruninga {

    /*!
     * \brief A simplified version of the AGC found in WB2OSZ's direwolf
     *
     * \ingroup bruninga
     *
     */
    class BRUNINGA_API direwolf_agc : virtual public gr::sync_block
    {
     public:
      typedef boost::shared_ptr<direwolf_agc> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of bruninga::direwolf_agc.
       *
       * Each radio's FM pre-emphasis filter is unique. As such, this results
       * in the amplitudes of each tone varying transmission to transmisison.
       * This block forms a "moving average" between the peaks and valleys,
       * and scales the waveform appropriately.
       *
       * The algorithm is simple. If we see a "peak" (or valley) beyond the
       * current average, we do:
       *     new_peak = (sample * attack) + (old_peak * (1 - attack))
       *
       * Therefore, setting the attack parameter to "1.0" means the average
       * instantly becomes the sample value when greater than the current
       * average.
       *
       * If the sample is within the current average, we replace "attack" with
       * decay.
       *
       * The peak and valley waveforms are sent out to (optional) ports, which
       * can be plotted alongside the input waveform for confirmation of
       * parameter choice.
       *
       * Attack and decay are specified in floating point numbers between
       * 0.0 and 1.0. It is possible to set the numbers outside this range,
       * although behavior will likely be detrimental.
       */
      static sptr make(float attack, float decay);
    };

  } // namespace bruninga
} // namespace gr

#endif /* INCLUDED_BRUNINGA_DIREWOLF_AGC_H */

