__author__ = 'erwin'
#coding=utf-8

import codecs
import jieba
import jieba.posseg as pseg
import sys
sys.path.append('..')
import mass_dict

mass_dict = mass_dict.Dict(lazy_load=False)


class FlagObj:
    def __init__(self, flag):
        self.flag = flag
        self.lines = []

    def put(self, line):
        self.lines.append(line)


class LabelObj:
    def __init__(self, label):
        self.label = label
        self.lines = []

    def put(self, line):
        self.lines.append(line)


class LabelCluster:
    def __init__(self):
        self.clusters = {}

    def put(self, label, line):
        label_obj = self.clusters.get(label, None)
        if label_obj is None:
            label_obj = LabelObj(label)
            self.clusters[label] = label_obj
        label_obj.put(line)


high_flag_vec = [
    "a          a",
    "v",
    "n_a		n",
    "d_a		a",
    "n_d_a	    n",
    "d_v		v",
    "n_v		n",
    "v_n		n",
    "n		    n",
    "v_v		v_v",
    "v_a		a",
    "d		    ?",
    "n_d		n",
    "n_d_v	    n",
    "n_n		n2",
    "n_n_a	    n2",
    "n_n_d_a	n2",
    "d_v_n	    ???",
    "v_d_v	    ???",
    "v_d_a	    a",
    "d_v_v	    ???",
    "a_n		n",
    "n_d_d      n"
    "n_d_d_a    n",
    "v_n_a	n",
    "d_d_v	v",
    "v_n_v	n v2",
    "v_a_n	n",
    "n_n_v	?",
    "v_n_n	???",
    "v_d		???",
    "n_v_a	n",
    "v_v_n	n",
    "n_v_v_n	n2",
    "a_v		???",
    "p_n		???discard",
    "n_v_v	???",
    "n_n_d	n2",
    "n_n_n	n1 n2",
    "d_n		n",
    "d_n_a	a",
    "d_d_a	a",
    "v_n_d_a	???",
    "n_v_n	n2",
    "v_v_a	???",
    "n_ng	ng",
    "n_n_d_d_a	n2",
    "n_l		n",
    "n_a_a	n",
    "n_n_d_v    n2",
    "n_d_d_v    n",
    "n_n_d_d_a  n2"
    ]


high_flag_map = {}
low_flag_cmds = ['n2', 'n', 'a2', 'a', 'v2', 'v']
for i in high_flag_vec:
    cmds = i.split()
    if len(cmds) < 2 or cmds[1][0] == '?':
        continue
    high_flag_map[cmds[0]] = cmds[1:]


def try_cmds(cmds, words, short_circut=False):
    chooses = []
    for cmd in cmds:
        index = 1
        if cmd[-1].isdigit():
            index = int(cmd[-1])
            cmd = cmd[0:-1]
        flag_cur_count = {}
        for word in words:
            count = flag_cur_count.get(word.flag, 0)
            flag_cur_count[word.flag] = count + 1
            if word.flag == cmd and flag_cur_count[word.flag] == index:
                chooses.append(word.word)
                if short_circut:
                    return chooses
                break
    return chooses


def choose_keyword(flag_str, words):
    cmds = high_flag_map.get(flag_str, None)
    if cmds is None:
        '''
        try low freq flags
        '''
        chooses = try_cmds(low_flag_cmds, words, short_circut=True)
        return chooses
    chooses = try_cmds(cmds, words)

    return chooses


def trashy_comment(words):
    '''
    filter by keyword?
    or by syntax rules?
    '''
    filter = False

    return filter


def extract_words():
    keywords_flags = set(['n', 'v', 'a', 'l', 'ng', 'nz', 'd', 'p', 'u' 'k'])
    jieba.load_userdict(mass_dict.user_dict_path)
    fin = codecs.open('/Users/erwin/work/comment_labeled/part_of_comments2', 'r', encoding='utf-8')
    fout = codecs.open('/Users/erwin/work/comment_labeled/part_of_comments_tokens', 'w', encoding='utf-8')
    label_clusters = LabelCluster()
    word_freqs = {}
    lineno = 0
    word_count = 0
    flag_objs = {}
    for line in fin.readlines():
        lineno += 1
        line = line.rstrip()
        tokens = pseg.cut(line)
        words1 = []  # attr from dict
        words2 = []  # attr from word_seg

        words3 = []  # attr from selected word_seg
        words4 = []  # word&attr from select word_seg
        marks = []
        for t in tokens:
            if t.word in mass_dict.stop_words:
                continue
            attr = mass_dict.word_attrs.get(t.word)
            if attr is None:
                words1.append(t.word)
            else:
                words1.append(t.word + '_' + ''.join(attr))
            words2.append(t.word + '_' + t.flag)
            if t.flag in keywords_flags:
                words3.append(t.word + '_' + t.flag)
                count = word_freqs.get(t.word, 0)
                word_freqs[t.word] = count + 1
                word_count += 1
                marks.append(t.flag)
                words4.append(t)
        mark_str = '_'.join(marks)
        chooses = choose_keyword(mark_str, words4)
        label = '/'.join(chooses)
        label_clusters.put(label, line)
        flag_obj = flag_objs.get(mark_str, None)
        if flag_obj is None:
            flag_obj = FlagObj(mark_str)
            flag_objs[mark_str] = flag_obj
        flag_obj.put("\t" + line + "\t\t\t\t" + label + "\n\t\t" + '/'.join(words3) + "\n")
    fin.close()

    tmp_flags = sorted(flag_objs.items(), key=lambda (f, o): len(o.lines), reverse=True)
    for (f, o) in tmp_flags:
        fout.write("%s\t%d\n" % (f, len(o.lines)))
        for l in o.lines:
            fout.write(l)

    fout_labels = codecs.open('/Users/erwin/work/comment_labeled/labels', 'w', encoding='utf-8')
    for (label, label_obj) in label_clusters.clusters.items():
        if len(label.strip()) < 1:
            continue
        if len(label_obj.lines) > 2:
            fout_labels.write(label + "\n")
        fout.write(label + "\n")
        for line in label_obj.lines:
            fout.write("\t\t" + line + "\n")
    fout.close()
    fout_labels.close()


if __name__ == '__main__':
    extract_words()