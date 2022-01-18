import sqlalchemy as db
from collections import Counter
from scipy.stats import mannwhitneyu
from math import floor
import re

INCLUSION  = 0
OOR = 1
COVERAGE = 2
WILCOXON = 3
NAMEMATCH = 4
CANDIDATES = 5


def getCandidateInclusionDependencies(schema, neigh_dx, table_to_col_to_dt):
        # , "varchar(60)", "varchar(255)", "varchar(100)"]
        desired_dt = ["int(11)", "bigint", "int", "INTEGER"]

        candidate_keys = []

		# NO PRIMARY KEY REQUIREMENT

        for curr_table in schema:
            for curr_table_col in table_to_col_to_dt[curr_table].keys():
                for other_table in schema:
                    if curr_table != other_table:
                        for check_col in table_to_col_to_dt[other_table].keys():
                            curr_table_col_dt = table_to_col_to_dt[curr_table][curr_table_col]
                            other_table_check_col_dt = table_to_col_to_dt[other_table][check_col]
                            if curr_table_col_dt == other_table_check_col_dt:
                                if curr_table_col_dt in desired_dt:
                                    edge = ((curr_table, curr_table_col), (other_table, check_col))
                                    candidate_keys.append(edge)

		# PRIMARY KEY REQUIREMENT

        # for curr_table in schema:
        #     if len(schema[curr_table].pk) >= 1:
        #         curr_pk = schema[curr_table].pk[0]
        #         curr_pk_dt = table_to_col_to_dt[curr_table][curr_pk]
        #         if curr_pk_dt in desired_dt:
        #             for other_table in schema:
		# 				# if curr_table != other_table:
        #                 for check_col in table_to_col_to_dt[other_table].keys():
        #                     if len(schema[other_table].pk) >= 1:
        #                         if check_col != schema[other_table].pk[0]:
        #                             if curr_pk_dt == table_to_col_to_dt[other_table][check_col]:
        #                                 edge = ((curr_table, curr_pk), (other_table, check_col))
        #                                 # print(edge)
        #                                 candidate_keys.append(edge)

		# END
        # 
        # adjusted_keys = []
        # for cand in candidate_keys:
        #     column1 = cand[0]
        #     column2 = cand[1]
            
        #     if column1 in neigh_dx:
        #         if column2 in neigh_dx[column1]:
        #             continue
            
        #     if column2 in neigh_dx:
        #         if column1 in neigh_dx[column2]:
        #             continue
            
            # adjusted_keys.append(cand)
            
        # return adjusted_keys
        return candidate_keys


# formatted_neigh_dx: is a dictionary of  dictionaries
#   key: (T, c)
#   value: another dictionary, where keys are (T1, c1) and values are 1 (but we don't ever use these values)
#   (T, c) have edges with all keys of the inside dictionary
def formatNeigh(neigh_dx):
    formatted_neigh_dx = {}
    edges = 0
    rep_edges = 0
    for col1 in neigh_dx.keys():
        formatted_neigh_dx[col1] = {}
        for col2 in neigh_dx[col1]:
            if col2 in formatted_neigh_dx[col1] or (col2 in formatted_neigh_dx and col1 in formatted_neigh_dx[col2]):
                rep_edges += 1
                continue
            else:
                formatted_neigh_dx[col1][col2] = 1
                edges += 1
    print("edges in formatted_neigh_dx ", edges, rep_edges)
    return formatted_neigh_dx

def deDuplicate(edge_list):
    formatted_edge_list = []
    seen = {}
    for pair in edge_list:
        col1 = pair[0]
        col2 = pair[1]
        
        if (col1, col2) in seen:
            continue
        seen[(col2, col1)] = 1
        seen[(col1, col2)] = 1
        formatted_edge_list.append(pair)

    return formatted_edge_list
        
