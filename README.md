
# Microsoft SQL Server Object Related Mapping
##### MSORM
[msorm](https://github.com/bilinenkisi/msorm) is a basic [MSSQL](https://en.wikipedia.org/wiki/Microsoft_SQL_Server) [Object Related Mapper](https://en.wikipedia.org/wiki/Object%E2%80%93relational_mapping) for Python3.x versions. With msorm, existing mssql database can be easily mapped with django style model system. It is still an alpha project
[Click For source code and pre-releases of msorm](https://github.com/bilinenkisi/msorm).

## Installation
You can install the [msorm](https://github.com/bilinenkisi/msorm) from [PyPI](https://pypi.org/project/msorm/):

    pip install msorm

 [msorm](https://github.com/bilinenkisi/msorm) is supported on Python 3.7 and above.

## How to use
To use [msorm](https://github.com/bilinenkisi/msorm) first of all you have to create python file (which is prefered name is "models.py"). After that you have to initialize [msorm](https://github.com/bilinenkisi/msorm) :
````Python
from msorm import models
ip_address = "ip address or server name"
database_name = "TestDatabase"
username = "username"
password = "********"
models.init(ip_address, database_name,username, password)
````
After initialization, you can start writing your own models. But models' name must have the same name as their representatives in  [MSSQL](https://en.wikipedia.org/wiki/Microsoft_SQL_Server). (without dbo tag in front of the table name).

But before creating the models you should know the fields. The only field that came from  [MSSQL](https://en.wikipedia.org/wiki/Microsoft_SQL_Server) is the Foreign key for the alpha version. The other fields are only reflections of  [MSSQL](https://en.wikipedia.org/wiki/Microsoft_SQL_Server) fields  on python variable types.
### FIELDS
Every field but the foreign key has a value parameter to be assigned as the value of the key in the database.
Fields:
```Python
from msorm.models import Field, Model

default_value = "default value of field 'For migrations'"

isnullable = True # For null parameter standart value is True

Field.bit(default=default_value, null=isnullable)

Field.bigint(default=default_value, null=isnullable)

Field.int(default=default_value, null=isnullable)

Field.smallint(default=default_value, null=isnullable)

Field.tinyint(default=default_value, null=isnullable)

Field.decimal(default=default_value, null=isnullable, precision=18, scale=0)
# precision and scale are not implemented yet
Field.numeric(default=default_value, null=isnullable, precision=18, scale=0)

Field.money(default=default_value, null=isnullable)

Field.smallmoney(default=default_value, null=isnullable)

Field.float(default=default_value, null=isnullable)

Field.real(default=default_value, null=isnullable)
length = 255 # length of the value, default value of length is min lenght of the field
Field.char(default=default_value, null=isnullable, length=length)

Field.nchar(default=default_value, null=isnullable, length=length)

Field.varchar(default=default_value, null=isnullable, length=length)

Field.nvarchar(default=default_value, null=isnullable, length=length)

Field.text(default=default_value, null=isnullable)

Field.ntext(default=default_value, null=isnullable)
length = 255 # size of the value, default value of length is min lenght of the field
Field.binary(default=default_value, null=isnullable, length=length)

Field.varbinary(default=default_value, null=isnullable, length=length)

Field.image(default=default_value, null=isnullable)

Field.date(default=default_value, null=isnullable)

Field.datetime(default=default_value, null=isnullable)

Field.smalldatetime(default=default_value, null=isnullable)
model = Model # the class of the foreign table
value = 1 # pk of the foreign table
name = "testTableID" # if the field's name is not same with class of the table set name as field's name
Field.foreignKey(model, value, name)
```
### CREATING THE MODELS
```Python
from msorm import models
from msorm.models import Field
class Server(models.Model):
    serverID = Field.int()
    discordSystemID = Field.nvarchar(length=128)
    languageID = Field.int()
    active = Field.bit()
    welcomeMessage = Field.text()
    welcomeMessagePrivate = Field.bit()
    premiumEndDate = Field.datetime()
    isBlockedAllURL = Field.bit()
    description = Field.text()
    inviteURL = Field.nvarchar(length=64)
    categoryID = Field.int()
    tags = Field.text()
    website = Field.nvarchar(length=128)
    updateUUID = Field.nvarchar(length=4000)


class Announce(models.Model):
    announceID = Field.int()
    serverID = Field.foreignKey(model=Server, name="serverID")
    channelID = Field.nvarchar(length=64)
    loopHours = Field.int()
    text = Field.text()
    title = Field.nvarchar(length=32)
```
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
````Python
from msorm.models import Model,Field
class model_name(Model):
    field1 = Field.int()

    field2 = Field.int()

    field3 = Field.int()
# There is no limit for fields or filters combination #
value = 1

value2 = 2

value3 = 4

model_name.where(field1=value,field2=value2,field3=value3)
	
model_name.where(field1=value,field2__gt=value2,field3__gte=value3)
	
model_name.where(field1=value,field2__lt=value2,field3__lte=value3)
	
model_name.where(field1=value,field2__not=value2,field3__notin=value3)
	
model_name.where(field1=value,field2__in=value2,field3__like=value3)
````
Also where(*args,**kwargs) method supports the special operators but all of them will probably be deprecated except OR(*other_operators, **kwargs) in newer versions.
#### HOW TO USE OR(*other_operators, **kwargs)
other_operators parameter will probably deprecated  in the newer versions. **kwargs variable represents collections of {field_name/filters:value}. OR operators can be used like this:
````Python
from msorm.models import Model,Field, OR
class model_name(Model):
    field1 = Field.int()

    field2 = Field.int()

    field3 = Field.int()	
# There is no limit for fields or filters combination #
value = 1

value2 = 2

value3 = 4

model_name.where(OR(field1=value)|OR(field1=value2)|OR(field1=value3))
	
model_name.where(OR(field1=value)|OR(field1__gt=value2)|OR(field1__gte=value3))
	
model_name.where(OR(field1=value)|OR(field1__lt=value2)|OR(field1__lte=value3))
	
model_name.where(OR(field1=value)|OR(field1__not=value2)|OR(field1__notin=value3))
	
model_name.where(OR(field1=value)|OR(field1__in=value2)|OR(field1__like=value3))
````
## TARGET FEATURES FOR VERSION 1.0.4a0
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
 - [x] Operators removed and OR was moved to models.py.
 - [x] Added __safe parameter for model __init\__ function to understand if __init\__ is called by a query or hand
 - [x] type_fields.py renamed as mssql_fields.py
 - [x] All fields were moved to Fields class which is in models.py
 - [x] Added developer usage for field class, now it can be called directly for creating test models
 - [x] Added settings.py
 - [x] With settings.py, added __MFA\__ and __MFL\__ to check if value is suitable for the field 
 - [x] Now, all fields except foreign key have produce method to  check if value is suitable for the field.
 - [x] **Added most of the fields of [MSSQL](https://en.wikipedia.org/wiki/Microsoft_SQL_Server) to [msorm](https://github.com/bilinenkisi/msorm)**
 - [x] Changed versioning system to Semantic Versioning 
 - [ ] Still working on automatic model creation from existing databases.
 - [ ] save system
 - [ ] Migration Support

