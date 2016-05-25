import os
from ftplib import FTP

user = ''
passw = ''
IP = ''

req = ''

tests = ['', '']

filenames = [('', ''), ('', '')]

ftp = FTP(IP)
ftp.login(user, passwd=passw)


def writeline(line):
    file.write(line + "\n")

os.makedirs('PPU {}'.format(req))

for test, name in enumerate(tests):
    folder = 'PPU {}\Caso {} - {}\\'.format(req, test + 1, name)
    os.makedirs(folder)
    for files in filenames:
        file = open(folder + files[0].format(name), 'w')
        ftp.retrlines("RETR '{}'".format(files[1].format(test + 1)), writeline)

ftp.quit()
