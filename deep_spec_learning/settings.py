import sys

root_folder = '/usr2/btdle/DataSpace/deep_spec_mining/'
shorten_data_dir = '/mnt/StorageArray2_DGX1/btdle/data_space/deep_spec_learning/cpu_training_data/original_specforge_data'
long_data_dir = '/mnt/StorageArray2_DGX1/btdle/data_space/deep_spec_learning/cpu_training_data/original_specforge_data_full'
revised_data_dir = '/usr2/btdle/DataSpace/deep_spec_mining/cpu_training_data/revised_specforge_data'
fixed_data_dir = '/usr2/btdle/DataSpace/deep_spec_mining/cpu_training_data/fixed_specforge_data'
smart_data_dir = '/usr2/btdle/DataSpace/deep_spec_mining/cpu_training_data/smart_specforge_data'
alpha_data_dir = '/usr2/btdle/DataSpace/deep_spec_mining/cpu_training_data/alpha_specforge_data'
delta_data_dir = '/usr2/btdle/DataSpace/deep_spec_mining/cpu_training_data/delta_specforge_data'

word_rnn_code = '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/word-rnn-tensorflow/'

rnnlm_training_project = '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/next_word_rnn/'

sampling_text_program = '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/next_word_rnn/sample.py'

automata_script_dir = '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/deep_spec_learning/automata/scripts'
f1_evaluation_script_dir = automata_script_dir + '/f1_evaluation/'

GA_clustering_script_dir = automata_script_dir + '/GA'
state_gen_script_dir = automata_script_dir + '/state_gen'

automata_cmd_dir = '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/deep_spec_learning/automata/cmd'
cpu_training_script_dir = '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/deep_spec_learning/cpu_lang_model/scripts'

trace_gen_script_dir = automata_script_dir + '/trace_gen'
random_walk_trace_script_dir = automata_script_dir + '/random_walk_trace'
seed_trace_script_dir = automata_script_dir + '/seed_trace'

genetic_algorithm_dir = '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/deep_spec_learning/automata/genetic_algorithm'

automata_result_dir = '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/deep_spec_learning/automata/results/'
automata_ground_truth_dir = ''

specforge_master_dir = '/usr2/btdle/DataSpace/deep_spec_mining/data/SpecForge-master'
ground_truth_traces = '/usr2/btdle/DataSpace/deep_spec_mining/data/ground_truth'
alpha_ground_truth_traces = '/usr2/btdle/DataSpace/deep_spec_mining/data/alpha_ground_truth'

dot_ground_truth_dir = '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/deep_spec_learning/automata/ground_truth_models/dot_gt'
fsm_ground_truth_dir = '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/deep_spec_learning/automata/ground_truth_models/fsm_gt'
ivokrka_ground_truth_dir = '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/deep_spec_learning/automata/ground_truth_models/orig_fsm_gt'

randoop_dir = '/usr2/btdle/DataSpace/deep_spec_mining/randoop_space'
randoop_method_dir= '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/RandoopUtil/methods4randoop'
randoop_ignored_method_dir= '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/RandoopUtil/omitted_methods'

hacked_rt_class_dir='/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/jws/myUtil/bin'

def is_interested_data_path(f):
    for d in ['Socket', 'DuyStringTokenizer', 'ZipOutputStream', 'Signature', 'StackAr']:
        if d in f:
            return True

    return False


def is_ivokrka_traces(f):
    for d in ['DataStructures_StackAr', 'java_net_Socket', 'java_security_Signature', 'java_util_zip_ZipOutputStream',
              'net_sf_jftp_net_wrappers_SftpConnection', 'org_apache_xml_serializer_ToHTMLStream',
              'org_columba_ristretto_smtp_SMTPProtocol', 'ElemNumber$NumberFormatStringTokenizer',
              'DuyStringTokenizer']:
        if d in f:
            return True
    return False


def class2path(clazz):
    if clazz in ['mjava.util.ArrayList', 'mjava.util.LinkedList', 'mjava.util.Hashtable', 'mjava.util.HashMap',
                 'mjava.util.HashSet', 'mjava.util.StringTokenizer', 'DataStructures.StackAr', 'java.net.Socket',
                 'java.security.Signature', 'java.util.zip.ZipOutputStream']:
        return '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/jws/myUtil/bin'
    # elif clazz == 'net.sf.jftp.net.wrappers.SftpConnection':
    #     return '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/jws/jftp.jar'
    elif clazz == 'org.apache.xalan.templates.ElemNumber$NumberFormatStringTokenizer':
        return '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/jws/myUtil/bin:/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/jws/xalan-j_2_7_2/xalan.jar'
    elif clazz == 'org.apache.xml.serializer.ToHTMLStream':
        return '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/jws/xalan-j_2_7_2/serializer.jar'
    elif clazz == 'org.columba.ristretto.smtp.SMTPProtocol':
        return '/usr2/btdle/dropbox_space/larc_server_dropbox/Dropbox/pc_share/deep_spec_learning_ws/jws/ristretto-1.0-all.jar'
    else:
        print("ERROR: unknown clazz " + clazz)
        sys.exit(0)


def data2groundtruth(data):
    if data == 'DataStructures_StackAr':
        return 'stackar'
    elif data == 'duy_java_util_DuyArrayList':
        return 'ArrayList'
    elif data == 'duy_java_util_DuyHashMap':
        return 'HashMap'
    elif data == 'duy_java_util_DuyHashSet':
        return 'HashSet'
    elif data == 'duy_java_util_DuyHashtable':
        return 'Hashtable'
    elif data == 'duy_java_util_DuyLinkedList':
        return 'LinkedList'
    elif data == 'duy_java_util_DuyStringTokenizer':
        return 'stringtokenizer'

    elif data == 'java_net_Socket':
        return 'socket'
    elif data == 'java_security_Signature':
        return 'signature'
    elif data == 'java_util_zip_ZipOutputStream':
        return 'zipoutputstream'
    elif data == 'net_sf_jftp_net_wrappers_SftpConnection':
        return 'sftpconnection'
    elif data == 'org_apache_xalan_templates_ElemNumber$NumberFormatStringTokenizer':
        return 'numberformatstringtokenizer'

    elif data == 'org_apache_xml_serializer_ToHTMLStream':
        return 'tohtmlstream'
    elif data == 'org_columba_ristretto_smtp_SMTPProtocol':
        return 'smtpprotocol'
