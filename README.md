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
signals.

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

However, you can easily hook a UV-5R (or other radio) to your microphone port, and
run examples/aprs-wav.grc.

## TODO
 * Get the demodulator working with the UHD/RTL-SDR
 * Finish the transmitter
 * Build a little TNC/KISS interface
 * Clean up the initial bandpass filter / resampler
