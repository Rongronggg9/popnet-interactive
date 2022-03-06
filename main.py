from __future__ import annotations
from random import randrange, random
import subprocess
import os
import shutil


# from collections import defaultdict
# from functools import partial


class Arg:
    def __init__(self, key: str, description: str, default: str = None, default_description: str = None,
                 value: str = None):
        self.key = key
        self.description = description
        self.default = default
        self.default_description = default_description
        self.value = value


args = {
    'array_size': Arg(key='-A', description='array size, the size of the network in each dimension.',
                      default='9', default_description='9 routers on each dimension'),
    'dimension': Arg(key='-c', description='cube dimension, WARNING: 3D is not supported yet.',
                     default='2', default_description='2D network'),
    'channel ': Arg(key='-V', description='virtual channel number', default='3'),
    'i_buffer': Arg(key='-B', description='input buffer size', default='12'),
    'o_buffer': Arg(key='-O', description='output buffer size', default='12'),
    'flit_size': Arg(key='-F', description='flit size (64-bit)', default='4', default_description='4*64=128'),
    'link_length': Arg(key='-L', description='link length in um', default='1000'),
    'cycles': Arg(key='-T', description='simulation cycles', default='20000'),
    'seed': Arg(key='-r', description='random seed', default='1'),
    'algo': Arg(key='-R', description='outing algorithm: 0-dimension 1-opty', default='0'),
}


def gen_packet(array_size: int, time: float, sx: int, sy: int, sz: int = None, dx: int = None, dy: int = None,
               dz: int = None, packet_size: int = 5, e_notation: bool = False):
    """
    Generate packet
    :param array_size: the size of the network in each dimension
    :param time: packet injection time
    :param sx: the address of the source router in x dimension
    :param sy: the address of the source router in y dimension
    :param sz: the address of the source router in z dimension
    :param dx: the address of the destination router in x dimension
    :param dy: the address of the destination router in y dimension
    :param dz: the address of the destination router in z dimension
    :param packet_size: packet size (number of flits)
    :param e_notation: use e notation
    :return: a string of packet
    """
    dimension = 3 if sz is not None else 2
    if dx is None:
        dx = randrange(array_size)
    if dy is None:
        dy = randrange(array_size)
    if dz is None:
        dz = randrange(array_size) if dimension == 3 else None
    else:
        dz = dz if dimension == 3 else None
    time = format(time, '.4e') if e_notation else int(time)
    return f'{time} {sx} {sy} {dx} {dy} {packet_size}' if dimension == 2 else \
        f'{time} {sx} {sy} {sz} {dx} {dy} {dz} {packet_size}'


def gen_trace(array_size: int, dimension: int, injection_rate: float, packet_size: int, cycles: int,
              add_jitter: bool = True):
    """
    Generate trace
    :param array_size: the size of the network in each dimension
    :param dimension: 2D or 3D
    :param injection_rate: injection rate
    :param packet_size: packet size (number of flits)
    :param cycles: simulation cycles
    :param add_jitter: add jitter or not
    :return: a string of trace
    """
    if os.path.exists('trace/'):
        shutil.rmtree('trace/')
    os.mkdir('trace/')
    # array_3d = defaultdict(partial(defaultdict, partial(defaultdict, lambda: None)))
    all_packets = []
    interval = int(packet_size / injection_rate)
    for x in range(array_size):
        for y in range(array_size):
            for z in (range(array_size) if dimension == 3 else [None]):
                packet_l = []
                for time in range(1, cycles + 1, interval):
                    jitter = random() * interval if add_jitter else 0
                    packet = gen_packet(array_size, time + jitter, x, y, z,
                                        packet_size=packet_size, e_notation=True)
                    packet_l.append(packet)
                    all_packets.append(packet)
                packet_l.sort(key=lambda s: float(s.split()[0]))
                # array_3d[x][y][z] = packet_l
                with open(f'trace/bench.{x}.{y}' + (f'.{z}' if z is not None else ''), 'w') as f:
                    f.write('\n'.join(packet_l) + '\n')
    all_packets.sort(key=lambda s: float(s.split()[0]))
    with open('trace/bench', 'w') as f:
        f.write('\n'.join(all_packets) + '\n')


if not os.path.exists('popnet/popnet'):
    make = subprocess.Popen(['make', '-C', 'popnet/', 'popnet'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            bufsize=1, text=True)
    for line in iter(make.stdout.readline, ''):
        print(line.rstrip())
    make.stdout.close()
    make.wait()

print()
for arg in args.values():
    value = input(f'"{arg.key}" [{arg.description}] '
                  f'(default={arg.default}{", " + arg.default_description if arg.default_description else ""}): ')
    if value:
        arg.value = value
    else:
        arg.value = arg.default

_injection_rate = float(input('injection rate (float, default: 0.01): ') or '0.01')
_packet_size = int(input('packet size (int, default: 5): ') or '5')
_add_jitter = input('add jitter or not? (bool, default: 1): ') or '1'
_add_jitter = True if _add_jitter.lower().strip() in {'1', 'true'} else False

gen_trace(array_size=int(args['array_size'].value), dimension=int(args['dimension'].value),
          injection_rate=_injection_rate, packet_size=_packet_size, cycles=int(args['cycles'].value),
          add_jitter=_add_jitter)

popnet = subprocess.Popen(['popnet/popnet', *(f'{arg.key} {arg.value}' for arg in args.values()), '-I',
                           'trace/bench'],
                          # 'popnet/random_trace/bench'],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, text=True)
for line in iter(popnet.stdout.readline, ''):
    print(line.rstrip())
popnet.stdout.close()
popnet.wait()
