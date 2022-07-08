import ast
import os
import sys

sys.path.append("/mnt/StorageArray2_DGX1/btdle/Dropbox/pc_share/deep_spec_learning_ws/deep_spec_learning")
sys.path.append(
    '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/deep_spec_learning')

import lib, time, settings, random
from collections import Counter
import data.trace_reader as reader
import signal, traceback
from lib import TimeoutError
from graphviz import Digraph
import random


def normalizing_label(label):
    label = label.replace('Duy', '')
    index = label.rfind('$')
    return label[index + 1:] if index >= 0 else label


def remove_suffix_line(method):
    underscore = method.find('_')
    if underscore < 0:
        return method
    colon = method.find(':')
    if colon < 0 and underscore < method.rfind('_'):
        arr = list(method)
        arr[method.rfind('_')] = ':'
        method = ''.join(arr)
        colon = method.find(':')
    ans= method[:underscore] + (method[colon:] if colon >= 0 else '')
    return ans


def remove_return_value(label):
    st = remove_suffix_line(label)
    colon = st.find(':')
    if colon >= 0:
        st = st[:colon]
    # if label!=st:
    #     print label,"vs",st
    return st


class WeightedAutomataGraph:
    def __init__(self, starting_nodes, edges, ending_nodes):
        self.edges = set([tuple(x) for x in edges])
        self.adjlist = {}
        nodes = set()
        self.label_set = set()
        for e in edges:
            # print e
            source = e[0]
            dest = e[1]
            label = e[2]
            if len(e) >= 4:
                p = float(e[3]) if '[' not in e[3] else lib.avg_of([float(x) for x in ast.literal_eval(e[3])])
            else:
                p = 0.99
            if source not in self.adjlist:
                self.adjlist[source] = []
            self.adjlist[source] += [(dest, label, p)]
            nodes.add(source)
            nodes.add(dest)
            self.label_set.add(label)

        for n in nodes:
            if n not in self.adjlist:
                self.adjlist[n] = []
            self.adjlist[n] = sorted(self.adjlist[n], key=lambda x: x[2], reverse=True)

        self.startings = starting_nodes
        self.endings = set(ending_nodes)

    def to_dot(self, filename, drawing_time=10):

        f = Digraph('Automata', format='eps')
        f.body.extend(['rankdir=LR', 'size="8,5"'])
        f.attr('node', shape='star')
        for n in self.startings:
            f.node(n)
        f.attr('node', shape='doublecircle')
        for n in self.endings:
            f.node(n)
        f.attr('node', shape='circle')

        for source in self.adjlist:
            for (dest, label, p) in self.adjlist[source]:
                f.edge(source, dest, label=label)

        if filename is not None:
            try:
                if drawing_time is not None:
                    signal.signal(signal.SIGALRM, lib.handler)
                    signal.alarm(drawing_time)
                f.render(filename, view=False)
            except TimeoutError as e:
                print("Drawing dot:", e)
            finally:
                signal.alarm(0)
        return f.source

    def to_string(self):
        ans = []
        ans += [len(self.startings)]
        for s in self.startings:
            ans += [s]
        ###
        ans += [len(self.endings)]
        for s in self.endings:
            ans += [s]
        ###
        ans += [len(self.edges)]
        for e in self.edges:
            ans += ['\t'.join(e)]
        ###
        ans = [str(x) for x in ans]
        return '\n'.join(ans)

    ##########################################################################################
    def seed_trace_generation(self, seed, max_label_coverage_per_trace,
                              min_overall_coverage_per_label, max_trace=1000, max_length=100, waiting_time=1,
                              max_generation_time=10 * 60):
        overall_label_coverage = Counter()
        random.seed(seed)
        outputs = Counter()
        sarr = list(self.startings)

        for _ in range(max_trace):
            s = random.choice(sarr)
            cur_trace = []
            local_label_coverage = Counter()
            try:
                if waiting_time is not None:
                    signal.signal(signal.SIGALRM, lib.handler)
                    signal.alarm(waiting_time)
                # visited_states = Counter()
                # visited_states[s] += 1
                t = self.find_random_walk(s, cur_trace, local_label_coverage, max_length,
                                          max_label_coverage_per_trace)
                outputs[t] += 1
                overall_label_coverage += local_label_coverage
                if min_overall_coverage_per_label is not None and self.is_enough(overall_label_coverage,
                                                                                 min_overall_coverage_per_label):
                    print("Enough data! Stop!")
                    break
            except Exception as e:
                print("ERROR when generate trace:", e)
                traceback.print_exc()

                random.random()
            finally:
                signal.alarm(0)
        return outputs

    def is_enough(self, overall_label_coverage, min_overall_coverage_per_label):
        for l in self.label_set:
            if l not in overall_label_coverage and l != reader.starting_char() and l != reader.ending_char():
                return False
        for e in overall_label_coverage:
            if overall_label_coverage[e] < min_overall_coverage_per_label:
                return False
        return True

    def find_random_walk(self, s, cur_trace, local_label_coverage, max_length,
                         max_label_coverage_per_trace):
        if len(cur_trace) > max_length:
            print('find_random_walk returning None since len(cur_trace) > max_length')
            return None
        if s in self.endings:
            p_to_exit = 1.0 / (1.0 + sum([x[-1] for x in self.adjlist[s]]))
            # p_to_exit = 1.0
            if len(self.adjlist[s]) == 0 or random.random() <= p_to_exit:
                return tuple(cur_trace) if cur_trace[-1] != '<END>' else tuple(cur_trace[:-1])
        probs = [x[-1] for x in self.adjlist[s]]
        next_ones = list(self.adjlist[s])
        while len(next_ones) > 0:
            index = lib.randomly_pick(probs)
            tp = next_ones[index]

            next_node = tp[0]
            method = tp[1]

            if method not in local_label_coverage or (
                    local_label_coverage[method] < max_label_coverage_per_trace
                    # and visited_states[next_node] < max_label_coverage_per_trace
            ):

                cur_trace += [method]
                local_label_coverage[method] += 1
                # visited_states[next_node] += 1

                # print s, len(cur_trace), cur_trace[-1] if len(cur_trace) > 0 else []
                # print next_ones
                # print
                random_path = self.find_random_walk(next_node, cur_trace, local_label_coverage,
                                                    max_length,
                                                    max_label_coverage_per_trace)
                if random_path is not None:
                    return random_path

                cur_trace.pop()
                local_label_coverage[method] -= 1
                # visited_states[next_node] -= 1

            del probs[index]
            del next_ones[index]

        # print('find_random_walk returning None since a random walk was enever found')
        return None

    ##################################################################
    def accept_trace_sets(self, trace_sets, ignore_suffix=False, ignore_return_value=False):
        unaccepted_traces = set()
        acceptance_rates = []

        highest = len(trace_sets.items())
        i =0
        for (name, e) in trace_sets.items():
            ratio, rejects = self.accept_traces(e, ignore_suffix=ignore_suffix, ignore_return_value=ignore_return_value)
            acceptance_rates += [(name, ratio)]
            unaccepted_traces.update(set(rejects))
            i += 1
            # if i % 100 == 0 :
            #     print("done with ", i , " out of ", highest)
        return acceptance_rates, list(unaccepted_traces),

    def is_accepted(self, node, index, tr, ignore_suffix=False, ignore_return_value=False, debug=False):
        # print '\t\t::', index, len(tr), tr[:index], node
        if index >= len(tr):
            return True
        if debug:
            print(node, tr[index], len(tr), tr)
        current_method = tr[index]
        adjlist = self.adjlist[node][:]
        random.shuffle(adjlist)
        for e in adjlist:
            nxt = e[0]
            label = e[1]
            # if 'DuyStringTokenizer' in label or 'hasMoreTokens' in label:
            #     print label,current_method, remove_suffix_line(label),remove_suffix_line(current_method)
            if debug:
                print('\t', nxt, label, current_method, remove_suffix_line(label), remove_suffix_line(current_method))
            label = normalizing_label(label)
            current_method = normalizing_label(current_method)
            # if ignore_return_value:
            #     print "Comparing", label, current_method
            #     print remove_return_value(label), remove_return_value(current_method)

            if label == current_method or (
                    ignore_suffix and remove_suffix_line(label) == remove_suffix_line(current_method)) \
                    or (ignore_return_value and remove_return_value(label) == remove_return_value(current_method)) \
                    or (ignore_return_value and ignore_suffix and remove_return_value(remove_suffix_line(label)) == remove_return_value(remove_suffix_line(current_method))) \
                    :
                # print("FOUND",label,current_method)
                if True: #debug:
                    pass
                    # print "\tGo to new state", index, nxt, label
                if self.is_accepted(nxt, index + 1, tr, ignore_suffix=ignore_suffix,
                                    ignore_return_value=ignore_return_value, debug=debug):
                    # print('accepted')
                    return True
        # sys.stderr.write("reject," + str(tr[:index]) + ' >' + str(tr[index]) + '<\n')
        return False

    def accept_traces(self, traces, ignore_suffix=False, ignore_return_value=False, waiting_time=1):
        accepted_count = 0
        total_traces = 0
        unaccepted_traces = []
        in_traces_is_dict = type(traces) is dict or type(traces) is Counter

        len_traces = len(traces)
        print('total traces', len_traces)
        for tr in traces:
            flag = False
            for s in self.startings:
                ###
                try:
                    if waiting_time is not None:
                        signal.signal(signal.SIGALRM, lib.handler)
                        signal.alarm(waiting_time)
                    if self.is_accepted(s, 0, tr, ignore_suffix=ignore_suffix, ignore_return_value=ignore_return_value):
                        flag = True
                        break
                except Exception as e:
                    print('Exception thrown when accepting data:', e)
                finally:
                    signal.alarm(0)
                    ###
            total_traces += traces[tr] if in_traces_is_dict else 1
            if flag:
                accepted_count += traces[tr] if in_traces_is_dict else 1
            else:
                unaccepted_traces += [tr]
            # print('done with ', accepted_count + len(unaccepted_traces), ' of ', len_traces)
        if total_traces == 0:
            print("total trace is 0")
            return 1.0, unaccepted_traces
        return float(accepted_count) / total_traces, unaccepted_traces

    def find_final_states(self, traces):
        last_states = None

        for tr in traces:

            for s in self.startings:
                ending_states = self.follow_trace(s, 0, tr)
                if ending_states is not None:
                    if last_states is None:
                        last_states = set()
                    last_states.update(ending_states)

        return last_states

    def follow_trace(self, node, index, tr):
        if index >= len(tr):
            return set([node])
        current_method = tr[index]
        ans = None
        for e in self.adjlist[node]:
            nxt = e[0]
            label = e[1]
            if label == current_method:
                last_states = self.follow_trace(nxt, index + 1, tr)
                if last_states is not None:
                    if ans is None:
                        ans = set()
                    ans.update(last_states)
        return ans


def create_graph(model_file, read_final_states='stops.txt'):
    lines = [l.strip() for l in open(model_file, 'r')]
    cnt = 0
    if len(lines) == 0:
        print("ERROR:", model_file, "has no lines!")
    #######################################
    n_startings = int(lines[cnt])
    cnt += 1
    startings = set()
    for _ in range(n_startings):
        startings.add(lines[cnt])
        cnt += 1
    #######################################
    n_endings = int(lines[cnt])
    cnt += 1
    endings = set()
    for _ in range(n_endings):
        endings.add(lines[cnt])
        cnt += 1
    #######################################
    n_transitions = int(lines[cnt])
    cnt += 1
    edges = []
    # print model_file

    for _ in range(n_transitions):
        
        e = lines[cnt].split()
        edges += [tuple(e)]
        cnt += 1
    #######################################

    if read_final_states is not None and os.path.isfile(os.path.dirname(model_file) + '/' + read_final_states):
        print("Reading final states!")
        endings = set([l.strip() for l in open(os.path.dirname(model_file) + '/' + read_final_states, 'r')])
    return WeightedAutomataGraph(startings, edges, endings)
