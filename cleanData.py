## 
# This file cleans the data, reads the schema and parses the queries
# Produces three files: clean_hotcrp-querylog.txt, schema.json and parsed_queries.json
##
import csv
import re
import string
import json
from moz_sql_parser import parse
import functools

# Function cleanQuery removes parts of the query that the parser cannot handle
# TODO: Check if losing anything meaningful
def cleanQuery(query):
	# If the query has substring, ignore that part 
	query_nosubs_comment = query.replace("substring(PaperComment.comment from 1 for ?)", "substring_comment")
	query_nosubs = query_nosubs_comment.replace("substring(Paper.title from 1 for ?)","substring_title")

	# If the query has regex, ignore that part
	query_noregs = query_nosubs.replace("email not regexp ? and ", "")
	
	# If the query is parametrized, subs the questionmark with a placeholder
	query_nolist = query_noregs.replace("(???)", "PLACEHOLDER")
	query_clean = query_nolist.replace("?", "PLACEHOLDER")

	return query_clean

# Function: findCloseParan finds the index of the close paranthesis corresponding to the open given
# Input: target string, index of open paranthesis
# Output: index of close paranthesis
def findCloseParan(target, open_paran):
	parans = [open_paran]
	index = open_paran
	popped = -1
	while (popped != open_paran):
		index += 1
		if target[index] == '(':
			parans.append(index)
		elif target[index] == ')':
			popped = parans.pop()
	# When the popped paranthesis is the first one, the matching paranthesis is in index
	return index	

# Function: findReplaceCol finds the columnname to replace the clause given
# Input: target string, index of open paranthesis
# Output: columnname to replace the clause
def findReplaceCol(target, open_paran):
	# Invalid keywords
	# TODO: Check if anything other than max, min, if, concat is used
	keywords = ['max', 'min', 'if', 'concat']
	# Valid characters in a column name
	allowed_chars = string.ascii_letters + '0123456789.'
	allowed_char_list = list(allowed_chars)
	# Start and end indices of column name
	startIndex=open_paran+1
	while (target[startIndex] not in allowed_char_list):
		startIndex += 1
	endIndex = startIndex
	while (target[endIndex] in allowed_char_list):
		endIndex += 1
	replace_col = target[startIndex:endIndex]
	# If the first word after is a keyword then use the first column name inside the subclause
	if replace_col in keywords:
		replace_col = findReplaceCol(target, endIndex)
	return replace_col

# Function: cleanClause removes a clause from the query
# Input: query with clause
# Output: query with clause replaced by some column name
def cleanClause(query, clause):
	# Find the first occurrence of clause
	index = query.find(clause)
	clause_length = len(clause)
	# Find the close paranthesis that ends the clause
	close_paran = findCloseParan(query, index+clause_length)
	# Find the column name to substitute, ignore other keywords
	replace_col = findReplaceCol(query, index+clause_length)
	
	# Replace the clause with the column name
	cleaned_query = query[0:index]+replace_col+query[close_paran+1:]
	# If there are any more clauses
	if (cleaned_query.find(clause) >= 0):
		cleaned_query = cleanClause(cleaned_query, clause)
	return cleaned_query


