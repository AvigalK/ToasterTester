import csv
import datetime
import numpy as np
import matplotlib.pyplot as plt
import test_parameters
from datetime import datetime
from scipy.fft import fft
from scipy import signal


def line_fixer(line, queue_lst, output_list):
    len_q_lst = len(queue_lst)
    while len(line) > 0:
        free_spaces = len(queue_lst) - sum(x is not None for x in queue_lst)
        data_range = min(free_spaces, len(line))
        words_in_range = line[:data_range]
        for m in range(data_range):
            first_index_available = queue_lst.index(None)
            if first_index_available is not None:
                queue_lst[first_index_available] = words_in_range[m]
        line = line[data_range:]
        free_spaces -= data_range
        if free_spaces == 0:
            i = 0
            fixed = []
            while i < len(queue_lst)-4:
                lsb = queue_lst[i]
                msb = 16 ** 2 * queue_lst[i + 1]
                fixed.append(msb + lsb - 2 ** 16 if (msb + lsb) >= (2 ** 15 - 1) else msb + lsb)
                i += 2
            snc0 = [i for x, i in enumerate(fixed) if x % 3 == 0]
            snc1 = [i for x, i in enumerate(fixed) if (x - 1) % 3 == 0]
            snc2 = [i for x, i in enumerate(fixed) if (x - 2) % 3 == 0]
            snc0.insert(0, 0)
            snc1.insert(0, 1)
            snc2.insert(0, 2)
            output_list.append(snc0)
            output_list.append(snc1)
            output_list.append(snc2)
            queue_lst = [None for _ in range(len_q_lst)]

    return queue_lst


