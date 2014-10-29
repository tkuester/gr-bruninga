# gr-bruninga

This project evolved out of several interests. Primarily, I wanted to
understand exactly what was happening inside an APRS modem, and design the
the best demodulator out there with GNU Radio.

To my surprise, several *excellent* projects exist which already have this
capability. Direwolf (by WB2OSZ) and APRSdroid/javAPRS (algorithm by 4X6IZ)
feature extellent demodulation algorithms, tested with the TNC Test CD
(WA8LMF). 

While this project has 1/10th the functionality of the above programs, it does
present an easy to understand and modular approach to demodulating AFSK
signals -- particularly in the signal processing realm.

## Installing
This package requires GNU Radio 3.7.4 for the HDLC Deframer block. Follow the
standard install procedure for other out of tree modules.

    git clone https://github.com/tkuester/gr-bruninga
    cd gr-bruninga 
    mkdir build
    cd build
    cmake ..
    make -j8
    make install

If you are using a version of GNU Radio installed via your distribution's
repository, you may need to tell cmake.

    cmake -DCMAKE_INSTALL_PREFIX=/usr ..

## Usage
The easiest way to get started is to hook up a handheld radio (like the UV-5R)
to your computer's input, and run examples/aprs-wav.grc

However, you can easily hook a UV-5R (or other radio) to your microphone port,
and run examples/aprs-wav.grc.

## TODO
 * Get the demodulator working with the UHD/RTL-SDR
 * Separate the TNC/KISS interface into separate blocks
 * Clean up the initial bandpass filter / resampler
 * Play with bit twiddling to save packets
 * Do BER testing on the demodulator
 * MOAR DOCUMENTATION
 * Parameterize the FSK Modulator

## Known Issues
 * The ALSA Audio Sink (as of 3.7.5) does not like it when you stop sending it
   samples. As a work around, the modulator block spits out 0's when no
   packets are available. This does cause a little lag
