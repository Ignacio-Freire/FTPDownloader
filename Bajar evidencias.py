# ------------------------------------------------Ignacio Freire-------------------------------------------------------#
import os
import gui
import sys
import time
import shutil
import dill
import atexit
from ftplib import FTP
from time import strftime, localtime


def print_log(message):
    log = '[{}] {}'.format(strftime("%H:%M:%S", localtime()), message)
    ui.plainTextLog.appendPlainText(log)


def comenzar_descarga():
    start = time.time()

    user = ui.lineUser.text()
    passw = ui.linePass.text()
    IP = ui.lineIP.text()

    req = ui.lineReq.text()

    if IP == '' or user == '' or passw == '':
        print_log('Datos de conexion incorrectos o faltantes.')
    else:
        try:
            ftp = FTP(IP)
            ftp.login(user, passwd=passw)

            carpeta = 'Archivos descargados' if req == '' else 'PPU {}'.format(req)

            def download_files(filesnames, location, **kwargs):
                names = kwargs.get('name', '')
                caso = kwargs.get('caso', 1)

                def writeline(line):
                    file.write(line + "\n")

                for files in filesnames:

                    if files[0] == '':
                        filename = location + files[1] + '.txt'
                    elif tests:
                        filename = location + files[0] + ' - {}.txt'.format(names)
                    else:
                        filename = location + files[0] + '.txt'

                    file = open(filename, 'w')

                    if files[2]:
                        retrieve = files[1] + '.T{}'.format(caso)
                    else:
                        retrieve = files[1]

                    try:
                        ftp.retrlines("RETR '{}'".format(retrieve), writeline)
                    except:
                        file.close()
                        print_log('Archivo {} no encontrado.'.format(retrieve))
                        os.remove(filename)

            try:
                os.makedirs(os.path.expanduser('~/Desktop/{}'.format(carpeta)))
            except FileExistsError:
                shutil.rmtree(os.path.expanduser('~/Desktop/{}'.format(carpeta)))
                os.makedirs(os.path.expanduser('~/Desktop/{}'.format(carpeta)))

            if tests:
                for test, name in enumerate(tests):
                    folder = os.path.expanduser('~/Desktop/{}/Caso {} - {}/'.format(carpeta, test + 1, name))
                    os.makedirs(folder)
                    download_files(filelist, folder, name=name, caso=test + 1)
            else:
                folder = os.path.expanduser('~/Desktop/{}/'.format(carpeta))
                download_files(filelist, folder)

            ftp.quit()
            print_log('Tiempo: {:.2f}'.format(time.time() - start))
        except:
            print_log('No connection')


def add_caso():
    test = ui.lineCaso.text()

    if test == '':
        print_log('Campo Caso vacio.')
    else:
        tests.append(test)
        ui.lineCaso.clear()
        load_casos()


def add_archivo():
    mainframe = ui.lineNombreMainframe.text()
    nombre = ui.lineNombre.text()
    tx = True if ui.checkTx.isChecked() else False

    if mainframe == '':
        print_log('Nombre en Mainframe vacio.')
    else:
        if nombre == '':
            print('Nombre vacio. Se nombrara como archivo en mainframe.')
        filelist.append((nombre, mainframe, tx))
        ui.lineNombreMainframe.clear()
        ui.lineNombre.clear()
        load_archivos()


def load_casos():
    ui.listPruebas.clear()
    for caso in tests:
        ui.listPruebas.addItem(caso.capitalize())


def load_archivos():
    ui.listArchivos.clear()
    for item in filelist:
        ui.listArchivos.addItem(
            '{} - {}   - {}'.format(item[0].capitalize(), item[1].upper(), 'Tx' if item[2] == True else 'Único'))


def clear_pruebas():
    tests.clear()
    ui.listPruebas.clear()
    load_casos()


def clear_archivos():
    filelist.clear()
    ui.listArchivos.clear()
    load_archivos()


def borrar_caso():
    index = ui.listPruebas.currentRow()
    if index == -1:
        print_log('Seleccionar item.')
    else:
        tests.pop()
        load_casos()


def borrar_archivo():
    index = ui.listArchivos.currentRow()
    if index == -1:
        print_log('Seleccionar item.')
    else:
        filelist.pop(index)
        load_archivos()


def renombrar_caso():
    new_name = ui.lineCaso.text()
    index = ui.listPruebas.currentRow()

    if new_name == '':
        print_log('Ingresar nombre nuevo')
    elif index == -1:
        print_log('Seleccionar item.')
    else:
        tests[index] = new_name
        ui.lineCaso.clear()
        load_casos()


def renombrar_archivo():
    index = ui.listArchivos.currentRow()

    new_name = ui.lineNombre.text()
    new_mainframe_name = ui.lineNombreMainframe.text()
    new_state = True if ui.checkTx.isChecked() else False

    if new_mainframe_name == '':
        print_log('Ingresar nombre nuevo.')
    elif index == -1:
        print_log('Seleccionar item.')
    else:
        filelist[index] = (new_name, new_mainframe_name, new_state)
        ui.lineNombre.clear()
        ui.lineNombreMainframe.clear()
        load_archivos()


def reset_all():
    clear_archivos()
    clear_pruebas()
    ui.lineReq.clear()
    ui.lineCaso.clear()
    ui.lineNombreMainframe.clear()
    ui.lineNombre.clear()
    ui.checkTx.setCheckState(0)


def save_state():
    dill.dump_session(filename)


def load_state():
    dill.load_session(filename)


if __name__ == "__main__":

    tests = []
    filelist = []

    global user
    global passw
    global IP

    filename = os.path.expanduser('~/Documents/mainframedownloader.pkl')

    if os.path.isfile(filename):
        load_state()

    app = gui.QtWidgets.QApplication(sys.argv)
    MainWindow = gui.QtWidgets.QMainWindow()
    ui = gui.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    ui.lineIP.setText(IP)

    load_casos()
    load_archivos()

    ui.pushAddPrueba.clicked.connect(add_caso)
    ui.pushAddArchivo.clicked.connect(add_archivo)
    ui.pushClearArchivos.clicked.connect(clear_archivos)
    ui.pushClearPruebas.clicked.connect(clear_pruebas)
    ui.pushDeletePrueba.clicked.connect(borrar_caso)
    ui.pushDeleteArchivo.clicked.connect(borrar_archivo)
    ui.pushRenamePrueba.clicked.connect(renombrar_caso)
    ui.pushRenameArchivo.clicked.connect(renombrar_archivo)

    ui.pushDownload.clicked.connect(comenzar_descarga)
    ui.pushClearAll.clicked.connect(reset_all)

    atexit.register(save_state)
    sys.exit(app.exec_())
