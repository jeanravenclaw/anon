import json

class Data:
	"""
	## OnKeyDB
	
	An easy-to-use python database.

	OnKeyDB uses JSON to store and manipulate its data,
	
	and takes advantage of Python dictionaries to create

	a simple database storage.
	
	#### It has simple functions:
	
	`db.get(path, key, default)`

	`db.set(path, key, value)`

	`db.delete(path, key, autoset)`

	`db.math(path, key, operation, value)`

	#### Advanced functions:

	`db.check(path, key, autoset)`

	`db.write(data)` 

	`db.read()`

	`db.factory(path, key, var)`
	"""
	def __init__(self):
		self.filename = "database.json"
	
	def config(self, filename : str = None):
		"""
		Configures the database.
		
		`filename` is the database json file. \
			Defaults to `database.json`"""
		self.filename = filename
	
	def read(self):
		"""
		Reads the database.

		`to_dict` is whether to return as a dictionary or not.
		Defaults to `True`.
		"""
		with open(self.filename, "r+") as file:
			# basically returns everything from the file
			data = file.read()
			data = json.loads(data) # get text from file
			return data

	def write(self, data):
		"""
		Overwrites everything in the database.
		
		`data` is the data put into the database.
		Must be a dict or a dict string.
		"""
		with open(self.filename, "w") as file:
			# just puts everything into the file
			json.dump(data, file, indent=4)
	
	def check(self, path : str, key : str, keyset = None, dictset : bool = True):
		"""
		Checks the path to avoid bugs.
		
		`path` is where to find the nested dicts
		
		`key` is the key you're looking for

		`keyset` is the default value for the key
		
		`dictset` is whether to autoset the missing paths to a dict. 
		
		Returns a dictionary of information.
		
		
		```py
		{ # if a path doesn't exist
			"status": "404_not_found",
			"report": f"{next_loc} doesn't exist in {path}"
		}
		{ # if everything was successful
			"status": "200_success",
			"report": "All values found",
			"all_data": data,
			"lowest_branch": loc,
			"key_value": loc.get(key)
		}
		```

		"""
		data = self.read() # reads the db
		paths = path.split('/') # makes a list of directories
		loc = data

		if path != "":
			for path_key in paths: # loops through the paths
				next_loc = loc.get(path_key) # gets the value of that path
				if next_loc is None: # if the path doesn't exist
					if dictset:
						next_loc = {} # assign it to a var
					else:
						return {
							"status": "404_not_found",
							"report": f"{next_loc} doesn't exist in {path}"
							}
				loc[path_key] = next_loc
				""" 
				this would be either:
				loc[path_key] = {} or
				loc[path_key] = {
					a: 1
					b: 2
				}
				"""
				loc = next_loc # to go check the next part of the dict
		
		if loc.get(key, "404_not_found") == "404_not_found":
			print(f"{key} not found in {loc} while CHECKing. defaulting to {keyset}")
			print(f"{path}/{key}")
			loc[key] = keyset
			self.write(data)
		
		return {
			"status": "200_success",
			"report": "All values found",
			"all_data": data,
			"lowest_branch": loc,
			"key_value": loc.get(key)
		}
	
	def set(self, path : str, key : str, value):
		"""
		Sets a key to a value.
		
		`path` is where to find the nested dicts
		
		`key` is the key
		
		`value` is the value set to the key
		"""
		checked = self.check(path, key)

		data = checked["all_data"]
		loc = checked["lowest_branch"]

		loc[key] = value # in the lowest part of the path, set key to value

		#print(data) # print it out to debug
		self.write(data) # finally, write it into the db
	
	def get(self, path : str, key : str, default = None):
		"""
		Returns the value of the key
		
		`path` is where to find the nested dicts
		
		`key` is the key to look for

		`default` is the default value set to key if the \
			key is `None`
		"""
		if default != None:
			checked = self.check(path, key, default)
		else:
			checked = self.check(path, key)

		data = checked["all_data"]
		loc = checked["lowest_branch"]
		
		found = loc.get(key, "404_not_found")
		if found != "404_not_found":
			return found
		else:
			print(f"{key} not found in {loc} while GETting. defaulting to {default}")
			print(f"{path}/{key}")
			loc[key] = default
			self.write(data) # write it into the db
			# default will default to None
			return loc[key]
		# return the data
	
	def delete(self, path : str, key : str, autoset : bool = True):
		"""
		Deletes the key and returns its value.
		
		`path` is where to find the nested dicts
		
		`key` is the key you're looking for
		
		`autoset` is whether to autoset the missing paths to a dict. \
			If set to false, it will return `"Invalid path."`

		"""
		data = self.read() # reads the db
		paths = path.split('/') # makes a list of directories
		loc = data

		for path_key in paths: # loops through the paths
			next_loc = loc.get(path_key) # gets the value of that path
			if next_loc is None: # if the path doesn't exist
				if autoset:
					next_loc = {} # assign it to a var
				else:
					return "Invalid path."
			loc[path_key] = next_loc
			""" 
			this would be either:
			loc[path_key] = {} or
			loc[path_key] = {
				a: 1
				b: 2
			}
			"""
			loc = next_loc # to go check the next part of the dict
		
		x = loc.pop(key, None)
		self.write(data)
		return x
	
	def math(self, path : str, key : str, operation : str, value):
		""" 
		Performs math on the key and sets it.

		`path` is where to find the nested dicts
		
		`key` is the key you're looking for

		`operation` is the operation to be performed. \
			Can be `+`, `-`, `*`, or `/`
		
		`value` is the value after the operation

		`var {operation}= {value}` eg.\
			`var += 1`
		"""
		current_value = self.get(path, key)
		#print(f"{key} before {current_value}")
		def mset(x):
			self.set(path, key, x)
		
		if operation == "+":
			self.set(path, key, current_value + value)
		if operation == "-":
			self.set(path, key, current_value - value)
		if operation == "*":
			self.set(path, key, current_value * value)
		if operation == "/":
			self.set(path, key, current_value / value)
		
		#print(f"{key} after {self.get(path, key)}")
	
	def factory(self, f_path : str, f_key : str):
		""" 
		Creates a class using the path `f_path` and the key `f_key` as arguments for all the db functions.
		Returns the class for you to set.
		"""
		s = self
		class Factory_Class:
			def read(self):
				return s.read()

			def write(self, data):
				return s.write(data)

			def check(self, keyset = None, dictset : bool = True):
				return s.check(f_path, f_key, keyset, dictset)

			def set(self, value):
				return s.set(f_path, f_key, value)

			def get(self, default = None):
				return s.get(f_path, f_key, default)

			def delete(self, autoset : bool = True):
				return s.delete(f_path, f_key, autoset)

			def math(self, operation : str, value):
				return s.math(f_path, f_key, operation, value)

		return Factory_Class

db = Data()