import json
import re
import sqlalchemy as db
from collections import deque
from traversal import valuesToString
from pathlib import Path
import pickle

###### import our files ####
from data_structures import *
from global_vars import *
from graph import *
from traversal import extractData
from inclusion_dependency import *
from addition import *
from heuristics_graph import *
from app_settings import *

GRAPH_R = 0
GRAPH_H = 1
UNION  = 2
INTERSECTION = 3

# Input: name of schema file
# readSchema reads the schema and initializes Table objects for all the tables in tables_dx and tables_dx_upper
# It also initializes the following fields of Table objects: tablename, colnames, obj_columns_dx
# Also creates a dictionary mapping from colname to tablename. This dx is used for de-aliasing
def readSchema(filename):
	n_cols_in_schema = 0
	with open(filename, "r") as f:
		l = json.load(f)
		# l[0] is dx_table_to_col, l[1] is dx_col_to_table 
		# and l[2] is a dictionary from tablename to pks
		# l[3] is a dictionary from tablename to list of fk contraints
		
		for tablename, colnames in l[0].items():
			pk = l[2][tablename]
			tables_dx[tablename] = Table(tablename, colnames, pk)
			tables_dx_upper[tablename.upper()] = Table(tablename.upper, [col.upper() for col in colnames], pk)
			n_cols_in_schema += len(colnames)

		# initializing the column objects for each table
		for tablename in tables_dx:
			obj_table = tables_dx[tablename]
			for colname in obj_table.colnames:
				obj_table.obj_columns_dx[colname] = Col(tablename, colname, -1)
	
		uniq_col_to_table = l[1]
		uniq_col_to_table_upper = {}
		for k, v in uniq_col_to_table.items():
			uniq_col_to_table_upper[k.upper()] = v.upper()

		# collect stats before returning
		global_stats_obj.n_cols_in_schema = n_cols_in_schema

		return uniq_col_to_table, uniq_col_to_table_upper, l[3], l[4]


# this function is not currently being used
# This initializes column objects for only foreign key columns
def initializeFKObjects():
	for tablename in tables_dx:
		for fkname in tables_dx[tablename].fk:
			tables_dx[tablename].obj_columns_dx[fkname] = Col(tablename, fkname, -1)


def connectMySql(dbname):
	# Connect to dbname on the local MySql server
	config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'marilyn',
    'password': 'pass123',
    'database': dbname
	}
	db_user = config.get('user')
	db_pwd = config.get('password')
	db_host = config.get('host')
	db_port = config.get('port')
	db_name = config.get('database')
	# specify connection string
	connection_str = f'mysql+pymysql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}'
	# connect to database
	engine = db.create_engine(connection_str)
	connection = engine.connect()
	
	# return a connection to the MySql database
	return connection


# takes a JSON filters file 
# initializes tables_dx.filtered_colnames and tables_dx.non_filtered_colnames for all the tables
def processFilters(filters_json):
	# if no filtering, we only set the list of non_filtered columns
	if filters_json == "NONE":
		for tablename in tables_dx:
			tables_dx[tablename].non_filtered_colnames = tables_dx[tablename].colnames
			tables_dx_upper[tablename.upper()].non_filtered_colnames = tables_dx_upper[tablename.upper()].colnames
	
	# otherwise set both
	else:
		with open(filters_json, "r") as filename:
			filters_dx = json.load(filename)

		for tablename, table_obj in tables_dx.items():
			table_obj_upper = tables_dx_upper[tablename.upper()]
			for colname in table_obj.colnames:
				if tablename in filters_dx and colname in filters_dx[tablename]:
					table_obj.filtered_colnames.append(colname)
					table_obj_upper.filtered_colnames.append(colname.upper())
				else:
					table_obj.non_filtered_colnames.append(colname)
					table_obj_upper.non_filtered_colnames.append(colname.upper())


