# Microsoft SQL Server Object Related Mapping
**MSORM**
[msorm](https://github.com/bilinenkisi/msorm) is a basic [MSSQL](https://en.wikipedia.org/wiki/Microsoft_SQL_Server) [Object Related Mapper](https://en.wikipedia.org/wiki/Object%E2%80%93relational_mapping) for Python3.x versions. With msorm, existing mssql database can be easily mapped with django style model system. It is still an alpha project
[Click For source code and pre-releases of msorm](https://github.com/bilinenkisi/msorm).

## Installation
You can install the [msorm](https://github.com/bilinenkisi/msorm) from [PyPI](https://pypi.org/project/realpython-reader/):

    pip install msorm

 [msorm](https://github.com/bilinenkisi/msorm) is supported on Python 3.7 and above.

## How to use
To use [msorm](https://github.com/bilinenkisi/msorm) first of all you have to create python file (which is prefered name is "models.py"). After that you have to initialize [msorm](https://github.com/bilinenkisi/msorm) :

	models.init(ip_adress or server_name, database_name,username, password)
After initialization, you can start writing your own models. But models' name must have the same name as their representatives in  [MSSQL](https://en.wikipedia.org/wiki/Microsoft_SQL_Server). (without dbo tag in front of the table name).

But before creating the models you should know the fields. The only field that came from  [MSSQL](https://en.wikipedia.org/wiki/Microsoft_SQL_Server) is the Foreign key for the alpha version. The other fields are only reflections of  [MSSQL](https://en.wikipedia.org/wiki/Microsoft_SQL_Server) fields  on python variable types.
### FIELDS
Every field but the foreign key has a value parameter to be assigned as the value of the key in the database.
Fields:

	from msorm.type_fields import Fields
	
	#value parameter is not a requirement
	Fields.int(value=default_value)
	
	#value parameter is not a requirement
	Fields.str(value=default_value)
	
	#value parameter is not a requirement
	Fields.bool(value=default_value)
	
	#value parameter is not a requirement
	Fields.float(value=default_value)
	
	#value parameter is not a requirement
	#model variable is a requirement. And it uses for accesing the foreign table from id.
	Fields.foreignKey(value=default_value,model=table_model)
In newer versions of [msorm](https://github.com/bilinenkisi/msorm), fields probably will be changed  with their  better version that has better capabilities to manage  [MSSQL](https://en.wikipedia.org/wiki/Microsoft_SQL_Server) with ORM 
### CREATING THE MODELS

    from msorm import models  
	from msorm.type_fields import Fields  
		
	models.init(server, database, username, password)  
   
	class Server(models.Model):  
	    serverID = Fields.int()  
	    languageID = Fields.int()  
	    active = Fields.bool()  
	    welcomeMessage = Fields.str()
		welcomeMessagePrivate = Fields.bool()  
	    premiumEndDate = Fields.str()  
	    isBlockedAllURL = Fields.bool()  
	    description = Fields.str()  
	    tags = Fields.str()  
	    website = Fields.str()  
	    updateUUID = Fields.str()  
	  
	  
	class Announce(models.Model):  
	    announceID = Fields.int() 
	    serverID = Fields.foreignKey(model=Server, name="serverID")  
	    channelID = Fields.int()  
	    loopHours = Fields.int()  
	    text = Fields.str()  
	    title = Fields.str()  
### HOW TO MAKE QUERIES
To make queries, In the alpha version [msorm](https://github.com/bilinenkisi/msorm) has only two methods. These are "where" and "all". Both methods have 'fields' parameter:
#### 'fields' PARAMETER
'fields' parameter gets a tuple which includes fields that are wanted to be pulled from the database .
When filled 'fields' parameter with field names,  [msorm](https://github.com/bilinenkisi/msorm) sets values of the fields as none which is not included in the tuple.
#### WHAT DO METHODS RETURN?
They return the collection of the model, which encapsulated as QueryDict
### QueryDict
A QueryDict which holds a collection of models, which all() method used on, and it can be iterated with for loop. Also QueryDict has six methods for easy accessing and managing the collections of the method. These methods are find(field, value), get(field, value), remove(field, value), pop(field, value), values(*fields), dicts(*fields).

	field: The name of the field holds the value
	value: wanted value of field
	
#### find(field, value)
find(field, value) method is used for filtering the model instances after queries. And it returns a new QueryDict  filled with filtered models.
#### get(field, value)
get(field, value) method is used for filtering the model instances after queries but it returns first model instance it found.
#### remove(field, value)
remove(field, value) method is used for removing the model instance. The method remove the first instance it found.
#### pop(field, value)
pop(field, value) method is used for removing the model instance. The method removes and returns  the first instance it found.
#### values(*fields)
values(*fields) method is used for retrieving values from QueryDict as a collection of tuples. 'fields' parameter gets a tuple which includes fields that are wanted to be pulled from the QueryDict.
#### dicts(*fields)
dicts(*fields) method is used for retrieving values from QueryDict as a tuple of dictionaries that hold fields and their values for every instance. 'fields' parameter gets a tuple which includes fields that are wanted to be pulled from the QueryDict.
### HOW TO USE ALL(*fields) AND WHERE(*args,**kwargs) METHODS
#### HOW TO USE  ALL(*fields) METHOD

	Announce.all() # Without using 'fields' parameter
	Announce.all("field_name")

	

#### HOW TO USE WHERE(*args,**kwargs) 
To use where you can use **kwargs variable which represents collections of {field_name/filters:value}. But to be able to use all featuers of where(*args,**kwargs) method, use filters.
#### Filters
	filedname	    : SELECT * FROM table WHERE (key=value) 
	
	fieldname__gt   : SELECT * FROM table WHERE (key>value)
	
	fieldname__gte  : SELECT * FROM table WHERE (key>=value)
	
	fieldname__lt   : SELECT * FROM table WHERE (key<value)
	
	fieldname__lte  : SELECT * FROM table WHERE (key<=value)
	
	fieldname__not	: SELECT * FROM table WHERE (key!=value)
	
	fieldname__in 	: SELECT * FROM table WHERE (key IN (tuple of given values))
	
	fieldname__not_in: SELECT * FROM table WHERE (key NOT IN (tuple of given values))
	#NOT IMPLEMENTED YET (v0.0.2a0)#
	fieldname__like : SELECT * FROM table WHERE (key LIKE given pattern)
with filters where(*args,**kwargs) method can be used like these:

	# There is no limit for fields or filters combination #
	
	model_name.where(field1=value,field2=value2,field3=value3)
	
	model_name.where(field1=value,field2__gt=value2,field3__gte=value3)
	
	model_name.where(field1=value,field2__lt=value2,field3__lte=value3)
	
	model_name.where(field1=value,field2__not=value2,field3__notin=value3)
	
	model_name.where(field1=value,field2__in=value2,field3__like=value3)
	
Also where(*args,**kwargs) method supports the special operators but all of them will probably be deprecated except OR(*other_operators, **kwargs) in newer versions.
#### HOW TO USE OR(*other_operators, **kwargs)
other_operators parameter will probably deprecated  in the newer versions. **kwargs variable represents collections of {field_name/filters:value}. OR operators can be used like this:
	
	# There is no limit for fields or filters combination #

	model_name.where(OR(field1=value)|OR(field1=value2)|OR(field1=value3))
	
	model_name.where(OR(field1=value)|OR(field1__gt=value2)|OR(field1__gte=value3))
	
	model_name.where(OR(field1=value)|OR(field1__lt=value2)|OR(field1__lte=value3))
	
	model_name.where(OR(field1=value)|OR(field1__not=value2)|OR(field1__notin=value3))
	
	model_name.where(OR(field1=value)|OR(field1__in=value2)|OR(field1__like=value3))
## TARGET FEATURES FOR VERSION 0.0.4a0
 - [x] Added get method
 - [x] Added first method
 - [x] Added count method to Model class
 - [x] Improved QueryDict class's dicts and values method
 - [x] Added dict() and values() method to Model class
 - [x] For dict() and dicts() methods, added depth parameter. (with depth parameter, related tables can be serialize as dictionary)
 - [x] Added metadata via __init_subclass to make it easier to access the field's value except for foreign field.
 - [x] Version data changed for better understanding of distributions of msorm.
 - [x] QueryObject's find, get, remove and pop functions are changed. Now, to find the wanted obj you have to give a lambda function. 
 Ex: QueryObject.get(lambda x: x.field_name == 1)
 - [x] if QueryObject's get function can't succeed to find the wanted obj, it will raise ItemNotFound (ItemNotFoundException)
 - [ ] Still working on automatic model creation from existing databases.
 - [ ] Operators still aren't deprecated.
 - [ ] Still working on make_safe function
 - [ ] save system
 - [ ] Migration Support

