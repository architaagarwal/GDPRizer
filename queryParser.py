# Function graphPrint prints out the equality tuple as Graphviz needs it -- no dots
# Inputs: 
	# eq_list: list of length 2. eq_list[0] is LHS of equality, eq_list[1] RHS
	# aliases: the dictionary of aliases
import json
import re
import string


# Inputs: s: string, aliases: dictionary
# Output: s if s is not an alias, otherwise the value for which s is an alias
def replaceAlias(s, aliases):
	global aliases_resolved, aliases_error
	if s in aliases:
		if aliases[s] != "ERROR":
			#aliases_resolved += 1
			return aliases[s]
		else:
			#aliases_error += 1
			return s
	else:
		return s

# schema: the global tables_dx dictionary which in some way stores the schema of the database
# Output: table and colname after de-aliasing
def deAlias(name, aliases, schema, uniq_col_to_table):
	if "." in name: # this means that name might have the correct table and col name already
		table, col = name.split('.')
		# try to de-alias table first
		if table not in schema:
			table_temp = replaceAlias(table, aliases)
			if "." not in table_temp and table_temp in schema:
				table = table_temp
			else: # if "." is in the value returned by replaceAlias, then it's not the right table
				table = "NOT_FOUND"
	else:
		col = name
		table = "NOT_FOUND"

	# at this point table has either been found or it's value = "NOT_FOUND"
	# let's first attempt to fix the column
	if table != "NOT_FOUND":
		if col in schema[table].colnames:
			return [table, col]
		else:
			col_temp = replaceAlias(col, aliases)
			if "." in col_temp:
				table_temp, col_temp = col_temp.split('.')
				# if this new table is same as the old one, then it's the right column, else not
				if table_temp == table:
					col = col_temp 
					return [table, col]
				else:
					return [table, "NOT_FOUND"]
			else: # col_temp didn't have a ".", which means some de-aliasing has happened
				if col_temp in schema[table].colnames:
					return [table, col_temp]
				else:
					return [table, "NOT_FOUND"]
	else:
		# if table is not found, first try to de-alias the col and see if it can return the tablename
		col_temp = replaceAlias(col, aliases)
		if "." in col_temp:
			table_temp, col_temp = col_temp.split('.')
			if table_temp in schema and col_temp in schema[table_temp].colnames:
				return (table_temp, col_temp)
			else:
				return ["NOT_FOUND", "NOT_FOUND"]
		else:
			# see if there exists only table with this col
			if col_temp in uniq_col_to_table:
				table = uniq_col_to_table[col_temp]
				return [table, col_temp]
			else:
				return ["NOT_FOUND", col_temp]


# An edge is valid if its end points are in schema 
def isValidEdge(ltable, lcol, rtable, rcol, schema):
	if (ltable in schema) and (rtable in schema) \
	and (lcol in schema[ltable].colnames) and (rcol in schema[rtable].colnames):
		return True
	else:
		return False

# if word is not of the form tablename.colname, attach the tablename to it
def appendTableName(word, from_tb):
	if "." in word:
		return word
	else:
		return from_tb + "." + word

# Function process computes the columns that the query was joined on and the aliases in query
def process(json_dict, join_list, aliases, inside_where, from_tb):
	# check for aliasing at the current level of recursion
	if "name" in json_dict:
		if "value" in json_dict and isinstance(json_dict["value"], str):
			aliases[json_dict["name"]] = json_dict["value"]
		# this means, a complicated alias has been created
		else: 
			aliases[json_dict["name"]] = "ERROR"

	# Recursively find all the eq keys and aliases
	for key, value in json_dict.items():
		# Direct check
		if key == 'eq':
			eq_list = json_dict[key]
			# Eliminate placeholder lines and lines where RHS of  equality is an integer
			# TODO: also eliminate lines where RHS of equality is a string constant
			if (len(eq_list)==2) and ('PLACEHOLDER' not in eq_list) and (not isinstance(eq_list[1], int) and (not isinstance(eq_list[1], dict))):
				
				# if query is of the form: FROM T WHERE x = y, then eq_list will be "[T.x, T.y]"
				if inside_where and from_tb != "":
					eq_list[0] = appendTableName(eq_list[0], from_tb)
					eq_list[1] = appendTableName(eq_list[1], from_tb)
				join_list.append(eq_list)

		if key == 'from': 
			if isinstance(value, str):
				from_tb = value 
			else:
				from_tb = ""

		# Nested dictionary
		if isinstance(value, dict):
			if key == 'where' or inside_where == True:
				process(value, join_list, aliases, True, from_tb)
			else:
				process(value, join_list, aliases, False, from_tb)

		# Nested list of dictionaries
		elif isinstance(value, list):
			for item in value:
				if isinstance(item, dict):
					if key == 'where' or inside_where == True:
						process(item, join_list, aliases, True, from_tb)
					else:
						process(item, join_list, aliases, False, from_tb)

