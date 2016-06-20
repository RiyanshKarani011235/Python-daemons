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
		if not(os.path.exists(source_directory[1:-1])) : 
			raise RuntimeError('incorrect source_directory -> ' + source_directory[1:-1])
		if not(os.path.exists(destination_directory[1:-1]))  :
			raise RuntimeError('incorrect destination_directory -> ' + destination_directory)
		# directories provided properly
		if source_directory[-2] != '/' : 
			source_directory = source_directory[:-1] + '/' + '"'
		os.system('rsync -az --delete ' + source_directory + ' ' + destination_directory)

		time.sleep(5)

def reverse_string(string) : 
	return_string = ''
	i = len(string) - 1
	while i >= 0 : 
		return_string += string[i]
		i -= 1
	return return_string

if __name__ == '__main__' : 
	if len(sys.argv) < 1 : 
		sys.stderr.write('Usage : \n[start] [source_directory] [destination_directory]\n[stop] [daemon_name]\n[cleanup]')
		raise SystemExit(1)

	filenumber_list = []

	if sys.argv[1] == 'start' : 

		# find find directory_sync daemons already running
		for root, dirs, files in os.walk('/tmp/') : 
			for file in files : 
				if ('directory_sync' in file) and ('directory_sync.' not in file) and ('.pid' in file): 
					filename = file.split('.pid')[0]
					filenumber = ''
					i = len(filename) - 1
					while i >= 0 : 
						try : 
							int(filename[i])
						except ValueError: 
							break
						else :
							filenumber += filename[i]
							i -= 1

					print('filenumber : ' + filenumber)

					filenumber = int(reverse_string(filenumber))
					filenumber_list.append(filenumber)

		# if empty
		if filenumber_list == [] : 
			filenumber_list.append(0)

		pidfile = '/tmp/directory_sync_' + str(max(filenumber_list) + 1) + '.pid'
		logfile = '/tmp/directory_sync_' + str(max(filenumber_list) + 1) + '.log'

		if len(sys.argv) < 4 : 
			sys.stderr.write('Usage : [start] [source_directory] [destination_directory]')
			raise SystemExit(1)
		try : 
			daemonize(pidfile, stdout=logfile, stderr=logfile)
		except RuntimeError as e :  
			raise SystemExit(1) 
		else : 
			# daemon started
			pass

		source_directory = '"'
		destination_directory = '"'
		end_index_list = []
		for i in range(len(sys.argv[2:])) :
			element = sys.argv[i] 
			if element[-1] != '\\' : 
				end_index_list.append(i)
		print(end_index_list)

		if len(end_index_list) != 2 : 
			sys.stderr.write('Usage : [start] [source_directory] [destination_directory]')
			raise SystemExit(1) 

		for i in range(end_index_list[0] + 1) : 
			source_directory += sys.argv[2:][i]
		source_directory += '"'
		for i in range(end_index_list[0] + 1, end_index_list[1] + 1) : 
			destination_directory += sys.argv[2:][i]
		destination_directory += '"'
		main(source_directory, destination_directory)


	elif sys.argv[1] == 'stop' : 
		if len(sys.argv) != 3 : 
			sys.stderr.write('Usage : [stop] [daemon_name]')
			raise SystemExit(1)

		pidfile = '/tmp/' + sys.argv[2] + '.pid'
		if os.path.exists(pidfile) :
			with open(pidfile) as f :
				pid = int(f.read()) 
				os.kill(pid, signal.SIGTERM) 
		else : 
			sys.stderr.write('daemon ' + sys.argv[2] + ' is not running')
			raise SystemExit(1)

	elif sys.argv[1] == 'cleanup' : 
		if len(sys.argv) != 2 : 
			sys.stderr.write('Usage : [cleanup]')
			raise SystemExit(1)
		for root, dirs, files in os.walk('/tmp/') : 
			for file in files : 
				if 'directory_sync' in file : 
					os.remove(os.path.join(root,file))

	else : 
		sys.stderr.write('unknown command') 
		raise SystemExit(1)