def snc_analyzer(file_path, serial_num):

    file = open(file_path, 'r+')
    from_txt = file.readline()
    from_txt = from_txt[1:-1]  # remove '[]' from string
    snc = from_txt.split(', b')
    lst = []
    line_len = len(bytes.fromhex(snc[0][2:-1]))
    lst_queue = [None for _ in range(line_len)]

    for j, data in enumerate(snc):
        if j:
            snc[j] = 'b' + data

        line_bytes = bytes.fromhex(snc[j][2:-1])

        if line_bytes is not None:
            lst_queue = line_fixer(line_bytes, lst_queue, lst)

    # write outputs to file
    # filename = 'output-SNC.csv'
    # file = open(filename, 'w', newline='')
    # write = csv.writer(file)
    # write.writerows(lst)

    data_0 = []
    data_1 = []
    data_2 = []

    for i, item in enumerate(lst):
        # group a few consecutive lines with same header for plot
        if item[0] == 0:
            data_0.append(item[1:-2])
        elif item[0] == 1:
            data_1.append(item[1:-2])
        elif item[0] == 2:
            data_2.append(item[1:-2])

    data0 = np.concatenate(data_0)
    data1 = np.concatenate(data_1)
    data2 = np.concatenate(data_2)

    filename = f"{test_parameters.main_dir}concated_signal_SNC_{serial_num}.csv"
    file_o = open(filename, 'w+')
    write = csv.writer(file_o)
    write.writerow(data0)
    write.writerow(data1)
    write.writerow(data2)
    #plt.clf()

    def NormalizeData(data):
        return (data - np.min(data)) / (np.max(data) - np.min(data))


    # plot and save images

    from matplotlib.widgets import Slider

    fig, axs = plt.subplots(3)


    axs[0].plot(data0)
    axs[1].plot(data1)
    axs[2].plot(data2)
    now = datetime.now()
    plt.xlabel(f'{now.strftime("%d/%m/%Y %H:%M:%S")}')
    axis_color = 'lightgoldenrodyellow'
    window = 500
    def update_wave(val):
        idx = int(slider.val)
        axs[0].cla()
        axs[1].cla()
        axs[2].cla()
        axs[0].plot(data0[idx:idx+window])
        axs[1].plot(data1[idx:idx+window])
        axs[2].plot(data2[idx:idx+window])
        fig.canvas.draw_idle()

    slider_ax = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=axis_color)
    #fig.subplots_adjust(left=0.25, bottom=0.5)
    slider = Slider(slider_ax, 'sample', 0, len(data0)-window)
    slider.on_changed(update_wave)
    # axs[0].set_xlabel("SNC 0")
    # axs[0].xaxis.set_label_position('top')
    axs[0].set_title(f"SNC 0")
    axs[1].set_title(f"SNC 1")
    axs[2].set_title(f"SNC 2")
    #fig.tight_layout()
    # axs[0].set_xlim([0, 1000])
    # axs[1].set_xlim([0, 1000])
    # axs[2].set_xlim([0, 1000])
    plt.savefig(f"{test_parameters.main_dir}SNC_{serial_num}.png")
    # plt.clf()
    #plt.show()
    file_o.close()

    # find correlation between normalized data and a square wave (input signal on snc electrodes)
    corr0 = np.convolve(NormalizeData(np.abs(data0)), np.ones(1000), mode='same')
    corr1 = np.convolve(NormalizeData(np.abs(data1)), np.ones(1000), mode='same')
    corr2 = np.convolve(NormalizeData(np.abs(data2)), np.ones(1000), mode='same')

    corr_threshold_high = 170
    corr_threshold_low = 100

    snc2_bound = [2900, 4100]
    snc1_bound = [1900, 3100]
    snc0_bound = [900, 2100]

    # check if high correlation in the snc bounds:
    snc0_corr = corr0[snc0_bound[0]: snc0_bound[1]]
    snc1_corr = corr1[snc1_bound[0]: snc1_bound[1]]
    snc2_corr = corr2[snc2_bound[0]: snc2_bound[1]]

    # check if low correlation out of the snc bounds:
    idle0_corr = np.concatenate([corr0[:snc0_bound[0]], corr0[snc0_bound[1]:]])
    idle1_corr = np.concatenate([corr1[:snc1_bound[0]], corr0[snc1_bound[1]:]])
    idle2_corr = np.concatenate([corr2[:snc2_bound[0]], corr0[snc2_bound[1]:]])

    snc0_test_res = True if np.mean(idle0_corr) < corr_threshold_low and np.mean(snc0_corr) > corr_threshold_high else False
    snc1_test_res = True if np.mean(idle1_corr) < corr_threshold_low and np.mean(snc1_corr) > corr_threshold_high else False
    snc2_test_res = True if np.mean(idle2_corr) < corr_threshold_low and np.mean(snc2_corr) > corr_threshold_high else False

    # snc0_test_res = True if np.mean(snc0_corr) > corr_threshold_high else False
    # snc1_test_res = True if np.mean(snc1_corr) > corr_threshold_high else False
    # snc2_test_res = True if np.mean(snc2_corr) > corr_threshold_high else False



    signal_test_res = True if snc0_test_res and snc1_test_res and snc2_test_res else False

    # # #TODO different approach for testing the signal

    n = data0.size
    sample_rate = 1040
    fft0 = np.fft.fft(data0)
    fft1 = np.fft.fft(data1)
    fft2 = np.fft.fft(data2)

    f0, t0, stft0 = signal.stft(data0, fs=1040)
    f1, t1, stft1 = signal.stft(data1, fs=1040)
    f2, t2, stft2 = signal.stft(data2, fs=1040)

    fig, axs = plt.subplots(3)
    # axs[0].pcolormesh(t0, f0, np.abs(stft0), shading='gouraud')
    # axs[1].pcolormesh(t1, f1, np.abs(stft1), shading='gouraud')
    # axs[2].pcolormesh(t2, f2, np.abs(stft2), shading='gouraud')

    axs[0].plot(np.abs(fft0))
    axs[1].plot(np.abs(fft1))
    axs[2].plot(np.abs(fft2))

    #plt.title('STFT Magnitude')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    #plt.show()
    plt.savefig(f"{test_parameters.main_dir}SNC_{serial_num}_STFT.png")
    plt.clf()



    #TODO if input single 50hz frequency to all sncs at the same time I still get inconsistent results

    # fig, axs = plt.subplots(3)
    # axs[0].plot(fft0)
    # axs[1].plot(fft1)
    # axs[2].plot(fft2)
    # now = datetime.now()
    # plt.xlabel(f'{now.strftime("%d/%m/%Y %H:%M:%S")}')
    # fig.tight_layout()
    # # axs[0].set_xlim([0, 1000])
    # # axs[1].set_xlim([0, 1000])
    # # axs[2].set_xlim([0, 1000])
    # plt.savefig(f"{test_parameters.main_dir}SNC_{serial_num}_FFT.png")
    # plt.clf()

    # fig, axs = plt.subplots(3)
    # axs[0].plot(idle0_corr)
    # axs[1].plot(idle1_corr)
    # axs[2].plot(idle2_corr)
    # now = datetime.now()
    # plt.xlabel(f'{now.strftime("%d/%m/%Y %H:%M:%S")}')
    # fig.tight_layout()
    # plt.savefig(f"{test_parameters.main_dir}SNC_{serial_num}_corr.png")
    # plt.clf()

    return lst, signal_test_res, snc0_test_res, snc1_test_res, snc2_test_res

if __name__ == '__main__':
    path = f'{test_parameters.main_dir}SNC_587.txt'
    list, test_res, snc0_test_res, snc1_test_res, snc2_test_res = snc_analyzer(path, 587)
    print(snc0_test_res, snc1_test_res, snc2_test_res)
    test = 1
    
