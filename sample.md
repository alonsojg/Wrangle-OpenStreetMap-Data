# OpenStreetMap Case Study

### Map Area

San Franciso CA, United States.

    https://www.openstreetmap.org/relation/111968
    https://mapzen.com/data/metro-extracts/metro/san-francisco-bay_california/
    
San Francisco is one of my favorite travel destinations. I decided to work with this datset to further expand my knowledge of this wonderful city.

##Problems Encountered in the Map

Looking at a small sample of this dataset, after it being processed and placed into a sqlite-based database, I noticed a few problems:

* Overabbreviated street names (e.g. 'A & B San Felipe Rd', 'A 4th St', 'A Marshall Ln', 'A Rose Ave', 'Acacia Ct', 'Adrian Ct', 'Adrian Dr', 'Ahwahnee St', 'Airline Hwy', 'Airport Blvd', ...)

* Inconsistent postal codes (e.g. '11 Westside Blvd, Hollister, CA 95023', '1350 Westside Blvd, Hollister, CA 95023', '200 Windmill Dr, Hollister, CA 95023', '201 Western Ct, Hollister, CA 95023', '641 Wiebe Way, Hollister, CA 95023', '796 Arriba Dr, Aromas, CA 95004', '981 Prospect Ave, Hollister, CA 95023', 'CA 94541', 'CA 94544', 'CA 94546', ...)

* Inconsistent and incorrectly spelled city names (e.g. 'APTOS', 'FREEDOM', 'SAN CARLOS', 'Sebastopol, CA', 'Sunnyvale, CA', 'Woodland, CA', 'cupertino', 'menlo park', 'pleasanton', 'santa clara', ...)

* Incorrectly spelled amenity names (e.g. 'clubhouse', 'dance', 'dojo', 'office', 'picnic_table', 'salon', 'shop', 'social_facility', 'taxi', 'truck_rental', ...)

* Incorrect state names (e.g. 'AZ', 'CA]', 'CAs', 'Ca', 'California', 'NC', 'None', 'ON', 'WA', 'dc', ...)

### Overabbreviated Street Names
Using simple queries one can see that in this data, just like in other, there is a lot of inconsistency in whether abbreviations should have been used. To solve this I decided to purge the data of abbreviations of most common street names using regular expressions and dictionaries. 

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
			       
	fltr1=re.compile(r' [A-z]+\.?$', re.IGNORECASE)
	
	street_results=cur.execute("SELECT street FROM places").fetchall()
	
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
				print osn
				m=fltr1.search(osn[-1]) 
				if m:
					street_type=m.group()
					if street_type in corrections:
						d[i[0]]=correct(osn, corrections)
		for i in d:
			cur.execute('''UPDATE places SET street=? WHERE street=?''',(d[i], i))\
			.fetchall()
		conn.commit()

The dictionary created works as an intermediary, this way problematic values found in the database could be sorted, then printed.

### Postal Codes

Some of the postal codes incloded alphabetic values, or even full addresses. Once again regular expressions were employed to find errors such as these in the postal code column.

	fltr2=re.compile(r'^[0-9]{5}-?[0-9]{0,5}$', re.IGNORECASE)
	fltr3=re.compile(r'[0-9]{5}-?[0-9]{0,5}', re.IGNORECASE)
	
	postcode_results=cur.execute('''SELECT postcode FROM places''').fetchall()

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
		
Here we looked for values which were neither empty (i.e. !=(u'None',)), nor filled with ONLY a range of numeric values that may vary between 5 and 10 in size. This way we could look for those which, aside from containing the numeric values, possessed alphabetic values too. Then the numeric values were extracted and set as the respective, new values.

### City Names

Inconsistent and incorrectly spelled city names were corrected using built-in python functions str.islower() and str.isupper() to look for those incorrectly capitilized city names; also a regular expression was employed in order to separate state abbreviations from city names found together as a city value.

	fltr4=re.compile(r'CA')
	fltr5=re.compile(r'^[A-z]+ ?[A-z]+')
	
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


## Some Stats

top postcode, and the cities they pertain too

	SELECT city, postcode, count(*) as count
		FROM places
		WHERE city != "None" AND postcode != "None" 
		GROUP BY postcode
		ORDER BY count
		DESC
		LIMIT 10
	
	Results
	#######
	
	City | Zip Code | # of instances
	West Sacramento , 95691 , 14817
	West Sacramento , 95605 , 5051
	San Francisco , 94122 , 4964
	Piedmont , 94611 , 2916
	San Francisco , 94116 , 2228
	Mountain View , 94043 , 2061
	Dublin , 94568 , 1897
	San Francisco , 94117 , 1423
	Oakland , 94610 , 1323
	San Francisco , 94118 , 1096
		
top facilities in the bay are:

	SELECT amenity, count(*) as count
		FROM places
		WHERE amenity != "None"
		GROUP BY amenity
		ORDER BY count
		DESC
		LIMIT 10

	Results
	#######

	Amenity | # of instances

	Parking, 15008
	Restaurant, 6469
	School, 4255
	Place Of Worship, 3241
	Bench, 2862
	Fast Food, 2389
	Cafe, 2052
	Toilets, 1707
	Bicycle Parking, 1636
	Fuel, 1402
	
Well it's no surprise that parking beats all others.

top 10 contributing users:

	SELECT user, count(*) as count
		FROM places
		GROUP BY user
		ORDER BY count
		DESC
		LIMIT 10

	Results
	#######
	
	andygol, 215875
	nmixter, 146092
	TheDutchMan13, 114632
	Eureka gold, 89029
	dannykath, 75316
	RichRico, 69184
	oldtopos, 60824
	ediyes, 47681
	Luis36995, 37251
	stevea, 34047
	
# Overview of Data

### Is the OSM XML large enough?

	211 MB before compression

### Number of Unique Users:
	
	SELECT count(*) as count FROM (SELECT DISTINCT user FROM places)
	
5407

### Number of nodes and ways

	SELECT count(*) as count FROM places
	
2062025	

# Other ideas about the dataset

One problem I found was that most marked buildings did not have a zip code assign to them
	
	SELECT count(*) as c
		FROM places
		WHERE building != "None"

Total marked buildings = 1089281

	SELECT count(*) as c
		FROM (SELECT building
		FROM places
		WHERE postcode == "None" AND building != "None")
		
Total marked buildings without a zipcode = 1044980

Over 95% of all marked buildings don't have a zipcode. This may be corrected by using their respective node's latitude and longitude values and crossreferencing with the closest designated zipcode. The benefits of this change could help more specifically describe the locality of any of these buildings. However doing so may introduce new errors into the data. Even though most of these building will be benefitted, the rest, which will then be marked off incorrectly, will be harder to locate since one of their location description may be filled with the zipcode of a wrong city, county or even state.

