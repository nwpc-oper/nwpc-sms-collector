# coding: utf-8
from datetime import datetime, timedelta
import subprocess
import re
import os

# default settings
default_sms_variable_list = [
    {
        'variable_name': 'SMSDATE',
        'variable_pattern': r"^.*SMSDATE '([0-9]+)'",  # TODO: gen var or edit var
        'variable_value_group_index': 0
    }
]


def get_cdp_output(cdp_path, sms_host, sms_prog, sms_user, sms_password, command):
    echo_pipe = subprocess.Popen(
        ['echo', command],
        stdout=subprocess.PIPE,
        encoding='utf-8',
        env=dict(
            os.environ,
            SMSHOST=sms_host,
            SMSNAME=sms_user,
            SMSPASS=str(sms_password),
            SMS_PROG=sms_prog
        ))
    cdp_pipe = subprocess.Popen(
        [cdp_path],
        stdin=echo_pipe.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8',
        env=dict(
            os.environ,
            SMSHOST=sms_host,
            SMSNAME=sms_user,
            SMSPASS=str(sms_password),
            SMS_PROG=sms_prog
        )
    )
    echo_pipe.stdout.close()
    (cdp_output, cdp_error) = cdp_pipe.communicate()

    # TODO: not login error
    return_code = cdp_pipe.returncode
    return return_code, cdp_output, cdp_error


def get_sms_variable(cdp_path, sms_host, sms_prog, sms_name, sms_user, sms_password, node_path, variable_list=None):
    """
    获取 node_path 节点的变量
    :param cdp_path:
    :param sms_host:
    :param sms_prog:
    :param sms_name:
    :param sms_user:
    :param sms_password:
    :param node_path: 节点路径，形如 /obs_reg
    :param variable_list: 变量列表
    :return:
    """
    if variable_list is None:
        variable_list = default_sms_variable_list

    command_string = "status;show -f -K {node_path};quit".format(
        sms_name=sms_name,
        sms_user=sms_user,
        sms_password=sms_password,
        node_path=node_path
    )
    return_code, cdp_output, cdp_error = get_cdp_output(
        cdp_path, sms_host, sms_prog, sms_user, sms_password, command_string)
    if return_code != 0:
        current_time = datetime.utcnow().isoformat()
        result = {
            'app': 'sms_status_collector',
            'timestamp': current_time,
            'error': 'command_return_code_error',
            'error-msg': cdp_error
        }
        return result
    cdp_output_lines = cdp_output.split('\n')

    variable_map = {}

    for a_variable in variable_list:
        a_variable['re_line'] = re.compile(a_variable['variable_pattern'])

    for line in cdp_output_lines:
        for a_variable in variable_list:
            m = a_variable['re_line'].match(line)
            if m is not None:
                g = m.groups()
                variable_value = g[a_variable['variable_value_group_index']]
                variable_map[a_variable['variable_name']] = variable_value
    return variable_map


##############################
# get whole status
##############################

class Node(object):
    def __int__(self):
        self.parent = None
        self.children = list()
        self.name = ''
        self.status = 'unknown'

    def to_dict(self):
        ret = dict()
        ret['name'] = self.name
        ret['children'] = list()
        ret['status'] = self.status
        ret['path'] = self.get_node_path()
        for a_child in self.children:
            ret['children'].append(a_child.to_dict())
        return ret

    def add_child(self, node):
        self.children.append(node)

    def get_node_path(self):
        cur_node = self
        node_list = []
        while cur_node is not None:
            node_list.insert(0, cur_node.name)
            cur_node = cur_node.parent
        node_path = "/".join(node_list)
        if node_path == "":
            node_path = "/"
        return node_path


class Bunch(Node):
    def __init__(self):
        Node.__init__(self)
        self.parent = None
        self.children = list()
        self.name = ''
        self.status = 'unknown'

    def add_node_status(self, node_status_object):

        node_path = node_status_object['path']
        node_status = node_status_object['status']
        node_name = node_status_object['name']

        if node_path == '/':
            self.status = node_status
            return self

        node = None
        if node_path[0] != '/':
            return node

        node_path = node_path[1:]
        tokens = node_path.split("/")
        cur_node = self
        for a_token in tokens:
            t_node = None
            for a_child in cur_node.children:
                if a_child.name == a_token:
                    t_node = a_child
                    break
            if t_node is None:
                t_node = Node()
                t_node.parent = cur_node
                t_node.name = node_name
                t_node.status = node_status
                t_node.children = list()
                cur_node.add_child(t_node)
            cur_node = t_node
        return cur_node


