# ------------------------------------------------Ignacio Freire-------------------------------------------------------#
import os
import shutil
import time
from ftplib import FTP

start = time.time()

user = ''
passw = ''
IP = ''

req = ''

tests = []

filelist = [('', '', True)]

ftp = FTP(IP)
ftp.login(user, passwd=passw)


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
            print('Archivo {} no encontrado.'.format(retrieve))
            os.remove(filename)


carpeta = 'Archivos descargados' if req == '' else 'PPU {}'.format(req)

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

print('Tiempo: {:.2f}'.format(time.time() - start))
