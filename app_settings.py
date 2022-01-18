from data_structures import *

def getAppSettings(app_name):
    # defining app and role specific parameters
    if app_name == 'tpch_cust':
        path = 'tpch'
        app_name = 'tpch'
        schema_filename_json = path + '/schema.json'
        parsed_queries_filename_json = path + '/parsed_queries.json'
        # NOTE: If no filtering is needed, set filters_filename_json to NONE
        filters_filename_json = 'NONE' #app_name + '/filters_customer.json'
        pruning_filename_json = path + '/pruning_customer.json'
        gt_filename = path + '/ground_truth_customer_sql.txt'
        db_name = 'tpch_tiny'
        vt_filename = 'NONE'
        edge_addition_file = 'NONE'
        start_table = 'CUSTOMER'
        start_column = 'C_CUSTKEY'
        qgraph = True
        mode = "R"
    elif app_name == 'tpch_supp':
        path = 'tpch'
        app_name = 'tpch'
        schema_filename_json = path + '/schema.json'
        parsed_queries_filename_json = path + '/parsed_queries.json'
        # NOTE: If no filtering is needed, set filters_filename_json to NONE
        filters_filename_json = 'NONE' #app_name + '/filters_supplier.json'
        pruning_filename_json = path + '/pruning_supplier.json'
        gt_filename = path + '/ground_truth_supplier_sql.txt'
        db_name = 'tpch_tiny'
        vt_filename = 'NONE'
        edge_addition_file = 'NONE'
        start_table = 'SUPPLIER'
        start_column = 'S_SUPPKEY'
        qgraph = True
        mode = "R"
    elif app_name == 'hotcrp':
        path = 'hotcrp'
        schema_filename_json = path + '/schema.json'
        parsed_queries_filename_json = path + '/parsed_queries.json'
        filters_filename_json = path + '/filters.json'
        pruning_filename_json = path + '/pruning.json'
        db_name = 'testconf'
        gt_filename = path + '/ground_truth_sql.txt'
        vt_filename = path + '/virtual_tables.json'
        edge_addition_file = 'NONE'
        start_table = 'ContactInfo'
        start_column = 'contactId'
        qgraph = True
        mode = "R"
    elif app_name == 'hotcrp_large':
        path = 'hotcrp_large'
        schema_filename_json = path + '/schema.json'
        parsed_queries_filename_json = path + '/parsed_queries.json'
        filters_filename_json = path + '/filters.json'
        pruning_filename_json = path + '/pruning.json'
        db_name = 'hotcrp_large'
        gt_filename = path + '/ground_truth_sql.txt'
        vt_filename = path + '/virtual_tables.json'
        edge_addition_file = path + '/additions.txt'
        start_table = 'ContactInfo'
        start_column = 'contactId'
        qgraph = True
        mode = "R"
    elif app_name == 'hotcrp_large_cap':
        path = 'hotcrp_large/h_cap_r'
        schema_filename_json = path + '/schema.json'
        parsed_queries_filename_json = path + '/parsed_queries.json'
        filters_filename_json = path + '/filters.json'
        pruning_filename_json = path + '/pruning.json'
        db_name = 'hotcrp_large'
        gt_filename = path + '/ground_truth_sql.txt'
        vt_filename = path + '/virtual_tables.json'
        edge_addition_file = path + '/additions.txt'
        start_table = 'ContactInfo'
        start_column = 'contactId'
        qgraph = True
        mode = "CAP"
    elif app_name == 'hotcrp_large_h':
        # app_name = 'hotcrp_large'
        path = 'hotcrp_large/h'
        schema_filename_json = path + '/schema.json'
        parsed_queries_filename_json = path + '/parsed_queries.json'
        filters_filename_json = path + '/filters.json'
        pruning_filename_json = path + '/pruning.json'
        db_name = 'hotcrp_large'
        gt_filename = path + '/ground_truth_sql.txt'
        vt_filename = 'NONE' #app_name + '/virtual_tables.json'
        edge_addition_file = path + '/additions.txt'
        start_table = 'ContactInfo'
        start_column = 'contactId'
        qgraph = True
        mode = "H"
    elif app_name == 'lobsters':
        path = 'lobsters'
        schema_filename_json = path + '/schema.json'
        parsed_queries_filename_json = path + '/parsed_queries.json'
        filters_filename_json = path + '/filters.json'
        pruning_filename_json = path + '/pruning.json'
        db_name = "lobsters"
        gt_filename = path + '/ground_truth_sql.txt'
        vt_filename = 'NONE'
        edge_addition_file = path + '/additions.txt'
        start_table = 'users'
        start_column = 'id'
        qgraph = True
        mode = "R"
    elif app_name == 'lobsters_h':
        # app_name = 'lobsters'
        path = 'lobsters/h'
        schema_filename_json = path + '/schema.json'
        parsed_queries_filename_json = path + '/parsed_queries.json'
        filters_filename_json = 'NONE' #path + '/filters.json'
        pruning_filename_json = path + '/pruning.json'
        db_name = "lobsters"
        gt_filename = path + '/ground_truth_sql.txt'
        vt_filename = 'NONE'
        edge_addition_file = path + '/additions.txt'
        start_table = 'users'
        start_column = 'id'
        qgraph = True
        mode = "H"
    elif app_name == 'lobsters_cap':
        # app_name = 'lobsters'
        path = 'lobsters/h_cap_r'
        schema_filename_json = path + '/schema.json'
        parsed_queries_filename_json = path + '/parsed_queries.json'
        filters_filename_json = 'NONE' #path + '/filters.json'
        pruning_filename_json = 'NONE' #path + '/pruning.json'
        db_name = "lobsters"
        gt_filename = path + '/ground_truth_sql.txt'
        vt_filename = 'NONE'
        edge_addition_file = 'NONE' #path + '/additions.txt'
        start_table = 'users'
        start_column = 'id'
        qgraph = True
        mode = "CAP"
    elif app_name == 'lobsters_h_union_s':
        # app_name = 'lobsters'
        path = 'lobsters/h_union_s'
        schema_filename_json = path + '/schema.json'
        parsed_queries_filename_json = path + '/parsed_queries.json'
        filters_filename_json = 'NONE' #path + '/filters.json'
        pruning_filename_json = path + '/pruning.json'
        vt_filename = 'NONE'
        edge_addition_file = 'NONE' #path + '/additions.txt'
        db_name = "lobsters"
        gt_filename = path + '/ground_truth_sql.txt'
        start_table = 'users'
        start_column = 'id'
        qgraph = False
        mode = "H_UNION_S"
    elif app_name == 'lobsters_h_union_s__cap_r':
        # app_name = 'lobsters'
        path = 'lobsters/h_union_s__cap_r'
        schema_filename_json = path + '/schema.json'
        parsed_queries_filename_json = path + '/parsed_queries.json'
        filters_filename_json = 'NONE' #path + '/filters.json'
        pruning_filename_json = path + '/pruning.json'
        vt_filename = 'NONE'
        edge_addition_file = path + '/additions.txt'
        db_name = "lobsters"
        gt_filename = path + '/ground_truth_sql.txt'
        start_table = 'users'
        start_column = 'id'
        qgraph = False
        mode = "H_UNION_S_CAP_R"
    elif app_name == 'wordpress':
        path = 'wordpress'
        schema_filename_json = path + '/schema.json'
        parsed_queries_filename_json = path + '/parsed_queries.json'
        filters_filename_json = 'NONE' # app_name + '/filters.json'
        pruning_filename_json = path + '/pruning.json'
        db_name = "wordpress_2"
        gt_filename = path + '/ground_truth_sql.txt'
        vt_filename = 'NONE'
        edge_addition_file = 'NONE' #app_name + '/additions.txt'
        start_table = 'wp_users'
        start_column = 'ID'
        qgraph = True
        mode = "R"
    elif app_name == 'wordpress_h':
        path = 'wordpress/h'
        # app_name = 'wordpress'
        schema_filename_json = path + '/schema.json'
        parsed_queries_filename_json = path + '/parsed_queries.json'
        filters_filename_json = 'NONE' # path + '/filters.json'
        pruning_filename_json = 'NONE' #path + '/pruning.json'
        db_name = "wordpress_2"
        gt_filename = path + '/ground_truth_sql.txt'
        vt_filename = 'NONE'
        edge_addition_file = 'NONE' #path + '/additions.txt'
        start_table = 'wp_users'
        start_column = 'ID'
        qgraph = True
        mode = "H"
    elif app_name == 'wordpress_cap':
        path = 'wordpress/h_cap_r'
        # app_name = 'wordpress'
        schema_filename_json = path + '/schema.json'
        parsed_queries_filename_json = path + '/parsed_queries.json'
        filters_filename_json = 'NONE' # path + '/filters.json'
        pruning_filename_json = 'NONE' #path + '/pruning.json'
        db_name = "wordpress_2"
        gt_filename = path + '/ground_truth_sql.txt'
        vt_filename = 'NONE'
        edge_addition_file = 'NONE' #path + '/additions.txt'
        start_table = 'wp_users'
        start_column = 'ID'
        qgraph = True
        mode = "CAP"
    elif app_name == 'wordpress_plugins':
        path = 'wordpress_plugins'
        # app_name = 'wordpress_plugins'
        schema_filename_json = path + '/schema.json'
        parsed_queries_filename_json = path + '/parsed_queries.json'
        filters_filename_json = 'NONE' # app_name + '/filters.json'
        pruning_filename_json = path + '/pruning.json'
        db_name = "wordpress_2"
        gt_filename = path + '/ground_truth_sql.txt'
        vt_filename = 'NONE'
        edge_addition_file = path + '/additions.txt'
        start_table = 'wp_users'
        start_column = 'ID'
        qgraph = True
        mode = "R"
    elif app_name == 'wordpress_plugins_h':
        path = 'wordpress_plugins/h'
        # app_name = 'wordpress_plugins'
        schema_filename_json = path + '/schema.json'
        parsed_queries_filename_json = path + '/parsed_queries.json'
        filters_filename_json = 'NONE' # path + '/filters.json'
        pruning_filename_json = path + '/pruning.json'
        db_name = "wordpress_2"
        gt_filename = path + '/ground_truth_sql.txt'
        vt_filename = 'NONE'
        edge_addition_file = path + '/additions.txt'
        start_table = 'wp_users'
        start_column = 'ID'
        qgraph = True
        mode = "H"
    elif app_name == 'wordpress_plugins_cap':
        path = 'wordpress_plugins/h_cap_r'
        # app_name = 'wordpress_plugins'
        schema_filename_json = path + '/schema.json'
        parsed_queries_filename_json = path + '/parsed_queries.json'
        filters_filename_json = 'NONE' # path + '/filters.json'
        pruning_filename_json = 'NONE' #path + '/pruning.json'
        db_name = "wordpress_2"
        gt_filename = path + '/ground_truth_sql.txt'
        vt_filename = 'NONE'
        edge_addition_file = 'NONE' #path + '/additions.txt'
        start_table = 'wp_users'
        start_column = 'ID'
        qgraph = True
        mode = "CAP"
    else:
        print('Invalid application name. Exiting.')
        exit(0)

    settings_obj = AppSettings(app_name, db_name, \
                    schema_filename_json, \
                    parsed_queries_filename_json,\
                    filters_filename_json,\
                    pruning_filename_json,\
                    gt_filename, vt_filename, \
                    edge_addition_file,	
                    start_table, start_column,\
                    qgraph, path, mode)

    return settings_obj
