#!/usr/bin/env python# -*- coding: utf-8 -*-from time import gmtime, strftimefrom constant import constantimport tempfileimport getpassimport loggingimport ctypesimport socketimport jsonimport os# --------------------------- Standard output functions ---------------------------tmp_user = Noneclass StandartOutput():	def __init__(self):		self.banner = '''|====================================================================||                                                                    ||                        The LaZagne Project                         ||                                                                    ||                          ! BANG BANG !                             ||                                                                    ||====================================================================|		'''		self.FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])	def setColor(self, s=None, color='cyan'):		if s is None:			return ''		if type(s) not in (str, unicode):			s = str(s)		COLOR_STOP = '\033[0m'		if color == 'blue':			s = '\033[34m'+ s + COLOR_STOP		elif color == 'red':			s = '\033[31m'+ s + COLOR_STOP		elif color == 'lightred':			s = '\033[31;1m'+ s + COLOR_STOP		elif color == 'green':			s = '\033[32m'+ s + COLOR_STOP		elif color == 'lightgreen':			s = '\033[32;1m'+ s + COLOR_STOP		elif color == 'yellow':			s = '\033[33m'+ s + COLOR_STOP		elif color == 'lightyellow':			s = '\033[1;33m'+ s + COLOR_STOP		elif color == 'magenta':			s = '\033[35m'+ s + COLOR_STOP		elif color == 'cyan':			s = '\033[36m'+ s + COLOR_STOP		elif color == 'grey':			s = '\033[37m'+ s + COLOR_STOP		elif color == 'darkgrey':			s = '\033[1;30m'+ s + COLOR_STOP		return s	# print banner	def first_title(self):		self.do_print(message=self.banner, color='lightyellow')		# info option for the logging	def print_title(self, title):		t = '------------------- {title} passwords -----------------\n'.format(title=title)		self.do_print(message=t, color='lightyellow')		# debug option for the logging	def title_info(self, title):		t = '------------------- {title} passwords -----------------\n'.format(title=title)		self.print_logging(function=logging.info, prefix='', message=t, color='lightyellow')	def print_user(self, user):		# Print user when verbose mode is enabled (without verbose mode the user is printed on the write_output python file)		if logging.getLogger().isEnabledFor(logging.INFO) == True:			self.do_print('########## User: {user} ##########\n'.format(user=user))	def print_footer(self):		footer = '[+] %s passwords found.\n' % str(constant.nbPasswordFound)		if logging.getLogger().isEnabledFor(logging.INFO) == False:			footer += 'For more information launch it again with the -v option'		self.do_print(footer)	def print_hex(self, src, length=8):		N=0; result=''		while src:			s,src = src[:length],src[length:]			hexa = ' '.join(["%02X"%ord(x) for x in s])			s = s.translate(self.FILTER)			result += "%04X   %-*s   %s\n" % (N, length*3, hexa, s)			N+=length		return result	def try_unicode(self, obj, encoding='utf-8'):		try:			if isinstance(obj, basestring):				if not isinstance(obj, unicode):					obj = unicode(obj, encoding)		except:			pass		return obj	# centralize print function	def do_print(self, message='', color=False):		# quiet mode => nothing is printed		if constant.quiet_mode:			return				message = self.try_unicode(message)		if color:			self.print_without_error(self.setColor(s=message, color=color))		else:			self.print_without_error(message)	def print_without_error(self, message):				try:			print message		except:			print repr(message)	def print_logging(self, function, prefix='[!]', message='', color=False):		if constant.quiet_mode:			return		if color:			function(u'{prefix} {message}'.format(prefix=self.setColor(s=prefix, color=color), message=message))		else:			function(u'{prefix} {message}'.format(prefix=prefix, message=message))	def print_output(self, software_name, pwdFound, title1 = False):			# manage differently hashes / and hex value		if pwdFound:			category = None			if '__LSASecrets__' in pwdFound:				pwdFound.remove('__LSASecrets__')				category = 'lsa'				pwdFound = pwdFound[0]			elif '__Hashdump__' in pwdFound:				pwdFound.remove('__Hashdump__')				category = 'hash'				pwdFound = pwdFound[0]			elif '__MSCache__' in pwdFound:				pwdFound.remove('__MSCache__')				category = 'mscache'				pwdFound = pwdFound[0]		if pwdFound:			# if the debug logging level is not apply => print the title			if logging.getLogger().isEnabledFor(logging.INFO) == False:				# print the username only if password have been found				user = constant.finalResults.get('User', '')				global tmp_user				if user != tmp_user:					tmp_user = user					self.print_user(user)				# if not title1:				self.print_title(software_name)						toWrite = []						# LSA Secrets will not be written on the output file			if category == 'lsa':				for k in pwdFound:					hex = self.print_hex(pwdFound[k], length=16)					toWrite.append([k, hex])					self.do_print(k)					self.do_print(hex)				self.do_print()						# Windows Hashes			elif category == 'hash':				for pwd in pwdFound:					self.do_print(pwd)					toWrite.append(pwd)				self.do_print()			# # Windows MSCache			elif category == 'mscache':				for pwd in pwdFound:					self.do_print(pwd)					toWrite.append(pwd)				self.do_print()			# Other passwords			else:				for pwd in pwdFound:					password_category = False					# detect which kinds of password has been found					lower_list = [s.lower() for s in pwd.keys()]					password = [s for s in lower_list if "password" in s]					if password: 						password_category = password					else:						key = [s for s in lower_list if "key" in s] # for the wifi						if key: 							password_category = key						else:							hash = [s for s in lower_list if "hash" in s]							if hash:								password_category = hash										# No password found					if not password_category:						print_debug("FAILED", u"Password not found !!!")					else:						print_debug("OK", u'{password_category} found !!!'.format(password_category=password_category[0].title()))						toWrite.append(pwd)												# Store all passwords found on a table => for dictionary attack if master password set						constant.nbPasswordFound += 1						try:							passwd = pwd[password_category[0].capitalize()]							if passwd not in constant.passwordFound:								constant.passwordFound.append(passwd)						except:							pass										for p in pwd.keys():						self.do_print('%s: %s' % (p, pwd[p]))					self.do_print()								# write credentials into a text file			self.checks_write(toWrite, software_name)		else:			logging.info("[!] No passwords found\n")	def write_header(self):		time = strftime("%Y-%m-%d %H:%M:%S", gmtime())		header = '{banner}\r\n- Date: {date}\r\n- Username: {username}\r\n- Hostname:{hostname}\r\n\r\n'.format(				banner=self.banner.replace('\n', '\r\n'),				date=str(time), 				username=getpass.getuser(), 				hostname=socket.gethostname()			)		open(os.path.join(constant.folder_name, '%s.txt' % constant.file_name_results),"a+b").write(header)	def write_footer(self):		footer = '\n[+] %s passwords found.\r\n\r\n' % str(constant.nbPasswordFound)		open(os.path.join(constant.folder_name, '%s.txt' % constant.file_name_results),"a+b").write(footer)		def checks_write(self, values, category):		if values:			if "Passwords" not in constant.finalResults:				constant.finalResults["Passwords"] = []			constant.finalResults["Passwords"].append([{"Category": category}, values])def print_debug(error_level, message):	# print when password is found	if error_level == 'OK':		constant.st.do_print(message='[+] {message}'.format(message=message), color='green')	# print when password is not found	elif error_level == 'FAILED':		constant.st.do_print(message='[-] {message}'.format(message=message), color='red')	elif error_level == 'CRITICAL' or error_level == 'ERROR':		constant.st.print_logging(function=logging.error, prefix='[-]', message=message, color='red')	elif error_level == 'WARNING':		constant.st.print_logging(function=logging.warning, prefix='[!]', message=message, color='cyan')	elif error_level == 'DEBUG':		constant.st.print_logging(function=logging.debug, prefix='[!]', message=message)	else:		constant.st.print_logging(function=logging.info, prefix='[!]', message=message, )# --------------------------- End of output functions ---------------------------def parseJsonResultToBuffer(jsonString, color=False):	buffer = u''	try:		for json in jsonString:			if json:				buffer += u'##################  User: {username} ################## \r\n'.format(username=json['User'])				if 'Passwords' not in json:					buffer += u'No passwords found for this user !\r\n\r\n'				else:					for all_passwords in json['Passwords']:						buffer += u'\r\n------------------- {password_category} -----------------\r\n'.format(password_category=all_passwords[0]['Category'])						if all_passwords[0]['Category'].lower() in ['lsa', 'hashdump', 'cachedump']:							for dic in all_passwords[1]:								if all_passwords[0]['Category'].lower() == 'lsa':									for d in dic:										buffer += u'%s\r\n' % (constant.st.try_unicode(d))								else:									buffer += u'%s\r\n' % (constant.st.try_unicode(dic))						else:							for password_by_category in all_passwords[1]:								buffer += u'\r\nPassword found !!!\r\n'								for dic in password_by_category.keys():									try:										buffer += u'%s: %s\r\n' % (dic, constant.st.try_unicode(password_by_category[dic]))									except Exception, e:										print_debug('ERROR', u'Error retrieving the password encoding: {error}'.format(error=e))						buffer += u'\r\n'	except Exception as e:		print_debug('ERROR', u'Error parsing the json results: {error}'.format(error=e))	return buffer 