def arePrunedEdgesInclusionDependent(edges_to_prune, db_conn):
	not_id_edge = []
	two_way = []
	one_way = []
	for prune in edges_to_prune.keys():

		start_node = prune[0]
		end_node = prune[1]
		curr_tup1 = (start_node, end_node)
		curr_tup2 = (end_node, start_node)

		inc_dep1 = InclusionDependency(db_conn, start_node, end_node)
		inc_dep2 = InclusionDependency(db_conn, end_node, start_node)
		if inc_dep1.checkHeuristic(INCLUSION) and inc_dep2.checkHeuristic(INCLUSION):
			if not (curr_tup1 in two_way or curr_tup2 in two_way):
				two_way.append(curr_tup1)			
		elif inc_dep1.checkHeuristic(INCLUSION) and not inc_dep2.checkHeuristic(INCLUSION):
			one_way.append(curr_tup1)
		elif not inc_dep1.checkHeuristic(INCLUSION) and not inc_dep2.checkHeuristic(INCLUSION):
			if not (curr_tup1 in not_id_edge or curr_tup2 in not_id_edge):
				not_id_edge.append(curr_tup1)

	with open('pruned_inclusion_dependencies.txt', 'a') as f:

		f.write("--------------\n")
		
		f.write("Pruned Edges in Graph:\n")
		f.write("Inclusion Dependent in Both Directions:\n")	
		[f.write(x[0][0]+"."+x[0][1]+" <---> "+ x[1][0]+"."+x[1][1]+"\n") for x in two_way]
		f.write("---\n")

		f.write("Inclusion Dependent in One Direction:")
		[f.write(x[0][0]+"."+x[0][1]+" <--- "+ x[1][0]+"."+x[1][1]+"\n") for x in one_way]
		f.write("---\n")

		f.write("Inclusion Dependent in Neither Direction:")
		[f.write(x[0][0]+"."+x[0][1]+" X "+ x[1][0]+"."+x[1][1]+"\n") for x in not_id_edge]
	return


def processPruning(pruning_json, neigh_dx_names, db_conn):
	# if no filtering, we only set the list of non_filtered columns
	pruning_dx = {}
	if pruning_json != "NONE":
		with open(pruning_json, "r") as filename:
			pruning_dx = json.load(filename)

	# if there is an edge on a column add it to colnames_with_edges
	# go over each edge in neigh_dx_names
	# if either end point is in pruning_dx, ignore the edge
	# else add the end points to colnames_with_edges

	# this dictionary is not used anywhere in code. 
	# It is just used to compute the edges to prune so that we could report it in the paper
	edges_to_prune = {}
	n_edges_to_prune = 0
	n_cols_to_prune = 0

	for table, col in neigh_dx_names.keys():
		neigh_list = neigh_dx_names[(table, col)]
		for t, c in neigh_list:
			if ((table in pruning_dx) and (col in pruning_dx[table])) or \
				((t in pruning_dx) and (c in pruning_dx[t])):
				# edge (table, col) -- (t, c) should be pruned
				if ((table, col), (t,c)) not in edges_to_prune and ((t, c), (table, col)) not in edges_to_prune:
					n_edges_to_prune += 1
					edges_to_prune[((table, col), (t,c))] = 1
				continue
			else:
				# update colnames_with_no_edges
				if col not in tables_dx[table].colnames_with_edges:
					tables_dx[table].colnames_with_edges.append(col)
				if c not in tables_dx[t].colnames_with_edges:
					tables_dx[t].colnames_with_edges.append(c)

				# update neigh_dx as well for the edge
				l_obj = tables_dx[table].obj_columns_dx[col]
				r_obj = tables_dx[t].obj_columns_dx[c]
				if l_obj not in neigh_dx:
					neigh_dx[l_obj] = []
				if r_obj not in neigh_dx:
					neigh_dx[r_obj] = []

				if l_obj not in neigh_dx[r_obj]:
					neigh_dx[r_obj].append(l_obj)

				if r_obj not in neigh_dx[l_obj]:
					neigh_dx[l_obj].append(r_obj)

	
	# GENERATING INCLUSION DEPENDENCY STATISTICS FOR PRUNED EDGES

	# check if the pruned edges are inclusion dependent
	arePrunedEdgesInclusionDependent(edges_to_prune, db_conn)

	# collect stats
	global_stats_obj.n_edges_pruned = n_edges_to_prune
	for tablename in pruning_dx.keys():
		n_cols_to_prune += len(pruning_dx[tablename])
	global_stats_obj.n_columns_pruned = n_cols_to_prune

# this function uses heuristics to deduce columns that should be filtered from the output
def inferFilters():
	# heuristic 1: if a table is a mapping table, then it should be removed from the output
	# a table is a mapping table if all its non-filtered columns have an edge on them (after pruning)
	computeMappingTables()
				
# a table is a mapping table if all its non-filtered columns have an edge on them (after pruning)
def computeMappingTables():
	# a table is a mapping table if all its non-filtered columns are either pk or fk
	for tablename in tables_dx:
		table_obj = tables_dx[tablename]
		mapping_table = True
		for nfc in table_obj.non_filtered_colnames:
			# if a column with no edges is found, then it's not a mapping table
			if nfc not in table_obj.colnames_with_edges:
				mapping_table = False
				break
		
		# if you came here, then all the non-filtered columns have edges on them
		# therefore this is a mapping table
		# therefore make all the non-filtered columns filtered
		if mapping_table:
			table_obj.filtered_colnames += table_obj.non_filtered_colnames
			table_obj.inf_filtered_colnames += table_obj.non_filtered_colnames
			table_obj.non_filtered_colnames = []
			
			print(tablename, "is a mapping table ")

