##
## This file is part of the libswo project.
##
## Copyright (C) 2017 Marc Schink <swo-dev@marcschink.de>
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

import sys
import swopy

BUFFER_SIZE = 1024

class Decoder:
    def __init__(self, buffer_size):
        self._ctx = swopy.Context(buffer_size)
        self._ctx.set_callback(self._packet_callback)

    def feed(self, data):
        self._ctx.feed(data)

    def decode(self, flags=swopy.DecoderFlags.NONE):
        self._ctx.decode(flags)

    def _handle_unknown_packet(self, packet):
        print('Unknown data (size = %u bytes)' % packet.get_size())

    def _handle_sync_packet(self, packet):
        size = packet.get_size()

        if (size % 8) > 0:
            print('Synchronization (size = %u bits)' % size)
        else:
            print('Synchronization (size = %u bytes)' % (size / 8))

    def _handle_overflow_packet(self, packet):
        print('Overflow')

    def _handle_lts_packet(self, packet):
        relation = packet.get_relation()

        if relation == swopy.LocalTimestampRelation.SYNC:
            tc = 'synchronous'
        elif relation == swopy.LocalTimestampRelation.TS:
            tc = 'timestamp delayed'
        elif relation == swopy.LocalTimestampRelation.SRC:
            tc = 'data delayed'
        elif relation == swopy.LocalTimestampRelation.BOTH:
            tc = 'data and timestamp delayed'
        else:
            return

        print('Local timestamp (relation = %s, value = %x)' % (tc,
            packet.get_value()))

    def _handle_gts1_packet(self, packet):
        print('Global timestamp (GTS1) (wrap = %u, clkch = %u, value = %x)' % (
            packet.get_wrap(), packet.get_clkch(), packet.get_value()))

    def _handle_gts2_packet(self, packet):
        print('Global timestamp (GTS2) (value = %x)' % packet.get_value())

    def _handle_ext_packet(self, packet):
        if packet.get_source() == swopy.ExtensionSource.ITM:
            src = 'ITM'
        elif packet.get_source() == swopy.ExtensionSource.HW:
            src = 'HW'
        else:
            print('Extension packet with invalid source: %u.' %
                packet.get_source())
            return

        print('Extension (source = %s, value = %x)' % (src,
            packet.get_value()))

    def _handle_inst_packet(self, packet):
        print('Instrumentation (address = %u, value = %x, size = %u bytes)' % (
            packet.get_address(), packet.get_value(), packet.get_size() - 1))

    def _handle_hw_packet(self, packet):
        print('Hardware source (address = %u, value = %x, size = %u bytes)' % (
            packet.get_address(), packet.get_value(), packet.get_size() - 1))

    def _handle_evtcnt_packet(self, packet):
        print('Event counter (CPI = %u, exc = %u, sleep = %u, LSU = %u, '
            'fold = %u, cyc = %u)' % (packet.get_cpi(), packet.get_exc(),
            packet.get_sleep(), packet.get_lsu(), packet.get_fold(),
            packet.get_cyc()));

    def _handle_exctrc_packet(self, packet):
        if packet.get_function() == swopy.ExceptionTraceFunction.ENTER:
            func = 'enter'
        elif packet.get_function() == swopy.ExceptionTraceFunction.EXIT:
            func = 'exit'
        elif packet.get_function() == swopy.ExceptionTraceFunction.RETURN:
            func = 'return'
        else:
            func = 'reserved'

        print('Exception trace (function = %s, exception = %u)' % (func,
            packet.get_exception()))

    def _handle_pc_sample_packet(self, packet):
        if packet.get_sleep():
            print('Periodic PC sleep')
        else:
            print('Periodic PC sample (value = %x)' % packet.get_value())

    def _handle_pc_value_packet(self, packet):
        print('Data trace PC value (comparator = %u, value = %x)' % (
            packet.get_comparator(), packet.get_value()))

    def _handle_addr_offset_packet(self, packet):
        print('Data trace address offset (comparator = %u, value = %x)' % (
            packet.get_comparator(), packet.get_value()))

    def _handle_data_value_packet(self, packet):
        print('Data trace data value (comparator = %u, WnR = %u, value = %x, '
            'size = %u bytes)' % (packet.get_comparator(), packet.get_wnr(),
            packet.get_value(), packet.get_size()))

    def _packet_callback(self, packet):
        packet_type = packet.get_type()

        if packet_type == swopy.PacketType.UNKNOWN:
            self._handle_unknown_packet(packet)
        elif packet_type == swopy.PacketType.SYNC:
            self._handle_sync_packet(packet)
        elif packet_type == swopy.PacketType.OF:
            self._handle_overflow_packet(packet)
        elif packet_type == swopy.PacketType.LTS:
            self._handle_lts_packet(packet)
        elif packet_type == swopy.PacketType.GTS1:
            self._handle_gts1_packet(packet)
        elif packet_type == swopy.PacketType.GTS2:
            self._handle_gts2_packet(packet)
        elif packet_type == swopy.PacketType.EXT:
            self._handle_ext_packet(packet)
        elif packet_type == swopy.PacketType.INST:
            self._handle_inst_packet(packet)
        elif packet_type == swopy.PacketType.HW:
            self._handle_hw_packet(packet)
        elif packet_type == swopy.PacketType.DWT_EVTCNT:
            self._handle_evtcnt_packet(packet)
        elif packet_type == swopy.PacketType.DWT_EXCTRC:
            self._handle_exctrc_packet(packet)
        elif packet_type == swopy.PacketType.DWT_PC_SAMPLE:
            self._handle_pc_sample_packet(packet)
        elif packet_type == swopy.PacketType.DWT_PC_VALUE:
            self._handle_pc_value_packet(packet)
        elif packet_type == swopy.PacketType.DWT_ADDR_OFFSET:
            self._handle_addr_offset_packet(packet)
        elif packet_type == swopy.PacketType.DWT_DATA_VALUE:
            self._handle_data_value_packet(packet)
        else:
            print('Unknown packet type %u' % packet_type, file=sys.stderr)
            return False

        return True

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: %s <filename>' % sys.argv[0], file=sys.stderr)
        sys.exit(1)

    try:
        with open(sys.argv[1], 'rb') as input_file:
            decoder = Decoder(2 * BUFFER_SIZE)

            while True:
                data = input_file.read(BUFFER_SIZE)

                if len(data) == 0:
                    break

                try:
                    decoder.feed(data)
                    decoder.decode()
                except BaseException as e:
                    print(e, file=sys.stderr)
                    break

            input_file.close()

            try:
                decoder.decode(swopy.DecoderFlags.EOS)
            except Exception as e:
                print(e, file=sys.stderr)

    except BaseException as e:
        print(e, file=sys.stderr)
