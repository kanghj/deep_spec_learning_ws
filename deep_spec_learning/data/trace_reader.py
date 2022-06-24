import os
import sys

sys.path.append("/mnt/StorageArray2_DGX1/btdle/Dropbox/pc_share/deep_spec_learning_ws/deep_spec_learning")
import lib
import gzip, itertools, shutil
import subprocess
import bz2

interested_apis = ['java.util.zip.ZipOutputStream', 'org.apache.xml.serializer.ToHTMLStream', 'DataStructures.StackAr',
                   'java.net.Socket', 'org.columba.ristretto.smtp.SMTPProtocol', 'java.security.Signature',
                   'net.sf.jftp.net.wrappers.SftpConnection',
                   'org.apache.xalan.templates.ElemNumber$NumberFormatStringTokenizer']


class DTraceEntry:
    def __init__(self, inputs):
        self.name = inputs[0].replace(' ', '')
        self.hashcode = None
        if 'this' in inputs:
            self.hashcode = inputs[inputs.index('this') + 1]
        self.return_value = None
        if 'return' in inputs:
            st = inputs[inputs.index('return') + 1]
            if st.lower() == 'true':
                self.return_value = True
            elif st.lower() == 'false':
                self.return_value = False
            else:
                self.return_value = None

    def get_signature(self):
        i = self.name.find(':::')
        st = self.name[:i]
        arr = st.split('.')
        for x in xrange(len(arr)):
            if '(' in arr[x]:
                st = '.'.join(arr[x:])
                break

        rt = ''
        if self.return_value is None:
            rt = ''
        elif self.return_value:
            rt = ':TRUE'
        elif not self.return_value:
            rt = ':FALSE'
        return st + rt  # + ' /// ' + self.hashcode


def interesting_api(api, interested_apis):
    for e in interested_apis:
        if e.startswith(api):
            return True
    return api.find('Duy') >= 0


def is_constructor(name):
    left_para = name.find('(')
    name = name[:left_para]
    arr = name.split('.')
    return arr[-1] == arr[-2]


def recovering_constructor_hashcodes(traces):
    stk = []
    for e in traces:
        if is_constructor(e.name):
            if e.name.find(':::ENTER') >= 0:
                stk += [e]
            elif e.name.find(':::EXIT') >= 0:
                c = stk.pop()
                if c.hashcode is None:
                    # print("Found", c.name)
                    c.hashcode = e.hashcode
    for e in stk:
        print("Unable to recover hashcode of", e.name)


def extract_api(m):
    left_para = m.find('(')
    name = m[:left_para]
    arr = name.split('.')
    s = '.'.join(arr[:-1])
    return s.split('$')[0]


def constructor_string(m):
    left_para = m.find('(')
    name = m[:left_para]
    arr = name.split('.')[:-1]
    arr += [arr[-1]]
    return '.'.join(arr)


def read_daikon_trace(dtrace_gz_file):
    with gzip.open(dtrace_gz_file, 'r') as f:
        lines = [l.strip() for l in f]
        groups = [list(y) for k, y in itertools.groupby(lines, lambda z: len(z.strip()) > 0) if k]
        traces = [DTraceEntry(g) for g in groups if g[0].find(':::EXIT') >= 0 and not g[0].startswith('ppt ')]
        # recovering_constructor_hashcodes(data)
        traces_by_api = {}
        for e in traces:
            api = extract_api(e.name)
            if not interesting_api(api, interested_apis):
                continue
            if api not in traces_by_api:
                traces_by_api[api] = []
            traces_by_api[api] += [e]
        ans = {}
        for api in traces_by_api:
            mp = {}
            ordered_hashcodes = []
            for e in traces_by_api[api]:
                hashcode = e.hashcode
                if hashcode is None:
                    continue
                if hashcode not in mp:
                    mp[hashcode] = []
                    ordered_hashcodes += [hashcode]
                mp[hashcode] += [e.get_signature()]
            ans[api] = []
            for hc in ordered_hashcodes:
                ans[api] += [mp[hc]]
        return ans


def process_7z_event(e):
    method = e.split(',')[1]

    left_para = method.rfind('(')
    right_para = method.rfind(')')

    loc = method[left_para + 1:right_para]
    line = loc.split(':')[-1]
    file = loc.split(':')[0]

    str = method[:left_para]
    m_name = str.split('.')[-1]
    return m_name + '(' + line + ')', method


def ending_char():
    return '\n'.join(["<END>"])


def starting_char():
    return '<START>'


def read_saner_trace_file(input_7z_file, output_folder, calling_7z=False):
    if calling_7z:
        temp_folder = output_folder + '/temp_7z'
        if not os.path.isdir(temp_folder):
            os.makedirs(temp_folder)
        print("extracting", input_7z_file)
        subprocess.check_output(['7z', 'x', input_7z_file, '-o' + temp_folder])
    else:
        temp_folder = input_7z_file
    ###################################################################################
    text_files = lib.find_files_by_suffix(temp_folder, 'txt')
    traces = {}
    method_index = {}
    for text_file in text_files:
        print("reading", text_file)
        with open(text_file, 'r') as f:
            lines = []
            for l in f:
                e, m = process_7z_event(l.strip())
                if e not in method_index:
                    method_index[e] = set()

                method_index[e].add(m)
                lines += [e]
            lines += [ending_char()]
            fname = os.path.basename(text_file)
            api = '_'.join(fname[:fname.rfind('.')].split('_')[:-1])
            if api not in traces:
                traces[api] = []
            traces[api] += lines
    #############################################################################

    for (api, tr) in traces.items():
        if len(set(tr)) < 3:
            continue
        print("writing", api)
        out_file = output_folder + '/' + api + '.bz2'
        output = bz2.BZ2File(out_file, 'w')
        try:
            output.write('\n'.join(tr))
        finally:
            output.close()

    open(output_folder + '/method_dictionary.dict', 'w').write(
        '\n'.join(['\t'.join([e[0]] + list(e[1])) for e in method_index.items()]))
    if calling_7z:
        shutil.rmtree(temp_folder)
