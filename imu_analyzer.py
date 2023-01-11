import matplotlib.pyplot as plt
import csv
import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")

def str_bytes_to_bytes(single_line):
    """ coverts string of format "b'\x00'" to bytes b'\x00'  """

    global i
    flag = False
    special_cha = False
    hex_str = ''
    prev_cha = ''

    for i, char in enumerate(single_line):

        if 3 < i < (len(single_line) - 1):
            if single_line[i - 1] == 'x' and single_line[i - 2] == '\\':
                flag = False
                if single_line[i + 1] == '\\' and single_line[i + 2] == 'x':
                    hex_str += hex(ord(char))[2:]
                    flag = True
                else:
                    hex_str += char
                prev_cha = char
            elif single_line[i - 3] == '\\' and single_line[i - 1] == prev_cha and single_line[i - 2] == 'x' and not flag:
                hex_str += char
            elif char != 'x' and char != '\\':
                hex_str += hex(ord(char))[2:]
            elif single_line[i + 1] != 'x' and char == '\\' and single_line[i - 1] != '\\':
                hex_str += hex(ord(char))[2:]
                special_cha = True
            elif single_line[i - 1] != '\\' and char == 'x':
                hex_str += hex(ord(char))[2:]
            elif char == '\\' and single_line[i + 1] != 'x' and single_line[i - 1] != '\\':
                hex_str += hex(ord(char))[2:]
    # print('len:', len(hex_str),' line:', hex_str)
   #if len(hex_str) < 10:
   #     print('input length is too short, ignoring line with index:', i)
   #     print(single_line)
    #    return
    #else:
    return bytes.fromhex(hex_str) if not special_cha else bytes.fromhex(hex_str).decode('unicode_escape').encode('raw_unicode_escape')



def parse_line(line, typ):
    """ extracts header, data, timestamp from each line and fixes reverse bit order """

    # TODO handle invalid inputs for code, data and timestamp
    header = None
    words_in_line = []
    timestamp = [16 ** 2 * ord(line[-1:]) + ord(line[-3:-2]), 16 ** 2 * ord(line[-5:-4]) + ord(line[-7:-6])] if \
        len(line) > 4 else None
    if typ== 'imu':
        header = line[0]
        data = line[1:-4]
    else:
        data = line[0:-4]
    for i, byte in enumerate(data):
        word = data[i] + 16 ** 2 * data[i + 1]
        if not i % 2:
            words_in_line.append(word)
        if (i == len(data) - 2):
            break

    # print('time stamp:', timestamp,'\nheader:', header,'\nline:', words_in_line)
    # if incorrect_header:
    #     print('header:', header, '\nline:', line, '\nparsed:', words_in_line)

    # print('len:', len(words_in_line))
    return [header, words_in_line, timestamp] if typ == 'imu' else [None, words_in_line, timestamp]


def signal_analyzer(path, type):
    file = open(path, 'r')
    from_txt = file.readline()
    from_txt = from_txt[1:-1]  # remove '[]' from string
    imu = from_txt.split(', b')
    lst = []
    # prev_line = None
    # prev_header = None
    # len_by_header = None
    # fixed_words_in_line = []
    # fixed_prev_line = []
    for j, data in enumerate(imu):
        if j:
            imu[j] = 'b' + data

        res = str_bytes_to_bytes(imu[j])

        if res is not None:
            # if j ==13:
            #     lst.append(parse_line(res.decode('unicode_escape').encode('raw_unicode_escape'), type))
            #     print(len(parse_line(res.decode('unicode_escape').encode('raw_unicode_escape'), type)))
                #print(res.decode('unicode_escape').encode('raw_unicode_escape'))
            # else:
            header, words_in_line, timestamp = parse_line(res, type)

            is_valid = True if header in [1, 11] else False  # if false it's partial data for imu only
            # if type == 'imu' and not is_valid:
            #     lst.remove(prev_line)
            #     if prev_header == 11:
            #         len_by_header = 16
            #     elif prev_header == 1:
            #         len_by_header = 8
            #
            #     if len_by_header <= len(words_in_line):
            #         fixed_prev_line = prev_line[:len_by_header]
            #         fixed_words_in_line = prev_line[len_by_header+1:]
            #         fixed_words_in_line.insert(0, header)
            #
            #         header = prev_header
            #         lst.append(fixed_prev_line)
            #         lst.append(fixed_words_in_line)
            #     else:
            #         fixed_prev_line = prev_line




                #lst.append(words_in_line)

            lst.append(words_in_line)
            # prev_line = words_in_line
            # prev_header = header
                #print(len(parse_line(res, type)))
        # if j == 13:
        #     print(res, 'len: ', len(parse_line(res.decode('unicode_escape').encode('raw_unicode_escape'), type)))
        #     print(imu[j])
    # write outputs to file
    filename = 'output-IMU.csv' if type == 'imu' else 'output-SNC.csv'
    file = open(filename, 'w', newline='')
    with file:
        write = csv.writer(file)
        write.writerows(lst)

    # plot data
    # for item in lst:
    #     plt.plot(item)
    #     plt.show()

    return lst


if __name__ == '__main__':
    path = '/Users/avigalk/PycharmProjects/avigal_testing/IMU.txt'
    # l = b'\x0b\x83!o\x1e\xc9\x1d\n"\x8e!b\x1e\xb8\x1d\x19"\x99!W\x1e\xa8\x1d\'"\xa2!L\x1e\x9a\x1d4"\xe4\x19\x14\x00'
    # l = str_bytes_to_bytes(l)

    # with open("my_file.txt", "wb") as binary_file:
    #     # Write bytes to file
    #     binary_file.write(l)
    lst = signal_analyzer(path, 'imu')
    # file = open("my_file.txt", 'rb')
    # from_txt = file.readline()
    a = 1