class SmsStatusAnalyzer(object):
    def __init__(self):
        self.cur_level = 0
        self.cur_node_path = ''

        # level_mapper 结构示例：
        # { level_start_position: level_no }
        self.level_mapper = dict()
        self.level_mapper[0] = 0

        # node_status 结构示例：
        # {
        #   'path': '/obs_reg'
        #   'name': 'obs_reg'
        #   'status': 'com'
        # }
        self.node_status_list = []

    def analytic_tokens(self, line_start_pos, line_tokens):
        cur_pos = line_start_pos
        for i in range(0, len(line_tokens)-1, 4):
            node_name_part = line_tokens[i]
            blank_part_one = line_tokens[i + 1]
            status_part = line_tokens[i + 2]
            blank_part_two = line_tokens[i + 3]
            if cur_pos not in self.level_mapper:
                self.level_mapper[cur_pos] = self.cur_level
            else:
                level_no = self.level_mapper[cur_pos]
                self.cur_level = level_no
                cur_node_path_tokens = self.cur_node_path.split('/')
                new_node_path_tokens = cur_node_path_tokens[0: level_no+1]
                self.cur_node_path = '/'.join(new_node_path_tokens)
            self.cur_level += 1
            node_path = self.cur_node_path + '/' + node_name_part
            if self.cur_level == 1:
                node_type = 'suite'
            elif blank_part_one[-1] == '{':
                node_type = 'family'
            elif blank_part_one[-1] == '[':
                node_type = 'task'
            else:
                node_type = 'unknown'
            status_item = {
                'path': node_path,
                'name': node_name_part,
                'status': status_part,
                'node_type': node_type
            }
            self.node_status_list.append(status_item)
            self.cur_node_path = node_path
            cur_pos += len(node_name_part) + len(blank_part_one) + len(status_part) + len(blank_part_two)

    def analyse_node_status(self, contents):
        lines = contents.split('\n')
        lines_length = len(lines)
        cur_line_no = 0
        while cur_line_no < lines_length and not lines[cur_line_no].startswith('/'):
            cur_line_no += 1

        if cur_line_no == lines_length:
            # 没有获取的数据
            return None

        # 分析第一行，示例
        # /{act}   obs_reg         [que]   aob       [que]   00E      [com]   getgmf              {com}
        cur_line = lines[cur_line_no].rstrip(' ')
        first_level = {
            'path': '/',
            'name': '/',
            'status': cur_line[2:5],
            'node_type': 'server'
        }
        self.node_status_list.append(first_level)
        tokens = re.split('(\W+|\{[a-z]{3}\}|\[[a-z]{3}\])', cur_line)
        start_pos = len(tokens[0]) + len(tokens[1]) + len(tokens[2]) + len(tokens[3])
        self.analytic_tokens(start_pos, tokens[4:])
        cur_line_no += 1
        while cur_line_no < lines_length and not lines[cur_line_no].startswith("# "):
            cur_line = lines[cur_line_no].rstrip(' ')
            # 使用 re.split('( +)', cur_line) 无法处理如下的特殊情况
            # 特殊情况：make_aob_rens_oracle{com}
            tokens = re.split('(\W+|\{[a-z]{3}\}|\[[a-z]{3}\])', cur_line)
            if len(tokens) <= 5:
                cur_line_no += 1
                continue
            start_pos = len(tokens[0]) + len(tokens[1])
            self.analytic_tokens(start_pos, tokens[2:])
            cur_line_no += 1
        return self.node_status_list


def get_sms_status(
        cdp_path, owner, repo, sms_host, sms_prog, sms_name, sms_user, sms_password, verbose=False,
):
    command_string = "status -f;exit"
    return_code, cdp_output, cdp_error = get_cdp_output(
        cdp_path, sms_host, sms_prog, sms_user, sms_password, command_string)

    if return_code != 0 and return_code != -11:
        current_time = datetime.utcnow().isoformat()
        result = {
            'app': 'sms_status_collector',
            'timestamp': current_time,
            'error': 'command_return_code_error',
            'data': {
                'message': cdp_error
            }
        }
        return result

    tool = SmsStatusAnalyzer()
    node_status_list = tool.analyse_node_status(cdp_output)
    if node_status_list is None:
        """
        SMS is not running, return error message:
            /-CDP> # ERR:RPC:nwpc_wangdp: RPC: 1832-016 Unknown host\n\n# ERR:SMS-CLIENT-LOGIN:Client creation failed for host nwpc_wangdp.\n
        """
        current_time = datetime.utcnow().isoformat()
        result = {
            'app': 'sms_status_collector',
            'timestamp': current_time,
            'error': 'cdp_cannot_get_satus',
            'data': {
                'message': cdp_error
            }
        }
        return result
    bunch = Bunch()
    for a_status in node_status_list:
        bunch.add_node_status(a_status)
    bunch_dict = bunch.to_dict()
    bunch_dict['name'] = sms_name

    current_time = (datetime.utcnow() + timedelta(hours=8)).isoformat()  # 北京时间
    result = {
        'app': 'sms_status_collector',
        'type': 'sms_status',
        'timestamp': current_time,
        'data': {
            'owner': owner,
            'repo': repo,
            'server_name': sms_name,
            'sms_name': sms_name,
            'sms_user': sms_user,
            'time': current_time,
            'status': bunch_dict
        }
    }
    return result
