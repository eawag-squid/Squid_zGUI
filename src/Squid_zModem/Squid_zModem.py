import os
import sys
import time

import serial

from .modem import ZMODEM


class ZModemAPI:

    def __init__(self):

        self.ser = None

        self.zmodemcmdopen = False
        self.zmodem = ZMODEM(self._getc, self._putc)
        self.SquidDIR = None

        return

    def _open_zmodem_cmd(self, retrylimit):
        retries = 0
        #time.sleep(5)  # let the squid finish it's startup routine!
        numbytestoread = self.ser.inWaiting()
        answer = self.ser.read(numbytestoread)

        if answer.find(b'1: Start Filemanager') == -1:  # TODO: check if keyword is still named in the same way!
            while answer.find(b'1: Start Filemanager') == -1:
                if retries >= retrylimit:
                    return False
                self.ser.flush()

                try:
                    self.ser.write(b'*****\r')  # get into Squid Command mode!
                except serial.serialutil.SerialTimeoutException:
                    return False

                time.sleep(0.5)
                numbytestoread = self.ser.inWaiting()
                answer = self.ser.read(numbytestoread)
                retries += 1
                #print(answer)

        answer = b''
        while answer.find(b'Arduino ZModem V2.1.2') == -1:
            self.ser.flush()

            try:
                self.ser.write(b'1\n')
            except serial.serialutil.SerialTimeoutException:
                return False

            time.sleep(0.5)
            numbytestoread = self.ser.inWaiting()
            answer = self.ser.read(numbytestoread)
            print(answer)
        self.ser.flush()
        self.zmodem_cmd_open = True
        return True

    def _check_zmodem_cmd_isopen(self):
        self.ser.flush()
        numbytestoread = self.ser.inWaiting()
        answer = self.ser.read(numbytestoread)
        try:
            self.ser.write(b'HELP\n')
        except serial.serialutil.SerialTimeoutException:
            print('pyserial timeout!')
            return False
        time.sleep(0.5)
        numbytestoread = self.ser.inWaiting()
        answer = self.ser.read(numbytestoread)
        if answer.find(b'Arduino ZModem V2.1.2') != -1:
            self.zmodem_cmd_open = True
            return True
        else:
            self.zmodem_cmd_open = False
            return False

    def _close_zmodem_cmd(self):
        try:
            self.ser.write(b'EXIT\n')
        except serial.serialutil.SerialTimeoutException:
            return False

        # TODO: check if we left zmodem control mode...
        time.sleep(0.5)
        numbytestoread = self.ser.inWaiting()
        print(self.ser.read(numbytestoread))
        self.zmodem_cmd_open = False
        return True

    def _delete_file_on_squid(self, filename):
        # TODO: get directory listing and check if file exists?!
        try:
            self.ser.write(b'DEL ' + bytearray(filename, 'utf-8') + b'\n')
        except serial.serialutil.SerialTimeoutException:
            return False

        time.sleep(0.5)
        numbytestoread = self.ser.inWaiting()
        print(self.ser.read(numbytestoread))

    def squid_dir(self):
        if not self._check_zmodem_cmd_isopen():
            if not self._open_zmodem_cmd(20):
                return False

        try:
            self.ser.write(b'DIR\n')
        except serial.serialutil.SerialTimeoutException:
            return False

        time.sleep(0.5)
        numbytestoread = self.ser.inWaiting()
        self.SquidDIR = self.ser.read(numbytestoread).decode('utf-8')
        while 'End of Directory' not in self.SquidDIR:
            time.sleep(0.5)
            numbytestoread = self.ser.inWaiting()
            self.SquidDIR += self.ser.read(numbytestoread).decode('utf-8')

        self.SquidDIR = self.SquidDIR.split('\r\n')
        i = 0
        while i < len(self.SquidDIR):
            if ('\t\t' not in self.SquidDIR[i]) or (self.SquidDIR[i].find('\t') == 0):
                self.SquidDIR.remove(self.SquidDIR[i])
            else:
                self. SquidDIR[i] = self.SquidDIR[i].split('\t\t')
                i += 1

        self._close_zmodem_cmd()
        return self.SquidDIR

    def squid_send_file(self, filepath):

        if not self._check_zmodem_cmd_isopen():
            if not self._open_zmodem_cmd(20):
                return False

        self._delete_file_on_squid(os.path.basename(filepath))

        try:
            self.ser.write(b'RZ\n')
        except serial.serialutil.SerialTimeoutException:
            return False

        fn = open(filepath)
        status = self.zmodem.send(fn, retry=30)

        time.sleep(0.5)
        numbytestoread = self.ser.inWaiting()
        print(self.ser.read(numbytestoread))
        print("Transmitting file finished, Press enter to continue:")

        self._close_zmodem_cmd()

    def squid_recv_file(self, filepath, file2get):
        if not self._check_zmodem_cmd_isopen():
            if not self._open_zmodem_cmd(20):
                return False

        self.ser.write(b'SZ ' + file2get.encode('utf-8') + b'\n')

        nfiles = self.zmodem.recv(filepath, retry=2)
        print(['received', nfiles, 'files in', filepath], sys.stderr)

        self._close_zmodem_cmd()

    # wrappers for serial port access for the Zmodem receive and send code
    def _getc(self, size, timeout=1):
        self.ser.timeout = timeout
        return self.ser.read(size) or None

    def _putc(self, data, timeout=1):
        self.ser.timeout = timeout
        if type(data) is str:
            return self.ser.write(bytearray(data, 'utf-8'))  # note that this ignores the timeout
        elif type(data) is int:
            return self.ser.write(bytearray([data]))
        else:
            return self.ser.write(data)