# takes in an edge list and writes to a file
# Note: this function is not yet used anywhere
def writeToFile():
    with open('inclusion_dependencies.txt', 'a') as f:
        f.write("Total Number of Candidates to Verify: " + str(len(candidates)) + "\n")
        f.write("Total Number of Verified Inclusion Dependencies: " + str(len(verified)) + "\n")
        f.write("--------------\n")
		
        f.write("Existing Edges in Graph:\n")
        f.write("Inclusion Dependent in Both Directions:\n")	
        [f.write(x[0][0]+"."+x[0][1]+" <---> "+ x[1][0]+"."+x[1][1]+"\n") for x in two_way]
        f.write("---\n")
        
        f.write("Inclusion Dependent in One Direction:")
        [f.write(x[0][0]+"."+x[0][1]+" <--- "+ x[1][0]+"."+x[1][1]+"\n") for x in one_way]
        f.write("---\n")
        
        f.write("Inclusion Dependent in Neither Direction:")
        [f.write(x[0][0]+"."+x[0][1]+" X "+ x[1][0]+"."+x[1][1]+"\n") for x in not_id_edge]
        
        f.write("--------------\n")
        f.write("All Verified Inclusion Dependencies:\n")
        for item in verified:
            f.write("ref: " + str(item[0]) + " | dep: "+ str(item[1]))
            f.write("\n")


# TODO: edges in both the parameters is represented in different formats. Fix it later
# edge_list: is a list of tuples where each tuple has ((T1, c1), (T2, c2)) form
# formatted_neigh_dx: is a dictionary of  dictionaries
def compare(edge_list, formatted_neigh_dx, heuristic_no, r, f):
    # since edge_list has directionality in its edges and formatted_neigh_dx doesn't 
    # we make edge_list direction-free as well
    # this is done by keeping one of the (a, b) and (b, a) pairs from edge_list
    
    formatted_edge_list = deDuplicate(edge_list)

    message = "H is the num of edges which passed the " + convertHeuristicNo(heuristic_no) + " heuristic"
    print(message)
    f.write(message + "\n")
    h_intersect_r = 0
    h_minus_r = 0
    r_minus_h = 0

    for pair in formatted_edge_list:
        col1 = pair[0]
        col2 = pair[1]
        f.write(str(col1) + " --- " + str(col2) + "\n")
        if ((col1 in formatted_neigh_dx and col2 in formatted_neigh_dx[col1]) or \
            (col2 in formatted_neigh_dx and col1 in formatted_neigh_dx[col2])):
            h_intersect_r += 1
        else:
            h_minus_r += 1
    
    r_minus_h = r - h_intersect_r
    print("|R| = ", r)
    print("|H| (directional) = ", len(edge_list))
    print("|H| = ", len(formatted_edge_list))
    print("|H \cap R| = ", h_intersect_r)
    print("|H - R| = ", h_minus_r)
    print("|R - H| = ", r_minus_h)
    f.write("|R| = " +  str(r) + "\n" + "|H| (directional) = " + str(len(edge_list)) + "\n" \
        + "|H| = " + str(len(formatted_edge_list)) + "\n" + \
        "|H \cap R| = " + str(h_intersect_r) + "\n")
    # print('------'*10)
    
def convertHeuristicNo(heuristic_no):
    if heuristic_no == INCLUSION:
        return  "INCLUSION"
    elif heuristic_no == OOR:
        return  "OOR"
    elif heuristic_no == COVERAGE:
        return  "COVERAGE"
    elif heuristic_no == WILCOXON:
        return "WILCOXON"        
    elif heuristic_no == NAMEMATCH:
        return "NAMEMATCH"
    elif heuristic_no == CANDIDATES:
        return "CANDIDATES"
    else:    
        print("WRONG TEST NO")
        exit(0)

