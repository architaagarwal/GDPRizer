import json
import re
import string
from queryParser import *
# from addition import *
from global_vars import *
# from inclusion_dependency import *


# Input: schema: the global tables_dx dictionary which in some way stores the schema of the database
# Output: creates clusters for join-graph as required for graphviz
# see Example 6 here: https://graphs.grevian.org/example
def createFullGraphHeader(schema):
	count = 0
	header = []
	for table, cols in schema.items():
		cluster = []
		cluster.append('subgraph cluster_' + str(count) + '{')
		cluster.append('\tlabel="' + table + '";')
		for col in cols:
			cluster.append('\t' + table + "_" +col + ' [label = "' + col + '"];')
		cluster.append('\t}')
		header.append('\n'.join(cluster))
		count += 1
	return header

# Input: 
	# schema: the global tables_dx dictionary which in some way stores the schema of the database
	# nodes_dx: dictionary of columns with atleast one incident edge.
# Output: creates clusters for join-graph with columns with at least one incident edge
# see Example 6 here: https://graphs.grevian.org/example
def createSmallGraphHeader(schema, nodes_dx):
	count = 0
	header = []
	for table in schema.keys():
		cols = schema[table].colnames
		cluster = []
		# graphviz syntax
		cluster.append('subgraph cluster_' + str(count) + '{')
		cluster.append('\tlabel="' + table + '";')
		# for each column in a table in schema, put it in the graph only if it has >= 1 incident edge
		for col in cols:
			node_name = table + "_" + col
			if node_name in nodes_dx:
				cluster.append('\t' + node_name + ' [label = "' + col + '"];')
		cluster.append('\t}')
		header.append('\n'.join(cluster))
		count += 1
	return header


def createGraphFromFk(fk_dx, schema):
	# fk_dx is a dictionary from tablename to list of triples
	# triples : (fk_col, table_pointed_to, col_pointed_to)
	if not areFkcsPresent(fk_dx):
		print("Foreign keys not found in schema")
		return {}, {}, {}

	nodes_dx = {}
	edges_dx = {}
	neigh_dx = {}

	for ltable, fkc in fk_dx.items():
		for lcol, rtable, rcol in fkc:

			left = ltable.upper() + "_" + lcol.upper()
			right = rtable.upper() + "_" + rcol.upper()
			# min and max sort the nodes of the edges. This helps to de-duplicate edges : a -- b and b -- a
			left, right = [min(left, right), max(left, right)]
			nodes_dx[left] = 1
			nodes_dx[right] = 1
			edges_dx[left + " -- " + right] = 1

			updateFks(ltable, lcol, rtable, rcol, schema)
			updateNeighborhood(ltable, lcol, rtable, rcol, neigh_dx)

	return nodes_dx, edges_dx, neigh_dx

# if all the tables in fk_dx have empty lists, then no fkc-s present
def areFkcsPresent(fk_dx):
	for tablename, v in fk_dx.items():
		if v != []:
			return True
	return False

# both dx_parent and dx_child have integers as dictionary value
def union1(dx_parent, dx_child):
	# c counts the number of overlaps between the two dxs
	# unique contains the unique keys in dx_child
	c = 0
	unique = {}
	for k, v in dx_child.items():
		if k in dx_parent:
			c += 1
		else: 
			unique[k] = v
		dx_parent[k] = v
	return (c, unique)

# both dx_parent and dx_child have sets as dictionary value
def union2(dx_parent, dx_child):
	for k, v_set in dx_child.items():
		if k not in dx_parent:
			dx_parent[k] = v_set
		else:
			dx_parent[k].union(v_set)

# both dx_parent and dx_child have integers as dictionary value
def intersection1(dx_parent, dx_child):
	# assuming that common keys will have same values
	dx_int = {}
	for k, v in dx_parent.items():
		if k in dx_child:
			dx_int[k] = v
	return dx_int

# both dx_parent and dx_child have sets as dictionary value
def intersection2(dx_parent, dx_child):
	dx_int = {}
	for k, _ in dx_parent.items():
		if k in dx_child:
			dx_int[k] = dx_parent[k] & dx_child[k]
			# no elements in intersection
			if len(dx_int[k]) == 0:
				del dx_int[k]
	return dx_int

# def getCandidateInclusionDependencies(schema, neigh_dx, table_to_col_to_dt):

# 		desired_dt = ["int(11)", "bigint", "int"]#, "varchar(60)", "varchar(255)", "varchar(100)"]

# 		candidate_keys = []

# 		# NO PRIMARY KEY REQUIREMENT

