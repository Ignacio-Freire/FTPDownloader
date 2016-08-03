# ------------------------------------------------Ignacio Freire------------------------------------------------------ #
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


def print_log(message):
    log = '[{}] {}'.format(strftime("%H:%M:%S", localtime()), message)
    ui.plainTextLog.appendPlainText(log)
    app.processEvents()


def prepara_descarga():
    print_log('Comenzando descargas.')
    start = time.time()
    progress = 0

    return_code = True

    req = ui.lineReq.text()

    nombre_carpeta = req if req else 'Archivos descargados'
    carpeta_base = os.path.expanduser('~/Desktop/{}/'.format(nombre_carpeta))

    try:
        os.makedirs(carpeta_base)
    except FileExistsError:
        shutil.rmtree(carpeta_base)
        os.makedirs(carpeta_base)

    test_files = [i for i in filelist if i[2] == True]
    singe_files = [i for i in filelist if i[2] == False]

    increment = 100 / (len(test_files) * len(tests) + len(singe_files))

    for caso, nombre in enumerate(tests):
        carpeta_caso = carpeta_base + 'Caso {} - {}/'.format(caso + 1, nombre)
        os.makedirs(carpeta_caso)
        return_code, prog = descargar(test_files, carpeta_caso, nombre_caso=nombre, num_caso=caso + 1,
                                      down_increment=increment, down_progress=progress)

        progress = prog
        if not return_code:
            break

    if return_code:
        return_code, prog = descargar(singe_files, carpeta_base, down_increment=increment, down_progress=progress)
        progress += prog
        ui.progressBar.setValue(prog)

        print_log('Descargas finalizadas.')
        print_log('Tiempo: {:.2f}'.format(time.time() - start))


def descargar(archivos, path, **kwargs):
    nombre_caso = kwargs.get('nombre_caso', '')
    num_caso = kwargs.get('num_caso', 0)
    d_increment = kwargs.get('down_increment', 0)
    d_progress = kwargs.get('down_progress', 0)

    user = ui.lineUser.text()
    passw = ui.linePass.text()
    ip = ui.lineIP.text()

    def writeline(line):
        file.write(line + "\r\n")

    if not ip or not user or not passw:
        print_log('Datos de conexion faltantes.')
        return False

    try:
        ftp = FTP(ip)
        ftp.login(user, passwd=passw)
    except all_errors:
        print_log('Error en la conexión al servidor. Chequear datos, VPN o red.')
        return False

    for files in archivos:

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

        if 'Migrated' in mig[1]:
            print_log('Desmigrando {}{}. Puede que no responda la pantalla en caso de que tarde más de lo esperado,'
                      ' no cerrar.'.format(files[1], '.T{}'.format(num_caso) if num_caso != 0 else ''))
            is_mig = True

        try:
            ftp.retrlines(command, writeline)
            d_progress += d_increment
            app.processEvents()
        except all_errors:
            file.close()
            print_log('No se encontró el archivo {}{}.'.format(files[1], ' del caso {}'.format(
                num_caso) if num_caso != 0 else ''))
            os.remove(archivo_nuevo)

        file.close()

        if is_mig:
            print_log('Desmigrado.')

        ui.progressBar.setValue(d_progress)

    return True, d_progress


def add_caso():
    test = ui.lineCaso.text()

    if test:
        tests.append(test.capitalize())
        ui.lineCaso.clear()
        load_casos()
    else:
        print_log('Campo Caso vacio.')


def add_archivo():
    mainframe = ui.lineNombreMainframe.text()
    nombre = ui.lineNombre.text()
    tx = True if ui.checkTx.isChecked() else False

    if mainframe:
        if not nombre:
            print_log('Nombre vacio. Se nombrara como archivo en mainframe.')
        filelist.append((nombre, mainframe.upper(), tx))
        ui.lineNombreMainframe.clear()
        ui.lineNombre.clear()
        load_archivos()
    else:
        print_log('Nombre en Mainframe vacio.')


def load_casos():
    ui.listPruebas.clear()
    for caso in tests:
        ui.listPruebas.addItem(caso.capitalize())


