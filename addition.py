import copy
from queryParser import *
from inflection import singularize

# The GraphAddition stores information about the graph, the schema, the column datatypes, and the primary table
# and is used to:
# - check if the graph has disconnected components
# - prompt the user to connect components in the graph, if they wish
# - connect components in the graph
class GraphAddition:

	def __init__(self, nodes_dx, edges_dx, neigh_dx, schema, table_to_col_to_dt, primary_table, inclusion_dependencies, to_use_inc_dep):
		self.nodes_dx = nodes_dx
		self.edges_dx = edges_dx
		self.neigh_dx = neigh_dx
		self.schema = schema
		self.table_to_col_to_dt = table_to_col_to_dt
		self.primary_table = primary_table
		self.inclusion_dependencies = inclusion_dependencies
		self.USE_INC_DEP = to_use_inc_dep

	# Output: returns true if the graph has disconnected components or tables in schema
	#         which are not in the graph
	def checkDisconnectedComponents(self):

		adj_list = self.neigh_dx.copy()
		
		# create list of unique nodes in the graph from the adjacency list's keys and values
		nodes = list(adj_list.keys()) + [tup for subset in adj_list.values() for tup in subset]
		nodes = list(set(nodes))

		# initialize variables for bfs
		to_visit = []
		visited = []
		curr_node = None
		components = [] # stores each disconnected component within the graph as a list of nodes

		while nodes:
			# we arrive at this point once we have traversed all possible edges but there are still nodes not reached
			# treat all nodes visited to this point as one component
			if visited:
				components.append(visited)
				visited = []
			to_visit.append(nodes[0])

			while to_visit:
				curr_node = to_visit.pop(0)
				visited.append(curr_node)
				nodes.remove(curr_node)
				[to_visit.append(tup) for tup in adj_list[curr_node] if tup not in visited and tup not in to_visit] # add edges to this node
				[to_visit.append(node) for node in nodes if node[0] == curr_node[0]  if node not in visited and node not in to_visit] # add cols in same table

		components.append(visited)
		self.components = components

		# remove all tables present in the graph from the schema
		schema_tables = list(self.schema.keys())
		for cmpnt in self.components:
			for table, _ in cmpnt:
				if table in schema_tables:
					schema_tables.remove(table)

		# graph with no unconnected components will have only one component
		# if schema_tables still has elements, there are tables in scherma not in graph
		return (len(self.components) > 1 or bool(schema_tables))
	

	# connectComponents connects disconnected components in the graph
	# Assumption: connectComponents is called after checkDisconnectedComponents
	def connectComponents(self):
		
		primary_component_index = self.getPrimaryComponentIndex(self.primary_table)
		primary_component = self.components.pop(primary_component_index)
		primary_component_tables = list(set([table for table, _ in primary_component]))
		primary_component_tables.sort(key=lambda a: "" if a == self.primary_table else a)
		prompt_idx_to_tbl_name, res = self.generatePrompt(primary_component_tables)

		for tpl in res:

			possible_edges = []

			# set tbl1 to table with smaller index and tbl2 to table with larger index
			# this is so checking whether one of the tables is in the primary component is easier
			tbl1 = min(tpl)
			tbl2 = max(tpl)

			# WITH INCLUSION DEPENDENCIES
			if self.USE_INC_DEP:
				table1 = prompt_idx_to_tbl_name[tbl1]
				col1 = self.schema[table1].pk[0]
				table2 = prompt_idx_to_tbl_name[tbl2]
				col2 = self.schema[table2].pk[0]
				
				for candidate in self.inclusion_dependencies:
					pair1 = candidate[0]
					pair2 = candidate[1]
					if (pair1[0] == table1 and pair2[0] == table2) or (pair1[0] == table2 and pair2[0] == table1):
						e = PossibleEdge(pair1[0], pair1[1], pair2[0], pair2[1], self.table_to_col_to_dt[table1][col1])
						possible_edges.append(e)
			else:
			# WITHOUT INCLUSION DEPENDENCIES
				table1 = prompt_idx_to_tbl_name[tbl1]
				p_col1 = self.schema[table1].pk[0]
				table2 = prompt_idx_to_tbl_name[tbl2]

				for col2 in self.table_to_col_to_dt[table2].keys():
					if len(self.schema[table2].pk) > 0:
						if col2 != self.schema[table2].pk[0]:
							if self.table_to_col_to_dt[table1][p_col1] == self.table_to_col_to_dt[table2][col2]:
								e = PossibleEdge(table1, p_col1, table2, col2, self.table_to_col_to_dt[table1][p_col1])
								if e not in possible_edges:
									possible_edges.append(e)
					else:
						if self.table_to_col_to_dt[table1][p_col1] == self.table_to_col_to_dt[table2][col2]:
								e = PossibleEdge(table1, p_col1, table2, col2, self.table_to_col_to_dt[table1][p_col1])
								if e not in possible_edges:
									possible_edges.append(e)

				# if the index of tbl1 is greater than the length of the primary_component_tables, 
				# it means that tbl1 is not in the primary component
				# this means neither of the tables is the primary component, so get edges from other direction
				if tbl1 >= len(primary_component_tables) or tbl2 <= len(primary_component_tables):
					p_col2 = self.schema[table2].pk[0]
					for col1 in self.table_to_col_to_dt[table1].keys():
						if col1 != self.schema[table1].pk[0]:
							if self.table_to_col_to_dt[table2][p_col2] == self.table_to_col_to_dt[table1][col1]:
								e = PossibleEdge(table2, p_col2, table1, col1, self.table_to_col_to_dt[table2][p_col2])
								if e not in possible_edges:
									possible_edges.append(e)

			# END #

			# sort possible edges based on their probability value
			if len(possible_edges) == 1:
				print(possible_edges[0])
				self.addEdge(possible_edges[0])
			else:
				possible_edges.sort(key=lambda x: x.probability, reverse=True)

				s = "The following possible edges have been identified based on both columns having the same data type:\n"
				for i in range(0, len(possible_edges)):
					s += (str(i) + ": " + str(possible_edges[i]) + "\n")
				s += "Please key in the numbers of the edges you wish to add to the graph, separated by commas\n>>"

				res = self.parseInputEdges(s)
				
				for edge_index in res:
					if edge_index < len(possible_edges):
						self.addEdge(possible_edges[edge_index])
				
	
	# generatePrompt is used to generate the prompt informing the user of the
	# disconnected components in the graph and prompting them to select tables
	# to be connected
	# Input: a list of tables in the primary component
	# Output: 
	# - a dictionary representing the number associated to the table name displayed in the prompt
	# - a list of tuples with each tuple representing a pair of tables to be connected
	def generatePrompt(self, primary_component_tables):

		prompt_idx_to_tbl_name = {}
		
		prompt = "The graph generated has the following disconnected components:\n"
		prompt += ("=" * 10 + "\nPrimary Component:\n")

		total_count = 0

		# print tables in the primary component
		for table_index in range(0, len(primary_component_tables)):
			prompt += (str(total_count) + ": " + primary_component_tables[table_index] + "\n")
			prompt_idx_to_tbl_name[total_count] = primary_component_tables[table_index]
			total_count += 1

		# print tables in all other components
		for component_index in range(0, len(self.components)):
			prompt += ("=" * 10 + "\nComponent " + str(component_index + 1) + ":\n")
			component_tables = list(set([table for table, _ in self.components[component_index]]))
			component_tables.sort()
			for table_index in range(0, len(component_tables)):
				prompt += (str(total_count) + ": " + component_tables[table_index] + "\n")
				prompt_idx_to_tbl_name[total_count] = component_tables[table_index]
				total_count += 1

		# print tables in the schema not in the graph
		prompt += ("=" * 10 + "\nUnconnected Components:\n")
		for table_name in self.schema.keys():
			if table_name not in prompt_idx_to_tbl_name.values():
				prompt += (str(total_count) + ": " + table_name + "\n")
				prompt += ('-' * 10 + '\n')
				prompt_idx_to_tbl_name[total_count] = table_name
				total_count += 1

		prompt += "Please enter the pair of tables you wish to connect, separated by a comma (e.g. '2,6'). If you would like to connect multiple tables, separate each pair with a semicolon (e.g. '1,2;3,4'):\n>>"

		tables_to_connect = self.parseInputTables(prompt)

		return prompt_idx_to_tbl_name, tables_to_connect

	# Output: returns a list of tuples with each tuple containing a pair of integers
	#         representing the indexes of the tables to be connected
	def parseInputTables(self, s):
		res = input(s)
		res.replace(' ', '')
		input_edges = res.split(';')
		parsed_edges = []
		for string in input_edges:
			input_tables = string.split(',')
			curr_table = []
			try:
				for tbl in input_tables:
					x = int(tbl)
					curr_table.append(x)
				parsed_edges.insert(0, tuple(curr_table))
			except:
				continue
		return parsed_edges

	# Output: returns the list of indexes of the PossibleEdges selected by the 
	#         user to add to the graph
	def parseInputEdges(self, s):
		res = input(s)
		res.replace(' ', '')
		input_edges = res.split(',')
		parsed_edges = []
		for string in input_edges:
			try:
				x = int(string)
				parsed_edges.insert(0, x)
			except:
				continue
		return parsed_edges
	
	# Output: the index of the primary component in the self.components list
	def getPrimaryComponentIndex(self, p_table):
		for i in range(0, len(self.components)):
			for table, _ in self.components[i]:
				if table == p_table:
					return i

	# addEdge adds an edge to the graph by modifying the dictionaries stored in the
	# class fields
	def addEdge(self, to_insert):

		ltable = to_insert.table1
		lcol = to_insert.col1
		rtable = to_insert.table2
		rcol = to_insert.col2

		left = ltable.upper() + "_" + lcol.upper()
		right = rtable.upper() + "_" + rcol.upper()
		self.nodes_dx[left] = 1
		self.nodes_dx[right] = 1
		self.edges_dx[left + " -- " + right] = 1

		updateFks(ltable, lcol, rtable, rcol, self.schema)
		updateNeighborhood(ltable, lcol, rtable, rcol, self.neigh_dx)
	
	# Output: returns the dictionaries representing the updated graph
	def getNewGraph(self):
		return self.nodes_dx, self.edges_dx, self.neigh_dx


