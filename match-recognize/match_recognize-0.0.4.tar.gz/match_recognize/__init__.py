import numpy as np
import pandas as pd
import operator
import warnings
warnings.filterwarnings('ignore')
from automata.fa.nfa import NFA



class match_recognize:
    
    def partition_handling(self, text):
        start = "PARTITION BY "
        end = "\n"
        grouping = text[text.find(start)+len(start):text.rfind(end)].split('\n')[0]
        grouping_list = grouping.split(",")
        grouping_list = [i.strip() for i in grouping_list]
        return grouping_list
    
    def order_handling(self, text):
        start = "ORDER BY "
        end = "\n"
        ordering = text[text.find(start)+len(start):text.rfind(end)].split('\n')[0]
        ordering_list = ordering.split(",")
        ordering_list = [i.strip() for i in ordering_list]
        return ordering_list
    
    def define_handling(self, text):
        start = "DEFINE"
        end = ")"
        txt = text[text.find(start)+len(start):text.rfind(end)]
        txt = txt.replace("\n", "")
        txt = txt.replace("   ", "")
        txt = txt.replace("  ", "")
        txt = txt.replace("\t", "")
        txt_list = txt.split(",")
        return txt_list
    
    def definition_splitting(self, define_text):
        dict_ = {}
        for i in define_text:
            key_ = i.split('AS')[0].lstrip()
            value_ = i.split('AS')[1].lstrip()
            dict_[key_]=value_
        return dict_
    
    def splitting_define(self, text):
        before_ = text[text.find('')+len(''):text.rfind(self.check_operand(text))].replace(" ", "")
        operand_ = self.check_operand(text)
        after_caluse= text[text.find(self.check_operand(text))+len(self.check_operand(text)):text.rfind('')].replace(" ", "")
        after_ = after_caluse[after_caluse.find('(')+len('('):after_caluse.rfind(')')].replace(")", "")
        return before_, operand_, after_
    
    def check_operand(self, text):
        final_operand = ''
        if text.find('<') != -1:
            return '<'
        elif text.find('<=') != -1:
            return '<='
        elif text.find('>') != -1:
            return '>'
        elif text.find('>=') != -1:
            return '>='
        elif text.find('=') != -1:
            return '='
        elif text.find('!=') != -1:
            return '!='
        else:
            print('error in check_operand')
    
    def get_truth(self, inp, relate, cut):
        ops = {'>': operator.gt,
               '<': operator.lt,
               '>=': operator.ge,
               '<=': operator.le,
               '=': operator.eq,
               '!=': operator.ne}
        return ops[relate](inp, cut)


    def prev_handling(self, df, column1_, operator_, column2_):
        a = []
        for i, row in df.iterrows():
            if(i != 0):
                a.append(df.loc[i] if self.get_truth(row[column1_], operator_, df.iloc[i-1][column2_]) else None)
        return pd.DataFrame([i for i in a if i is not None], columns = df.columns.tolist()).reset_index(drop = True)
    def numeric_handling(self, df, column1_, operator_, value_):
        a = []
        for i, row in df.iterrows():
            if(i != 0):
                a.append(df.loc[i] if self.get_truth(row[column1_], operator_, int(value_)) else None)
        return pd.DataFrame([i for i in a if i is not None], columns = df.columns.tolist()).reset_index(drop = True)

    def assembly_func(self, txt, df):
        df_ = df
        dict_ = {}
        text = self.definition_splitting(self.define_handling(txt))
        for keys, values in text.items():
          if('prev' in values.lower()):
              column1_, operator_, column2_ = self.splitting_define(values)
              df1 = self.prev_handling(df_, column1_, operator_, column2_)
              dict_[keys] = df1
          else:
              column1_, operator_, value_ = values.split(" ")
              df1 = self.numeric_handling(df_, column1_, operator_, value_)
              dict_[keys] = df1
        return dict_
    
    def dictionary_creation(self, df, txt):
        firsts_ = {}
        lasts_ = {}
        dictionary_ = self.assembly_func(txt, df)
        for keys, values in dictionary_.items():
            up_first = pd.DataFrame(columns = df.columns)
            up_last = pd.DataFrame(columns = df.columns)
            for i in range(len(values)):
                if i == 0:
                    up_first = up_first.append(values.iloc[i])
                elif i == len(values)-1:
                    up_last = up_last.append(values.iloc[i])
                else:
                    if values[df.columns[0]][i]-1 != values[df.columns[0]][i-1]:
                        up_first = up_first.append(values.iloc[i])
                        up_last = up_last.append(values.iloc[i-1])
            firsts_[keys] = up_first.reset_index(drop = True)
            lasts_[keys] = up_last.reset_index(drop = True)
        return firsts_, lasts_, dictionary_
    
    def MEASURES_handling(self,text):
        start = "MEASURES"
        end = "PATTERN"
        txt = text[text.find(start)+len(start):text.rfind(end)].split(",")
        txt_list = [i.strip() for i in txt]
        return txt_list
    
    def expression_detection(self,txt):
        txt[txt.find("PATTERN")+len("PATTERN"):txt.rfind(")")]
        l = (txt.split("PATTERN ("))[1].split(")")[0].strip().split(" ")
        star_list = [i.strip()[:-1] for i in l if '*' in i]
        plus_list = [i.strip()[:-1] for i in l if '+' in i]
        return star_list, plus_list
    
    def match_final(self, df,txt):
        firsts_, lasts_, dictionary_ = self.dictionary_creation(df, txt)
        data_length = min([len(lasts_[keys]) for keys, values in dictionary_.items()])
        col = [val.split(" ")[-1] for val in [i.strip() for i in self.MEASURES_handling(txt)]]        
        star_list, plus_list = self.expression_detection(txt)
        [val[val.find(" AS ")+len(" AS "):val.rfind("")] for val in self.MEASURES_handling(txt)]
        partitioning = self.partition_handling(txt)
        output_ = pd.DataFrame(columns = partitioning+col)
        ordering = self.order_handling(txt)
        for i in self.MEASURES_handling(txt):
            val = i
            first_ = pd.DataFrame(columns = df.columns)
            last_ = pd.DataFrame(columns = df.columns)
            for keys, values in dictionary_.items():
                lasts_[keys] = lasts_[keys][:data_length].reset_index(drop = True)
                firsts_[keys] = firsts_[keys][:data_length].reset_index(drop = True)
                values = values.sort_values(by = ordering).reset_index(drop = True)
                if(keys.strip() in plus_list):
                    if i.find(keys.strip()) != -1 and val[val.find("")+len(""):val.rfind("(")].lower() == 'last':
                      output_[val[val.find(" AS ")+len(" AS "):val.rfind("")]] = lasts_[keys][val[val.find(".")+len("."):val.rfind(")")]].tolist()
                    if i.find(keys.strip()) != -1 and val[val.find("")+len(""):val.rfind("(")].lower() == 'first':
                      output_[partitioning] = firsts_[keys][partitioning].reset_index(drop = True)
                      # print('CHECK HERE!!!!!!!', [i for i in col if i != val[val.find(" AS ")+len(" AS "):val.rfind("")]])
                      # print('val[val.find(" AS ")+len(" AS "):val.rfind("")]', val[val.find(" AS ")+len(" AS "):val.rfind("")])
                      output_[val[val.find(" AS ")+len(" AS "):val.rfind("")]] = firsts_[keys][val[val.find(".")+len("."):val.rfind(")")]].tolist()
                      # print('CHECK HERE!!!!', [i for i in col if i in firsts_[keys].columns]) 
                      # missing_ = [i for i in col if i in firsts_[keys].columns][0]
                      # print(first_[keys][missing_])
                      # output_[[i for i in col if i in firsts_[keys].columns]] = first_[keys][missing_]\
        output_ = output_[output_[col[0]] > output_[col[-1]]]
        output_ = output_[partitioning+col]
        return output_

    def select_handling(self, txt):
      start = "SELECT"
      end = "FROM"
      grouping = txt[txt.find(start)+len(start):txt.rfind(end)].split(",")
      grouping_list = list(map(str.strip,grouping))
      return grouping_list
    
    def match_recognize(self, df, txt):
        act_output = self.match_final(df, txt)
        if(self.select_handling(txt)[0] != '*'):
          # print('[self.select_handling(txt)]: ', [self.select_handling(txt)])
          act_output = act_output[self.select_handling(txt)]
        else:
          act_output = act_output
        return act_output
    
    def match_automata(self, txt, txt_):
        dicto = {}
        pattern_ = (txt.split("PATTERN ("))[1].split(")")[0].strip().split(" ")
        pattern_ = [i[:-1] for i in pattern_]
        pattern_rep = [chr(ord('`')+i+1) for i in range(len(pattern_))]
        reps_ = [i[:-1] for i in txt_.split(" ")]
        star_list, plus_list = self.expression_detection(txt)
        nfa_string = [pattern_rep[i] for i in range(len(pattern_)) if pattern_[i] in reps_]
        star_list_ = [pattern_rep[i] for i in range(len(pattern_)) if pattern_[i] in star_list]
        plus_list_ = [pattern_rep[i] for i in range(len(pattern_)) if pattern_[i] in plus_list]
        set_ = set([ f'q{i}' for i in range(len(set(star_list + plus_list)))])
        qs = list(set_)
        qs.sort()
        subdict = {}
        for i in range(len(qs)):
            if(i != len(qs)-1):
              if(pattern_rep[i+1] in plus_list_):
                dicto[qs[i]] = {pattern_rep[i]: {qs[i]}, pattern_rep[i+1]: {qs[i+1]}}
              else:
                dicto[qs[i]] = {pattern_rep[i]: {qs[i]}, pattern_rep[i+1]: {qs[i+2]}}
            else:
              dicto[qs[i]] = {pattern_rep[i]: {qs[i]}}
        
        nfa = NFA(
            states=set([ f'q{i}' for i in range(len(set(star_list + plus_list))+1)]),
            input_symbols=set(pattern_rep),
            transitions= dicto
            ,
            initial_state=qs[0],
            final_states={qs[-1]}
        )
        quantifier_validation = [x for x in [i[:-1] for i in txt_.split(" ") if i[-1] == '*'] if x in plus_list]
        if (len(quantifier_validation) == 0) & (pattern_ == reps_) & (nfa.accepts_input(nfa_string)):
            return 'accepted'
        else:
            return 'rejected'