from collections import defaultdict
from checks import check_postcode,check_city,check_amenity,check_state
from xml_to_sqlite import xml_to_sqlite 

import pprint as pp
import re
import sqlite3
import sys

fltr1=re.compile(r'^[A-z]+\.?$', re.IGNORECASE)
fltr2=re.compile(r'^[0-9]{5}-?[0-9]{0,5}$', re.IGNORECASE)
fltr3=re.compile(r'[0-9]{5}-?[0-9]{0,5}', re.IGNORECASE)
fltr4=re.compile(r'CA')
fltr5=re.compile(r'^[A-z]+ ?[A-z]+')

conn=sqlite3.Connection('Project.db')
cur=conn.cursor()

 
### Attributes of interest

def get_attributes():
	c=[]

	with open('Data/survey.txt') as f:
		for i in f:
			b=eval(i)
			print "Attributes of interest \n######################"
			for tup in b[:30]:
				c.append(tup[0]) 
				print tup[0]


def correct(osn, corrections):
	a=osn[:-1]
	b=corrections[osn[-1]]
	a.append(b)
	try:
		return ' '.join(a)
	except Exception as e:
		raise e


def update_street_names(street_results, corrections):
	d={}

	for i in street_results:
		if i!=(u'None',):
			osn=i[0].split() 
			m=fltr1.search(osn[-1]) 
			if m:
				street_type=m.group()
				if street_type in corrections:
					d[i[0]]=correct(osn, corrections)

	for i in d:
		cur.execute('''UPDATE places SET street=? WHERE street=?''',(d[i], i))\
		.fetchall()
	conn.commit()

	print "\nProblematic Street names: \n#########################"
	pp.pprint(sorted(d.keys()))


def update(att_name, check, results):
	d=check(results)

	for i in d:
		cur.execute('''UPDATE places SET {}=? WHERE {}=?'''.format(att_name,att_name),\
			(d[i],i,))
	conn.commit()

	print "\nProblems with {}: \n{}\n".format(att_name, "#"*(20))
	pp.pprint(sorted(d.keys()))


def main():

	# xml_to_sqlite is a function that converts the osm file's data to sqlite
	# it's arguments include:
	# xml_f_name: What is the osm-xml file's name to be processed?
	# dname: What is the osm-xml file's directory (Also where all processed data will be placed,
		# including the database file); the default value is the directory where the 
		# xml_to_sqlite.py file is located. Attention: the xml_to_sqlite.py file most be located 
		# in the same directory as where this file and the osm file are located in order to be able
		# to operate. 
	# toi: What is the tag value of interest? Here we look for all parent elements containing
		# the tag on interest; the default value is tags named 'tag'.
	# top_x_attributes=30: after while data is processed, a survey is conducted in order to
		# to determine the toi's most popular attributes, here we let the script know how many
		# top attributes do we want there to be in the database per tag; the default value is 30.

	# xml_to_sqlite()

	# corrections possesses a few predefined correction for our street type
	# names in order to correct these once they are evaluated

	corrections={u'Dr':u'Drive', u'St':u'Street', u'Rd':u'Road', u'Ct':u'Court'
               , u'Ave':u'Avenue', u'Pl':u'Place', u'Ln':u'Lane'
               , u'Cir':u'Circle', u'Blvd':u'Boulevard', u'PL':u'Place'
               , u'Pl':u'Place', u'Ave.':u'Avenue', u'Avenie':u'Avenue'
               , u'Blvd.':u'Boulevard', u'Boulevar':u'Boulevard'
               , u'Boulvevard':u'Boulevard', u'Ct.':u'Court'
               , u'Dr.':u'Drive', u'E':u'East', u'Hwy':u'Highway'
               , u'Ln.':u'Lane', u'PK':u'Parkway', u'PKWY':u'Parkway'
               , u'Pkwy':u'Parkway', u'Plz':u'Plaza', u'Raod':u'Road'
               , u'Rd':u'Road', u'Rd.':u'Road', u'St.':u'Street'
               , u'avenue':u'Avenue', u'ave':u'Avenue', u'blvd':u'Boulevard'
               , u'st':u'Street', u'BLVD.':u'Boulevard', u'AVE':u'Avenue'}

	### Let's find the top 15 column names in our database

	# these should be the top 15 attributes that where filled
	# out in our xml data, and then passed into our database.
	# data/survey.txt contains a list of attributes
	# in the original xml file, sorted by the number of times
	# that attribute was found in each xml branch, in descending
	# order. 

	get_attributes()

	### Fixing problems with street names
	# some of these values had unnecessary street name abbreviations.

	street_results=cur.execute("SELECT street FROM places").fetchall()
	update_street_names(street_results, corrections)

	# Most common abbreviations where translated to their full name.

	### Fixing problems with postalcode
	# some of the problems with values in the postal code include:
	# full or partial addresses instead of zip codes, 
	# postalcodes with misinterpreted characters and
	# plain letters added unto these values.
	# here we are using a regular expression to find the integer 
	# values inside of each string.

	postcode_results=cur.execute('''SELECT postcode FROM places''').fetchall()
	update("postcode", check_postcode, postcode_results)

	# all of these values were converted to one of 3 formats:
	# a five digit number, an eight to nine digit long format
	# or an empty valyes denoted by 'None'.
	# either their original value was empty, or contained an
	# unnecessarily long format value, such as:
	# complete addresses, postcodes along with State's abbreviation or others.


	### Fixing problems with city names
	# Some of the problems include:
	# all capital letter names, inclusion
	# of state name abbreviation and lack of proper capitalization.

	city_results=cur.execute('''SELECT city FROM places''').fetchall()
	update("city", check_city, city_results)

	# Improperly capitalized names were corrected and
	# state abbreviations were cut out.  

	### Fixing amenity problems:
	# there were improperly capitilized amenity names. 

	amenity_results=cur.execute('''SELECT amenity FROM places''').fetchall()
	update("amenity", check_amenity, amenity_results)

	# all names have been properly capitlized 

	### Fixing State Names:
	# Given that this data set is that
	# of the city of San Francisco then
	# all state values should equal to California;
	# however some of these aren't.

	state_results=cur.execute('''SELECT state FROM places''').fetchall()
	update("state", check_state, state_results)

	# all values have been set to "CA";
	# including those that where initially empty.

if __name__ == '__main__':

	main()