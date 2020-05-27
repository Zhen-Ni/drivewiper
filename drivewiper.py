
"""Wipe all data in the free space of a drive.

This program wipes free space of a drive by filling it with random binary
data. The random data is suitable for cryptographic use which means the
security of this program is guaranteed."""

import os
import base64
import ctypes
import argparse
import threading
import queue
import time

B = 1
K = B * 1024
M = K * 1024
G = M * 1024
T = G * 1024
UNIT = dict(b=B,k=K,m=M,g=G,t=T)
FILENAME_LENGTH = 12
MAX_FILE_SIZE = G*1
BLOCK_SIZE = M*4

def get_free_space(folder):
    """ Return drive free space (in bytes).
    """
    free_bytes = ctypes.c_ulonglong(0)
    ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder),
                                               None, None,
                                               ctypes.pointer(free_bytes))
    return free_bytes.value


class Wiper:
    def __init__(self, drive, * ,max_file_size=MAX_FILE_SIZE,
                 block_size=BLOCK_SIZE, filename_length = FILENAME_LENGTH):
        self._drive = drive
        self._max_file_size = max_file_size
        self._block_size = block_size
        self._filename_length = filename_length
        self._files = []
        self._status = {'current_round':0,'total_rounds':0,'total_space':0}

    def _fill(self):
        """Fill the drive with random data."""
        free_space_size = get_free_space(self._drive)
        while free_space_size:
            if MAX_FILE_SIZE < free_space_size:
                f = self._openfile()
                self._writefile(f, self._max_file_size)
                self._closefile(f)
            else:
                f = self._openfile()
                self._writefile(f, free_space_size)
                self._closefile(f)
            free_space_size = get_free_space(self._drive)

    def wipe(self, n=1):
        """Wipe all data in the free space of a drive."""
        self._status['total_rounds'] = n
        for i in range(n):
            self._status['current_round'] = i+1
            self._status['total_space'] = get_free_space(self._drive)
            self._fill()
            self._delfiles()

    def _writefile(self, file, size):
        while self._block_size < size:
            self._writefile_helper(file, self._block_size)
            size -= self._block_size
        self._writefile_helper(file, size)

    def _writefile_helper(self, file, size):
        try:
            file.write(os.urandom(size))
        except OSError:
            pass

    def _closefile(self, f):
        try:
            f.close()
            is_successful = True
        except OSError:
            is_successful = False
        return is_successful

    def _openfile(self):
        filename = base64.encodebytes(os.urandom(self._filename_length))
        filename = filename[:-1].decode()
        filename = filename.replace('/','-')
        if filename in os.listdir():
            return self._openfile()
        
        file = '/'.join([self._drive, filename])
        f = open(file, 'wb', 0)
        self._files.append(file)
        return f

    def _delfiles(self):
        while self._files:
            f = self._files.pop()
            os.remove(f)

    def __del__(self):
        self._delfiles()


def show_status(wiper, unit, check_stop, return_value):
    max_length = 0
    while not check_stop():
        status = wiper._status
        remain = get_free_space(wiper._drive)/UNIT[unit]
        total = status['total_space']/UNIT[unit]
        current = total - remain
        percentage = current / total if total != 0.0 else 0.0
        msg = '{:.6g}{u}/{:.6g}{u} {:.2f}% wiped,' \
              ' round {}/{}'.format(current, total, percentage*100, 
                                    status['current_round'],
                                    status['total_rounds'],
                                    u=unit.upper())
        max_length = max(max_length, len(msg))
        if len(msg) < max_length:
            msg += ' '*(max_length-len(msg))
        print('\r'+msg, end='')
        time.sleep(0.5)
    return_value.put(max_length)

def _main():
    parser = argparse.ArgumentParser(description="Select a drive to wipe.")
    parser.add_argument('drive', help='the drive to be wiped')
    parser.add_argument('-n', '--numrounds', default=1, type=int,
                        help='the number of rounds to wipe the drive')
    parser.add_argument('-s', '--silent', action='store_true',
                        help='silent mode')
    parser.add_argument('-u', '--unit', choices='bkmgt', default='m',
                        help='the unit used')
    parser.add_argument('--filesize', type=int,
                        help='the maximum size of files')
    parser.add_argument('--blocksize', type=int,
                        help='the maximum block size to be written to a file')
    parser.add_argument('--namelength', type=int,
                        help='the length of the names of the created files')

    args = parser.parse_args()
    kwargs = {}
    if args.filesize:
        kwargs['max_file_size'] = args.filesize * UNIT[args.unit]
    if args.blocksize:
        kwargs['block_size'] = args.blocksize * UNIT[args.unit]
    if args.blocksize:
        kwargs['filename_length'] = args.namelength
    
    wiper = Wiper(args.drive)
    if not args.silent:
        max_length = queue.Queue(1)
        stop = False
        t_msg = threading.Thread(target=show_status,
                                 args=(wiper, args.unit,
                                       lambda: stop, max_length),
                                 daemon=True)
        t_msg.start()
    wiper.wipe(args.numrounds)
    stop = True
    if not args.silent:
        t_msg.join()
        print('Finish!' + ' ' * max_length.get())


if __name__ == '__main__':
    _main()
#    w=Wiper('F:')
#    w._fill()

