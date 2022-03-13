import re
import subprocess
from collections import defaultdict
from functools import partial

pattern = re.compile(r'(?P<time>\d+)\s+(?P<sx>\d+)\s+(?P<sy>\d+)\s+(?P<dx>\d+)\s+(?P<dy>\d+)\s+(?P<size>\d+)')

max_x = 0
max_y = 0
array_2d = defaultdict(partial(defaultdict, list))
with open('trace/bench', 'r') as f:
    for line in f:
        m = pattern.match(line)
        if m:
            time = int(m.group('time'))
            sx = int(m.group('sx'))
            sy = int(m.group('sy'))
            dx = int(m.group('dx'))
            dy = int(m.group('dy'))
            size = int(m.group('size'))
            max_x = max(max_x, sx, dx)
            max_y = max(max_y, sy, dy)
            array_2d[sx][sy].append((time, dx, dy, size))

for x in range(max_x + 1):
    for y in range(max_y + 1):
        array_2d[x][y].sort(key=lambda t: t[0])

for x in range(max_x + 1):
    for y in range(max_y + 1):
        with open(f'trace/bench.{x}.{y}', 'w') as f:
            f.write('\n'.join(map(lambda t: f'{t[0]} {x} {y} {t[1]} {t[2]} {t[3]}', array_2d[x][y])) + '\n')

popnet = subprocess.Popen(['popnet/popnet', '-A 9', '-c 2', '-V 1', '-B 12', '-O 12', '-F 4', '-L 1000', '-T 20000',
                           '-r 1', '-R 0', '-I',
                           'trace/bench'],
                          # 'popnet/random_trace/bench'],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, text=True)
for line in iter(popnet.stdout.readline, ''):
    print(line.rstrip())
popnet.stdout.close()
popnet.wait()
