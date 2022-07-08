import sys, os

sys.path.append("/mnt/StorageArray2_DGX1/btdle/Dropbox/pc_share/deep_spec_learning_ws/deep_spec_learning")
sys.path.append(
    '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/deep_spec_learning')
import lib

import graph_libs.Weighted_FSM as graph_lib


def read_traces(trace_file, include_ending=False):
    with open(trace_file, 'r') as r:
        lines = [l.strip() for l in r]
    ans = {}
    for i in range(0, len(lines), 2):
        count = int(lines[i])
        if i + 1 >= len(lines):
            print(lines)
        tr = lines[i + 1].split() + [lib.ending_char()] if include_ending else lines[
            i + 1].split()
        ans[tuple(tr)] = count

    return ans


##########################################################################################

def read_seed_traces_folder(seed_trace_dir, include_ending):
    print("Reading", seed_trace_dir)
    ans = {}
    for trace_file in os.listdir(seed_trace_dir):
        trace_file_name = os.path.basename(trace_file).split('.')[0]
        ans[trace_file_name] = read_traces(seed_trace_dir + '/' + trace_file,
                                           include_ending=include_ending)
    return ans


def write_rejected_seed_traces(results, rejected_by_ground_truth, rejected_by_inferred_model, output_dir, prefix=''):
    print("writing to", output_dir)
    # print(rejected_by_ground_truth)
    with open(output_dir + '/' + prefix + 'rejected_by_GT_model.txt', 'w') as w:
        w.write('\n'.join([' '.join(x) for x in rejected_by_ground_truth]))

    with open(output_dir + '/' + prefix + 'rejected_by_inferred_model.txt', 'w') as w:
        w.write('\n'.join([' '.join(x) for x in rejected_by_inferred_model]))

    with open(output_dir + '/' + prefix + 'results.txt', 'w') as w:
        (precision, recall, f1) = results
        w.write(str(precision) + '\t' + str(recall) + '\t' + str(f1) + '\n')


def write_rejected_traces(results, rejected_by_ground_truth, rejected_by_inferred_model, output_dir, prefix=''):
    print("writing to", output_dir)
    with open(output_dir + '/' + prefix + 'rejected_by_GT_model.txt', 'w') as w:
        w.write('\n'.join([' '.join(x[0]) for x in rejected_by_ground_truth]))

    with open(output_dir + '/' + prefix + 'rejected_by_inferred_model.txt', 'w') as w:
        w.write('\n'.join([' '.join(x[0]) for x in rejected_by_inferred_model]))

    with open(output_dir + '/' + prefix + 'results.txt', 'w') as w:
        (precision, recall, f1) = results
        w.write(str(precision) + '\t' + str(recall) + '\t' + str(f1) + '\n')


def compute_f1(p, r):
    if p + r > 0.0:
        return 2.0 * p * r / (p + r)
    else:
        return 0.0


def avg_of_rates(rates):
    return lib.avg_of([x[1] for x in rates])



def handle(fsm_model_file, gt_model_file, fsm_trace_folder, gt_trace_folder, output_folder, ignore_suffix=False):
    gt_model = graph_lib.create_graph(gt_model_file)
    fsm_model = graph_lib.create_graph(fsm_model_file)

    fsm_traces = read_seed_traces_folder(fsm_trace_folder, include_starting_ending=False)
    gt_traces = read_seed_traces_folder(gt_trace_folder, include_starting_ending=True)

    compute_results_statistics(fsm_model, fsm_traces, gt_model, gt_traces, output_folder, ignore_suffix=ignore_suffix)

def keep_digit(s):
    if type(s)==str:
        return int(''.join([c for c in s if str.isdigit(c)]))
    else:
        return s

def output_list_precisions_recalls_f1(precision_rates, recall_rates, f):
    p = os.path.dirname(f)
    if not os.path.isdir(p):
        os.makedirs(p)
    ###
    precision_dict = {keep_digit(k): v for k, v in precision_rates}
    recall_dict = {keep_digit(k): v for k, v in recall_rates}
    ###

    f1_dict = []
    # print(precision_dict)
    # print(recall_dict)

    # for seed in precision_dict:
    for p, r in zip(precision_dict.values(), recall_dict.values()):
        # p = precision_dict[seed]
        # r = recall_dict[seed]

        f1 = 2.0 * p * r / (p + r) if p + r > 0 else 0

        # f1_dict[seed]=f1
        f1_dict.append((p, r, f1))
    ###
    with open(f,'w') as writer:
        writer.write("precision,recall,f1"+'\n')
        for p, r, f1 in f1_dict:
            writer.write(str(p) + ',' + str(r) + ',' + str(f1))
            writer.write('\n')
        # for name in f1_dict:
        #     writer.write(str(precision_dict[name])+','+str(recall_dict[name])+','+str(f1_dict[name]))
        #     writer.write('\n')

## This function is important
def compute_results_statistics(fsm_model, fsm_traces, gt_model, gt_traces, output_folder, ignore_suffix=False,
                               ignore_return_value=False):
    if ignore_return_value:
        print('ignore_return_value', ignore_return_value)
    recall_rates, rejected_by_inferred_model = fsm_model.accept_trace_sets(gt_traces, ignore_suffix=ignore_suffix,
                                                                           ignore_return_value=ignore_return_value)
    print('done with using fsm model to accept gt traces')
    precision_rates, rejected_by_ground_truth = gt_model.accept_trace_sets(fsm_traces, ignore_suffix=ignore_suffix,
                                                                           ignore_return_value=ignore_return_value)
    #####################################################################################

    avg_precision = avg_of_rates(precision_rates)
    avg_recall = avg_of_rates(recall_rates)
    avg_f1 = compute_f1(avg_precision, avg_recall)
    lib.makedirs(output_folder)
    write_rejected_seed_traces((avg_precision, avg_recall, avg_f1), rejected_by_ground_truth,
                               rejected_by_inferred_model,
                               output_folder)
    output_list_precisions_recalls_f1(precision_rates, recall_rates, output_folder + '/result_stats.txt')
    return avg_precision, avg_recall, avg_f1


def generate_trace(max_label_repeated_per_trace, min_overall_coverage_per_label, seed_list, model_file, output_folder,
                   max_trace_length=100, max_number_of_traces=1000):
    g = graph_lib.create_graph(model_file)
    ans = {}
    if output_folder is not None:
        lib.init_dir(output_folder)

    for seed in seed_list:

        traces = g.seed_trace_generation(seed=seed, max_label_coverage_per_trace=max_label_repeated_per_trace,
                                         min_overall_coverage_per_label=min_overall_coverage_per_label,
                                         max_length=max_trace_length, max_trace=max_number_of_traces)
        ans[seed] = traces
        if output_folder is not None:
            with open(output_folder + '/' + str(seed) + '_traces.txt', 'w') as w:
                for (tr, cnt) in traces.most_common():
                    if tr is None:
                        print("WARNING: found NONE trace!")
                        continue
                    w.write(str(cnt) + '\n')
                    w.write(' '.join(tr) + '\n')
        print("Finished", seed)
    return g, ans
