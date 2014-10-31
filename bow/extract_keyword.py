__author__ = 'erwin'
#coding=utf-8

import codecs
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


flag_vec = [
    "a",
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
    "n_d_d_a	n",
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
    "n_a_a	n" ]


flag_map = {}
for i in flag_vec:
    cmds = i.split()
    if len(cmds) < 2 or cmds[1][0] == '?':
        continue
    flag_map[cmds[0]] = cmds[1:]


def choose_keyword(flag_str, words):
    cmds = flag_map.get(flag_str, None)
    chooses = []
    if cmds is None:
        return chooses

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
                break
    return chooses



def cut_words():
    kw_flags = set(['n', 'v', 'a', 'l', 'ng', 'nz', 'd', 'p', 'u' 'k'])
    fin = codecs.open('/Users/erwin/work/comment_labeled/part_of_comments', 'r', encoding='utf-8')
    fout = codecs.open('/Users/erwin/work/comment_labeled/part_of_comments_tokens', 'w', encoding='utf-8')
    word_freqs = {}
    line_count = 0
    word_count = 0
    flags_freq = {}
    flag_objs = {}
    for line in fin.readlines():
        line_count += 1
        line = line.rstrip()
        tokens = pseg.cut(line)
        words1 = []  # attr from dict
        words2 = []  # attr from word_seg

        words3 = []  # attr from selected word_seg
        words4 = []
        flags = []
        for t in tokens:
            if t.word in mass_dict.stop_words:
                continue
            attr = mass_dict.word_attrs.get(t.word)
            if attr is None:
                words1.append(t.word)
            else:
                words1.append(t.word + '_' + ''.join(attr))
            words2.append(t.word + '_' + t.flag)
            if t.flag in kw_flags:
                words3.append(t.word + '_' + t.flag)
                count = word_freqs.get(t.word, 0)
                word_freqs[t.word] = count + 1
                word_count += 1
                flags.append(t.flag)
                words4.append(t)
        flag_str = '_'.join(flags)
        chooses = choose_keyword(flag_str, words4)
        flag_obj = flag_objs.get(flag_str, None)
        if flag_obj is None:
            flag_obj = FlagObj(flag_str)
            flag_objs[flag_str] = flag_obj
        flag_obj.put("\t" + line + "\t\t" + '/'.join(chooses) + "\n\t\t" + '/'.join(words3) + "\n")

    '''
    f2w = []
    for (w, freq) in word_freqs.items():
        tf = freq * 1.0 / word_count
        idf = mass_dict.idf.get(w, 1.0)
        f2w.append([w, tf*idf])
        #print(w + "\t" + str(tf) + "\t" + str(idf))
    f2w = sorted(f2w, key=lambda x: x[1], reverse=True)
    for (w, f) in f2w:
        print(w + "\t" + str(f))
    '''
    tmp_flags = sorted(flag_objs.items(), key=lambda (f, o): len(o.lines), reverse=True)
    for (f, o) in tmp_flags:
        fout.write("%s\t%d\n" % (f, len(o.lines)))
        for l in o.lines:
            fout.write(l)

    fout.close()
    fin.close()

    '''
    tmp_flags = sorted(flags_freq.items(), key=lambda (x, y): y, reverse=True)
    for (flag_str, flag_freq) in tmp_flags:
        print(flag_str + "\t" + str(flag_freq))
    '''


if __name__ == '__main__':
    #hallo()
    #foo()
    cut_words()