def computeGroundTruth(ds_id, db_conn, gt_filename):
	f = open(gt_filename, "r")

	query = f.readline()
	while(query):
		# ans = re.findall('ds_id', query)
		query = re.sub('ds_id', ds_id, query)
		tablename = re.findall('FROM (\w+)', query)[0]
		# Note: replacing * with non_filtered_colnames is just a hack to avoid writing the list of colnames in the ground truth file
		# Ideally the ground truth queries should be executed as they are specified in the ground truth file
		# The problem is that SQL doesn't ensure the ordering of columns when it executes select * queries
		# and hence we do not know how to compare ground truth data with the data we extract.
		# therefore, we do this hack. 
		# Instead of replacing * with the list of columns, we replace it here in code.

		# NOTE: assuming only first tablename uses a SELECT *
		string_colnames = valuesToString(tables_dx[tablename].non_filtered_colnames, False)
		# replacing the * with a list of columns instead
		num_stars = len(re.findall('\*', query))
		# assuming at most one SELECT *
		if num_stars <= 1:
			query = re.sub('\*', string_colnames, query)
		else:
			print(f"Error: More than one asterisk * in ground truth query: {query}")
		# print(query, tablename, "\n ****** \n")
		# print("in gt", query)
		output_data = db_conn.execute(query)

		for row in output_data:
			# will use False/True value to see if our traversal can successfully extract this row (False = UNSUCCESSFULL, True = SUCCESSFUL)
			key = str(row)
			# print(key)
			tables_dx[tablename].result.gt[key] = False

		# for initialization purposes set fn to be equal to the rows in ground truth
		# as more of these ground truth rows are recovered, we will reduce the value of fn 
		tables_dx[tablename].result.fn = len(tables_dx[tablename].result.gt.keys())
		query = f.readline()

	# print("GROUND TRUTH \n", tables_dx['LINEITEM'].result.gt.keys())

def computeAccuracy(ds_id):
	for tablename in tables_dx:
		fp = tables_dx[tablename].result.fp
		tp = tables_dx[tablename].result.tp
		fn = tables_dx[tablename].result.fn
		
		# tp = what I extarcted correctly
		# fp = what I extracted incorrectly
		# fn = what I did not extract  but was supposed to extract
		# tn = what I did not extract and was also not supposed to extract

		# tp + fp = 0 => I did not extract anything
		# tp + fn => intuitively, the positives

		# precision: what fraction of what you pulled was correct
		if tp + fp == 0: # we did not extract anything
			# if fn == 0: # and there was nothing to extract
			# 	precision = 1.0
			# else: # otherwise
			precision = 1.0
		else:
			precision = tp / (tp + fp)

		# recall: what fraction of ground truth did you pull correctly
		if tp + fn == 0: # there was nothing to extract
			recall = 1.0
		else:
			recall = tp / (tp + fn)

		# if computing overall precision and recall, do not forget to exclude the mapping tables in computation
		print(f'{tablename:21}: tp = {tp:3} | fp = {fp:3} | fn = {fn:3} | Prec = {precision:4.2} | Rec = {recall:4.2}')

		tables_dx[tablename].precision += precision
		tables_dx[tablename].recall += recall

		# only include this DS into final prec computation if the following holds (inflated avgs business)
		if (tp != 0 and (fp == 0 and fn == 0)) or fp > 0:
			tables_dx[tablename].deflated_precision += precision
			tables_dx[tablename].deflated_n_ds_prec += 1
		if (tp != 0 and (fp == 0 and fn == 0)) or fn > 0:
			tables_dx[tablename].deflated_recall += recall
			tables_dx[tablename].deflated_n_ds_recall += 1

		# if this DS has supoptimal prec and/or recall, save it
		if precision != 1: 
			tables_dx[tablename].bad_prec_ds.append((ds_id, precision))
			tables_dx[tablename].min_bad_prec = min(tables_dx[tablename].min_bad_prec, precision)

		if recall != 1: 
			tables_dx[tablename].bad_rec_ds.append((ds_id, recall))
			tables_dx[tablename].min_bad_rec = min(tables_dx[tablename].min_bad_rec, recall)
 


