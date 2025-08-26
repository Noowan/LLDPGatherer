# TO-DO-PLAN
# 1. Parse devices lists
# 2. Sort list by ip
# 3. Connect to all vendors and get all interfaces
# 5. generate output
# 6. Rewrite code for multithreading
import time
from threading import Thread

import huawei

DEVICES_FILENAME = 'hosts.env'
MAXTHREADS = 1500
lldpneighbours = []

def read_devices_file_to_list_of_tuples(_filename: str) -> list:
    with open(_filename, "r", encoding="utf-8") as somefile:
        linesfromfile = somefile.read()
        linesfromfile = linesfromfile.replace("\n", "\n\n\n\n\n")
        linesfromfile = linesfromfile.replace(" ", "-")
    lines = linesfromfile.split(sep="\n\n\n\n\n")
    devices_list = []
    for line in lines:
        line_splitted = line.split(sep="\t")
        devices_list.append((line_splitted[0], line_splitted[1], line_splitted[2], line_splitted[3], line_splitted[4]))
    return devices_list

def sort_devices_by_ip(_devices: list) -> list:
    return sorted(_devices, key=lambda device: tuple(map(int, device[1].split('.'))))

def get_interfaces_neighbours(_device):
    match _device[3]:
        case "ECI":
            print(f'{_device} - THERE IS NO LLDP!!!')
        case "Cisco":
            pass
            #return Cisco.get_interfaces_and_ips(_device)
        case "Huawei":
            return huawei.get_lldp_info(_device)
        case "Juniper":
            pass
            #return Juniper.get_interfaces_and_ips(_device)
        case _:
            print(f'{_device} - UNKNOWN DEVICE')

def main_func(_device):
    result = get_interfaces_neighbours(_device)
    if result:
        lldpneighbours = (_device[0], _device[1], _device[2], _device[3], _device[4], result[0], result[1])
        with open("result.txt", "a", encoding="utf-8") as resultfile:
            resultfile.write('\t'.join(str(s) for s in lldpneighbours) + '\n')


if __name__ == '__main__':
    devices = read_devices_file_to_list_of_tuples(DEVICES_FILENAME)
    for device in devices:
        main_func(device)
        # threads = []
        # tries = int(len(devices) / MAXTHREADS)
        # leastTries = len(devices) % MAXTHREADS
        # START = 0
        # FINISH = MAXTHREADS
        #
        # i = 1
        # while i <= tries:
        #     for j in range(START, FINISH):
        #         threads.append(
        #             Thread(target=main_func, args=(devices[j], ), name=f"{devices[j]}:Thread"))
        #         print(f"Thread {j} created")
        #     for thread in threads:
        #         # print(f"start {thread.name}")
        #         thread.start()
        #         time.sleep(0.1)
        #     for thread in threads:
        #         thread.join()
        #     threads.clear()
        #     START = FINISH
        #     i = i + 1
        #     FINISH = FINISH + MAXTHREADS
        # i = 1
        # if tries == 0:
        #     j = -1
        # while i <= leastTries:
        #     threads.append(
        #         Thread(target=main_func, args=(devices[i+j], ), name=f"{devices[i+j]}:Thread"))
        #     print(f"Thread {i + j} created")
        #     i = i + 1
        # for thread in threads:
        #     # print(f"start {thread.name}")
        #     thread.start()
        # for thread in threads:
        #     thread.join()
        # threads.clear()