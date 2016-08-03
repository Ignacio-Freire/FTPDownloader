import os
import gui
import sys
import time
import shutil
import pickle
import atexit
import codecs
from ftplib import FTP, all_errors
from time import strftime, localtime
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox


class MainWindow(QMainWindow, gui.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.tests = []
        self.filelist = []
        self.filename = os.path.expanduser('~/Documents/FTPDownloader.pickle')

        if os.path.isfile(self.filename):
            with open(self.filename, 'rb') as f:
                self.tests, self.filelist, self.loadIP, self.loadPass, self.loadReq, self.loadUser = pickle.load(f)

            self.lineIP.setText(self.loadIP)
            self.lineUser.setText(self.loadUser)
            self.linePass.setText(self.loadPass)
            self.lineReq.setText(self.loadReq)

        self.load_archivos()
        self.load_casos()

        self.pushAddPrueba.clicked.connect(self.add_caso)
        self.lineCaso.returnPressed.connect(self.add_caso)
        self.pushAddArchivo.clicked.connect(self.add_archivo)
        self.lineNombreMainframe.returnPressed.connect(self.add_archivo)
        self.pushClearArchivos.clicked.connect(self.clear_archivos)
        self.pushClearPruebas.clicked.connect(self.clear_pruebas)
        self.pushDeletePrueba.clicked.connect(self.borrar_caso)
        self.pushDeleteArchivo.clicked.connect(self.borrar_archivo)
        self.pushRenamePrueba.clicked.connect(self.renombrar_caso)
        self.pushRenameArchivo.clicked.connect(self.renombrar_archivo)

        self.pushButton.clicked.connect(about)

        self.pushDownload.clicked.connect(self.nothing)
        self.pushClearAll.clicked.connect(self.reset_all)

        atexit.register(self.save_state)

    def nothing(self):
        pass

    def print_log(self, message):
        log = '[{}] {}'.format(strftime("%H:%M:%S", localtime()), message)
        self.plainTextLog.appendPlainText(log)

    def load_casos(self):
        self.listPruebas.clear()
        for caso in self.tests:
            self.listPruebas.addItem(caso.capitalize())

    def load_archivos(self):
        self.listArchivos.clear()
        for item in self.filelist:
            self.listArchivos.addItem(
                '{} - {}   - {}'.format(item[0], item[1].upper(), 'Tx' if item[2] == True else 'Único'))

    def add_caso(self):
        test = self.lineCaso.text()

        if test:
            self.tests.append(test.capitalize())
            self.lineCaso.clear()
            self.load_casos()
        else:
            self.print_log('Campo Caso vacio.')

    def add_archivo(self):
        mainframe = self.lineNombreMainframe.text()
        nombre = self.lineNombre.text()
        tx = True if self.checkTx.isChecked() else False

        if mainframe:
            if not nombre:
                self.print_log('Nombre vacio. Se nombrara como archivo en mainframe.')
            self.filelist.append((nombre, mainframe.upper(), tx))
            self.lineNombreMainframe.clear()
            self.lineNombre.clear()
            self.load_archivos()
        else:
            self.print_log('Nombre en Mainframe vacio.')

    def clear_archivos(self):
        confirm = del_confirmation('Reset', 'Desea borrar todos los archivos?')

        if confirm == gui.QtWidgets.QMessageBox.Yes:
            self.filelist.clear()
            self.listArchivos.clear()
            self.load_archivos()

    def clear_pruebas(self):
        confirm = del_confirmation('Reset', 'Desea borrar todas las pruebas?')

        if confirm == gui.QtWidgets.QMessageBox.Yes:
            self.tests.clear()
            self.listPruebas.clear()
            self.load_casos()

    def borrar_caso(self):
        index = self.listPruebas.currentRow()
        if index == -1:
            self.print_log('Seleccionar item.')
        else:
            self.tests.pop()
            self.load_casos()

    def borrar_archivo(self):
        index = self.listArchivos.currentRow()
        if index == -1:
            self.print_log('Seleccionar item.')
        else:
            self.filelist.pop(index)
            self.load_archivos()

    def renombrar_caso(self):
        new_name = self.lineCaso.text()
        index = self.listPruebas.currentRow()

        if not new_name:
            self.print_log('Ingresar nombre nuevo')
        elif index == -1:
            self.print_log('Seleccionar item.')
        else:
            self.tests[index] = new_name
            self.lineCaso.clear()
            self.load_casos()

    def renombrar_archivo(self):
        index = self.listArchivos.currentRow()

        new_name = self.lineNombre.text()
        new_mainframe_name = self.lineNombreMainframe.text()
        new_state = True if self.checkTx.isChecked() else False

        if not new_mainframe_name:
            self.print_log('Ingresar nombre nuevo.')
        elif index == -1:
            self.print_log('Seleccionar item.')
        else:
            self.filelist[index] = (new_name, new_mainframe_name, new_state)
            self.lineNombre.clear()
            self.lineNombreMainframe.clear()
            self.load_archivos()

    def reset_all(self):
        confirm = del_confirmation('Reset', 'Se borrarán todos los datos,\n'
                                            'excepto la info de login.\n'
                                            'Desea continuar?')
        if confirm == QMessageBox.Yes:
            self.clear_archivos()
            self.clear_pruebas()
            self.lineReq.clear()
            self.lineCaso.clear()
            self.lineNombreMainframe.clear()
            self.lineNombre.clear()
            self.checkTx.setCheckState(0)
            self.plainTextLog.clear()

    def save_state(self):
        save_ip = self.lineIP.text()
        save_user = self.lineUser.text()
        save_pass = self.linePass.text()
        save_req = self.lineReq.text()

        with open(self.filename, 'wb') as s:
            pickle.dump([self.tests, self.filelist, save_ip, save_pass, save_req, save_user], s)


def main():
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    app.exec_()


def del_confirmation(title, message):
    choice = QMessageBox.question(QMessageBox(), title, message,
                                  QMessageBox.Yes | QMessageBox.No,
                                  QMessageBox.No)
    return choice


def about():
    gui.QtWidgets.QMessageBox.information(gui.QtWidgets.QMessageBox(), 'About',
                                          '  \'FTPDownlader 2016\' \n         Ignacio Freire',
                                          QMessageBox.Ok)


if __name__ == '__main__':
    main()
