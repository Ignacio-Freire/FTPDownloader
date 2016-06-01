# ------------------------------------------------Ignacio Freire------------------------------------------------------ #
import os
import gui
import sys
import time
import shutil
import pickle
import atexit
from ftplib import FTP, all_errors
from time import strftime, localtime


def print_log(message):
    log = '[{}] {}'.format(strftime("%H:%M:%S", localtime()), message)
    ui.plainTextLog.appendPlainText(log)


def inicio_descarga():
    print_log('Comenzando descargas.')
    start = time.time()

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

    for caso, nombre in enumerate(tests):
        carpeta_caso = carpeta_base + 'Caso {} - {}/'.format(caso + 1, nombre)
        os.makedirs(carpeta_caso)
        return_code = descargar(test_files, carpeta_caso, nombre_caso=nombre, num_caso=caso + 1)

        if not return_code:
            break

    if return_code:
        descargar(singe_files, carpeta_base)
        print_log('Descargas finalizadas.')
        print_log('Tiempo: {:.2f}'.format(time.time() - start))


def descargar(archivos, path, **kwargs):
    nombre_caso = kwargs.get('nombre_caso', '')
    num_caso = kwargs.get('num_caso', 1)

    user = ui.lineUser.text()
    passw = ui.linePass.text()
    ip = ui.lineIP.text()

    def writeline(line):
        file.write(line + "\n")

    if not ip or not user or not passw:
        print_log('Datos de conexion incorrectos o faltantes.')
        return False

    try:
        ftp = FTP(ip)
        ftp.login(user, passwd=passw)
    except all_errors:
        print_log('Error en la conexión al servidor. Chequear datos, VPN o red.')
        return False

    for files in archivos:
        if nombre_caso and num_caso:
            archivo = '{} - {}.txt'.format(files[0] if files[0] else files[1], nombre_caso)
            command = 'RETR \'{}.T{}\''.format(files[1], num_caso)
        else:
            archivo = '{}.txt'.format(files[0] if files[0] else files[1])
            command = 'RETR \'{}\''.format(files[1])

        archivo_nuevo = path + archivo

        try:
            file = open(archivo_nuevo, 'w')
        except FileExistsError:
            os.remove(archivo_nuevo)
            file = open(archivo_nuevo, 'w')

        try:
            ftp.retrlines(command, writeline)
        except all_errors:
            file.close()
            print_log('Archivo {} no encontrado.'.format(archivo))
            os.remove(archivo_nuevo)

            ftp.quit()

    return True


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

    if confirm == gui.QMessageBox.Yes:
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
    choice = gui.QMessageBox.question(gui.QMessageBox(), title, message, gui.QMessageBox.Yes | gui.QMessageBox.No,
                                      gui.QMessageBox.No)
    return choice


def about():
    gui.QMessageBox.information(gui.QMessageBox(), 'About', '  \'FTPDownlader 2016\'© \n Creado por Ignacio Freire',
                                gui.QMessageBox.Ok)


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

    ui.pushDownload.clicked.connect(inicio_descarga)
    ui.pushClearAll.clicked.connect(reset_all)

    atexit.register(save_state)
    sys.exit(app.exec_())
