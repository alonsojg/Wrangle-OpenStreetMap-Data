import re

fltr1=re.compile(r' [A-z]+\.?$', re.IGNORECASE)
fltr2=re.compile(r'^[0-9]{5}-?[0-9]{0,5}$', re.IGNORECASE)
fltr3=re.compile(r'[0-9]{5}-?[0-9]{0,5}', re.IGNORECASE)
fltr4=re.compile(r'CA')
fltr5=re.compile(r'^[A-z]+ ?[A-z]+')


def check_postcode(postcode_results):
	d={}

	for i in postcode_results:
		if i != (u'None',):
			l=fltr2.search(i[0])
			m=fltr3.search(i[0])
			if l:
				pass
			elif m:
				d[i[0]]=m.group() 

	return d


def check_city(city_results):
	d={}

	for i in city_results:
		if i!=(u'None',):
			n=fltr4.search(i[0])
			if i[0].isupper():
				if i[0] not in d:
					d[i[0]]=i[0].title()
			elif i[0].islower():
				if i[0] not in d:
					d[i[0]]=i[0].title()
			elif n:
				a=fltr5.search(i[0])
				d[i[0]]=a.group().replace(' CA','').title()
			elif not i[0].istitle():
				d[i[0]]=i[0].title()

	return d


def check_amenity(amenity_results):
	d={}
	for i in amenity_results:
		if i!=(u'None',):
			if i[0].isupper():
				if i[0] not in d:
					d[i[0]]=i[0].title()
			elif i[0].islower():
				if i[0] not in d:
					d[i[0]]=i[0].title()
			elif not i[0].istitle():
				d[i[0]]=i[0].title()

	for i in d:
		if '_' in d[i]:
			d[i] = d[i].replace('_',' ')

	return d


def check_state(state_results):
	d={}

	for i in state_results:
		d[i[0]]="CA"

	return d