def cleanData(readFile, writeFile):
	f = open(writeFile,'w')
	with open(readFile) as csvfile:
		reader = csv.DictReader(csvfile)
		# All 188 queries found
		i = 0
		j = 0
		for row in reader:
			i += 1
			# str_join = "join"
			str_coal = "coalesce"
			str_group = "group_concat"
			str_interval = "interval"
			str_extract = "extract"
			query = row['query']

			print("i -", i)

			# Queries that have joins
			# if str_join in query:
			if True:
				# Skipping non-select queries that the parser cannot handle
				if query[:4] in ['alte','crea','dele','inse','lock','unlo','show','upda']:
					continue
				# Skipping select queries that the parser cannot handle
				# check with MG: AA added 'substring' and 'sum' clauses in the following line
				if 'collate' in query or 'substring' in query:# or 'sum' in query:
					continue
				j += 1
				# print(str(i))
				# Handling queries with special placeholder for a comparator
				if i in [182, 207]:
					query = query.replace("?a", "> a")
				# Handling query 267 complicated sum clause
				if i==267:
					query = cleanClause(query, "sum")
				# Handling group_concat clauses by substituting column name
				if str_group in query:
					query = cleanClause(query, str_group)
				# Handling coalesce clauses by substituting column name
				if str_coal in query:
					query = cleanClause(query, str_coal)
				
				# Check with MG: Handling interval clauses by substituting it with empty string
				if str_interval in query:
					query = re.sub("[+-] interval '\w+' month|[+-] interval '\w+' year|[+-] interval '\w+' day", " ", query)

				# Check with MG
				if str_extract in query:
					query = re.sub("extract\(\w+ \w+ \w+\) as \w+", "extract_clause", query)
				# Cleaning anything remaining the parser cannot handle
				clean_query = cleanQuery(query)
				f.write(clean_query+"\n")
	f.close()

# DO NOT change the order of values in original l
def removeDups(l):
	final = []
	dx = {}
	for v in l:
		if v in dx:
			continue
		else:
			final.append(v)
			dx[v] = True
	return final

# Input: 
#	s: a string representing the CREATE TABLE statement of the specified table
# Output: 
# 	1) a list of strings, containing the table name and column names in the table
#	2) a dictionary mapping the column names in the table to their datatypes
# Assumptions: 
# - clauses are split with ','
# - clauses which define columns always begin with backticks
# - first clause will always contain the table name and the first column

def cleanTable(s):
	
	clauses = s.split(',')
	col_clauses = filter(lambda a: a.strip().startswith('`'), clauses[1:])
	cols = map(lambda b: re.findall('`([^`]*)`', b), col_clauses)
	keywords = re.findall('`([^`]*)`', clauses[0]) + functools.reduce(list.__add__, cols, [])

	table_name = keywords[0]
	col_names = keywords[1:]
	to_check = list(filter(lambda a: a.strip().startswith('`'), clauses[1:]))
	to_check.insert(0, clauses[0])
	data_types = {}

	for i in range(0, len(to_check)):
		curr_clause = to_check[i]
		curr_col = col_names[i]
		if i == 0:
			curr_clause = curr_clause.replace('CREATE TABLE','').replace('(','', 1).replace(table_name, '', 1)
		filtered_clause = curr_clause.replace(curr_col,'').replace('`','').strip().split(' ')[0]
		if curr_col not in data_types:
			data_types[curr_col] = filtered_clause

	return keywords, data_types


# Input: 
#	readFile: name of the schema file
# 	writeFille: output filename
# Output: a file with dictionary (JSON) where keys are table names and values are set of column names
# Assumptions: 
	# 1. Queries are separated by semicolon
	# 2. table names and column names are wrapped in backquotes
	# 3. primary keys are listed exactly as follows: PRIMARY KEY (`key1`, `key2`, `key3`)
# Bug: might return extra column names. 
	# E.g., column names returned corresponding to UNIQUE KEY name
