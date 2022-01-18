from data_structures import *

# Global dictionaries
neigh_dx = {} # key = obj_col corresponding to a column in a table, value = list of obj_cols corresponding to its neighbors
level_dx = {} # key = level number for the current bfs, value = queue of root query objects at that bfs level
tables_dx = {} # key = tablename, value = table object corresponding to tablename
tables_dx_upper = {} # this is exactly the same as tables_dx. The only difference is that all the names are in uppercase. Needed for creating query graph

# global object which collects various stats about the app
global_stats_obj = Stats()