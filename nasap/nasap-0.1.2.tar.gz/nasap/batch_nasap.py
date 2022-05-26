import os, fire, psutil

class BatchNasap(object):
  def _run_batch_cmd(self, para_dic, cmd_list):
    filter_para_dic = {k:v for k, v in para_dic.items() if v}
    for k, v in filter_para_dic.items():
      if k == 'self': continue
      if k == 'read_file': continue
      cmd_list.extend(['--'+k, str(v)])
    os.system( ' '.join(cmd_list))
    # print( ' '.join(cmd_list) )

  def all(self, read_file=None, bowtie_index=None,  gtf=None, output_root=None, cores=1, adapter1=None, adapter2=None):
    all_para_dic = locals()

    for read_ln in open(read_file):
      para_dic = all_para_dic.copy()
      if ',' in read_ln:
        para_dic['read1'] = read_ln.split(',')[0].strip()
        para_dic['read2'] = read_ln.split(',')[1].strip()
      else:
        para_dic['read1'] = read_ln.strip()
      self._run_batch_cmd(para_dic , ['nasap', 'all'] )

def main():
  fire.Fire(BatchNasap)

if __name__ == '__main__':
  main()