# print DS IDs with suboptimal prec and/or recall
def printBadAccuracyDSIds():
	# unique set of ds ids
	unique_ids = set()

	print("\n*** Bad Precision and Recall DS ids ***")
	for tablename in tables_dx:
		bad_prec_ds = tables_dx[tablename].bad_prec_ds
		bad_rec_ds = tables_dx[tablename].bad_rec_ds
		
		unique_ids.update(int(ds_id) for (ds_id, _) in bad_prec_ds)
		unique_ids.update(int(ds_id) for (ds_id, _) in bad_rec_ds)

		if bad_prec_ds or bad_rec_ds:
			print("-----" + tablename + "------")
			
		
		if bad_prec_ds: 
			print("Bad precision DS ids: ")
			print(f'{tables_dx[tablename].bad_prec_ds}')
			print("Min Precision:", tables_dx[tablename].min_bad_prec)
		
		if bad_rec_ds: 
			print("Bad recall DS ids: ")
			print(f'{tables_dx[tablename].bad_rec_ds}')
			print("Min Recall:", tables_dx[tablename].min_bad_rec)

	print("\n*** Unique DS ids for Bad Precision and Recall ***")
	print(sorted(unique_ids))
	print(f'Total number of imperfect DS ids: {len(unique_ids)}.')

def computeInfAccPerTable(num_ds_ids):
	print("\n*** Inflated Averaged Results ***")
	for tablename in tables_dx:
		avg_p = tables_dx[tablename].precision / num_ds_ids
		avg_r = tables_dx[tablename].recall / num_ds_ids
		tables_dx[tablename].avg_p = avg_p
		tables_dx[tablename].avg_r = avg_r
		print(f'{tablename:21}: Prec = {avg_p:4.2} | Rec = {avg_r:4.2}')


def computeDefAccPerTable():
	print("\n*** Deflated Averaged Results ***")
	
	for tablename in tables_dx:
		numer_p = tables_dx[tablename].deflated_precision
		denom_p = float(tables_dx[tablename].deflated_n_ds_prec)
		numer_r = tables_dx[tablename].deflated_recall
		denom_r = float(tables_dx[tablename].deflated_n_ds_recall)

		if tables_dx[tablename].deflated_n_ds_prec != 0:
			avg_dp = tables_dx[tablename].deflated_precision / tables_dx[tablename].deflated_n_ds_prec
		else:
			avg_dp = 1.0 # if no data subjects passed the condition?
		if tables_dx[tablename].deflated_n_ds_recall != 0:
			avg_dr = tables_dx[tablename].deflated_recall / tables_dx[tablename].deflated_n_ds_recall
		else:
			avg_dr = 1.0
		tables_dx[tablename].avg_dp = avg_dp
		tables_dx[tablename].avg_dr = avg_dr
		print(f'{tablename:21}: Prec = {avg_dp:4.2} | Rec = {avg_dr:4.2} | num_p = {numer_p:4} | denom_p = {denom_p:4} | num_r = {numer_r:4} | denom_r = {denom_r:4}')

# for each table, computes F1 scores from their deflated precision and recall 
def computeF1PerTable():
	print("\n*** F1 Results ***")
	for tablename in tables_dx:
		avg_dp = tables_dx[tablename].avg_dp
		avg_dr = tables_dx[tablename].avg_dr
		if avg_dp + avg_dr == 0:
			f1 = 0.0
		else: 
			f1 = (2 * avg_dp * avg_dr) / (avg_dp + avg_dr)
		tables_dx[tablename].f1 = f1
		print(f'{tablename:21}: F1 = {f1:4.2}')

def computeAccPerTable(num_ds_ids):
	computeInfAccPerTable(num_ds_ids)
	computeDefAccPerTable()
	computeF1PerTable()

def	computeAvgAcc():
	print("\n*** Averaged Results ***")
	n_tables = 0
	avg_p = 0
	avg_r = 0
	avg_dp = 0
	avg_dr = 0
	f1 = 0
	for tablename in tables_dx:
		avg_p += tables_dx[tablename].avg_p
		avg_r += tables_dx[tablename].avg_r
		avg_dp += tables_dx[tablename].avg_dp
		avg_dr += tables_dx[tablename].avg_dr
		f1 += tables_dx[tablename].f1
		n_tables += 1
	print('Average Precision: ', avg_p/n_tables)
	print('Average Recall: ', avg_r/n_tables)
	print('Average Deflated Precision: ', avg_dp/n_tables)
	print('Average Deflated Recall: ', avg_dr/n_tables)
	print('Average Deflated F1: ', f1/n_tables)

def initializeDataObjects(ds_id):
	for tablename in tables_dx:
		tables_dx[tablename].result = Data(ds_id, tablename)

