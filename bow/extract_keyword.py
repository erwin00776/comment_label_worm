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


class LabelClusters:
    def __init__(self):
        self.clusters = {}

    def put(self, label, line):
        label_obj = self.clusters.get(label, None)
        if label_obj is None:
            label_obj = LabelObj(label)
            self.clusters[label] = label_obj
        label_obj.put(line)


class ExtractKeyword:
    def __init__(self):
        pass

    def get_keyword(self, sentence):
        pass

    @staticmethod
    def trashy_comment(patterns, words):
        # filter by keyword? or by syntax rules?
        for pattern in patterns:
            if pattern == '*discard*':
                return True
        return False

    def try_match_patterns(self, patterns, words, short_circut=False):
        # short circut: for low frequency syntax rules.
        chooses = []
        if self.trashy_comment(words, patterns):
            return chooses

        for pattern in patterns:
            index = 1
            if pattern[-1].isdigit():
                index = int(pattern[-1])
                pattern = pattern[0:-1]
            flag_cur_count = {}
            for word in words:
                count = flag_cur_count.get(word.flag, 0)
                flag_cur_count[word.flag] = count + 1
                if word.flag == pattern and flag_cur_count[word.flag] == index:
                    chooses.append(word.word)
                    if short_circut:
                        return chooses
                    break
        return chooses

    def choose_keyword(self, flag_str, words):
        pattern = high_freq_patterns.get(flag_str, None)
        if pattern is None:
            # try low freq flags
            chooses = self.try_match_patterns(low_freq_patterns, words, short_circut=True)
            return chooses
        chooses = self.try_match_patterns(pattern, words)

        return chooses

    def train(self, in_fname='', out_fname=''):
        keywords_flags = set(['n', 'v', 'a', 'l', 'ng', 'nz', 'd', 'p', 'u' 'k'])
        jieba.load_userdict(mass_dict.user_dict_path)

        fin = codecs.open('/Users/erwin/work/comment_labeled/all_tmall_comments_clothes2', 'r', encoding='utf-8')
        fout = codecs.open('/Users/erwin/work/comment_labeled/part_of_comments_tokens', 'w', encoding='utf-8')

        label_clusters = LabelClusters()
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
            chooses = self.choose_keyword(mark_str, words4)
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

        # output labels
        fout_labels = codecs.open('/Users/erwin/work/comment_labeled/labels', 'w', encoding='utf-8')
        labels = []
        for (label, label_obj) in label_clusters.clusters.items():
            label = label.strip()
            if len(label) < 2:
                continue
            if len(label_obj.lines) > 2:
                # fout_labels.write(label + "\n")
                labels.append([label.strip(), len(label_obj.lines)])
            fout.write(label + "\n")
            for line in label_obj.lines:
                fout.write("\t\t" + line + "\n")

        labels = sorted(labels, key=lambda item: item[1], reverse=True)
        for (label, label_count) in labels:
            fout_labels.write(label + "\t" + str(label_count) + "\n")

        fout.close()
        fout_labels.close()


high_freq_patterns_vec = [
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
    "n_v_v	???",
    "n_n_d	n2",
    "n_n_n	n1 n2",
    "d_n		n",
    "d_n_a	a",
    "d_n_a_a a",
    "n_v_d_v v",
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
    "n_n_d_d_a  n2",

    "p_v    *discard*",
    "p_n    *discard*",
    ]


# high frequency syntax rules
high_freq_patterns = {}
# low frequency syntax rules (basic)
low_freq_patterns = ['nz', 'n2', 'n', 'a2', 'a', 'v2', 'v']
for i in high_freq_patterns_vec:
    cmds = i.split()
    if len(cmds) < 2 or cmds[1][0] == '?':
        continue
    high_freq_patterns[cmds[0]] = cmds[1:]


if __name__ == '__main__':
    extractor = ExtractKeyword()
    extractor.train()