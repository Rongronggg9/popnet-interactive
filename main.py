from __future__ import annotations
import subprocess
import os
import re

from popnet_executer import ArgsDict, run_popnet
from trace_generator import gen_trace

if not os.path.exists('popnet/popnet'):
    make = subprocess.Popen(['make', '-C', 'popnet/', 'popnet'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            bufsize=1, text=True)
    for _ in iter(make.stdout.readline, ''):
        print(_.rstrip())
    make.stdout.close()
    make.wait()

print()

if __name__ == '__main__':
    for arg in ArgsDict.values():
        _value = input(f'"{arg.key}" [{arg.description}] '
                       f'(default={arg.default}'
                       f'{", " + arg.default_description if arg.default_description else ""}): ')
        if _value:
            arg.value = _value
        else:
            arg.value = arg.default

    _injection_rate = float(input('injection rate (float, default: 0.01): ') or '0.01')
    _packet_size = int(input('packet size (int, default: 5): ') or '5')
    _add_jitter = input('add jitter or not? (bool, default: 1): ') or '1'
    _add_jitter = True if _add_jitter.lower().strip() in {'1', 'true'} else False

    gen_trace(array_size=int(ArgsDict['array_size'].value), dimension=int(ArgsDict['dimension'].value),
              injection_rate=_injection_rate, packet_size=_packet_size, cycles=int(int(ArgsDict['cycles'].value) / 3),
              add_jitter=_add_jitter)

    run_popnet(ArgsDict, bench_file='trace/bench')