def createVirtualTables(filename, db_conn):
	if filename == "NONE":
		return
	with open(filename, "r") as f:
		dx = json.load(f)
		
		for tablename in dx.keys():
			# v_columns is a list of lists. 
			# Tiny lists are triples where index #0 is v_column name and it will mimic #1.#2 column
			v_columns = dx[tablename]["v_columns"] 
			query =  dx[tablename]["query"]
			
			tables_dx[tablename].is_virtual = True

			# create edges for each virtual column similar to the edges of the column that it is mimicking
			for vc, ot, oc in v_columns:
				tables_dx[tablename].v_colnames.append(vc)
				tables_dx[tablename].colnames.append(vc)

				# create and store a Col obj for this new virtual column
				obj_col = Col(tablename, vc)
				assert vc not in tables_dx, "ERROR: In parseVirtualTable: vc already exists in table"
				tables_dx[tablename].obj_columns_dx[vc] = obj_col

				# retrieve the Col obj for the column this virtual column is mimicking
				orig_obj_col = tables_dx[ot].obj_columns_dx[oc]
				assert orig_obj_col != None, "ERROR: In parseVirtualTable: original column does not exist"

				# if the original column has edges incident on it, create the same edges for this virtual column
				if orig_obj_col in neigh_dx:
					neigh_dx[obj_col] = neigh_dx[orig_obj_col]
					tables_dx[tablename].fk.append(vc)

					for neigh in neigh_dx[obj_col]:
						neigh_dx[neigh].append(obj_col)

			# create a view for table using DBA given query
			# delete view if already exists -- NOTE: will cause issues if already a DB VIEW
			delete_view_query = "DROP VIEW IF EXISTS V_" + tablename
			db_conn.execute(delete_view_query)
			view_query = "CREATE VIEW V_" + tablename + " AS " + query
			# print(view_query)
			output_data = db_conn.execute(view_query)

def cleanVirtualTables(db_conn):
	for tablename in tables_dx.keys():
		if True: #tables_dx[tablename].is_virtual:
			query = "DROP VIEW IF EXISTS V_" + tablename 
			db_conn.execute(query)

def test(db_conn):

	# for table_obj in tables_dx.values():
	# 	print(table_obj.result)

	print("********")
	# query1 = "create view test as select paperId as hello from Paper;"
	# output_data1 = db_conn.execute(query1)

	query2 = "select paperId, v_author from V_Paper;"
	output_data2 = db_conn.execute(query2)

	# print(output_data1, str(output_data1)
	for row in output_data2:
		# print("******", row, type(row))
		s1 = str(row)
		print(s1, type(s1))

	print("^^^^^^^")

	n_cols = 0
	for tablename in tables_dx.keys():
		n_cols += len(tables_dx[tablename].colnames)
	global_stats_obj.n_cols_in_schema = n_cols
	# print("Total number of columns in schema")

def printStats():
	print("***** Printing customization stats *****")
	print ("n_edges_in_fk:", global_stats_obj.n_edges_in_fk)
	print ("n_edges_in_joins:", global_stats_obj.n_edges_in_joins)
	print ("n_common_edges:", global_stats_obj.n_common_edges)
	print ("n_edges_in_rel_graph:", global_stats_obj.n_edges_in_rel_graph)
	print ("n_columns_pruned", global_stats_obj.n_columns_pruned)
	print ("n_edges_pruned:", global_stats_obj.n_edges_pruned)
	print ("n_cols_in_schema:", global_stats_obj.n_cols_in_schema)
	print("***** Printing heuristic graph stats *****")
	print ("n_edges_candidate_directional:", global_stats_obj.n_edges_candidate_directional)
	print ("n_edges_candidate:", global_stats_obj.n_edges_candidate)
	print ("n_edges_candidate_int_R:", global_stats_obj.n_edges_candidate_int_R)
	print ("n_edges_inc_dep_directional:", global_stats_obj.n_edges_inc_dep_directional)
	print ("n_edges_inc_dep:", global_stats_obj.n_edges_inc_dep)
	print ("n_edges_inc_dep_int_R:", global_stats_obj.n_edges_inc_dep_int_R)
	print ("n_edges_oor_directional:", global_stats_obj.n_edges_dir_dx['oor'])
	print ("n_edges_oor:", global_stats_obj.n_edges_dx['oor'])
	print ("n_edges_oor_int_R:", global_stats_obj.n_edges_int_R_dx['oor'])
	print ("n_edges_coverage_directional:", global_stats_obj.n_edges_dir_dx['coverage']) 
	print ("n_edges_coverage:", global_stats_obj.n_edges_dx['coverage']) 
	print ("n_edges_coverage_int_R:", global_stats_obj.n_edges_int_R_dx['coverage'])  
	print ("n_edges_wilcoxon_directional:", global_stats_obj.n_edges_dir_dx['wilcoxon'])  
	print ("n_edges_wilcoxon:", global_stats_obj.n_edges_dx['wilcoxon'])  
	print ("n_edges_wilcoxon_int_R:", global_stats_obj.n_edges_int_R_dx['wilcoxon']) 
	print ("n_edges_namematch_directional:", global_stats_obj.n_edges_dir_dx['namematch'])
	print ("n_edges_namematch:", global_stats_obj.n_edges_dx['namematch'])
	print ("n_edges_namematch_int_R:", global_stats_obj.n_edges_int_R_dx['namematch'])
	print("***********************************")
	print ("n_edges_operated_graph:", global_stats_obj.n_edges_in_operated_graph)

