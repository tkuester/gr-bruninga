#!/usr/bin/env python
import packet

a = packet.AX25Address()
a.callsign = 'KB3VOZ'
a.ssid = 0

p = packet.AX25Packet()
p.src = a
p.dest = a
p.control = 0x03
p.protocol_id = 0xf0
p.info = 'qwerqwerqwerqwer'

print p.hdlc_wrap()
