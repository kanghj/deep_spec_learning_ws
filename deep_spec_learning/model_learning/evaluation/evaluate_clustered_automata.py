import sys
sys.path.append('/Users/kanghongjin/repos/deep_spec_learning_ws/deep_spec_learning')
sys.path.append('/Users/kanghongjin/repos/deep_spec_learning_ws/deep_spec_learning/lib')
sys.path.append('/deep_spec_learning_ws/deep_spec_learning/')
sys.path.append('/workspace/deep_spec_learning_ws/deep_spec_learning/')
sys.path.append('/workspace/deep_spec_learning_ws/deep_spec_learning/lib')
sys.path.append('/deep_spec_learning_ws/deep_spec_learning/lib')

sys.path.append("/mnt/StorageArray2_DGX1/btdle/Dropbox/pc_share/deep_spec_learning_ws/deep_spec_learning")
sys.path.append(
    '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/deep_spec_learning')

import argparse
import lib
import graph_libs.Weighted_FSM as graph_lib
import graph_libs.Eval_Lib as eval_lib
import random


def avg_of_rates(rates):
    return lib.avg_of([x[1] for x in rates])


def compute_f1(p, r):
    if p + r > 0.0:
        return 2.0 * p * r / (p + r)
    else:
        return 0.0


def process(args):
    print(args.cluster_folder)
    random.seed(args.seed)

    seed_list = set()
    while len(seed_list) < args.num_seeds:
        seed_list.add(random.randint(0, 2 ** 30))
    print(seed_list)
    fsm_file = args.cluster_folder + '/fsm.txt'
    dfa_file = args.cluster_folder + '/dfa.txt'
    mindfa_file = args.cluster_folder + '/mindfa.txt'

    lib.init_dir(args.result_folder)
    if args.dfa_only ==0:
        fsm_model, fsm_traces = eval_lib.generate_trace(args.max_label_repeated_per_trace, args.overall_min_label_coverage,
                                                        seed_list, fsm_file, args.result_folder + '/fsm_traces',
                                                        max_trace_length=args.max_trace_length,
                                                        max_number_of_traces=args.max_num_trace)
    # dfa_model, dfa_traces = eval_lib.generate_trace(args.max_label_repeated_per_trace, args.overall_min_label_coverage,
    #                                                 seed_list, dfa_file, args.result_folder + '/eval_traces/dfa',
    #                                                 max_trace_length=args.max_trace_length,
    #                                                 max_number_of_traces=args.max_num_trace)
    #mindfa_model, mindfa_traces = eval_lib.generate_trace(args.max_label_repeated_per_trace,
    #                                                      args.overall_min_label_coverage,
    #                                                      seed_list, mindfa_file, args.result_folder + '/mindfa_traces',
    #                                                      max_trace_length=args.max_trace_length,
    #                                                      max_number_of_traces=args.max_num_trace)

    ###
    if args.evaluate_mode:
        ground_truth_traces_dir = args.ground_truth_folder + '/seed_trace'
        gt_traces = eval_lib.read_seed_traces_folder(ground_truth_traces_dir, include_ending=True)
        gt_model = graph_lib.create_graph(args.ground_truth_folder + '/gt_fsm.txt')
        ###
        if args.dfa_only==0:
            print('compute')
            eval_lib.compute_results_statistics(fsm_model, fsm_traces, gt_model, gt_traces,
                                                args.result_folder + '/fsm_results',
                                                ignore_suffix=args.ignore_method_suffix,
                                                ignore_return_value=args.ignore_return_value)
        # eval_lib.compute_results_statistics(dfa_model, dfa_traces, gt_model, gt_traces,
        #                                     args.result_folder + '/dfa_results',
        #                                     ignore_suffix=args.ignore_method_suffix)
        #eval_lib.compute_results_statistics(mindfa_model, mindfa_traces, gt_model, gt_traces,
        #                                    args.result_folder + '/mindfa_results',
        #                                    ignore_suffix=args.ignore_method_suffix)
    print('end')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cluster_folder', type=str, default=None,
                        help='Path to folder of created clusters')
    parser.add_argument('--ground_truth_folder', type=str, default=None,
                        help='Path to folder of ground truth model')
    parser.add_argument('--result_folder', type=str, default=None,
                        help='Path to result folder')
    parser.add_argument('--seed', type=int, default=88,
                        help='seed value')
    parser.add_argument('--num_seeds', type=int, default=10,
                        help='Number of seeds')
    parser.add_argument('--max_label_repeated_per_trace', type=int, default=2,
                        help='Max. number of repeated labels per trace')
    parser.add_argument('--max_trace_length', type=int, default=100,
                        help='Max. trace length')
    parser.add_argument('--max_num_trace', type=int, default=1000,
                        help='Max. number of data to generate')
    parser.add_argument('--overall_min_label_coverage', type=int, default=10,
                        help='Min. Coverage of Each Label in Generated Traces')
    parser.add_argument('--ignore_method_suffix', type=int, default=0,
                        help='True if suffices of methods are ignore in comparision.')
    parser.add_argument('--ignore_return_value', type=int, default=0,
                        help='True if return_value of methods are ignore in comparision.')
    parser.add_argument('--evaluate_mode', type=int, default=1,
                        help='1: precision,recall,f1 are computed; 0: just trace generated.')
    parser.add_argument('--dfa_only', type=int, default=0,
                        help='1: consider DFA only; 0: consider DFA and NFA')
    args = parser.parse_args()

    sys.setrecursionlimit(10000)

    process(args)
