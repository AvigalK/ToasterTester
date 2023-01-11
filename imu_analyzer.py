import csv
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import test_parameters

OLD_FW = False
def line_fixer(line, queue_lst, list):
    len_q_lst = len(queue_lst)
    while len(line) > 0:
        free_spaces11 = len(queue_lst) - sum(x is not None for x in queue_lst)
        range11 = min(free_spaces11, len(line))
        words_in_range = line[:range11]
        for m in range(range11):
            first_index_available = queue_lst.index(None)
            if first_index_available is not None:
                queue_lst[first_index_available] = words_in_range[m]
        line = line[range11:]
        free_spaces11 -= range11
        if free_spaces11 == 0:
            i = 1
            fixed = [queue_lst[0]]
            while 0 < i < len(queue_lst) - 4:
                lsb = queue_lst[i]
                msb = 16 ** 2 * queue_lst[i+1]

               # print(f'{msb},{lsb}')
                fixed.append(msb + lsb)# - 2 ** 16 if (msb + lsb) >= (2 ** 15 - 1) else msb + lsb)
                i += 2
            list.append(fixed)

            queue_lst = [None for _ in range(len_q_lst)]

    return queue_lst


def NormalizeData(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))


def imu_analyzer(path, serial_num):
    file = open(path, 'r')
    from_txt = file.readline()
    from_txt = from_txt[1:-1]  # remove '[]' from string
    imu = from_txt.split(', b')
    lst = []
    line_len = len(bytes.fromhex(imu[0][2:-1])) if OLD_FW else int(len(bytes.fromhex(imu[0][2:-1]))/5)

    lst_queue1 = [None for _ in range(line_len)]
    lst_queue11 = [None for _ in range(37)]  # 1 byte header + 16 words in line + 2 words timestamp = 1+32+4
    #lst_queue1 = [None for _ in range(21)]  # 1 byte header + 8 words in line + 2 words timestamp = 1+16+4
    # word = 2 bytes
    for j, data in enumerate(imu):
        if j:
            imu[j] = 'b' + data

        line_bytes = bytes.fromhex(imu[j][2:-1])
        header = line_bytes[0]
        if line_bytes is not None:

            # valid headers:
            if header == 11:
                if len(line_bytes) < len(lst_queue11) and line_bytes[-1] == 0:  # line too short and ends with timestamp
                    lst_queue11 = [None for _ in range(len(lst_queue11))]
                else:
                    lst_queue11 = line_fixer(line_bytes, lst_queue11, lst)

            elif header == 1:
                if len(line_bytes) < len(lst_queue1) and line_bytes[-1] == 0:
                    lst_queue1 = [None for _ in range(len(lst_queue1))]
                else:
                    lst_queue1 = line_fixer(line_bytes, lst_queue1, lst)

            else:  # invalid headers
                if lst_queue1[0] == 1:
                    lst_queue1 = line_fixer(line_bytes, lst_queue1, lst)

                elif lst_queue11[0] == 11:
                    lst_queue11 = line_fixer(line_bytes, lst_queue11, lst)

    # write outputs to file
    # filename = f'/home/wld-hw/rpi_band_tester/output-IMU_{serial_num}.csv'
    # file = open(filename, 'w', newline='')
    # write = csv.writer(file)
    # write.writerows(lst)
    data_11 = []
    data_1 = []

    for item in lst:

        # group a few consecutive lines with same header for plot
        if item[0] == 11:
            data_11.append(item[1:-2])
        if item[0] == 1:
            data_1.append(item[1:-2])

    concat = np.concatenate(data_1)

    # verify signal
    corr_threshold_high = 150
    corr_threshold_low = 100
    imu_bound = [1050, 3050] if not OLD_FW else [950, 2050]

    corr = np.convolve(NormalizeData(concat[1500:]), np.ones(1000), mode='same')
    imu_corr = corr[imu_bound[0]: imu_bound[1]]  # check if high correlation in the bounds
    idle_corr = np.concatenate([corr[:imu_bound[0]], corr[imu_bound[1]:]])  # check if low correlation out of the bounds

    imu_test_res = True if np.mean(idle_corr) < corr_threshold_low and np.mean(imu_corr) > corr_threshold_high else False

    filename = f"{test_parameters.main_dir}concated_signal_{serial_num}.csv"
    print(serial_num)
    file_o = open(filename, 'w+')
    # file_o.seek(0,0)
    write = csv.writer(file_o)
    write.writerow(list(concat))
    file_o.close()
    now = datetime.now()
    plt.xlabel(f'{now.strftime("%d/%m/%Y %H:%M:%S")}')
    plt.title("IMU")
    plt.plot(concat[1500:])
    plt.savefig(f"{test_parameters.main_dir}IMU_{serial_num}.png", dpi=1000)
    plt.clf()


    # plt.clf()
    # plt.xlabel(f'{now.strftime("%d/%m/%Y %H:%M:%S")}')
    # plt.title("IMU_corr")
    # plt.plot(corr)
    # plt.show()

    return lst, imu_test_res

# if __name__ == '__main__':
#     path = f'{test_parameters.main_dir}IMU_1426.txt'
#     lst, res = imu_analyzer(path, 1426)
#     done = 1


