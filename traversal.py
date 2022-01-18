from collections import deque
from global_vars import *
from data_structures import *

def traverseLevels(tablename, columnname, query_value, db_conn):
	# Creating a query object at level 0
	root_col = tables_dx[tablename].obj_columns_dx[columnname]
	root = Query(root_col, [query_value], False)
	level_dx[0].append(root)
	level = 0
	
	while level in level_dx:
		# list to store query objects for unvisited columns
		listQueries = []
		for obj_query in level_dx[level]:
			if obj_query.obj_col.proximity == -1:
				listQueries.append(obj_query)
		# remove query objects that are connected by Pk-- edges
		processedQueries = removePkConnections(listQueries)	
		# processedQueries = listQueries
		# Q for bfs: using deque to be able to iterate without popping from Q
		q = deque(processedQueries)	

		# DO NOT merge this for-loop with the above one by setting proximity inside of if-statement
		for obj_query in q:
			obj_query.obj_col.proximity = level
		# Run the bfs for the current level
		bfsLevel(q, db_conn)
		level += 1

def removePkConnections(listQueries):
	# remove non-Pk queries that are connected to a Pk query already in the queue
	# remove composite Pk in favor of non-composite ones
	
	# More explanation: if two columns are at the same level and have an edge between them,
	# we check if one of them is a pk. If yes, we remove the other one from level_dx and let the bfs start from the pk column
	# if non of them are pks, both of them stay in level_dx.

	# using a duplicate list to avoid weird iteration
	duplicateListQueries = listQueries[:]
	
	for obj_query in listQueries:
		obj_curr_col = obj_query.obj_col
		if isNonCompPrimaryKey(obj_curr_col) and obj_curr_col in neigh_dx:
			neighborQueries = [query for query in listQueries if query.obj_col in neigh_dx[obj_curr_col] and not isNonCompPrimaryKey(query.obj_col)]
			for neighborQuery in neighborQueries:
				# sometimes main Pk is repeated in listQueries
				if neighborQuery in duplicateListQueries:
					# print(f"removing edge \t {neighborQuery.obj_col.tablename}.{neighborQuery.obj_col.colname} -- [PK] {obj_curr_col.tablename}.{obj_curr_col.colname}")
					duplicateListQueries.remove(neighborQuery)
	return duplicateListQueries

def isNonCompPrimaryKey(obj_col):
	# returns true if the column object is (non-composite) Pk
	obj_table = tables_dx[obj_col.tablename]
	if obj_col.colname in obj_table.pk and len(obj_table.pk)==1:
		return True
	return False

def bfsLevel(q, db_conn):
	# Checking for values
	while q:
		curr_query = q.popleft()
		curr_table = curr_query.obj_col.tablename
		curr_col = curr_query.obj_col.colname
		curr_prox = curr_query.obj_col.proximity

		obj_curr_table = tables_dx[curr_table]

		# see if data needs to be extracted from a view or otherwise
		if obj_curr_table.is_virtual:
			view_table = "V_" + curr_table
		else:
			view_table = curr_table

		if not curr_query.is_sibling:
			if validList(obj_curr_table.non_filtered_colnames) and validList(curr_query.value):
				# Add SQL query for this query object to output
				output_query = "SELECT DISTINCT "+ valuesToString(obj_curr_table.non_filtered_colnames, False) + " FROM " + view_table + " WHERE "+curr_col+" IN "+valuesToString(curr_query.value, True)+";"
				
				# Uncomment the lines with output_data to output data instead of queries
				output_data = db_conn.execute(output_query) 
				# Uncomment the following line to see the set of queries that will extract user data
				# print("*********** \n ",output_query)
				# for row in output_data:
				# 	print(row)	
				# if view_table == 'PaperReview':
				# 	print("Output query is ******** ", output_query)
				logExtractedData(output_data, curr_table)

		# Add all (not redacted) siblings to level_dx
		siblings = obj_curr_table.colnames_with_edges
		for sibling in siblings:
			# if sibling in obj_curr_table.redacted_colnames:
			# 	continue
			obj_sibling = obj_curr_table.obj_columns_dx[sibling]
			if obj_sibling.proximity == -1 and validList(curr_query.value):
				sibling_value_query = "SELECT DISTINCT "+sibling+" FROM "+view_table+" WHERE "+curr_col+" IN "+ valuesToString(curr_query.value, True)
				# execute the query
				# print("*********** SIBLING", sibling_value_query)
				sibling_value_data = db_conn.execute(sibling_value_query)
				# convert answers to list - unpacking tuples
				sibling_value = [value for value, in sibling_value_data]
				sibling_query = Query(obj_sibling, sibling_value, True)
				level_dx[curr_prox + 1].append(sibling_query)
	
		# Traverse children
		child_prox = curr_prox + 1
		if curr_query.obj_col in neigh_dx:
			for child in neigh_dx[curr_query.obj_col]:
				if child.proximity == -1 or child.proximity == child_prox:
					child_query = Query(child, curr_query.value, False)
					child.proximity = child_prox
					q.append(child_query)

def validList(inputList):
	# returns True if the list contains at least one non-None element
	for val in inputList:
		if val is not None:
			return True
	return False

def valuesToString(valueList, parans):
	# assuming valueList is valid -- contains at least one non-None value
	# converts a list of values into a string to add to the IN clause
	valueStringForQuery = ""
	if parans:
		valueStringForQuery = "("
	for value in valueList:
		if value is not None:
			valueStringForQuery += str(value)+', '
	# removing last comma
	valueStringForQuery = valueStringForQuery[:-2]
	if parans:
		valueStringForQuery += ")"
	return valueStringForQuery

def logExtractedData(output_data, tablename):
	result_obj = tables_dx[tablename].result
	for row in output_data:
		key = str(row)

		# if this row is already been extracted in the past, ignore it
		if key in result_obj.extracted:
			# print("DUPLICATE ROW EXTRACTED")
			continue
		else:
			result_obj.extracted[key] = True
			if key in result_obj.gt:
				# if tablename == "LINEITEM":
				# 	print("came here")	
				result_obj.gt[key] = True
				result_obj.tp += 1
				result_obj.fn -= 1 
			else:
				# print("incrementing fp for query ", key)
				result_obj.fp += 1

def initializeLevelDX():
	# Initialize the level dictionary with levels = total no. of col and empty Qs
	col_count = 0
	for table in tables_dx:
		curr_cols = len(tables_dx[table].colnames)
		col_count += curr_cols
	for i in range(col_count):
		empty_q = deque()
		level_dx[i] = empty_q

def setProximities():
	# initializing the column objects for each table
	for tablename in tables_dx:
		obj_table = tables_dx[tablename]
		for obj_col in obj_table.obj_columns_dx.values():
			obj_col.proximity = -1

def extractData(app_settings, ds_id, db_conn):
	# initialize levels for the traversal and then traverse
	initializeLevelDX()
	setProximities()
	traverseLevels(app_settings.start_table, app_settings.start_column, ds_id, db_conn)
