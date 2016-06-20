#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3

import os, sys
import atexit, signal
import time

def daemonize(pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null') : 

	try : 
		if os.fork() > 0 : 
			raise SystemExit(0) 
	except : 
		raise RuntimeError('fork number 1 failed') 
	else : 
		pass # fork1 succesfull

	os.chdir('/')
	os.umask(0)
	os.setsid()

	try : 
		if os.fork() > 0 :
			raise SystemExit(0)
	except : 
		raise RuntimeError('fork number 2 failed')
	else : 
		pass # fork2 succesfull

	with open(stdin,'rb',0) as f : 
		os.dup2(f.fileno(),sys.stdin.fileno())
	with open (stdout,'ab',0) as f : 
		os.dup2(f.fileno(),sys.stdout.fileno())
	with open(stderr,'ab',0) as f : 
		os.dup2(f.fileno(),sys.stderr.fileno())

	with open(pidfile,'w') as f : 
		f.write(str(os.getpid()))

	atexit.register(lambda: os.remove(pidfile))

	def sigterm_handler(signo, frame) : 
		raise SystemExit(1)

	signal.signal(signal.SIGTERM, sigterm_handler)

def main(source_directory, destination_directory) :
	# all the important code here 
	while True : 
		if not(os.path.exists(source_directory) and os.path.exists(destination_directory)) :
			raise RuntimeError('improper directory path provided')
		# directories provided properly
		if source_directory[-1] != '/' : 
			source_directory += '/'
		os.system('rsync -az --delete ' + source_directory + ' ' + destination_directory)

		time.sleep(5)

if __name__ == '__main__' : 
	if len(sys.argv) != 4 : 
		sys.stderr.write('Usage : [start|stop] [source_directory] [destination_directory]')
		raise SystemExit(1)
	
	pidfile = '/tmp/directory_sync.pid'
	logfile = '/tmp/directory_sync.log'

	if sys.argv[1] == 'start' : 
		try : 
			daemonize(pidfile, stdout=logfile, stderr=logfile)
		except RuntimeError as e :  
			raise SystemExit(1) 
		else : 
			# daemon started
			pass
		main(sys.argv[2], sys.argv[3]) 

	elif sys.argv[1] == 'stop' : 
		if os.path.exists(pidfile) :
			with open(pidfile) as f :
				pid = int(f.read()) 
				os.kill(pid, signal.SIGTERM) 

		else : 
			system.stderr.write('daemon is not running') 
			raise SystemExit(1)

	else : 
		sys.stderr.write('unknown command') 
		raise SystemExit(1)






