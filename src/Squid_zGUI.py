from functools import partial

from PyQt5 import QtCore, uic, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import _thread


import serial
import serial.tools.list_ports


import atexit
import subprocess
import sys

import tempfile
import shutil

import winreg
import itertools

from Squid_zModem.Squid_zModem import *


def enumerate_serial_ports():
    """ Uses the Win32 registry to return an
        iterator of serial (COM) ports
        existing on this computer.
    """
    path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
    except WindowsError:
        raise EnvironmentError

    for i in itertools.count():
        try:
            val = winreg.EnumValue(key, i)
            yield str(val[1])
        except EnvironmentError:
            break


filelocations = [os.getcwd(), tempfile.mkdtemp()]
ser = serial.Serial


class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        uic.loadUi("Squid_zGUI.ui", self)

        self.setFixedSize(self.size())  # prevent the user from resizing the window.
        self.setWindowTitle('Squid_zGUI')

        # register button functions:
        self.btn_open_Sport.clicked.connect(self._on_btn_open_sport_clicked)
        self.btn_refresh_Sport.clicked.connect(self._on_btn_refresh_sport_clicked)
        self.btn_browse_file2send.clicked.connect(partial(self._openfilenamedialog, 'file2send_loc'))
        self.btn_browse_file2recv.clicked.connect(partial(self._openfilenamedialog, 'file2recv_loc'))
        self.btn_send.clicked.connect(self._on_btn_send_click)
        self.buttonBox.accepted.connect(partial(self._on_buttonbox_input, 'start'))
        self.buttonBox.rejected.connect(partial(self._on_buttonbox_input, 'cancel'))

        self._button_crtl('disconnected')
        self.lbl_status.setText('')

        # radio button functions:
        self.radioBtn_dl_sel.setChecked(True)  # default: get single files...

        # refresh serial port list entries:
        self._on_btn_refresh_sport_clicked()

        # set temporary file folder for receiving filepath
        self.lineEdit_file2recv.setText(filelocations[1])

        # create a zmodem object
        self.ZmodemObj = ZModemAPI()

    def _button_crtl(self, state):
        if state == 'disconnected':
            self.btn_browse_file2send.setEnabled(False)
            self.btn_browse_file2recv.setEnabled(False)
            self.btn_send.setEnabled(False)
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setEnabled(False)
        if state == 'connected':
            self.btn_browse_file2send.setEnabled(True)
            self.btn_browse_file2recv.setEnabled(True)
            self.btn_send.setEnabled(True)
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setEnabled(False)
        if state == 'receiving':
            self.btn_browse_file2send.setEnabled(False)
            self.btn_browse_file2recv.setEnabled(False)
            self.btn_send.setEnabled(False)
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setEnabled(True)
        if state == 'sending':
            self.btn_browse_file2send.setEnabled(False)
            self.btn_browse_file2recv.setEnabled(False)
            self.btn_send.setEnabled(False)
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setEnabled(False)

    def _openfilenamedialog(self, loc):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog

        if loc == 'file2send_loc':
            filepath, _ = QFileDialog.getOpenFileName(self, "Open file to send", "",
                                                      "Squid Config Files (*.CFG)", options=options)
            self.lineEdit_file2send.setText(filepath)
            filelocations[0] = filepath
        elif loc == 'file2recv_loc':
            filepath = QFileDialog.getExistingDirectory(
                self,
                "Select receive folder",
                "/home/my_user_name/",
                QFileDialog.ShowDirsOnly
            )

            self.lineEdit_file2recv.setText(filepath)
            filelocations[1] = filepath

    # functions connected to GUI objects:
    def _on_btn_open_sport_clicked(self):
        buttontext = self.btn_open_Sport.text()
        # print('button clicked ' + buttontext)
        if buttontext == 'Connect':
            self.btn_open_Sport.setText('Connecting')
            sportname = self.comboBox_Sport.currentText()
            self.lbl_status.setText('opening serial port ' + sportname)
            _thread.start_new_thread(self._openserialport, (sportname, ))

        elif buttontext == 'Disconnect':
            ser.close()
            self.btn_open_Sport.setText('Connect')
            self.lbl_status.setText('serial port ' + ser._port + ' closed')
            self._button_crtl('disconnected')
            self.filelist.clear()

        else:
            if ser.is_open:
                ser.close()
            self.btn_open_Sport.setText('Connect')
            self._button_crtl('disconnected')

    def _on_btn_refresh_sport_clicked(self):
        self.comboBox_Sport.clear()
        for portname in enumerate_serial_ports():
            self.comboBox_Sport.addItem(portname)

    def _on_buttonbox_input(self, crtl):
        if crtl == 'start':
            receivemode = self._get_radiobtn_dl_state()
            self.recv_thread_id = _thread.start_new_thread(self._receivefiles, (receivemode, ))
        else:
            print('cancel file transfer')
            # FIXME: kill receive thread! For now we just let the thread crash by closing the serial port... :(
            ser.close()
            self.btn_open_Sport.setText('Connect')
            self.lbl_status.setText('File transfer cancelled and serial port closed!')
            self._button_crtl('disconnected')
            self.filelist.clear()


    def _on_btn_send_click(self):
        self._button_crtl('sending')
        self.lbl_status.setText('sending file: ' + os.path.basename(filelocations[0]))
        _thread.start_new_thread(self._sendfile, ())

    def _get_radiobtn_dl_state(self):
        if self.radioBtn_dl_sel.isChecked():  # default: get single files...
            return 'sel'
        else:
            return 'all'
            print(filelocations)

    def _populate_file_list(self, squid_file_list):
        self.filelist.clear()
        for entry in reversed(squid_file_list):
            item = QtWidgets.QTreeWidgetItem(entry)
            self.filelist.addTopLevelItem(item)

    def _openserialport(self, portnum):
        global ser

        # if ser.is_open:
        #     ser.close()
        # ser.timeout = 10
        try:
            ser = serial.Serial(portnum, 57600, timeout=5, writeTimeout=2)
        except serial.SerialException:
            self.lbl_status.setText('Failed to open serial port: ' + str(serial.SerialException))
            self.btn_open_Sport.setText('Connect')
            return False

        self.btn_open_Sport.setText('Disconnect')
        self.lbl_status.setText('serial port ' + portnum + ' open, fetching available file list')
        self.ZmodemObj.ser = ser
        squiddir = self.ZmodemObj.squid_dir()
        if not squiddir:
            self.lbl_status.setText('fetching available file list failed - SQUID did not answer!')
            return
        self._populate_file_list(squiddir)
        self._button_crtl('connected')
        self.lbl_status.setText('SQUID file transfer ready!')
        return True

    def _sendfile(self):
        if not self.ZmodemObj.squid_send_file(filelocations[0]):
            self.lbl_status.setText('File transmission failed - SQUID did not answer!')
        self._button_crtl('connected')
        self.lbl_status.setText('SQUID file transfer ready!')

    def _receivefiles(self, receivemode):
        self._button_crtl('receiving')
        print('start receiving file(s) ')
        if receivemode == 'sel':
            # get selected filenames to request from the squid:
            getselected = self.filelist.selectedItems()
            if getselected:
                for i in range(len(getselected)):
                    basenode = getselected[i]
                    filename = basenode.text(0)

                    self.lbl_status.setText('Downloading file ' + filename)
                    if not self.ZmodemObj.squid_recv_file(filelocations[1], filename):  # FIXME: receiving of binarx files (e.g. FIRMWARE.BIN) is not working because of decoding errors in the ZModem code!
                        self.lbl_status.setText('File transmission failed - SQUID did not answer!')

            else:
                self.lbl_status.setText('No file selected - aborting download!')
                self._button_crtl('connected')
                return

        elif self._get_radiobtn_dl_state() == 'all':
            self.lbl_status.setText('Downloading all files on SQUID SD')
            if not self.ZmodemObj.squid_recv_file(filelocations[1], '*'):
                self.lbl_status.setText('File transmission failed - SQUID did not answer!')
            filename = self.ZmodemObj.SquidDIR[0][0]  # get some filename to open the explorer on this file location...

        if filelocations[1].find('\\') == -1:
            subprocess.Popen(r'explorer /select,"%s"' % (filelocations[1] + '/' + filename).replace('/', '\\'))
        else:
            subprocess.Popen(r'explorer /select,"%s"' % (filelocations[1] + '\\' + filename))
        self._button_crtl('connected')
        self.lbl_status.setText('SQUID file transfer ready!')


def exit_handler():
    if ser.is_open:
        ser.close()
    print('application is ending!')


atexit.register(exit_handler)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()


    sys.exit(app.exec_())

