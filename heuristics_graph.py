from inclusion_dependency import *
from graph import createSmallGraphHeader
from global_vars import *
from queryParser import updateNeighborhood

# Function to create a graph using the heuristics
# Returns nodes_dx, edges_dx, neigh_dx
def createGraphFromHeuristics(tables_dx, tables_dx_upper, dt_dx, db_conn, formatted_neigh_dx, heuristic_no=-1, th=-1, combined=False, th_dx={}, printing=False):
	nodes_dx,  edges_dx, neigh_dx = {}, {}, {}

	if heuristic_no not in range(0, 5) and not combined:
		print("Invalid option: select a heuristic or run a combined test.")
		return nodes_dx, edges_dx, neigh_dx

	# check all pairs of columns for inclusion dependency
	# candidates is a list of tuples where each tuple has ((T1, c1), (T2, c2)) form
	candidates = getCandidateInclusionDependencies(tables_dx, neigh_dx, dt_dx)
	inclusion_edges_list = applyHeuristic(candidates, INCLUSION, db_conn)
	if printing:
		print("--edges that passed inclusion detection--")
		printUniqueEdges(inclusion_edges_list)

	# stats
	global_stats_obj.n_edges_candidate_directional = len(candidates)
	global_stats_obj.n_edges_candidate = len(deDuplicate(candidates))
	global_stats_obj.n_edges_candidate_int_R = compareEdges(candidates, formatted_neigh_dx)
	global_stats_obj.n_edges_inc_dep_directional = len(inclusion_edges_list)
	global_stats_obj.n_edges_inc_dep = len(deDuplicate(inclusion_edges_list))
	global_stats_obj.n_edges_inc_dep_int_R = compareEdges(inclusion_edges_list, formatted_neigh_dx)

	if combined:
		# combined check for all the heuristics
		print("Running combined heuristics...")
		if len(th_dx) != 4:
			print("Insufficient thresholds: specify 4 thresholds for a combined test")
			return nodes_dx, edges_dx, neigh_dx

		thresholds_list = [th_dx['oor_th'], th_dx['cover_th'], th_dx['wilcoxon_th'], th_dx['name_th']]
		heuristic_order = [OOR, COVERAGE, WILCOXON, NAMEMATCH]

		combined_edges_list = inclusion_edges_list
		for i in range(len(thresholds_list)):
			combined_edges_list = applyHeuristic(combined_edges_list, heuristic_order[i], db_conn, thresholds_list[i])
			# collect stats
			key = convertHeuristicNo(heuristic_order[i]).lower()
			global_stats_obj.n_edges_dir_dx[key] = len(combined_edges_list)
			global_stats_obj.n_edges_dx[key] = len(deDuplicate(combined_edges_list))
			global_stats_obj.n_edges_int_R_dx[key] = compareEdges(combined_edges_list, formatted_neigh_dx)
			if printing:
				print(f"--edges that passed {key} with threshold {thresholds_list[i]}--")
				printUniqueEdges(combined_edges_list)
				
		nodes_dx, edges_dx, neigh_dx = edgeListToDict(combined_edges_list)

	else:
		# individual heuristics	
		if heuristic_no == OOR:
			h_edges_list = applyHeuristic(inclusion_edges_list, OOR, db_conn, th)
		elif heuristic_no == COVERAGE:
			h_edges_list = applyHeuristic(inclusion_edges_list, COVERAGE, db_conn, th)
		elif heuristic_no == WILCOXON:
			h_edges_list = applyHeuristic(inclusion_edges_list, WILCOXON, db_conn, th)
		elif heuristic_no == NAMEMATCH:
			h_edges_list = applyHeuristic(inclusion_edges_list, NAMEMATCH, db_conn, th)
		# collect stats
		key = convertHeuristicNo(heuristic_no).lower()
		global_stats_obj.n_edges_dir_dx[key] = len(h_edges_list)
		global_stats_obj.n_edges_dx[key] = len(deDuplicate(h_edges_list))
		global_stats_obj.n_edges_int_R_dx[convertHeuristicNo(heuristic_no).lower()] = compareEdges(h_edges_list, formatted_neigh_dx)
		if printing:
				print(f"--edges that passed {key} with threshold {th}--")
				printUniqueEdges(h_edges_list)

		nodes_dx, edges_dx, neigh_dx = edgeListToDict(h_edges_list)
	
	# small graph
	header = createSmallGraphHeader(tables_dx_upper, nodes_dx)
	# write the graph in a file
	f = open("heuristics_graph.txt", "w")
	f.write("graph G {" + "\n".join(header) + "\n".join(edges_dx.keys()) + "}")
	f.close()
	return nodes_dx, edges_dx, neigh_dx
	
# Function to convert a list of edges (as tuples) to node_dx, edge_dx and neigh_dx format
def edgeListToDict(edgeList):
	nodes_dx = {}
	edges_dx = {}
	neigh_dx = {}

	for edge in edgeList:
		ltable = edge[0][0]
		lcol = edge[0][1]
		rtable = edge[1][0]
		rcol = edge[1][1]
		left = ltable.upper() + "_" + lcol.upper()
		right = rtable.upper() + "_" + rcol.upper()
		# min and max sort the nodes of the edges. This helps to de-duplicate edges : a -- b and b -- a
		left, right = [min(left, right), max(left, right)]
		nodes_dx[left] = 1
		nodes_dx[right] = 1
		edges_dx[left + " -- " + right] = 1
		updateNeighborhood(ltable, lcol, rtable, rcol, neigh_dx)
	return nodes_dx, edges_dx, neigh_dx

# Function to compute the intersection size given edge_list and formatted_neigh_dx
def compareEdges(h_edges_list, formatted_neigh_dx):
	formatted_edge_list = deDuplicate(h_edges_list)
	h_intersect_r = 0
	for pair in formatted_edge_list:
		col1 = pair[0]
		col2 = pair[1]
		if ((col1 in formatted_neigh_dx and col2 in formatted_neigh_dx[col1]) or \
			(col2 in formatted_neigh_dx and col1 in formatted_neigh_dx[col2])):
			h_intersect_r += 1
	return h_intersect_r

# Function to print unique edges in a given edge_list:
def printUniqueEdges(h_edges_list):
	uniqueEdges = deDuplicate(h_edges_list)
	for (left, right) in uniqueEdges:
		print(f'{left} --- {right}')