def applyHeuristic(edge_list, heuristic_no, db_conn, th = 1):
    print("Applying heuristic " + convertHeuristicNo(heuristic_no))
    print("Threshold = ", th)
    # for each edge in the edge list, check if the edge passes the heuristic
    # if yes, add it to the verified list
    verified = []
    i = 0
    for pair in edge_list:
        print(" "*10, end = "\r")
        print(str(i) +" of " + str(len(edge_list)), end = "\r")
        ref = pair[0]
        dep = pair[1]
        curr = InclusionDependency(db_conn, ref, dep)
        res = curr.checkHeuristic(heuristic_no, th)
        if res:
            verified.append(pair)
        i += 1
    print(len(verified), "of", len(edge_list), " edges passed " + convertHeuristicNo(heuristic_no) + " heuristic")
    return verified

def runIndividualHeuristics(inclusion_edges_list, db_conn, formatted_neigh_dx, n_edges_in_rel_graph, f):
    
    # oor
    th = 0
    while (th <= 0.4):
        print('-----'*10)
        print('-----'*10)
        print("Threshold = ", th)
        f.write('-----'*10 + "\n" + '-----'*10 + "\n" + "Threshold = " + str(th) + "\n")
        oor_edges_list = applyHeuristic(inclusion_edges_list, OOR, db_conn, th)
        compare(oor_edges_list, formatted_neigh_dx, OOR, n_edges_in_rel_graph, f)
        th += 0.1

    # coverage
    th = 1
    while (th >= 0.6):
        print('-----'*10)
        print('-----'*10)
        print("Threshold = ", th)
        f.write('-----'*10 + "\n" + '-----'*10 + "\n" + "Threshold = " + str(th) + "\n")
        coverage_edges_list = applyHeuristic(inclusion_edges_list, COVERAGE, db_conn, th)
        compare(coverage_edges_list, formatted_neigh_dx, COVERAGE, n_edges_in_rel_graph, f)
        th -= 0.1

    # wilcoxon
    th = 0.5
    while (th <= 0.9):
        print('-----'*10)
        print('-----'*10)
        print("alpha = ", th)
        f.write('-----'*10 + "\n" + '-----'*10 + "\n" + "Alpha = " + str(th) + "\n")
        wilcoxon_edges_list  = applyHeuristic(inclusion_edges_list, WILCOXON, db_conn, th)
        compare(wilcoxon_edges_list, formatted_neigh_dx, WILCOXON, n_edges_in_rel_graph, f)
        th += 0.1

    # name similarity
    th = 0
    while (th <= 5):
        print('-----'*10)
        print('-----'*10)
        print("alpha = ", th)
        name_matching_edges_list  = applyHeuristic(inclusion_edges_list, NAMEMATCH, db_conn, th)
        compare(name_matching_edges_list, formatted_neigh_dx, NAMEMATCH, n_edges_in_rel_graph)
        th += 0.5

    return inclusion_edges_list

# runs all the heuristics sequentially on inclusion dependent edges. 
# The order is fixed: oor --> coverage --> wilcoxon
def runCombinedHeuristics(inclusion_edges_list, db_conn, formatted_neigh_dx, n_edges_in_rel_graph, oor_th, cover_th, wilcoxon_th, name_th, f):
    fd_edges_list = inclusion_edges_list
    
    thresholds_list = [oor_th, cover_th, wilcoxon_th, name_th]
    heuristic_order = [OOR, COVERAGE, WILCOXON, NAMEMATCH]

    for i in range(len(thresholds_list)):
        print('-----'*10)
        print('-----'*10)
        f.write('-----'*10 + "\n" + '-----'*10 + "\n" + "Threshold = " + str(thresholds_list[i]) + "\n")
        fd_edges_list = applyHeuristic(fd_edges_list, heuristic_order[i], db_conn, thresholds_list[i])
        compare(fd_edges_list, formatted_neigh_dx, heuristic_order[i], n_edges_in_rel_graph, f)
    
    return fd_edges_list

