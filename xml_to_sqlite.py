from collections import defaultdict

import os
import re
import sqlite3
import sys
import xml.etree.cElementTree as CET


def merge_dicts(x,y):
	z = x.copy()
	z.update(y)
	return z


def make_dicts(dname, toi, xml_f_name):
	print '\t\tmake_dicts() activated'
	tree = CET.iterparse(os.path.join(dname,xml_f_name), events =('start',))
	f = open(os.path.join(dname,'Data/nodes.txt'), 'wb')

	for _, element in tree:
		y = element.attrib
		x = element.findall(toi)
		if x:
			a = {}
			for i in x:
				a[i.attrib['k']] = i.attrib['v']
			print >> f, merge_dicts(y,a)
		element.clear()

	f.close()
	print '\t\t\tnodes.txt made'


def attribute_set(dname):
	f = open(os.path.join(dname,'Data/nodes.txt'),'rb')
	a = []

	for i in f:
		d = eval(i)
		a += d.keys()
		a = list(set(a))

	return sorted(a)


def make_survey(top_x_attributes, dname):
	print 'finding attribute set.'

	x = attribute_set(dname)
	y = defaultdict(int)
	f = open(os.path.join(dname, 'Data/nodes.txt'), 'rb')
	f1 = open(os.path.join(dname, 'Data/survey.txt'), 'wb')

	print 'making survey.'

	for i in f:
		a = eval(i)
		for k in x:
			if k in a:
				y[k] += 1

	f.close()

	print 'sorting survey'
	y = sorted(y.items(), key = lambda (x,y): y, reverse = True)

	print
	print(y[:top_x_attributes])
	print 

	print >> f1, y
	s = [i[0] for i in y[:top_x_attributes]]
	print '\t\t\tsurvey.txt made'
	return s


def survey_check(top_x_attributes, dname):
	global headers_set
	if 'survey.txt' not in os.listdir(os.path.join(dname,'Data')): 
		print '\t\tnodes.txt found, making survey.' 
		headers_set = make_survey(top_x_attributes, dname)

	elif 'survey.txt' in os.listdir(os.path.join(dname,'Data')):
		f = open(os.path.join(dname,'Data/survey.txt'), 'rb')
		for i in f:
			s = eval(i)
			s = s[:top_x_attributes]
			s = [i[0] for i in s] 
			headers_set = s 
	else:
		print '\t\tSurvey and header_set weren\'t made'


def switch_1(top_x_attributes, dname, toi, xml_f_name):
	print 'switch 1 activated'

	if 'nodes.txt' not in os.listdir(os.path.join(dname,'Data')):
		print '\tnodes.txt not found, processing'
		make_dicts(dname, toi, xml_f_name)
		survey_check(top_x_attributes, dname)
	else:
		survey_check(top_x_attributes, dname)


def make_array(dname):
	print '\t\tmaking array.txt'
	f1 = open(os.path.join(dname,'Data/nodes.txt'), 'rb')
	f2 = open(os.path.join(dname,'Data/array.txt'), 'wb')
	for i in f1:
		d = eval(i)
		l = []
		for ii in headers_set:
			try:
				l.append(d[ii])
			except:
				l.append('None')
		print >> f2, l
	f1.close()
	f2.close()
	print '\t\t\tarray.txt made'

def switch_2(dname):
	print 'switch 2 activated'

	if 'survey.txt' in os.listdir(os.path.join(dname,'Data')):
		print '\tsurvey found'
		if 'array.txt' not in os.listdir(os.path.join(dname,'Data')):
			make_array(dname)
	else:
		print '\tsurvey not found, redirecting to switch_1'
		switch_1()
		print '\tsurvey found'
		if 'array.txt' not in os.listdir(os.path.join(dname,'Data')):
			make_array(dname)
	

def sanitize_string(l):
	x = []
	for i in l:
		if ':' in i:
			x.append(i[i.index(':')+1:] + ' BLOB')
		else:
			x.append(i+ ' BLOB')
	return x



def ins_in_db(top_x_attributes,dname,toi,xml_f_name):
	pass
	switch_1(top_x_attributes, dname, toi, xml_f_name)
	switch_2(dname)

	f1 = open(os.path.join(dname,'Data/nodes.txt'), 'rb')
	f2 = open(os.path.join(dname,'Data/array.txt'), 'rb')
	conn = sqlite3.Connection(os.path.join(dname,'Project.db'))
	c = conn.cursor()
	
	headers = 0
	for i in f1:

		headers = sanitize_string(headers_set)
	f1.close()

	try:
		c.execute('''DROP TABLE places''')
		c.execute('CREATE TABLE places ({})'.format(', '.join(headers)))
	except:
		c.execute('CREATE TABLE places ({})'.format(', '.join(headers)))
	
	for i in f2:
		x = tuple(eval(i))
		c.execute('INSERT INTO places VALUES {}'.format(str('('+'?,'*len(headers))[:-1]+')'), x)
	conn.commit()
	f2.close()


def xml_to_sqlite(xml_f_name,top_x_attributes=30,dname=os.getcwd(),toi='tag'):
	

	if 'Data' not in os.listdir(dname):
		os.mkdir(os.path.join(dname,'Data'))
	
	ins_in_db(top_x_attributes,dname,toi,xml_f_name)
	

if __name__ == '__main__':
			
	db=re.compile(r'.+\.db$',re.I)
	osm=re.compile(r'.+\.osm$',re.I)
	a=os.listdir(os.getcwd())
	x=0

	for i in a:
		x=db.search(i)
		y=osm.search(i)
		if x:
			print 'Database in folder.'
			pass
		elif y:
			xml_to_sqlite(top_x_attributes=30,dname=os.getcwd(),toi='tag',xml_f_name=y.group())
	


