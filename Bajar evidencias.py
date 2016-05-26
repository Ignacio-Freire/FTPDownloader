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


def download_files(filesnames):
    def writeline(line):
        file.write(line + "\n")

    for files in filesnames:

        if files[0] == '':
            file = open(folder + files[1] + '.txt', 'w')
        else:
            file = open(folder + files[0] + ' - {}.txt'.format(name), 'w')

        if files[2]:
            retrieve = files[1] + '.T{}'.format(test + 1)
        else:
            retrieve = files[1]

        try:
            ftp.retrlines("RETR '{}'".format(retrieve), writeline)
        except:
            print('Archivo {} no encontrado.'.format(retrieve))


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
        download_files(filelist)
else:
    download_files(filelist)

ftp.quit()

print('Tiempo: {:.2f}'.format(time.time() - start))