# this function generates functional dependencies and returns them
# neigh_dx have edges from our rel. graph
# neigh_dx stores neighborhoods. key = (tablename,  colname), value = set of (tablename, colname) pairs
def getFunctionalDependencies(schema, neigh_dx,  dt_dx, db_conn, n_edges_in_rel_graph):

    # erasing old content from file
    # everywhere else, this file will be opened in append mode
    f = open("inclusion_dependencies.txt", "w")

    # get as candidates all pairs of columns from the schema
    print("Generating and Verifying Inclusion Dependencies...")
    # candidates is a list of tuples where each tuple has ((T1, c1), (T2, c2)) form
    candidates = getCandidateInclusionDependencies(schema, neigh_dx, dt_dx)

    # since neigh_dx will be used in comparison again and again, better to convert it in a format 
    # which is more amenable to comparisons
    # TODO: maybe this can be removed in future
    # Note: formatted_neigh_dx has de-duplicated_edges
    formatted_neigh_dx = formatNeigh(neigh_dx)
    # print(formatted_neigh_dx)

    print('-----'*10)
    print('-----'*10)
    f.write('-----'*10 + "\n" + '-----'*10 + "\n")
    # compare inclusion dependency candidates with relationship graph
    compare(candidates, formatted_neigh_dx, CANDIDATES, n_edges_in_rel_graph, f)

    print('-----'*10)
    print('-----'*10)
    f.write('-----'*10 + "\n" + '-----'*10 + "\n")
    inclusion_edges_list = applyHeuristic(candidates, INCLUSION, db_conn)
    compare(inclusion_edges_list, formatted_neigh_dx, INCLUSION, n_edges_in_rel_graph, f)

    # runs coverage, oor, wilcoxon individually. Each heuristic is run for different thresholds
    # if you need to change the range of thresholds, go to the function and change them 
    # fd_edges_list in this case will be inclusion_edges_list
    # NOTE: UNCOMMENT the following line if you want to run heuristics individually
    # fd_edges_list = runIndividualHeuristics(inclusion_edges_list, db_conn, formatted_neigh_dx, n_edges_in_rel_graph, f)

    # hacky way to clear similarity.txt
    
    sf = open("similarity.txt", "w")
    sf.write("")
    sf.close()

    # runs all the heuristics sequentially. The order is fixed: oor --> coverage --> wilcoxon
    # for each heuristic, the following thresholds are used
    oor_th = 0.2
    cover_th = 0.8
    wilcoxon_th = 0.7
    name_th = 1.0
    fd_edges_list = runCombinedHeuristics(inclusion_edges_list, db_conn, formatted_neigh_dx, n_edges_in_rel_graph, oor_th, cover_th, wilcoxon_th, name_th, f)


    '''   
    not_id_edge = []
    two_way = []
    one_way = []
    for start_node in neigh_dx:
        for end_node in neigh_dx[start_node]:
            curr_tup1 = (start_node, end_node)
            curr_tup2 = (end_node, start_node)
            
            # 
            inc_dep1 = InclusionDependency(db_conn, start_node, end_node)
            inc_dep2 = InclusionDependency(db_conn, end_node, start_node)
            if inc_dep1.checkInclusionDependency() and inc_dep2.checkInclusionDependency():
                if not (curr_tup1 in two_way or curr_tup2 in two_way):
                    two_way.append(curr_tup1)			
            elif inc_dep1.checkInclusionDependency() and not inc_dep2.checkInclusionDependency():
                one_way.append(curr_tup1)
            elif not inc_dep1.checkInclusionDependency() and not inc_dep2.checkInclusionDependency():
                if not (curr_tup1 in not_id_edge or curr_tup2 in not_id_edge):
                    not_id_edge.append(curr_tup1)

    with open('inclusion_dependencies.txt', 'w') as f:
        f.write("Total Number of Candidates to Verify: " + str(len(candidates)) + "\n")
        f.write("Total Number of Verified Inclusion Dependencies: " + str(len(verified)) + "\n")
        f.write("--------------\n")
		
        f.write("Existing Edges in Graph:\n")
        f.write("Inclusion Dependent in Both Directions:\n")	
        [f.write(x[0][0]+"."+x[0][1]+" <---> "+ x[1][0]+"."+x[1][1]+"\n") for x in two_way]
        f.write("---\n")
        
        f.write("Inclusion Dependent in One Direction:")
        [f.write(x[0][0]+"."+x[0][1]+" <--- "+ x[1][0]+"."+x[1][1]+"\n") for x in one_way]
        f.write("---\n")
        
        f.write("Inclusion Dependent in Neither Direction:")
        [f.write(x[0][0]+"."+x[0][1]+" X "+ x[1][0]+"."+x[1][1]+"\n") for x in not_id_edge]
        
        f.write("--------------\n")
        f.write("All Verified Inclusion Dependencies:\n")
        for item in verified:
            f.write("ref: " + str(item[0]) + " | dep: "+ str(item[1]))
            f.write("\n")
    '''
    print("Finished Applying Heuristics!")
    print('-----'*10)

    f.close()
    return fd_edges_list


