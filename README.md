# FTPDownloader

This is my first fully fledged script with a GUI that has been distributed in my workplace (using PyInstaller). It started as a simple way to download a couple of files from an IBM Mainframe but later evolved in a tool that saved a lot of time during the testing stage of a requirement. Some of the biggest requirements that took around 1 hour to download and organize 100 files went down up to 5 seconds after the user loaded everything. 

To use it:

On the program load the test cases on the left box, all the files needed per case on the right side, the server IP and your login info. You can also add single files and they will be downloaded separately in order to avoid repetition in case the same file is used across all tests. Then the program will iterate through the test cases downloading each file and saving them in an organizaed fashion on the user desktop.

On the Mainframe side, it is recomended to generate a Schedule which runs all the tests one after the other. A good way to fully automate the process is to add a variable `%%TEST` on each mask and assigning the test number to it. Then at the end of the file you wish to download, add `.T%%TEST`. This way the program knows which files need to be downloaded for each test case, otherwise it will just download the file as unique. For example `TDSP.PIG.HIGIT.T%%TEST` then this will be`TDSP.PIG.HIGIT.T1` for the first case, `TDSP.PIG.HIGIT.T2` for the next and so on. If you choose to download it as a single file you can just use `TDSP.PIG.HIGIT`



