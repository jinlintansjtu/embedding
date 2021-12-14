"""
Step 1: Get the topological order of DAGs.
Step 2: Generate the scenario.
Step 3: Run the three algorithms and compare the results.
    Author: Hailiang Zhao (hliangzhao@zju.edu.cn)
"""
from embedding.dataset_processing import sample_DAG, get_topological_order
from embedding.scenario import *
from embedding.algos.dpe import DPE
from embedding.algos.fixdoc import FixDoc
from embedding.algos.heft import HEFT
from embedding.algos.interpretate_result import *
from embedding.parameters import *
import datetime
import argparse

def _argparse():
    parser = argparse.ArgumentParser(description = "------Graph Parameters------")
    parser.add_argument('-server_batches', type = int, dest = 'server_batches', default = 1, 
        help = "Server batch numbers")
    parser.add_argument('-server_num', type = int, dest = 'server_num', default = 15,
        help = "Server numbers in a batch")
    parser.add_argument('-density', type = int, dest = 'density', default = 10, 
        help = 'The density of the graph')
    parser.add_argument('-bw_lower', type = int, dest = 'bw_lower', default = 1, 
        help = 'The lower bandwidth')
    parser.add_argument('-bw_upper', type = int, dest = 'bw_upper', default = 11,
        help = 'The upper bandwidth')
    parser.add_argument('-pp_lower', type = int, dest = 'pp_lower', default = 7,
        help = 'The lower processing power')
    parser.add_argument('-pp_upper', type = int, dest = 'pp_upper', default = 14,
        help = 'The upper processing power')
    parser.add_argument('-pp_required_lower', type = int, dest = 'pp_required_lower', default = 1,
        help = 'The lower power required by each function')
    parser.add_argument('-pp_required_upper', type = int, dest = 'pp_required_upper', default = 2,
        help = 'The upper power required by each function')
    
    return parser.parse_args()


