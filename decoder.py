##
## This file is part of the libswo project.
## Hacked by karl to do some task stuff.
## stupid gpl3
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

import argparse
import os
import sys
import time
import swopy

BUFFER_SIZE = 1024

def millis():
    return int(round(time.time() * 1000))

class Decoder:
    def __init__(self, opts, buffer_size=BUFFER_SIZE*2):
        self._ctx = swopy.Context(buffer_size)
        self._ctx.set_callback(self._packet_callback)
        self.opts = opts

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
        if self.opts.address < 0 or self.opts.address == packet.get_address():
            print('Instrumentation (address = %u, value = %x, size = %u bytes)' % (
                packet.get_address(), packet.get_value(), packet.get_size() - 1))

    def _handle_hw_packet(self, packet):
        if self.opts.address < 0 or self.opts.address == packet.get_address():
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

class KTask():
    def __init__(self, tag, opts={}):
        self.tag = tag
        self.invoke_cnt = 0
        self.invoke_cnt_recent = 0
        self.time_total = 0
        self.time_recent = 0
        # hoho, we could do things like stddev stuff of last x calls?
        self.times_recent = []
        self.opts = opts

    def add(self, tval):
        self.invoke_cnt += 1
        self.invoke_cnt_recent += 1
        self.time_total += tval
        self.time_recent += tval
        self.times_recent.append(tval)
        self.times_recent = self.times_recent[-100:]

    def reset(self):
        self.invoke_cnt_recent = 0
        self.time_recent = 0
        # um, for consistency, we should junk the moving averge too, right?
        self.times_recent = []

    def __repr__(self):
        avg = 0.0
        ravg = 0.0
        if self.invoke_cnt:
            avg = self.time_total / self.invoke_cnt
        if self.invoke_cnt_recent:
            ravg = self.time_recent / self.invoke_cnt_recent
        if self.opts.wallclock:
            avg /= self.opts.nominal_clock / 1000
            ravg /= self.opts.nominal_clock / 1000
            return f"Task<{self.tag}>(cnt:{self.invoke_cnt:>8}/{self.invoke_cnt_recent:>5} avg:{avg:>5.2f}ms ravg:{ravg:>5.2f}ms)"
        else:
            return f"Task<{self.tag}>(cnt:{self.invoke_cnt:>8}/{self.invoke_cnt_recent:>5} avg:{avg:>10.2f} ravg:{ravg:>10.2f})"

class KFreeRtosDecoder(Decoder):
    """
    given a stream of taskids+time deltas, construct a view of
    "tasks, counts, %of totals" sort of thing.
    """
    def __init__(self, opts):
        # python3 baby
        super().__init__(opts)
        self.tasks = {}
        self.last_report = millis()

    def handle_exit(self, tag, ts):
        task = self.tasks.get(tag, None)
        if not task:
            task = KTask(tag, self.opts)
            self.tasks[tag] = task
        task.add(ts)

    def _handle_inst_packet(self, packet):
        if self.opts.address < 0:
            print("um, you need to say which address has the tagging plz")
            os.exit(1)
        if self.opts.address != packet.get_address():
            return

        #print('Instrumentation (address = %u, value = %x, size = %u bytes)' % (
        #    packet.get_address(), packet.get_value(), packet.get_size() - 1))
        if packet.get_size() == 5 and ((packet.get_value() >> 24) & 0x80):
            tag = (packet.get_value() >> 24) & 0x1f
            ts = packet.get_value() & 0xffffff
            self.handle_exit(tag, ts)
        else:
            print(f"unexpected/badly formatted trace packet: address: {packet.get_address()}, value: {packet.get_value()}, size: {packet.get_size() - 1 }")

    def _handle_pc_sample_packet(self, packet):
        # shush, we might be doing both of these at the same time.
        pass
    def _handle_ext_packet(self, packet):
        pass


    def summary(self):
        if len(self.tasks) == 0:
            print("Haven't seen any tags yet...")
            return
        sum_time_total = sum([t.time_total for tag,t in self.tasks.items()])
        sum_time_recent = sum([t.time_recent for tag,t in self.tasks.items()])
        if not sum_time_recent:
            print("No trace tags for %.1f secs" % ((millis() - self.last_good_report) / 1000))
            return
        self.last_good_report = millis()
        if self.opts.wallclock:
            sum_time_total /= self.opts.nominal_clock
            sum_time_recent /= self.opts.nominal_clock
        print(f"total time: {sum_time_total} recent time: {sum_time_recent}")
        for tag,t in sorted(self.tasks.items()):
            pct_total = t.time_total / sum_time_total * 100
            pct_recent = t.time_recent / sum_time_recent * 100
            if self.opts.wallclock:
                pct_total /= self.opts.nominal_clock
                pct_recent /= self.opts.nominal_clock
            print(f"{t} occupied recent: {pct_recent:>5.2f}% all time: {pct_total:>5.2f}%")
            t.reset()

    def report(self):
        now = millis()
        if now - self.last_report > self.opts.report_interval:
            self.summary()
            self.last_report = now
        


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('file', type=argparse.FileType('rb', 0), help="swo binary output file to parse", default="-")
    ap.add_argument("--address", "-a", type=int, default=-1, help="which channels to print, -1 for all")
    ap.add_argument("--follow", "-f", action="store_true", help="Seek to the 1024 bytes before the end of file first!", default=False)
    ap.add_argument("--report_interval", type=int, default=1000, help="How often to dump summary reporting")
    ap.add_argument("--nominal_clock", type=float, default=32e6, help="nominal clock, allows converting ticks to pseudo realistic wall clock times")
    ap.add_argument("--wallclock", "-w", action="store_true", help="divide all ticks by nominal clock to get wall clock results")
    opts = ap.parse_args()

    try:
        with opts.file as input_file:
            decoder = KFreeRtosDecoder(opts)
            if opts.follow:
                input_file.seek(0, os.SEEK_END)
                size = input_file.tell()
                if size > 1024:
                    print("Jumping to the near the end")
                    input_file.seek(-1024, os.SEEK_END)
                else:
                    input_file.seek(0)

            while True:
                data = input_file.read(BUFFER_SIZE)

                if len(data) == 0:
                    # Wait for more...
                    if opts.follow:
                        time.sleep(0.5)
                    else:
                        break

                try:
                    decoder.feed(data)
                    decoder.decode()
                except BaseException as e:
                    print(e, file=sys.stderr)
                    break

                decoder.report()

            input_file.close()

            try:
                decoder.decode(swopy.DecoderFlags.EOS)
            except Exception as e:
                print(e, file=sys.stderr)

    except BaseException as e:
        print(e, file=sys.stderr)
