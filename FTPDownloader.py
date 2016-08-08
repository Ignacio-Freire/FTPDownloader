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
from PyQt5.QtCore import QThread, pyqtSignal, QObject


class MainWindow(QMainWindow, gui.Ui_MainWindow):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.thread = QThread()

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

        self.downloader = Downloader(self.lineIP.text(), self.lineUser.text(), self.linePass.text(), self.lineReq.text(),
                                self.filelist, self.tests)
        self.downloader.moveToThread(self.thread)
        self.downloader.log.connect(self.print_log)
        self.downloader.progress.connect(self.descargado)
        self.thread.started.connect(self.downloader.prepara_descarga)
        self.downloader.finished.connect(self.thread.terminate)

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

        self.pushDownload.clicked.connect(self.start_downloads)
        self.pushStop.clicked.connect(self.stop_process)
        self.pushClearAll.clicked.connect(self.reset_all)

        atexit.register(self.save_state)

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

    def start_downloads(self):
        if not self.thread.isRunning():
            self.progressBar.setMaximum(len(self.tests) * len(self.filelist))
            self.progressBar.setValue(0)
            self.thread.start()
        else:
            self.print_log('Hay una descarga en proceso. Cancelar o reintentar al finalizar.')

    def stop_process(self):
        self.downloader.cancelar.emit()

    def descargado(self):
        self.progressBar.setValue(self.progressBar.value() + 1)


class Downloader(QObject):
    log = pyqtSignal(str, name='log')
    progress = pyqtSignal(name='progress')
    finished = pyqtSignal(name='finished')
    cancelar = pyqtSignal(name='cancelar')

    def __init__(self, ip, user, passw, req, archivos, casos):
        super().__init__()

        self.c_ip = ip
        self.c_user = user
        self.c_passw = passw
        self.c_req = req
        self.c_archivos = archivos
        self.c_casos = casos
        self.stop = False

        self.cancelar.connect(self.stop_everything)

    def stop_everything(self):
        self.stop = True

    def prepara_descarga(self):
        self.log.emit('Comenzando descargas.')
        start = time.time()

        return_code = True
        test_files = []
        singe_files = []

        reqs = self.c_req
        nombre_carpeta = reqs if reqs else 'Archivos descargados'
        carpeta_base = os.path.expanduser('~/Desktop/{}/'.format(nombre_carpeta))

        try:
            os.makedirs(carpeta_base)
        except FileExistsError:
            shutil.rmtree(carpeta_base)
            os.makedirs(carpeta_base)

        if not self.stop:
            for i in self.c_archivos:
                if i[2]:
                    test_files.append(i)
                else:
                    singe_files.append(i)

        for caso, nombre in enumerate(self.c_casos):
            if not self.stop:
                carpeta_caso = carpeta_base + 'Caso {} - {}/'.format(caso + 1, nombre)
                os.makedirs(carpeta_caso)
                return_code = self.descargar(test_files, carpeta_caso, nombre_caso=nombre, num_caso=caso + 1)

                if not return_code:
                    shutil.rmtree(carpeta_base)
                    break
            else:
                break

        if return_code:
            if not self.stop:
                self.descargar(singe_files, carpeta_base)
                self.log.emit('Descargas finalizadas.')
                self.log.emit('Tiempo: {:.2f}'.format(time.time() - start))

        if self.stop:
            self.log.emit('Descargas canceladas.')
            self.stop = False

        self.finished.emit()

    def descargar(self, archivos, path, **kwargs):
        nombre_caso = kwargs.get('nombre_caso', '')
        num_caso = kwargs.get('num_caso', 0)

        user = self.c_user
        passw = self.c_passw
        ip = self.c_ip

        def writeline(line):
            file.write(line + "\r\n")

        if not ip or not user or not passw:
            self.log.emit('Datos de conexion faltantes.')
            return False

        try:
            ftp = FTP(ip)
            ftp.login(user, passwd=passw)
        except all_errors:
            self.log.emit('Error en la conexión al servidor. Chequear datos, VPN o red.')
            return False

        for files in archivos:
            if not self.stop:
                mig = []
                is_mig = False

                if nombre_caso and num_caso:
                    ftp.retrlines('LIST \'{}.T{}\''.format(files[1], num_caso), mig.append)
                    archivo = '{} - {}.txt'.format(files[0] if files[0] else files[1], nombre_caso)
                    command = 'RETR \'{}.T{}\''.format(files[1], num_caso)
                else:
                    ftp.retrlines('LIST \'{}\''.format(files[1]), mig.append)
                    archivo = '{}.txt'.format(files[0] if files[0] else files[1])
                    command = 'RETR \'{}\''.format(files[1])

                archivo_nuevo = path + archivo

                try:
                    file = codecs.open(archivo_nuevo, 'w', "utf-8")
                except FileExistsError:
                    os.remove(archivo_nuevo)
                    file = codecs.open(archivo_nuevo, 'w', "utf-8")

                if 'Migrated' in mig[1] and not self.stop:
                    self.log.emit('Desmigrando {}{}.'
                                  ' Puede tardar varios minutos dependiendo el nivel de mirgación.'
                                  .format(files[1], '.T{}'.format(num_caso) if num_caso != 0 else ''))
                    is_mig = True

                    while is_mig:
                        print('desmig')
                        if not self.stop:
                            break
                elif self.stop:
                    return False

                try:
                    if not self.stop:
                        ftp.retrlines(command, writeline)
                        self.progress.emit()
                    else:
                        return False
                except all_errors:
                    file.close()
                    self.log.emit('No se encontró el archivo {}{}.'.format(files[1], ' del caso {}'.format(
                        num_caso) if num_caso != 0 else ''))
                    os.remove(archivo_nuevo)

                file.close()

                if is_mig:
                    self.log.emit('Desmigrado.')
            else:
                return False
        return True


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