# 		# for curr_table in schema:
# 		# 	for curr_table_col in table_to_col_to_dt[curr_table].keys():
# 		# 		for other_table in schema:
# 		# 			if curr_table != other_table:
# 		# 				for check_col in table_to_col_to_dt[other_table].keys():
# 		# 					curr_table_col_dt = table_to_col_to_dt[curr_table][curr_table_col]
# 		# 					other_table_check_col_dt = table_to_col_to_dt[other_table][check_col]
# 		# 					if curr_table_col_dt == other_table_check_col_dt:
# 		# 						if curr_table_col_dt in desired_dt:
# 		# 							edge = ((curr_table, curr_table_col), (other_table, check_col))
# 		# 							candidate_keys.append(edge)
		
# 		# PRIMARY KEY REQUIREMENT 

# 		for curr_table in schema:
# 			if len(schema[curr_table].pk) >= 1:
# 				curr_pk = schema[curr_table].pk[0]
# 				curr_pk_dt = table_to_col_to_dt[curr_table][curr_pk]
# 				if curr_pk_dt in desired_dt:
# 					for other_table in schema:
# 						# if curr_table != other_table:
# 						for check_col in table_to_col_to_dt[other_table].keys():
# 							if len(schema[other_table].pk) >= 1:
# 								if check_col != schema[other_table].pk[0]:
# 									if curr_pk_dt == table_to_col_to_dt[other_table][check_col]:
# 										edge = ((curr_table, curr_pk), (other_table, check_col))
# 										print(edge)
# 										candidate_keys.append(edge)

# 		# END

# 		adjusted_keys = []

# 		for cand in candidate_keys:
# 			column1 = cand[0]
# 			column2 = cand[1]
			
# 			if column1 in neigh_dx:
# 				if column2 in neigh_dx[column1]:
# 					continue
			
# 			if column2 in neigh_dx:
# 				if column1 in neigh_dx[column2]:
# 					continue

# 			adjusted_keys.append(cand)
			
# 		return adjusted_keys



# def createGraph(schema, schema_upper, uniq_col_to_table, uniq_col_to_table_upper, parsed_queries_filename_json, fk_dx, use_queries):
	
# 	nodes_dx,  edges_dx, neigh_dx = {}, {}, {}
# 	nodes_dx_1, edges_dx_1, neigh_dx_1 = {}, {}, {}

# 	# if foreign key constraints are present, use them; else infer them from joins in queries
# 	if areFkcsPresent(fk_dx):
# 		print("fk contraints found in schema")
# 		# Note: edges_dx and neigh_dx represent the same information just in different formats.
# 		# edges_dx has edge info uselful for graph drawing
# 		# neigh_dx has info amenable for traversal (essentially adjacency list)
# 		nodes_dx, edges_dx, neigh_dx = createGraphFromFk(fk_dx, schema)

# 	# collect some stats
# 	global_stats_obj.n_edges_in_fk = len(edges_dx.items())
# 	global_stats_obj.n_edges_in_rel_graph = len(edges_dx.keys()) # n_edges_in_fk same as n_edges_in_rel_graph

# 	if use_queries:
# 		print("--- Using joins to infer edges ---")
# 		nodes_dx_1, edges_dx_1, neigh_dx_1 = createGraphFromQueries(schema, schema_upper, uniq_col_to_table, uniq_col_to_table_upper, parsed_queries_filename_json)

# 		# combine the join graph with fk-graph
# 		union1(nodes_dx, nodes_dx_1)
# 		overlap_count, unique_dx = union1(edges_dx, edges_dx_1)
# 		union2(neigh_dx, neigh_dx_1)

# 		# collect more stats
# 		global_stats_obj.n_edges_in_joins = len(edges_dx_1.items())
# 		global_stats_obj.n_common_edges = overlap_count
# 		global_stats_obj.edges_in_joins_not_in_fk = unique_dx.keys()
# 		global_stats_obj.n_edges_in_rel_graph = len(edges_dx.keys())
	
	
# 	# if you want to create header for entire schema (as required by graphviz)
# 	# use createFullGraphHeader(schema) 
# 	header = createSmallGraphHeader(schema_upper, nodes_dx)
# 	# write the graph in a file
# 	f = open("graph.txt", "w")
# 	f.write("graph G {" + "\n".join(header) + "\n".join(edges_dx.keys()) + "}")
# 	f.close()

# 	#  before Archita pulled out Aaron's inclusion dependecy and edge addition code, 
# 	# it was only return neigh_dx
# 	return nodes_dx, edges_dx, neigh_dx
	