def updateFks(ltable, lcol, rtable, rcol, schema):
	assert ltable in schema, "ltable not found in schema"
	assert rtable in schema, "rtable not found in schema"
	if lcol not in schema[ltable].fk:
		schema[ltable].fk.append(lcol)

	if rcol not in schema[rtable].fk:
		schema[rtable].fk.append(rcol)

# neigh_dx: 
	# key : (tablename T, colname C); 
	# Value: set of (tablename, colname) pairs representing neighbors of T.C
def updateNeighborhood(ltable, lcol, rtable, rcol, neigh_dx):
	# if this table.col is not yet known to have an edge, first initialize it in the dx
	if (ltable, lcol) not in neigh_dx:
		neigh_dx[(ltable, lcol)] = set()
	if (rtable, rcol) not in neigh_dx:
		neigh_dx[(rtable, rcol)] = set()
	
	# update the neighborhood of both the endpoints of the edge
	neigh_dx[(ltable, lcol)].add((rtable, rcol))
	neigh_dx[(rtable, rcol)].add((ltable, lcol))		

def convertToRightCase(ls, label):
	for k in ls:
		if k.upper() == label:
			return k
	print("SOMETHING WENT WRONG: NO MATCHING FOUND FOR TABLE: ", label)
	return "CASE_ERROR"

'''
create the query graph from parsed queries (constructed by cleanData.py)
'''
def createGraphFromQueries(schema, schema_upper, uniq_col_to_table, uniq_col_to_table_upper, parsed_queries_filename_json):
	# since we do not know whether the the queries and the schema would be in the same case (upper or lower)
	# we use the uppercase data-structures to test whether a key (for eg, a tablename or a colname) exists or not
	# for example a tablename in DX can be tested by simply converting tablename to uppercase and testing if it exists in dx.	
	# NOTE: since queries are already in uppercase (cleanData.py does that), there is no need to convert them to uppercase first
	
	nodes_dx = {}
	edges_dx = {}
	neigh_dx = {}
	valid_edges_count = 0
	invalid_edges = 0

	with open(parsed_queries_filename_json, "r") as fr:
		parsed_queries = json.load(fr)
		i = 0
		for json_dict in parsed_queries:
			aliases = {} # dictionary with key = alias, value = original name
			join_list = [] # list of list
			i += 1	
			process(json_dict, join_list, aliases, False, "")
		
			for eq_list in join_list:

				# de-alias the two end points of each equality
				ltable, lcol = deAlias(eq_list[0], aliases, schema_upper, uniq_col_to_table_upper)
				rtable, rcol = deAlias(eq_list[1], aliases, schema_upper, uniq_col_to_table_upper)

				left = ltable + "_" + lcol
				right = rtable + "_" + rcol	
				# min and max sort the nodes of the edges. This helps to de-duplicate edges : a -- b and b -- a
				left, right = [min(left, right), max(left, right)]
				# store them in nodes_dx : will be helpful to draw the join-graph with only the nodes with edges incident on them
				nodes_dx[left] = 1
				nodes_dx[right] = 1

				# create the edge from two end points
				edge = left + " -- " + right
				
				# An edge is valid if its end points are in schema 
				is_valid = isValidEdge(ltable, lcol, rtable, rcol, schema_upper)

				# de-duplication of edges
				if edge not in edges_dx :
					if is_valid:
						edges_dx[edge] = 1
						valid_edges_count += 1
						# print("valid edge found", edge)
					else:
						invalid_edges += 1
						# print("invalid edge found", edge, eq_list)
				
				# if edge is valid, add its endpoints as foreign keys
				if(is_valid):
					# ltable, lcol, rtable, rcol will all be in uppercase
					# However foreign-key columnames and valid_edges_dx should be in the same case as the schema
					# therefore use schema to do the correct case conversion before adding edges and foreign-key colnames 
					# in their data structures
					ltable = convertToRightCase(schema.keys(), ltable)
					rtable = convertToRightCase(schema.keys(), rtable)
					lcol = convertToRightCase(schema[ltable].colnames, lcol)
					rcol = convertToRightCase(schema[rtable].colnames, rcol)
					updateFks(ltable, lcol, rtable, rcol, schema)
					updateNeighborhood(ltable, lcol, rtable, rcol, neigh_dx)

	return nodes_dx, edges_dx, neigh_dx