def createEdges(nodes_dx, edges_dx, neigh_dx_names, schema, dt_dx, p_table, use_inc_dep, verified=[]):
	# The last non-optional argument to GraphAddition is use_inc_dep. Set to:
	#   - True = use inclusion dependencies for edge addition
	#   - False = use datatype matching for edge addition
	g = GraphAddition(nodes_dx, edges_dx, neigh_dx_names, schema, dt_dx, p_table, verified, use_inc_dep)

	if g.checkDisconnectedComponents():
		g.connectComponents()
		nodes_dx, edges_dx, neigh_dx_names = g.getNewGraph()
	return nodes_dx, edges_dx, neigh_dx_names

def createEdgesFromFile(nodes_dx, edges_dx, neigh_dx_names, schema, edges_filename):
	if edges_filename == 'NONE':
		return nodes_dx, edges_dx, neigh_dx_names

	input_file = open(edges_filename, 'r')
	for edge in input_file:
		temp = edge.strip().split('--')
		print(temp)
		l = temp[0].strip().split(".")
		r = temp[1].strip().split(".")

		ltable = l[0]
		lcol = l[1]
		rtable = r[0]
		rcol = r[1]
		print(ltable, lcol, rtable, rcol)
		left = ltable.upper() + "_" + lcol.upper()
		right = rtable.upper() + "_" + rcol.upper()
		nodes_dx[left] = 1
		nodes_dx[right] = 1
		edges_dx[left + " -- " + right] = 1

		updateFks(ltable, lcol, rtable, rcol, schema)
		updateNeighborhood(ltable, lcol, rtable, rcol, neigh_dx_names)
	
	return nodes_dx, edges_dx, neigh_dx_names

# function that operates on two graphs as specifiec
def operateGraphs(operation, nodes_dx_1, nodes_dx_2, edges_dx_1, edges_dx_2, neigh_dx_names_1, neigh_dx_names_2):
	if operation == UNION:
		# combining the edges from both the graphs
		union1(nodes_dx_1, nodes_dx_2)
		union1(edges_dx_1, edges_dx_2)
		union2(neigh_dx_names_1, neigh_dx_names_2)
		global_stats_obj.n_edges_in_operated_graph = len(edges_dx_1)
	elif operation == INTERSECTION:
		# intersecting the edges from both the graphs
		nodes_dx_1 = intersection1(nodes_dx_1, nodes_dx_2)
		edges_dx_1 = intersection1(edges_dx_1, edges_dx_2)
		neigh_dx_names_1 = intersection2(neigh_dx_names_1, neigh_dx_names_2)
		global_stats_obj.n_edges_in_operated_graph = len(edges_dx_1)
	else:
		print("Invalid operation")
		exit(0)
	
	# small graph
	header = createSmallGraphHeader(tables_dx_upper, nodes_dx_1)
	# write the graph in a file
	f = open("operated_graph.txt", "w")
	f.write("graph G {" + "\n".join(header) + "\n".join(edges_dx_1.keys()) + "}")
	f.close()

	return nodes_dx_1, edges_dx_1, neigh_dx_names_1 

def operateOneGraph(operation, nodes_dx_1, edges_dx_1, neigh_dx_names_1):
	# function to make running experiments easier, returns whatever it is given
	# operation passed for readability
	global_stats_obj.n_edges_in_operated_graph = len(edges_dx_1)

	# small graph
	header = createSmallGraphHeader(tables_dx_upper, nodes_dx_1)
	# write the graph in a file
	f = open("S_graph.txt", "w")
	f.write("graph G {" + "\n".join(header) + "\n".join(edges_dx_1.keys()) + "}")
	f.close()

	return nodes_dx_1, edges_dx_1, neigh_dx_names_1