def createSchema(readFile, writeFile):
	fd = open(readFile, 'r')
	sqlFile = fd.read()
	fd.close()

	# all SQL commands (split on ';')
	sqlCommands = sqlFile.split(';')

	nTables = 1
	schema_table_to_col = {}
	schema_col_to_table = {}
	temp_col_to_table = {}
	pk_dx = {} # tablename to list of primary key columns
	fk_dx = {} # tablename to list of foreign key triples. Triples are of form (fk_colname, table_pointed_to, column_pointed_to)
	table_to_col_to_data_type = {} # a nested dx, key: tablename, value: dx {key: column name, value: data type}

	for command in sqlCommands:
		# remove extra whitespaces from around the command
		command = command.strip()

		if command.upper().startswith('CREATE TABLE'):

			keywords, col_to_data_types = cleanTable(command)
			table_to_col_to_data_type[keywords[0]] = col_to_data_types

			# keywords[0]  is the table name
			# keywords[1], ... are column names
			if keywords[0] in schema_table_to_col:
				print("TABLE ALREADY FOUND")
				return
			else:
				unique = removeDups(keywords[1:])
				schema_table_to_col[keywords[0]] = unique
				for col in unique:
					if col not in temp_col_to_table:
						temp_col_to_table[col] = keywords[0]
					else:
						temp_col_to_table[col] = "DUPLICATE"
			
			# extract the primary key
			# Assumption: Primary keys are specified as follows in schema.sql
			# PRIMARY KEY (`pk1`, `pk2`)
			pks = re.findall('PRIMARY KEY \((.*)\)', command)
			pks_clean = []

			if len(pks) > 0:
				pks_list = pks[0].split(",")
				for pk in pks_list:
					pks_clean.append(pk.strip()[1:-1]) #strip the starting and ending space if any and then remove the starting and ending quotes

			pk_dx[keywords[0]] = pks_clean

			# extract the foreign keys (if at all)
			# Assumption: foreign keys are specified as follows:
			# FOREIGN KEY (`colname`) REFEREENCES `tablename` (`colname`)
			fks = re.findall('FOREIGN KEY \(`(.*)`\) REFERENCES `(.*)` \(`(.*)`\)', command)
			fk_dx[keywords[0]] = fks
			
			nTables += 1

	# remove the duplicate entries  from schema_col_to_table
	for col, table in temp_col_to_table.items():
		if table != "DUPLICATE":
			schema_col_to_table[col] = table
		
	
	#print(schema_table_to_col)
	with open(writeFile, 'w') as fp:
		# json.dump([schema_table_to_col, schema_col_to_table, pk_dx, fk_dx], fp, indent=2)
		json.dump([schema_table_to_col, schema_col_to_table, pk_dx, fk_dx, table_to_col_to_data_type], fp, indent=2)
	return



def parseQueries(query_file, parsed_file):
	fr = open(query_file,'r')
	clean_query = "hello"
	i = 0
	n_failed_to_parse_queries = 0
	parsed_query_list = []

	print("Came here!!!")
	while clean_query:
		i += 1
		clean_query = fr.readline()
		if not clean_query:
			break
		# print("****", clean_query)
		try:
			json_dict = parse(clean_query.upper())
		except Exception as err:
			n_failed_to_parse_queries += 1
			print("********", clean_query)
			print("Some error")
		# json_dict = parse(clean_query)
		parsed_query_list.append(json_dict)

	print("Total No of queries parsed = ", i, "Failed to parse = ", n_failed_to_parse_queries)
	with open(parsed_file, 'w') as fp:
		json.dump(parsed_query_list, fp, indent=2)
	return


def readSchemaTester(filename):
	with open(filename, "r") as f:
		print("Converting JSON encoded data into Python dictionary")
		l = json.load(f)
		# l[0] is dx_table_to_col and l[1] is dx_col_to_table
		#print(dx[1]["tagIndex"])
		print(dx[0]["ActionLog"])



if __name__ == '__main__':
	app_name = "tpch"
	# create the clean data file
	# cleanData(app_name + '/querylog.csv', app_name + '/clean_querylog.txt')
	print('CLEANED DATA')
	# read the schema and, create and store two dictionaries in schema.json
	# two dictionaries: schema_table_to_col, schema_uniq_col_to_table
	createSchema(app_name + '/schema.sql', app_name + '/schema.json')
	# createSchema(app_name + '/schema.sql', app_name + '/schema.json')

	# just a tester to see if schema.json is being read correctly
	#readSchemaTester('schema.json')

	# parseQueries(app_name + '/clean_querylog.txt', app_name + '/parsed_queries.json')
	# TPCH -- clean dates, skip create, change substring, extract
	# parseQueries(app_name + '/clean_querylog.txt', app_name + '/parsed_queries.json')


