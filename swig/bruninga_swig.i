/* -*- c++ -*- */

#define BRUNINGA_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "bruninga_swig_doc.i"

%{
#include "bruninga/direwolf_agc.h"
%}


%include "bruninga/direwolf_agc.h"
GR_SWIG_BLOCK_MAGIC2(bruninga, direwolf_agc);
