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
     * \brief <+description of block+>
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
       * To avoid accidental use of raw pointers, bruninga::direwolf_agc's
       * constructor is in a private implementation
       * class. bruninga::direwolf_agc::make is the public interface for
       * creating new instances.
       */
      static sptr make(float attack, float decay);
    };

  } // namespace bruninga
} // namespace gr

#endif /* INCLUDED_BRUNINGA_DIREWOLF_AGC_H */

