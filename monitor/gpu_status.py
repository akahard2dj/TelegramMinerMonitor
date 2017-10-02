import subprocess


class GPUInfo:
    def __init__(self):
        self._host = ''
        self._user = 'miner'
        self._query = 'nvidia-smi --query-gpu=timestamp,name,temperature.gpu,power.draw,fan.speed --format=csv'

    def get_info(self, host):
        cmd = []
        cmd.append('ssh')
        cmd.append('{}@{}'.format(self._user, host))
        cmd.append(self._query)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        stdout = []
        for line in iter(proc.stdout.readline, b''):
            stdout.append(line.decode("UTF-8"))

        res = {}
        res['num_gpu'] = len(stdout) - 1

        gpu = []

        for line in stdout[1:]:
            item = dict()
            tmp = line.split(',')
            item['timestamp'] = tmp[0]
            item['name'] = tmp[1]
            item['temp'] = tmp[2]
            item['power'] = tmp[3]
            item['fan'] = tmp[4].replace('\n', '')
            gpu.append(item)

        res['gpu_info'] = gpu

        #print(res)
        return res
