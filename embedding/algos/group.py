import numpy as np
import pandas as pd
import random
from embedding.parameters import *
from embedding.scenario import bar, get_ratio, get_simple_paths 
from fixdoc import *

TEMP_DAG_PATH = 'dataset/temp_dag.csv'

class GDP:
    def __init__(self, G_ll, G_lower, G_middle, G_upper, G_uu, 
                ll_bw, ll_pp, ll_ca, lower_bw, lower_pp, lower_ca,
                middle_bw, middle_pp, middle_ca, upper_bw, upper_pp, upper_ca,
                uu_bw, uu_pp, uu_ca, pp_required, data_stream, mem_required, 
                ll_para, lower_para, middle_para, upper_para, uu_para):
        self.G_ll, self.ll_bw, self.ll_pp, self.ll_ca = G_ll, ll_bw, ll_pp, ll_ca
        self.ll_paths = get_simple_paths(G_ll, ll_para.get_server_num() / 5)
        self.ll_reciprocals_list, self.ll_proportions_list = get_ratio(self.ll_paths, self.ll_bw, ll_para.get_server_num() / 5)
        
        self.G_lower, self.lower_bw, self.lower_pp, self.lower_ca = G_lower, lower_bw, lower_pp, lower_ca
        self.lower_paths = get_simple_paths(G_lower, lower_para.get_server_num() / 5)
        self.lower_reciprocals_list, self.lower_proportions_list = get_ratio(self.simple_paths, self.simple_bw, self.para.get_server_num() / 5)
        
        self.G_middle, self.middle_bw, self.middle_pp, self.middle_ca = G_middle, middle_bw, middle_pp, middle_ca
        self.middle_paths = get_simple_paths(G_middle, middle_para.get_server_num() / 5)
        self.middle_reciprocals_list, self.middle_proportions_list = get_ratio(self.middle_paths, self.middle_bw, self.para.get_server_num() / 5)
        
        self.G_upper, self.upper_bw, self.upper_pp, self.upper_ca = G_upper, upper_bw, upper_pp, upper_ca
        self.upper_paths = get_simple_paths(G_upper, upper_para.get_server_num() / 5)
        self.upper_reciprocals_list, self.upper_proportions_list = get_ratio(self.upper_paths, self.upper_bw, self.para.get_server_num() / 5)
        
        self.G_uu, self.uu_bw, self.uu_pp, self.uu_ca = G_uu, uu_bw, uu_pp, self.uu_ca
        self.uu_paths = get_simple_paths(G_uu, uu_para.get_server_num() / 5)
        self.uu_reciprocals_list, self.uu_proportions_list = get_ratio(self.uu_paths, self.uu_bw, self.para.get_server_num() / 5)

        self.ll_fixdoc = FixDoc(G_ll, ll_bw, ll_pp, self.ll_paths, self.ll_reciprocals_list, self.ll_proportions_list,
                            pp_required, data_stream, ll_para)
        self.lower_fixdoc = FixDoc(G_lower, lower_bw, lower_pp, self.lower_paths, self.lower_reciprocals_list, self.lower_proportions_list,
                            pp_required, data_stream, lower_para)

    def get_response_time(self, sorted_DAG_path=SORTED_DAG_PATH):
        if not os.path.exists(sorted_DAG_path):
            print('DAGs\' topological order has not been obtained! Please get topological order firstly.')
            return

        df = pd.read_csv(sorted_DAG_path)
        df_len = df.shape[0]
        idx = 0

        DAGs_deploy_ll = []
        T_optimal_ll = []
        start_time_ll = []
        process_sequence_ll = []
        makespan_ll = 0
        makespan_of_all_DAGs = 0

        required_num = REQUIRED_NUM
        all_DAG_num = sum(required_num)
        calculated_num = 0
        print('\nGetting makespan for %d DAGs by FixDoc algorithm ...' % all_DAG_num)
        while idx < df_len:
            # get a DAG
            DAG_name = df.loc[idx, 'job_name']
            DAG_len = 0
            while (idx + DAG_len < df_len) and (df.loc[idx + DAG_len, 'job_name'] == DAG_name):
                DAG_len = DAG_len + 1
            DAG = df.loc[idx: idx + DAG_len]
            DAG_pp_required = self.pp_required[:DAG_len]
            DAG_data_stream = self.data_stream[:DAG_len]

            temp_DAG = DAG.copy()
            temp_DAG.to_csv(TEMP_DAG_PATH)
            temp_T_optimal_ll, temp_deploy_ll, temp_process_sequence_ll, temp_start_time_ll, temp_makespan = self.ll_fixdoc.get_response_time(TEMP_DAG_PATH, makespan_ll) 
            T_optimal_ll.append(temp_T_optimal_ll)
            start_time_ll.append(temp_start_time_ll)
            process_sequence_ll.append(temp_process_sequence_ll)
            DAGs_deploy_ll.append(temp_deploy_ll)
            makespan_ll = temp_makespan
            calculated_num += 1

        print('The overall makespan achieved by FixDoc: %f second' % makespan_ll)
        print('The average makespan: %f second' % (makespan_of_all_DAGs / sum(REQUIRED_NUM)))
        return T_optimal_ll, DAGs_deploy_ll, process_sequence_ll, start_time_ll
            
        
    @staticmethod
    def get_dag_complexity(DAG, DAG_len, DAG_pp_required, DAG_data_stream, DAG_mem_required):
        dag_complexity = 0
        for i in range(DAG_len):
            dag_complexity += DAG_pp_required[i]
        return dag_complexity


    
        


