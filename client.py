from ftplib import FTP
if __name__ == '__main__':
	ftp = FTP('localhost')
	ftp.set_debuglevel(2)
	ftp.login(('admin', 'admin'))
