from .build_dataset import FakeDataset

import torch
import os


class HANDataset(FakeDataset):
    def __init__(self, tokenizer, max_word_len, max_sent_len, saved_data_path=False):
        super(HANDataset, self).__init__(tokenizer=tokenizer)

        self.max_word_len = max_word_len
        self.max_sent_len = max_sent_len

        # load data
        self.saved_data_path = saved_data_path

    def transform(self, title, text):
        sent_list = [title] + text

        sent_list = sent_list[:self.max_sent_len]
        doc = [self.tokenizer.encode(sent)[:self.max_word_len] for sent in sent_list] 
        
        doc = self.padding(doc)

        doc = {'input_ids':torch.tensor(doc)}

        return doc
    
    def padding(self, doc):
        num_pad_doc = self.max_sent_len - len(doc)
        num_pad_sent = [max(0, self.max_word_len - len(sent)) for sent in doc]

        doc = [sent + [self.tokenizer.pad_token_id] * num_pad_sent[idx] for idx, sent in enumerate(doc)]
        doc = doc + [[self.tokenizer.pad_token_id] * self.max_word_len for i in range(num_pad_doc)]
            
        return doc

    def __getitem__(self, i):

        if self.saved_data_path:
            doc = {}
            for k in self.data['doc'].keys():
                doc[k] = self.data['doc'][k][i]

            label = self.data['label'][i]

            return doc, label
        
        else:
            news_idx = self.data_info.iloc[i]
            news_info = self.data[news_idx['filename']]
        
            # label
            label = 1 if news_idx['label']=='fake' else 0
        
            # transform and padding
            doc = self.transform(
                title = news_info['sourceDataInfo']['newsTitle'], 
                text  = news_info['sourceDataInfo']['newsContent'].split('\n')
            )

            return doc, label


    def __len__(self):
        if self.saved_data_path:
            return len(self.data['doc']['input_ids'])
        else:
            return len(self.data)