# PossibleEdge is a class used to represent a potential edge that might exist
# between two columns in the graph
class PossibleEdge:
	def __init__(self, table1, col1, table2, col2, data_type):
		self.table1 = table1
		self.col1 = col1
		self.table2 = table2
		self.col2 = col2
		self.dt = data_type

		# the self.probability field is a float which represents the likelihood 
		# of the edge existing 
		self.probability = 1.0
		self.calculateLikelihood()
	
	# used to determine the likelihood of an edge existing between the columns
	# specified in the class attributes
	def calculateLikelihood(self):
		if singularize(self.table2.lower()) in self.col1.lower():
			self.probability *= 2
		if self.col2.lower() in self.col1.lower():
			self.probability *= 2
		if singularize(self.table1.lower()) in self.col2.lower():
			self.probability *= 2
		if self.col1.lower() in self.col2.lower():
			self.probability *= 2

	def __eq__(self, other):
		if isinstance(other, PossibleEdge):
			if (self.table1 == other.table1 and self.col1 == other.col1):
				if (self.table2 == other.table2 and self.col2 == other.col2):
					return True
			elif (self.table1 == other.table2 and self.col1 == other.col2):
				if (self.table2 == other.table1 and self.col2 == other.col1):
					return True
		return False

	def __repr__(self):
		s = self.table1 + ":" + self.col1 + " <----> " + self.table2 + ":" + self.col2
		return s