import os
import shutil
import time
from ftplib import FTP


start = time.time()

user = ''
passw = ''
IP = ''

req = ''

tests = ['']

filenames = [('', '', True)]

ftp = FTP(IP)
ftp.login(user, passwd=passw)

addtest = True


def writeline(line):
    file.write(line + "\n")

try:
    os.makedirs('PPU {}'.format(req))
except FileExistsError:
    shutil.rmtree('PPU {}'.format(req))
    os.makedirs('PPU {}'.format(req))

for test, name in enumerate(tests):
    folder = 'PPU {}\Caso {} - {}\\'.format(req, test + 1, name)
    os.makedirs(folder)
    for files in filenames:

        if files[0] == '':
            file = open(folder + files[1] + 'txt', 'w')
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

ftp.quit()

print('Tiempo: {:.2f}'.format(time.time()-start))