# Function to calculate the
# Jaro Similarity of two strings
def jaro_distance(s1, s2):
    # If the strings are equal
    if (s1 == s2):
        return 1.0

    # Length of two strings
    len1 = len(s1)
    len2 = len(s2)

    if (len1 == 0 or len2 == 0):
        return 0.0;

    # Maximum distance upto which matching
    # is allowed
    max_dist = (max(len(s1), len(s2)) // 2 ) - 1

    # Count of matches
    match = 0;

    # Hash for matches
    hash_s1 = [0] * len(s1)
    hash_s2 = [0] * len(s2)

    # Traverse through the first string
    for i in range(len1):
        # Check if there is any matches
        for j in range( max(0, i - max_dist),
                    min(len2, i + max_dist + 1)):
            # If there is a match
            if (s1[i] == s2[j] and hash_s2[j] == 0):
                hash_s1[i] = 1
                hash_s2[j] = 1
                match += 1
                break

    # If there is no match
    if (match == 0):
        return 0.0

    # Number of transpositions
    t = 0

    point = 0

    # Count number of occurrences
    # where two characters match but
    # there is a third matched character
    # in between the indices
    for i in range(len1):
        if (hash_s1[i]):
            # Find the next matched character
            # in second string
            while (hash_s2[point] == 0):
                point += 1

            if (s1[i] != s2[point]):
                point += 1
                t += 1
            else:
                point += 1

        t /= 2

    # Return the Jaro Similarity
    return ((match / len1 + match / len2 +
            (match - t) / match ) / 3.0)

# Jaro Winkler Similarity
def jaroWinklerDistance(s1, s2):
    jaro_dist = jaro_distance(s1, s2)

    # If the jaro Similarity is above a threshold
    if (jaro_dist > 0.7):

        # Find the length of common prefix
        prefix = 0

        for i in range(min(len(s1), len(s2))):
            # If the characters match
            if (s1[i] == s2[i]):
                prefix += 1
            else:
                break

        # Maximum of 4 characters are allowed in prefix
        prefix = min(4, prefix)

        # Calculate jaro winkler Similarity
        jaro_dist += 0.1 * prefix * (1 - jaro_dist)

    return jaro_dist

def split_by_case(tokens):
    new_tokens = []
    for token in tokens:
        split_offsets = []
        for i in range(len(token) - 1):
            if token[i].islower() and token[i+1].isupper():
                split_offsets.append(i)
        if len(split_offsets) == 0:
            new_tokens.append(token)
        else:
            start = 0
            for offset in split_offsets:
                if offset == 0:
                    continue
                new_tokens.append(token[start:offset + 1])
                start = offset + 1
            new_tokens.append(token[start:len(token)])

    return new_tokens


class InclusionDependency:
    # raw_dep_attr and raw_ref_attr are tuples of (table_name, column_name)
    # referenced is the column being referenced (i.e. primary key)
    # dependent is the column dependent on the referenced column (i.e. foreign key)
    def __init__(self, db_conn, raw_ref_attr, raw_dep_attr):
        self.ref_attr = Attribute(db_conn, raw_ref_attr[0], raw_ref_attr[1])
        self.dep_attr = Attribute(db_conn, raw_dep_attr[0], raw_dep_attr[1])
            
    def checkHeuristic(self, heuristic_no, th=1):
        if heuristic_no == INCLUSION:
            res = self.checkInclusion(self.ref_attr, self.dep_attr)
        elif heuristic_no == OOR:
            res = self.checkOutOfRange(self.ref_attr.data, self.dep_attr.data, th)
        elif heuristic_no == COVERAGE:
            res = self.checkCoverage(self.ref_attr.data, self.dep_attr.data, th)
        elif heuristic_no == WILCOXON:
            res = self.checkWilcoxonConjunction(self.ref_attr, self.dep_attr, th)
        elif heuristic_no == NAMEMATCH:
            sf = open("similarity.txt", "a")
            res = self.checkColNameSimilarity(self.ref_attr.table_name,self.ref_attr.column_name,self.dep_attr.table_name,self.dep_attr.column_name, th, sf)
            sf.close()
        else:
            print("WRONG TEST NO")
            exit(0)
        return res

    # def checkInclusionDependency(self):
    #     return self.checkInclusion(self.ref_attr, self.dep_attr)
        # self.checkOutOfRange(self.ref_attr.data, self.dep_attr.data) and \
            # self.checkCoverage(self.ref_attr.data, self.dep_attr.data)

        # return self.checkColNameSimilarity(self.ref_attr.table_name,self.ref_attr.column_name,self.dep_attr.table_name,self.dep_attr.column_name) and 
        # return self.checkWilcoxon(self.ref_attr, self.dep_attr)
        
    def checkInclusion(self, ref, dep):
        # check that every dependent value is in referenced
        while dep.cursor < dep.max_len:

            # we have run out of values in the Referenced column
            # but still have values in the Dependent column
            if ref.cursor == ref.max_len:
                return False

            if dep.getCurrentValue() == ref.getCurrentValue():
                dep.incrementCursor()
                ref.incrementCursor()
            elif dep.getCurrentValue() > ref.getCurrentValue():
                ref.incrementCursor()
            else:
                return False
        return True

    def checkCoverage(self, ref_data, dep_data, th):
        num_values_of_ref_in_dep = 0
        num_values_ref = len(ref_data) if len(ref_data) > 0 else 1

        # if coverage is larger than this threshold return true
        THRESHOLD = th

        for x in ref_data:
            if x in dep_data:
                num_values_of_ref_in_dep += 1

        return (num_values_of_ref_in_dep / num_values_ref) >= THRESHOLD

    def checkOutOfRange(self, ref_data, dep_data, th):
        min_dep = min(dep_data) if len(dep_data) > 0 else 0
        max_dep = max(dep_data) if len(dep_data) > 0 else 0
        not_in_range = 0
        total = len(ref_data) if len(ref_data) > 0 else 1

        # if ratio of out of range to total values is larger than this threshold
        # return false
        THRESHOLD = th
        for x in ref_data:
            if not min_dep <= x <= max_dep:
                not_in_range+=1

        return (not_in_range/total) <= THRESHOLD

    def checkWilcoxon(self, ref, dep):
        ref_data = ref.data
        dep_data = dep.data

        # level of significance to reject the null
        alpha = 0.05
        # null hypothesis that dep_data ~ ref_data
        res = mannwhitneyu(ref_data, dep_data, alternative='two-sided')
        # if the prob that the null hypothesis is true < alpha
        if res.pvalue < alpha:
            return False
        return True

    # th should be set to something >=0.5
    def checkWilcoxonConjunction(self, ref, dep, th):
        ref_data = ref.data
        dep_data = dep.data

        # level of significance to accept the null
        alpha = th
        # null hypothesis that dep_data ~ ref_data
        try:
            res = mannwhitneyu(ref_data, dep_data, alternative='two-sided')
            # print(f'p-value: for column REF {ref.table_name}.{ref.column_name} DEP {dep.table_name}.{dep.column_name} -- {res.pvalue}')
        except ValueError:
            # checking for the Value Error, happens in columns with many of the same value
            print(f'Error: for column REF {ref.table_name}.{ref.column_name} DEP {dep.table_name}.{dep.column_name}')
            return False
        # if the prob that the null hypothesis is true > alpha
        if res.pvalue > alpha:
            return True
        return False
        
    def checkColNameSimilarity(self, ref_table_name, ref_col_name, dep_table_name, dep_col_name, th, sf):
        SPLIT_RE = "[\s\:,\-_\.]"
        x_tokens = re.split(SPLIT_RE, ref_col_name)
        y_tokens = re.split(SPLIT_RE, dep_col_name)
        x_tokens = split_by_case(x_tokens)
        y_tokens = split_by_case(y_tokens)
        mapped_tokens = {}
        for j, ytkn in enumerate(y_tokens):
            best_so_far = None
            for i, xtkn in enumerate(x_tokens):
                if i in mapped_tokens.keys():
                    continue
                if best_so_far == None or jaroWinklerDistance(xtkn, ytkn) > best_so_far[1]:
                    best_so_far = (i, jaroWinklerDistance(xtkn, ytkn))
            if best_so_far != None:
                 mapped_tokens[best_so_far[0]] = (j, best_so_far[1])

        sim = 0
        # fudges the similarity score for now, since we don't have an easy way to calculate
        # f_j for all of our tables and for each table's columns (see §3.2 of Chen et al., VLDB'14)
        for i, e in mapped_tokens.items():
            sim += e[1]

        sf.write("refColName: \"" + ref_col_name + "\", depColName: \"" + dep_col_name + "\" | similarity: " + str(sim) + "\n")
        if sim >= th:
            return True
        else:
            return False

class Attribute:

    def __init__(self, db_conn, table_name, column_name):
        self.db_conn = db_conn
        self.table_name = table_name
        self.column_name = column_name
        self.cursor = 0
        self.getAttributeValues()
        self.max_len = len(self.data)

    def getAttributeValues(self):
        # ordering is done in the sql query to leverage database indexes built on columns for sorting
        query = "SELECT DISTINCT `" + self.column_name + "` FROM `" + \
            self.table_name + "` ORDER BY `" + self.column_name + "` ASC;"
        query_output = self.db_conn.execute(query)
        data = []
        for row in query_output:
            # eliminate null and placeholder values in column, as these wouldn't affect inclusion dependency
            if row[0] != None and row[0] != 0:
                data.append(row[0])
        self.data = data

    def incrementCursor(self):
        self.cursor += 1

    def getCurrentValue(self):
        return self.data[self.cursor]



###### The code below this is ONLY for testing purposes #######
def connectMySql(dbname):
    # Connect to dbname on the local MySql server
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '',
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


def main():
    conn = connectMySql("hotcrp_large")
    # test = InclusionDependency(conn, ("ContactInfo", "contactId"), ("ReviewRating", "contactId"))
    # test = InclusionDependency(conn, ("messages", "author_user_id"), ("users", "invited_by_user_id"))
    test = InclusionDependency(
        conn, ("PaperReview", "reviewId"), ("ReviewRating", "reviewId"))
    # test = InclusionDependency(conn, ("wp_term_relationships", "object_id"), ("wp_posts", "ID"))
    # test = Attribute(conn, "users", "id")
    print(test.ref_attr.data)
    print(test.dep_attr.data)
    [print(x) for x in test.dep_attr.data if x not in test.ref_attr.data]
    [print(x) for x in test.ref_attr.data if x not in test.dep_attr.data]
    print(test.checkInclusionDependency())

if __name__ == '__main__':
    main()
