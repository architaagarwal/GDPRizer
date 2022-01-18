class Table:
	def __init__(self, tablename = None, colnames = None, pk = [], result = None):
		self.tablename = tablename # name of table
		self.colnames = colnames # list of column names (orig + virtual)
		self.pk = pk # list of column names that are primary keys
		self.fk = [] # list of column names (orig + virtual) that are foreign keys i.e. any columns that have an edge incident on them
		self.filtered_colnames = [] # list of column names that are filtered
		self.non_filtered_colnames = [] # list of (not virtual) column names that are not filtered
		# list of colnames (orig + virtual) that have atleast one edge incident on them (after edge pruning)
		# note that currently this will be equal to the columns that are not given in "edge pruning through columns" file
		# However, when we switch to edge pruning (instead of edge pruning through columns), this has to be smartly computed
		self.colnames_with_edges = [] 
		self.obj_columns_dx = {} # dictionary from column names to their column objects
		self.result = result # of type "Data"
		self.is_virtual = False
		self.v_colnames = [] # list of virtual column names
		self.inf_filtered_colnames = [] # can help in debugging

		# cumulative accuracy across multiple data subjects
		self.precision = 0 # sum of precision values of all ds
		self.recall = 0 # sum of recall values of all ds
		self.deflated_precision = 0
		self.deflated_recall = 0
		self.deflated_n_ds_prec = 0 # number of ds ids to be used for averaging 'deflated precision'
		self.deflated_n_ds_recall = 0 # number of ds ids to be used for averaging 'deflated recall'
		self.bad_prec_ds = [] 
		self.bad_rec_ds = []
		self.min_bad_prec = 1 #initialized to 1 so that min(initial, x) = x
		self.min_bad_rec = 1

		self.avg_p = 0 # avg precision over all DS
		self.avg_r = 0 # avg recall over all DS
		self.avg_dp = 0 # avg deflated precision over all DS
		self.avg_dr = 0 # avg deflated recall over all DS
		self.f1 = 0

	def __repr__(self):  
		return "[\ntablename: %s \ncolnames: %s \npk: %s \nfk: %s \nfiltered_cols: %s \nnon_filtered_cols: %s \ncolnames_with_edges: %s \ninf_filtered_colnames: %s \n]" \
		% (self.tablename, self.colnames, self.pk, self.fk, self.filtered_colnames, self.non_filtered_colnames, self.colnames_with_edges, self.inf_filtered_colnames)  	

class Data:
	def __init__(self, ds_id, tablename):
		self.ds_id = ds_id # data subject id
		self.tablename = tablename
		self.gt = {} # hashes of rows in ground truth
		self.extracted = {} # hashes of rows that are extracted
		
		# these three will only store the results for ONE data subject
		self.fp = 0
		self.fn = 0
		self.tp = 0

	def __repr__(self):  
		return "[%s, %s, %s, %s, %s, %s, %s]" % (self.ds_id, self.tablename, self.gt, self.extracted, self.fp, self.fn, self.tp)

class Col:
	def __init__(self, tablename = None, colname = None, proximity = -1):
		self.tablename = tablename
		self.colname = colname
		self.proximity = proximity

	def __repr__(self):  
		return "[%s, %s, %s]" % (self.tablename, self.colname, self.proximity)  
		
class Query:
	def __init__(self, obj_col = None, value = [], is_sibling = False):
		self.obj_col = obj_col
		self.value = value
		self.is_sibling = is_sibling

	def __repr__(self):
		return "[%s, %s]" % (self.obj_col, self.value) 

class AppSettings:
	def __init__(self, app_name, db_name, schema_file, pq_file, f_file, prune_file, gt_file, vt_file, additions_file, start_table, start_col, qgraph, path, mode):
		self.app_name = app_name
		self.db_name = db_name
		self.schema_json = schema_file
		self.parsed_queries_json = pq_file
		# NOTE: If no filtering is needed, set filters_filename_json to NONE
		self.filters_json = f_file
		self.pruning_json = prune_file	
		self.gt_filename = gt_file
		self.vt_json = vt_file
		self.edge_addition_file = additions_file
		self.start_table = start_table
		self.start_column = start_col
		self.qgraph = qgraph
		self.path = path
		self.mode = mode

class Stats:
	def __init__(self):
		self.n_edges_in_fk = 0
		self.n_edges_in_joins = 0
		self.n_common_edges = 0 # common edges from the schema and joins
		self.n_edges_in_rel_graph = 0 # technically this is equal to n_edges_in_fk + n_edges_in_joins - n_common_edges
		self.edges_in_joins_not_in_fk = []

		self.n_columns_pruned = 0
		self.n_edges_pruned = 0
		self.n_cols_filtered = 0 # to be implemented

		self.n_cols_in_schema = 0

		# stats for heuristics
		self.n_edges_candidate_directional = 0
		self.n_edges_candidate = 0
		self.n_edges_candidate_int_R = 0
		self.n_edges_inc_dep_directional = 0
		self.n_edges_inc_dep = 0
		self.n_edges_inc_dep_int_R = 0
		## each test
		self.n_edges_dir_dx = {'oor': 0, 'coverage': 0, 'wilcoxon': 0, 'namematch': 0}
		self.n_edges_dx = {'oor': 0, 'coverage': 0, 'wilcoxon': 0, 'namematch': 0}
		## each test intersection with the relationship graph
		self.n_edges_int_R_dx = {'oor': 0, 'coverage': 0, 'wilcoxon': 0, 'namematch': 0}

		self.n_edges_in_operated_graph = 0
		def __repr__(self):  
			return "[n_edges_in_fk: %s\n \
					n_edges_in_joins: %s\n \
					n_common_edges: %s\n \
					n_edges_in_rel_graph: %s\n\
					n_edges_pruned: %s\n\
					n_cols_in_schema: %s\
					]" % \
				(self.n_edges_in_fk, self.n_edges_in_joins, self.n_common_edges, \
					self.n_edges_in_rel_graph, self.n_edges_pruned, self.n_cols_in_schema)  
			

