from __future__ import annotations
import re
import numpy as np
import matplotlib.pyplot as plt
from collections.abc import Iterable

from popnet_executer import run_popnet, ArgsDict, set_default_args
from trace_generator import gen_trace

resultMatcher = re.compile(r'Incoming packets\s*(?P<tot_packet>\d+).*\n'
                           + r'\*' * 50 + r'\n'
                           + r'[^*]+?'
                           + r'\*' * 50 + r'\n'
                           + r'\*' * 50 + r'\n'
                           + r'total finished:\s*(?P<finished_packet>\d+)\s*'
                             r'average Delay:\s*(?P<avg_delay>[\d.e+-]+)\s*'
                             r'total mem power:\s*(?P<mem_power>[\d.e+-]+)\s*'
                             r'total crossbar power:\s*(?P<crossbar_power>[\d.e+-]+)\s*'
                             r'total arbiter power:\s*(?P<arbiter_power>[\d.e+-]+)\s*'
                             r'total link power:\s*(?P<link_power>[\d.e+-]+)\s*'
                             r'total power:\s*(?P<tot_power>[\d.e+-]+)\s*'
                           + r'\*' * 50)

arg_ranges = {
    'array_size': range(1, 10 + 1),
    'channel': range(1, 10 + 1),
    'i_buffer': range(0, 10 + 1),
    'o_buffer': range(0, 10 + 1),
    'flit_size': range(0, 100 + 1, 4),
    'link_length': range(100, 2000 + 1, 100),
    'cycles': range(2000, 24000 + 1, 2000),
    'seed': range(1, 10 + 1),
    'algo': (0, 1),
}


def bold(s: str) -> str:
    s_l = s.split(' ')
    return ' '.join(r'$\bf{' + sub_s + '}$' for sub_s in s_l)


class Results:
    def __init__(self, x: str, x_range: Iterable, results: list[re.Match]):
        self.x = x
        self.x_range = x_range
        self.tot_packet = np.array([int(result.group('tot_packet')) for result in results])
        self.finished_packet = np.array([int(r.group('finished_packet')) for r in results])
        self.packet_finish_rate = np.array(self.finished_packet / self.tot_packet * 100)
        self.avg_delay = np.array([float(r.group('avg_delay')) for r in results])
        self.mem_power = np.array([float(r.group('mem_power')) for r in results])
        self.crossbar_power = np.array([float(r.group('crossbar_power')) for r in results])
        self.arbiter_power = np.array([float(r.group('arbiter_power')) for r in results])
        self.link_power = np.array([float(r.group('link_power')) for r in results])
        self.tot_power = np.array([float(r.group('tot_power')) for r in results])

    def show(self):
        plt.figure(dpi=300)
        plt.title('Relation between {} and {}'.format(bold(self.x), bold('packet finish rate')))
        plt.xlabel(self.x)
        plt.ylabel(f'packet finish rate (%)')
        plt.plot(self.x_range, self.packet_finish_rate, 'o-')
        plt.show()

        plt.figure(dpi=300)
        plt.title('Relation between {} and {}'.format(bold(self.x), bold('average delay')))
        plt.xlabel(self.x)
        plt.ylabel('average delay (ms)')
        plt.plot(self.x_range, self.avg_delay, 'o-')
        plt.show()

        plt.figure(dpi=300)
        plt.title('Relation between {} and {}'.format(bold(self.x), bold('powers')))
        plt.xlabel(self.x)
        plt.ylabel('power')
        plt.stackplot(self.x_range, self.mem_power, self.link_power, self.crossbar_power, self.arbiter_power,
                      labels=['mem', 'link', 'crossbar', 'arbiter'])
        plt.legend(loc='upper left')
        plt.show()


def main():
    for arg_to_examine in arg_ranges:
        arg_range = arg_ranges[arg_to_examine]
        results = []
        set_default_args(ArgsDict)
        for arg_value in arg_range:
            ArgsDict[arg_to_examine].value = arg_value
            if arg_to_examine == 'array_size':
                gen_trace(array_size=arg_value, dimension=2, injection_rate=0.1, packet_size=5, cycles=int(20000 / 3))
            print(f'{arg_to_examine}: {arg_value}/{max(arg_range)}')
            popnet_res = run_popnet(
                ArgsDict,
                bench_file='trace/bench' if arg_to_examine == 'array_size' else 'popnet/random_trace/bench',
                verbose=False
            )
            result = resultMatcher.search(popnet_res)
            if result is None:
                raise RuntimeError
            results.append(result)
        title = (ArgsDict[arg_to_examine].description.split(':')[0].split('(')[0].split(',')[0]
                 + f' [{ArgsDict[arg_to_examine].key}]')
        Results(title, arg_range, results).show()

    set_default_args(ArgsDict)
    title = 'injection rate'
    injection_rate_ranges = (np.arange(0.01, 0.1 + 0.01, 0.01), np.arange(0.1, 3 + 0.1, 0.1))
    for divisor in (10, 1):
        for injection_rate_range in injection_rate_ranges:
            results = []
            for injection_rate in injection_rate_range:
                gen_trace(array_size=9, dimension=2, injection_rate=injection_rate, packet_size=5,
                          cycles=int(20000 / divisor))
                print(f'injection_rate: {injection_rate}')
                popnet_res = run_popnet(ArgsDict, bench_file='trace/bench', verbose=False)
                result = resultMatcher.search(popnet_res)
                if result is None:
                    raise RuntimeError
                results.append(result)
            Results(title, injection_rate_range, results).show()


if __name__ == '__main__':
    main()