def main():
	######## DEFINE APP-SPECIFIC PARAMETERS #####
	# app_name = 'tpch_cust'
	# app_name = 'tpch_supp'
	# app_name = 'hotcrp'
	# app_name = 'hotcrp_large'
	# app_name = 'hotcrp_large_cap'
	# app_name = 'hotcrp_large_h'
	# app_name = 'lobsters'
	# app_name = 'lobsters_h'
	# app_name = 'lobsters_cap'
	# app_name = 'lobsters_h_union_s'
	app_name = 'lobsters_h_union_s__cap_r'
	# app_name = 'wordpress'
	# app_name = 'wordpress_h'
	# app_name = 'wordpress_cap'
	# app_name = 'wordpress_plugins'
	# app_name = 'wordpress_plugins_cap'
	app_settings = getAppSettings(app_name)
	
	##################################################
	######### Initialize a bunch of things ############
	db_conn = connectMySql(app_settings.db_name)

	# uniq_col_to_table is a DX: key = colname, value = tablename. This only contains those columns which appear in a SINGLE table
	uniq_col_to_table, uniq_col_to_table_upper, fk_dx, dt_dx = readSchema(app_settings.schema_json)
	use_queries = app_settings.qgraph
	# neigh_dx_names stores neighborhoods. key = (tablename,  colname), value = set of (tablename, colname) pairs
	# create Graph from schema + queries

	nodes_dx_s, edges_dx_s, neigh_dx_names_s = createGraphFromFk(fk_dx, tables_dx)
	nodes_dx_q, edges_dx_q, neigh_dx_names_q = createGraphFromQueries(tables_dx, tables_dx_upper, uniq_col_to_table, uniq_col_to_table_upper, app_settings.parsed_queries_json)
	
	##################### This section for heuristics #############
	# create Graph from heuristics
	pickle_nodes = Path(app_settings.path+"/nodes")
	pickle_edges = Path(app_settings.path+"/edges")
	pickle_neigh = Path(app_settings.path+"/neigh")
	if pickle_nodes.is_file() and pickle_edges.is_file() and pickle_neigh.is_file():
		# reading in from serialized
		print(f'Reading from serialized files for {app_settings.app_name}')
		infile = open(pickle_nodes,'rb')
		nodes_dx_h = pickle.load(infile)
		infile = open(pickle_edges,'rb')
		edges_dx_h = pickle.load(infile)
		infile = open(pickle_neigh,'rb')
		neigh_dx_names_h = pickle.load(infile)
		infile.close()
	else:
		# to run:
		## individual heuristic use the arguments heuristic_no and th
		# nodes_dx_2, edges_dx_2, neigh_dx_names_2 = createGraphFromHeuristics(tables_dx, tables_dx_upper, dt_dx, db_conn, formatNeigh(neigh_dx_names_1), heuristic_no=NAMEMATCH, th=0.3)
		# combined heuristics set the argument combined to True and pass a th_dx of thresholds
		th_dx = {'oor_th': 0.2, 'cover_th': 0.8, 'wilcoxon_th': 0.7, 'name_th': 1.0}
		# NOTE: we are currently passing in neigh_dx_names_s but should pass neigh_dx_names_r
		# NOTE: can't simply change it because union1 and union2 happen in-place
		nodes_dx_h, edges_dx_h, neigh_dx_names_h = createGraphFromHeuristics(tables_dx, tables_dx_upper, dt_dx, db_conn, formatNeigh(neigh_dx_names_s), combined=True, th_dx=th_dx, printing=True)

		# serializing for later use
		print(f'Writing to serialized files for {app_settings.app_name}')
		outfile = open(pickle_nodes,'wb')
		pickle.dump(nodes_dx_h, outfile)
		outfile = open(pickle_edges,'wb')
		pickle.dump(edges_dx_h, outfile)
		outfile = open(pickle_neigh,'wb')
		pickle.dump(neigh_dx_names_h, outfile)
		outfile.close()


	# combine the two graphs above
	# use GRAPH_R for only relationship edges, use GRAPH_H for only heuristic edges
	mode = app_settings.mode

	if mode == "R":
		nodes_dx, edges_dx, neigh_dx_names = operateGraphs(UNION, nodes_dx_s, nodes_dx_q, edges_dx_s, edges_dx_q, neigh_dx_names_s, neigh_dx_names_q)
	elif mode == "H":
		nodes_dx, edges_dx, neigh_dx_names = operateOneGraph(GRAPH_H, nodes_dx_h, edges_dx_h, neigh_dx_names_h)
	elif mode == "S":
		nodes_dx, edges_dx, neigh_dx_names = operateOneGraph(GRAPH_H, nodes_dx_s, edges_dx_s, neigh_dx_names_s)
	elif mode == "H_UNION_S":
		nodes_dx, edges_dx, neigh_dx_names = operateGraphs(UNION, nodes_dx_s, nodes_dx_h, edges_dx_s, edges_dx_h, neigh_dx_names_s, neigh_dx_names_h)
	elif mode == "CAP":
		nodes_dx_r, edges_dx_r, neigh_dx_names_r = operateGraphs(UNION, nodes_dx_s, nodes_dx_q, edges_dx_s, edges_dx_q, neigh_dx_names_s, neigh_dx_names_q)
		nodes_dx, edges_dx, neigh_dx_names = operateGraphs(INTERSECTION, nodes_dx_r, nodes_dx_h, edges_dx_r, edges_dx_h, neigh_dx_names_r, neigh_dx_names_h)
	elif mode == "Q_CAP_H":
		nodes_dx, edges_dx, neigh_dx_names = operateGraphs(INTERSECTION, nodes_dx_q, nodes_dx_h, edges_dx_q, edges_dx_h, neigh_dx_names_q, neigh_dx_names_h)
	elif mode == "Q_CAP_H_CAP_S":
		nodes_dx, edges_dx, neigh_dx_names = operateGraphs(INTERSECTION, nodes_dx_q, nodes_dx_h, edges_dx_q, edges_dx_h, neigh_dx_names_q, neigh_dx_names_h)
		nodes_dx, edges_dx, neigh_dx_names = operateGraphs(INTERSECTION, nodes_dx, nodes_dx_s, edges_dx, edges_dx_s, neigh_dx_names, neigh_dx_names_s)
	elif mode == "H_UNION_S_CAP_R":
		nodes_dx_s_copy = nodes_dx_s.copy()
		edges_dx_s_copy = edges_dx_s.copy()
		neigh_dx_names_s_copy = neigh_dx_names_s.copy()
		nodes_dx_r, edges_dx_r, neigh_dx_names_r = operateGraphs(UNION, nodes_dx_s, nodes_dx_q, edges_dx_s, edges_dx_q, neigh_dx_names_s, neigh_dx_names_q)
		nodes_dx_hs, edges_dx_hs, neigh_dx_names_hs = operateGraphs(UNION, nodes_dx_s_copy, nodes_dx_h, edges_dx_s_copy, edges_dx_h, neigh_dx_names_s_copy, neigh_dx_names_h)
		nodes_dx, edges_dx, neigh_dx_names = operateGraphs(INTERSECTION, nodes_dx_r, nodes_dx_hs, edges_dx_r, edges_dx_hs, neigh_dx_names_r, neigh_dx_names_hs)

	else:
		print("Incorrect mode set in app settings")
		exit(1)
	
	###############################################################

	# returns functional dependencies
	# fd_edges_list = getFunctionalDependencies(tables_dx, neigh_dx_names, dt_dx, db_conn, global_stats_obj.n_edges_in_rel_graph)

	#######################################################
	############# Graph Customizations ###################
	# see if user wants to add some edges to this graph
	# TODO: edit this function for if we want to suggest edges using heuristics without running getFD
	# set this boolean to true to use the inclusion dependent edges in the addition prompt
	# pass the edges in fd_edges_list
	# use_inc_dep = False
	# nodes_dx, edges_dx, neigh_dx_names = createEdges(nodes_dx, edges_dx, neigh_dx_names, tables_dx, dt_dx, app_settings.start_table, use_inc_dep)

	nodes_dx, edges_dx, neigh_dx_names = createEdgesFromFile(nodes_dx, edges_dx, neigh_dx_names, tables_dx, app_settings.edge_addition_file)

	# NOTE: for filters
	processFilters(app_settings.filters_json)
	# # remove pruned edges and create adjacency lists in form of column objects instead of column names
	processPruning(app_settings.pruning_json, neigh_dx_names, db_conn)

	# # also check if the edges to be pruned are functional dependencies
	# TODO: finish this function
	# checkIntersectionWithFDs(fd_edges_list, pruned_edges_list)
	# # NOTE: Do not put inferFilters() before processPruning() as some heuristics (e.g. mapping-tables) depend on edges to be pruned first
	if app_settings.filters_json != "NONE":
		inferFilters()
	createVirtualTables(app_settings.vt_json, db_conn)

	# ######################################
	query = "SELECT DISTINCT "+ app_settings.start_column + " FROM " + app_settings.start_table + ";"
	ds_ids = db_conn.execute(query) 

	# # Note: to extract data for specific ds_ids, set ds_ids as a list of tuples. E.g. ds_ids = [(1, ), (2,)]
	# ds_ids = [(1, )]
	num_ds_ids = 0
	for x,  in ds_ids:
		ds_id = str(x)
		print(f'\nThe data extracted for user id {ds_id} is:')
		# Compute the ground truth
		initializeDataObjects(ds_id)
		computeGroundTruth(ds_id, db_conn, app_settings.gt_filename)
		
		extractData(app_settings, ds_id, db_conn)
		# compare with the ground truth to compute accuracy (precision + recall)
		computeAccuracy(ds_id)
		num_ds_ids += 1
	# ######################################
	computeAccPerTable(num_ds_ids)
	computeAvgAcc()
	# printBadAccuracyDSIds()
	# ######################################
	cleanVirtualTables(db_conn)
	# ######################################
	# # print stats for the paper
	printStats()

if __name__ == '__main__':
	main()
	