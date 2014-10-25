#!/usr/bin/env python
import packet

s = packet.AX25Address()
s.callsign = 'KB3VOZ'
s.ssid = 0

p = packet.AX25Packet()
p.src = s
p.dest= s
p.control = 0x03
p.protocol_id = 0xf0
p.info = 'hello!'

print p.hdlc_wrap()
