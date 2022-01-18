import csv, json
import re
from moz_sql_parser import parse

# Input: name of the schema file
# Output: dictionary where keys are table names and values are set of column names
# Assumptions: 
	# 1. Queries are separated by semicolon
	# 2. table names and column names are wrapped in backquotes
# Bug: might return extra column names. 
	# E.g., column names returned corresponding to UNIQUE KEY name
def createSchema(filename):
	fd = open(filename, 'r')
	sqlFile = fd.read()
	fd.close()

	# all SQL commands (split on ';')
	sqlCommands = sqlFile.split(';')

	nTables = 1
	# tableNames is a dictionary
	# key = table name
	# value = set of column names
	tableNames  = {}

	for command in sqlCommands:
		# remove extra whitespaces from around the command
		command = command.strip()

		if command.startswith('CREATE TABLE'):
			# extract all the words within back quotes
			keywords = re.findall('`([^`]*)`', command)

			# keywords[0]  is the table name
			# keywords[1], ... are column names
			if keywords[0] in tableNames:
				print("TABLE ALREADY FOUND")
				return
			else:
				tableNames[keywords[0]] = set(keywords[1:])
			nTables += 1
		
	return tableNames
		

# Function cleanQuery removes parts of the query that the parser cannot handle
# TODO: Check if losing anything meaningful
def cleanQuery(query):
	# If the query has substring, ignore that part 
	query_nosubs_comment = query.replace("substring(PaperComment.comment from 1 for ?)", "substring_comment")
	query_nosubs = query_nosubs_comment.replace("substring(Paper.title from 1 for ?)","substring_title")

	# If the query is parametrized, subs the questionmark with a placeholder
	query_nolist = query_nosubs.replace("(???)", "PLACEHOLDER")
	query_clean = query_nolist.replace("?", "PLACEHOLDER")
	return query_clean


def computeAliases(json_dict, aliases):
	if "name" in json_dict:
		#print("CAME HERE")
		if isinstance(json_dict["value"], str):
		#	print("SETTING")
			aliases[json_dict["name"]] = json_dict["value"]
		else:
			aliases[json_dict["name"]] = "ERROR"
	for key, value in json_dict.items():
		if isinstance(value, dict):
			computeAliases(value, aliases)
		elif isinstance(value, list):
			for item in value:
				if isinstance(item, dict):
					computeAliases(item, aliases)
		# else: base case of recursion

def main():
	aliases = {}

	tableNames = createSchema('tpch/schema_tpch.sql')
	#print(tableNames['ReviewRequest'])

	#query =  'select PaperReview.*, ContactInfo.firstName, ContactInfo.lastName, ContactInfo.email, ContactInfo.roles as contactRoles, ContactInfo.contactTags, ReqCI.firstName as reqFirstName, ReqCI.lastName as reqLastName, ReqCI.email as reqEmail from PaperReview join ContactInfo using (contactId) left join ContactInfo as ReqCI on (ReqCI.contactId=PaperReview.requestedBy) where PaperReview.paperId=XX group by PaperReview.reviewId order by PaperReview.paperId, reviewOrdinal, timeRequested, reviewType desc, reviewId'
	query = 'select MPR.reviewId from PaperReview as MPR left join (select paperId, count(reviewId) as numReviews from PaperReview where reviewType>1 and reviewNeedsSubmit=0 group by paperId) as NPR on (NPR.paperId=MPR.paperId) left join (select paperId, count(rating) as numRatings from PaperReview join ReviewRating using (paperId,reviewId) group by paperId) as NRR on (NRR.paperId=MPR.paperId) where MPR.contactId=XX and numReviews<=XX and numRatings<=XX'
	clean_query = cleanQuery(query)
	json_dict = parse(clean_query)
	print(json_dict)
	print("*******")
	computeAliases(json_dict, aliases)
	print(aliases)

if __name__ == '__main__':
	main()