if __name__ == '__main__':
    print('------------------------ Step 1 ------------------------')
    sample_DAG()
    get_topological_order()

    print('\n\n------------------------ Step 2 ------------------------')
    args = _argparse()
    
    para = Parameter(args.server_num, args.density, args.bw_lower, args.bw_upper, args.pp_lower,
        args.pp_upper, args.pp_required_lower, args.pp_required_upper)
    ll_para = Parameter(int(args.server_num / 5), args.density, para.get_ll_bw_lower(), para.get_ll_bw_upper(),
                        para.get_ll_pp_lower(), para.get_ll_pp_upper(), args.pp_required_lower, args.pp_required_upper)
    lower_para = Parameter(int(args.server_num / 5), args.density, para.get_lower_bw_lower(), para.get_lower_bw_upper(),
                        para.get_lower_pp_lower(), para.get_lower_pp_upper(), args.pp_required_lower, args.pp_required_upper)
    middle_para = Parameter(int(args.server_num/ 5), args.density, para.get_middle_bw_lower(), para.get_middle_bw_upper(),
                        para.get_middle_pp_lower(), para.get_middle_pp_upper(), args.pp_required_lower, args.pp_required_upper)
    upper_para = Parameter(int(args.server_num / 5), args.density, para.get_upper_bw_lower(), para.get_upper_bw_upper(),
                        para.get_upper_pp_lower(), para.get_upper_pp_upper(), args.pp_required_lower, args.pp_required_upper)
    uu_para = Parameter(int(args.server_num / 5), args.density, para.get_uu_bw_lower(), para.get_uu_bw_upper(),
                        para.get_uu_pp_lower(), para.get_uu_pp_upper(), args.pp_required_lower, args.pp_required_upper)
    
    G, bw, pp, compute = generate_scenario(para.get_server_num(),
                                para.get_density(),
                                para.get_bw_lower(),
                                para.get_bw_upper(),
                                para.get_pp_lower(),
                                para.get_pp_upper(), 0, 1)
    print_scenario(G, bw, pp)

    G_ll, ll_bw, ll_pp, ll_compute = generate_scenario(ll_para.get_server_num(),
                                ll_para.get_density(),
                                ll_para.get_bw_lower(),
                                ll_para.get_bw_upper(),
                                ll_para.get_pp_lower(),
                                ll_para.get_pp_upper(), 1, 2)
    print_scenario(G_ll, ll_bw, ll_pp)

    G_lower, lower_bw, lower_pp, uu_compute = generate_scenario(lower_para.get_server_num(),
                                lower_para.get_density(),
                                lower_para.get_bw_lower(),
                                lower_para.get_bw_upper(),
                                lower_para.get_pp_lower(),
                                lower_para.get_pp_upper(), 3, 4)
    print_scenario(G_lower, lower_bw, lower_pp)

    G_middle, middle_bw, middle_pp, uu_compute = generate_scenario(middle_para.get_server_num(),
                                middle_para.get_density(),
                                middle_para.get_bw_lower(),
                                middle_para.get_bw_upper(),
                                middle_para.get_pp_lower(),
                                middle_para.get_pp_upper(), 5, 6)
    print_scenario(G_middle, middle_bw, middle_pp)

    G_upper, upper_bw, upper_pp, uu_compute = generate_scenario(upper_para.get_server_num(),
                                upper_para.get_density(),
                                upper_para.get_bw_lower(),
                                upper_para.get_bw_upper(),
                                upper_para.get_pp_lower(),
                                upper_para.get_pp_upper(), 6, 7)
    print_scenario(G_upper, upper_bw, upper_pp)
    
    """
    G_uu, uu_bw, uu_pp, uu_compute = generate_scenario(uu_para.get_server_num(),
                                uu_para.get_density(),
                                uu_para.get_bw_lower(),
                                uu_para.get_bw_upper(),
                                uu_para.get_pp_lower(),
                                uu_para.get_pp_upper(), 8, 10)
    print_scenario(G_uu, uu_bw, uu_pp)
    """
    
    simple_paths = get_simple_paths(G, para.get_server_num())
    print_simple_paths(simple_paths)
    reciprocals_list, proportions_list = get_ratio(simple_paths, bw, para.get_server_num())
    pp_required, data_stream, _ = set_funcs(para.get_pp_required_lower(),
                                        para.get_pp_required_upper(),
                                        para.get_data_stream_size_lower(),
                                        para.get_data_stream_size_upper(),
                                        para.get_max_func_num())

    print('\n\n------------------------ Step 3 ------------------------')
    dpe = DPE(G, bw, pp, simple_paths, reciprocals_list, proportions_list, pp_required, data_stream, para)
    start = datetime.datetime.now()
    T_optimal_all_dpe, DAGs_deploy_dpe, process_sequence_all_dpe, start_time_all_dpe = dpe.get_response_time(sorted_DAG_path=SORTED_DAG_PATH)
    end = datetime.datetime.now()
    print('Computer\'s running time:', (end - start).seconds, 'seconds')
    DAG_chosen = 2010    # a randomly peeked number
    print_scheduling_results(T_optimal_all_dpe, DAGs_deploy_dpe, process_sequence_all_dpe, start_time_all_dpe, DAG_chosen, para.get_server_num())

    fixdoc = FixDoc(G, bw, pp, simple_paths, reciprocals_list, proportions_list, pp_required, data_stream, para)
    start = datetime.datetime.now()
    T_optimal_all_fixdoc, DAGs_deploy_fixdoc, process_sequence_all_fixdoc, start_time_all_fixdoc = fixdoc.get_response_time(sorted_DAG_path=SORTED_DAG_PATH)
    end = datetime.datetime.now()
    print('Computer\'s running time:', (end - start).seconds, 'seconds')
    print_scheduling_results(T_optimal_all_fixdoc, DAGs_deploy_fixdoc, process_sequence_all_fixdoc, start_time_all_fixdoc, DAG_chosen, para.get_server_num())

    
    heft = HEFT(G, bw, pp, simple_paths, reciprocals_list, proportions_list, pp_required, data_stream, para)
    start = datetime.datetime.now()
    DAGs_orders, DAGs_deploy = heft.get_response_time(sorted_DAG_path=SORTED_DAG_PATH)
    end = datetime.datetime.now()
    print('Computer\'s running time:', (end - start).seconds, 'seconds')
    print('\nThe finish time of each function on the chosen server for DAG #%d:' % DAG_chosen)
    pprint.pprint(DAGs_orders[DAG_chosen])
