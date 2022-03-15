from __future__ import annotations
import subprocess


class Arg:
    def __init__(self, key: str, description: str, default: str = None, default_description: str = None,
                 value: str = None):
        self.key = key
        self.description = description
        self.default = default
        self.default_description = default_description
        self.value = value


ArgsDict: dict[str, Arg] = {
    'array_size': Arg(key='-A', description='array size, the size of the network in each dimension.',
                      default='9', default_description='9 routers on each dimension'),
    'dimension': Arg(key='-c', description='cube dimension, WARNING: 3D is not supported yet.',
                     default='2', default_description='2D network'),
    'channel': Arg(key='-V', description='virtual channel number', default='3'),
    'i_buffer': Arg(key='-B', description='input buffer size', default='12'),
    'o_buffer': Arg(key='-O', description='output buffer size', default='12'),
    'flit_size': Arg(key='-F', description='flit size (64-bit)', default='4', default_description='4*64=128'),
    'link_length': Arg(key='-L', description='link length in um', default='1000'),
    'cycles': Arg(key='-T', description='simulation cycles', default='20000'),
    'seed': Arg(key='-r', description='random seed', default='1'),
    'algo': Arg(key='-R', description='routing algorithm: 0-dimension 1-opty', default='0'),
}


def set_default_args(args_dict: dict[str, Arg]) -> None:
    for arg in args_dict.values():
        arg.value = arg.default


def run_popnet(args_dict: dict[str, Arg], bench_file: str = 'popnet/random_trace/bench', verbose: bool = True) -> str:
    popnet = subprocess.Popen(['popnet/popnet', *(f'{arg.key} {arg.value}' for arg in args_dict.values()), '-I',
                               bench_file],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, text=True)
    buffer = ''
    for line in iter(popnet.stdout.readline, ''):
        line = line.rstrip()
        print(line) if verbose else None
        buffer += line + '\n'
    popnet.stdout.close()
    popnet.wait()
    return buffer
