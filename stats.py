import pprint as pp 
import sqlite3 as sq

c = sq.Connection('Project.db')
cu = c.cursor()

### Top ten amenities

a = cu.execute('SELECT amenity, count(*) as count\
					FROM places\
					WHERE amenity != "None"\
					GROUP BY amenity\
					ORDER BY count\
					DESC\
					LIMIT 10').fetchall()

print '\nTop ten amenities\n'
pp.pprint(a)

### Top Ten Postcode and their Cities

a = cu.execute('SELECT city, postcode, count(*) as count\
					FROM places\
					WHERE city != "None" AND postcode != "None" \
					GROUP BY postcode\
					ORDER BY count\
					DESC\
					LIMIT 10').fetchall()

print '\nTop Ten Postcode and their Cities\n'
pp.pprint(a)

### Top Ten Contributing Users

a = cu.execute('SELECT user, count(*) as count\
 					FROM places\
 					GROUP BY user\
 					ORDER BY count\
 					DESC\
 					LIMIT 10').fetchall()

print '\nTop Ten contributing Users\n'
pp.pprint(a)

### Number of Rows

a = cu.execute('SELECT count(*) as count\
 					FROM places').fetchall()

print '\nNumber of Rows\n'
pp.pprint(a)

### Number of Distinct Users

a = cu.execute('SELECT count(*) as count\
 					FROM (SELECT DISTINCT user FROM places)').fetchall()

print '\nNumber of Distinct Users\n'
pp.pprint(a)

### Number of Instances of each Amenity

a = cu.execute('SELECT amenity, count(*) as c\
 					 FROM places\
 					 WHERE postcode == "None"\
 					 GROUP BY amenity').fetchall()

print '\nNumber of Instances of each Amenity\n'
pp.pprint(a)

### Number of Rows with Building Values

a = cu.execute('SELECT count(*) as c\
					FROM places\
 					WHERE building != "None"').fetchall()

print '\nNumber of Rows with Building Values\n'
pp.pprint(a)

### Number of Rows with Building and Postcode Values

a = cu.execute('SELECT count(*) as c\
					FROM (SELECT building\
 					FROM places\
 					WHERE postcode == "None" AND building != "None")').fetchall()

print '\nNumber of Rows with Building and Postcode Values\n'
pp.pprint(a)