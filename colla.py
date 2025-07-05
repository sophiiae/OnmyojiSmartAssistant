import concurrent.futures

from module.control.server.device import Device
from tasks.main_page.colla import Colla

# port = 16384  # 浅 default
# port = 16416  # 念
# port = 16448  # 小
# port = 16480  # 3
# port = 16512  # 4
# port = 16544  # 5

config_names = [
    'qian',
    'nian',
    'xiao',
    '3',
    '4',
    '5',
]

def run_colla(name):
    d = Device(config_name=name)
    colla = Colla(device=d)
    colla.start_colla()
    # colla.return_to_exp()


if __name__ == '__main__':
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(run_colla, config_names)