def load_archivos():
    ui.listArchivos.clear()
    for item in filelist:
        ui.listArchivos.addItem(
            '{} - {}   - {}'.format(item[0], item[1].upper(), 'Tx' if item[2] == True else 'Único'))


def clear_pruebas():
    confirm = del_confirmation('Reset', 'Desea borrar todas las pruebas?')

    if confirm == gui.QtWidgets.QMessageBox.Yes:
        tests.clear()
        ui.listPruebas.clear()
        load_casos()


def clear_archivos():
    confirm = del_confirmation('Reset', 'Desea borrar todos los archivos?')

    if confirm == gui.QtWidgets.QMessageBox.Yes:
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

    if not new_name:
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

    if not new_mainframe_name:
        print_log('Ingresar nombre nuevo.')
    elif index == -1:
        print_log('Seleccionar item.')
    else:
        filelist[index] = (new_name, new_mainframe_name, new_state)
        ui.lineNombre.clear()
        ui.lineNombreMainframe.clear()
        load_archivos()


def reset_all():
    confirm = del_confirmation('Reset', 'Se borrarán todos los datos,\n'
                                        'excepto la info de login.\n'
                                        'Desea continuar?')
    if confirm == gui.QtWidgets.QMessageBox.Yes:
        clear_archivos()
        clear_pruebas()
        ui.lineReq.clear()
        ui.lineCaso.clear()
        ui.lineNombreMainframe.clear()
        ui.lineNombre.clear()
        ui.checkTx.setCheckState(0)
        ui.plainTextLog.clear()


def save_state():
    save_ip = ui.lineIP.text()
    save_user = ui.lineUser.text()
    save_pass = ui.linePass.text()
    save_req = ui.lineReq.text()

    with open(filename, 'wb') as s:
        pickle.dump([tests, filelist, save_ip, save_pass, save_req, save_user], s)


def del_confirmation(title, message):
    choice = gui.QtWidgets.QMessageBox.question(gui.QtWidgets.QMessageBox(), title, message,
                                                gui.QtWidgets.QMessageBox.Yes | gui.QtWidgets.QMessageBox.No,
                                                gui.QtWidgets.QMessageBox.No)
    return choice


def about():
    gui.QtWidgets.QMessageBox.information(gui.QtWidgets.QMessageBox(), 'About',
                                          '  \'FTPDownlader 2016\' \n         Ignacio Freire',
                                          gui.QtWidgets.QMessageBox.Ok)


if __name__ == "__main__":

    tests = []
    filelist = []

    filename = os.path.expanduser('~/Documents/FTPDownloader.pickle')

    app = gui.QtWidgets.QApplication(sys.argv)
    MainWindow = gui.QtWidgets.QMainWindow()
    ui = gui.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            tests, filelist, loadIP, loadPass, loadReq, loadUser = pickle.load(f)

        ui.lineIP.setText(loadIP)
        ui.lineUser.setText(loadUser)
        ui.linePass.setText(loadPass)
        ui.lineReq.setText(loadReq)

    load_casos()
    load_archivos()

    ui.pushAddPrueba.clicked.connect(add_caso)
    ui.lineCaso.returnPressed.connect(add_caso)
    ui.pushAddArchivo.clicked.connect(add_archivo)
    ui.lineNombreMainframe.returnPressed.connect(add_archivo)
    ui.pushClearArchivos.clicked.connect(clear_archivos)
    ui.pushClearPruebas.clicked.connect(clear_pruebas)
    ui.pushDeletePrueba.clicked.connect(borrar_caso)
    ui.pushDeleteArchivo.clicked.connect(borrar_archivo)
    ui.pushRenamePrueba.clicked.connect(renombrar_caso)
    ui.pushRenameArchivo.clicked.connect(renombrar_archivo)

    ui.pushButton.clicked.connect(about)

    ui.pushDownload.clicked.connect(prepara_descarga)
    ui.pushClearAll.clicked.connect(reset_all)

    atexit.register(save_state)
    sys.exit(app.exec_())
