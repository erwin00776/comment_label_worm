__author__ = 'erwin'
#coding=utf-8

import jieba
import codecs
import os


class EmotionDetect:
    '''
    用于生成SVM使用的train和test数据文件格式
    '''
    def __init__(self, work_dir, train_file_name, test_file_name):
        self.work_dir = work_dir
        self.train_file_name = train_file_name
        self.test_file_name = test_file_name
        self.word2index = {}
        self.index2word = []
        self.train_features_size = 0

        self.prepare_data(os.path.join(self.work_dir, self.train_file_name),
                          os.path.join(self.work_dir, self.train_file_name + '.prepared'))
        self.prepare_data(os.path.join(self.work_dir, self.test_file_name),
                          os.path.join(self.work_dir, self.test_file_name + '.prepared'))

    def prepare_data(self, in_name, out_name):
        train_fin = codecs.open(in_name, 'r', encoding='utf-8')
        line_words = []
        for line in train_fin.readlines():
            line = line.rstrip()
            clazz, sentence = line.split()
            words = {'#clazz#': clazz}
            for word in jieba.cut(sentence, cut_all=False):
                if not word in self.word2index:
                    self.word2index[word] = len(self.word2index)
                    self.index2word.append(word)
                count = words.get(word, 0)
                words[word] = count + 1
            line_words.append(words)
        train_fin.close()

        if self.train_features_size == 0:
            self.train_features_size = len(self.index2word)

        train_fout = open(out_name, 'w')
        for words in line_words:
            clazz = words.get('#clazz#', '+1')
            features = []
            for i in range(0, self.train_features_size):
                count = words.get(self.index2word[i], 0)
                features.append("%d:%d" % (i+1, count))
            train_fout.write(clazz + ' ' + ' '.join(features) + "\n")
        train_fout.close()

    def train(self):
        pass

if __name__ == '__main__':
    emotion = EmotionDetect('/Users/erwin/work/comment_labeled', 'emotion_cases', 'emotion_tests')