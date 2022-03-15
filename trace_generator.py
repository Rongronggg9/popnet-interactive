from __future__ import annotations
import os
import shutil
import numpy as np
from random import randrange, random


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
    time = format(time, '.4e') if e_notation else time
    return f'{time} {sx} {sy} {dx} {dy} {packet_size}' if dimension == 2 else \
        f'{time} {sx} {sy} {sz} {dx} {dy} {dz} {packet_size}'


def gen_trace(array_size: int, dimension: int, injection_rate: float, packet_size: int, cycles: int,
              add_jitter: bool = True, e_notation: bool = False) -> int:
    """
    Generate trace
    :param array_size: the size of the network in each dimension
    :param dimension: 2D or 3D
    :param injection_rate: injection rate
    :param packet_size: packet size (number of flits)
    :param cycles: simulation cycles
    :param add_jitter: add jitter or not
    :param e_notation: use e notation
    :return: packet count
    """
    if os.path.exists('trace/'):
        shutil.rmtree('trace/')
    os.mkdir('trace/')
    # array_3d = defaultdict(partial(defaultdict, partial(defaultdict, lambda: None)))
    all_packets = []
    interval = float(packet_size / injection_rate)
    for x in range(array_size):
        for y in range(array_size):
            for z in (range(array_size) if dimension == 3 else [None]):
                packet_l = []
                for time in np.arange(1, cycles + 1, interval):
                    jitter = random() * interval if add_jitter else 0
                    packet = gen_packet(array_size, time + jitter, x, y, z,
                                        packet_size=packet_size, e_notation=e_notation)
                    packet_l.append(packet)
                    all_packets.append(packet)
                packet_l.sort(key=lambda s: float(s.split()[0]))
                # array_3d[x][y][z] = packet_l
                with open(f'trace/bench.{x}.{y}' + (f'.{z}' if z is not None else ''), 'w') as f:
                    f.write('\n'.join(packet_l) + '\n')
    all_packets.sort(key=lambda s: float(s.split()[0]))
    with open('trace/bench', 'w') as f:
        f.write('\n'.join(all_packets) + '\n')
    return len(all_packets)
