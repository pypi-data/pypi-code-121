import os, fire, psutil

# from .libs.py_ext import
# 思路:
# 每个命令都有参数，参数是值或文件(文件夹)
# 如果是文件则检查文件是否存在
# 文件夹如果不存在，并创建


class Nasap(object):
  def __init__(self):
    self.root = os.path.abspath( os.path.join(os.path.dirname(__file__)) ) + '/'
    self.libs = self.root + 'libs/'
    self.scripts = self.root + 'scripts/'

  def _check_para(self, name, value, type, isFile=False):
    # 先检查参数的类型，
    # 如果是文件就检查文件是否存在
    # 如果是文件夹就判断文件夹是否存在，不存在就创建
    if not isinstance(value, type):
      print('Error', name, 'should be a', type, 'type.')
      os.sys.exit(0)
    if isFile:
      if not os.path.exists(value):
        print('Error', value, 'not exist!')
        os.sys.exit(0)
    return True

  def _get_cores(self, value):
    total_cores = psutil.cpu_count()
    cur_cores = 1
    if isinstance(value, int):
      if value > total_cores:
        print("warning: your cpu cores number is", total_cores, "we set the parameter cores to", total_cores)
        cur_cores = total_cores
      else:
        cur_cores = value
      return cur_cores
    if isinstance(value, str):
      if str.lower() == 'max':
        cur_cores = total_cores
        return cur_cores
      if str.lower == 'max/2':
        cur_cores = total_cores/2
        return cur_cores
    print("warning: cores parameter error use default cores=1")
    return 1

  def _build_project_path(self, root_dir):
    if not root_dir.endswith('/'): root_dir = root_dir + '/'
    json_dir=root_dir + 'json/'
    fq_dir=root_dir + 'fastq/'
    txt_dir=root_dir + 'txt/'
    img_dir=root_dir + 'imgs/'
    sam_dir=root_dir + 'sam/'
    bed_dir=root_dir + 'bed/'
    bw_dir=root_dir + 'bw/'
    csv_dir=root_dir + 'csv/'
    html_dir=root_dir + 'html/'
    for d in [root_dir, json_dir, fq_dir, txt_dir, img_dir, sam_dir, bed_dir, bw_dir, csv_dir, html_dir]:
      if not os.path.exists(d):
        os.makedirs(d)

  def _check_output(self, root_dir):
    output_subdir = ['json/','fastq/','txt/', 'imgs/','sam/','bed/','bw/', 'html/']

    for sub_dir in output_subdir:
      if not root_dir.endswith('/'): root_dir = root_dir + '/'
      sub_dir = root_dir + sub_dir
      if not os.listdir(sub_dir):
        os.removedirs(sub_dir)

  def all(self, read1=None, bowtie_index=None,  gtf=None, output_root=None, cores=1, read2=None, adapter1=None, adapter2=None):
    preprocess_cmd_list = ['bash', self.scripts + 'preprocess.bash']
    extract_preprocess_cmd_list = ['python', self.scripts + 'extract_preprocess.py']
    map1_cmd_list = ['bash', self.scripts + 'map1.bash']
    map2_cmd_list = ['python', self.scripts + 'map_split.py', '--sam_file=original.sam']
    map3_cmd_list = ['bash', self.scripts + 'map2.bash']
    genome_track_cmd_list = ['bamCoverage', '--binSize', '1']
    feature_assign_cmd_list = ['python', self.scripts + 'feature_attrs.py']
    pausing_sites_cmd_list = ['python', self.scripts + 'pausing_sites.py']

    # 必须参数 参数什么都不加
    if read1 and self._check_para('--read1', read1, str, isFile=True):
      preprocess_cmd_list.extend(['--read1', read1])

    if bowtie_index and self._check_para('--bowtie_index', bowtie_index, str):
      map1_cmd_list.extend(['--bowtie_index', bowtie_index])
      map3_cmd_list.extend(['--bowtie_index', bowtie_index])
    if gtf and self._check_para('--gtf', gtf, str, isFile=True):
      map1_cmd_list.extend(['--gtf', gtf])
      map3_cmd_list.extend(['--gtf', gtf])
      feature_assign_cmd_list.extend(['--gtf', gtf])

    if output_root:
      if not output_root.endswith('/'): output_root = output_root +'/'
      preprocess_cmd_list.extend(['--output_root', output_root])
      extract_preprocess_cmd_list.append(output_root)
      map1_cmd_list.extend(['--output_root', output_root])
      map1_cmd_list.extend(['--read1', output_root + 'fastq/clean_read1.fq.gz'])
      map2_cmd_list.append('--sam_dir='+output_root+'sam/')
      map3_cmd_list.extend(['--output_root', output_root])
      map3_cmd_list.extend(['--read1', output_root + 'fastq/clean_read1.fq.gz'])
      genome_track_cmd_list.extend(['--bam', output_root + 'sam/uniquemapped_sort.bam'])
      feature_assign_cmd_list.extend(['--forward_bw', output_root + 'bw/forward.bw'] )
      feature_assign_cmd_list.extend(['--reverse_bw', output_root + 'bw/reverse.bw'] )
      feature_assign_cmd_list.extend(['--output_root', output_root])
      pausing_sites_cmd_list.extend(['--forward_bw', output_root + 'bw/forward.bw'] )
      pausing_sites_cmd_list.extend(['--reverse_bw', output_root + 'bw/reverse.bw'] )
      pausing_sites_cmd_list.extend(['--output_root', output_root])
    if cores:
      cur_cores = str( self._get_cores(cores) )
      preprocess_cmd_list.extend(['--cores', cur_cores])
      map1_cmd_list.extend(['--cores', cur_cores])
      map3_cmd_list.extend(['--cores', cur_cores])
      genome_track_cmd_list.extend(['-p', cur_cores])
      pausing_sites_cmd_list.extend(['--cores', cur_cores])

    # 可选参数
    if read2 and self._check_para('--read2', read2, str, isFile=True):
      preprocess_cmd_list.extend(['--read2', read2])
      clean_read2=output_root + 'fastq/clean_read2.fq.gz'
      map1_cmd_list.extend(['--read2', clean_read2])
      map3_cmd_list.extend(['--read2', clean_read2])
    if adapter1 and self._check_para('--adapter1', adapter1, str):
      preprocess_cmd_list.extend(['--adapter1', adapter1])
    if adapter2 and self._check_para('--adapter2', adapter2, str):
      preprocess_cmd_list.extend(['--adapter2', adapter2])

    foward_genome_track_cmd_list, reverse_genome_track_cmd_list = genome_track_cmd_list.copy(), genome_track_cmd_list.copy()
    foward_genome_track_cmd_list.extend(['--filterRNAstrand', 'forward'])
    reverse_genome_track_cmd_list.extend(['--filterRNAstrand', 'reverse'])
    foward_genome_track_cmd_list.extend(['-o', output_root + 'bw/forward.bw'])
    reverse_genome_track_cmd_list.extend(['-o', output_root + 'bw/reverse.bw'])

    all_steps = [preprocess_cmd_list, extract_preprocess_cmd_list, map1_cmd_list, map2_cmd_list, map3_cmd_list,
    foward_genome_track_cmd_list, reverse_genome_track_cmd_list, pausing_sites_cmd_list]
    self._build_project_path(output_root)
    for cmd_list in all_steps:
      os.system( ' '.join(cmd_list) )
      # print( ' '.join(cmd_list) )

    # self._check_output(output_root)

  def preprocess(self, read1=None, output_root=None, cores=1, read2=None, adapter1=None, adapter2=None, umi=None):
    cmd_list = ['bash', self.scripts + 'preprocess.bash']
    # 必须参数 参数什么都不加
    if read1 and self._check_para('--read1', read1, str, isFile=True):
      cmd_list.extend(['--read1', read1])
    if not output_root.endswith('/'):
      output_root = output_root + '/'
    self._build_project_path(output_root)
    cmd_list.extend(['--output_root', output_root])
    if cores:
      cur_cores = self._get_cores(cores)
      cmd_list.extend(['--cores', str(cur_cores)])

    # 可选参数
    if read2 and self._check_para('--read2', read2, str, isFile=True):
      cmd_list.extend(['--read2', read2])
    if adapter1 and self._check_para('--adapter1', adapter1, str):
      cmd_list.extend(['--adapter1', adapter1])
    if adapter2 and self._check_para('--adapter2', adapter2, str):
      cmd_list.extend(['--adapter2', adapter2])

    # print( ' '.join(cmd_list) )
    os.system( ' '.join(cmd_list) )
    # extract preprocess
    os.system( ' '.join(['python', self.scripts + 'extract_preprocess.py', output_root]) )


  def alignment(self, read1=None, bowtie_index=None, gtf=None, output_root=None, cores=1, read2=None ):
    cmd_list = ['bash', self.scripts + 'map1.bash']
    if read1 and self._check_para('--read1', read1, str, isFile=True):
      cmd_list.extend(['--read1', read1])
    if bowtie_index and self._check_para('--bowtie_index', bowtie_index, str):
      cmd_list.extend(['--bowtie_index', bowtie_index])
    if gtf and self._check_para('--gtf', gtf, str, isFile=True):
      cmd_list.extend(['--gtf', gtf])
    if not output_root.endswith('/'):
      output_root = output_root + '/'
    self._build_project_path(output_root)
    cmd_list.extend(['--output_root', output_root])
    if cores:
      cur_cores = self._get_cores(cores)
      cmd_list.extend(['--cores', str(cur_cores)])

    if read2 and self._check_para('--read2', read2, str, isFile=True):
      cmd_list.extend(['--read2', read2])

    os.system( ' '.join(cmd_list) )
    os.system( ' '.join(['python', self.scripts + 'map_split.py',
    '--sam_dir='+output_root+'sam/', '--sam_file=original.sam'
    ]) )
    cmd_list[1] = self.scripts + 'map2.bash'
    os.system( ' '.join(cmd_list) )


  def genome_tracks(self, bam=None, output_root=None, cores=1):
    cmd_list = ['bamCoverage']
    if bam and self._check_para('--bam', bam, str, isFile=True):
      cmd_list.extend(['--bam', bam])
    cmd_list.extend(['--binSize', '1'])
    if cores:
      cur_cores = self._get_cores(cores)
      cmd_list.extend(['-p', str(cur_cores)])
    if not output_root.endswith('/'):
      output_root = output_root + '/'
    self._build_project_path(output_root)

    cmd_list_forward, cmd_list_reverse = cmd_list.copy(), cmd_list.copy()
    cmd_list_forward.extend(['--filterRNAstrand', 'forward'])
    cmd_list_reverse.extend(['--filterRNAstrand', 'reverse'])
    cmd_list_forward.extend(['-o', output_root + 'bw/forward.bw'])
    cmd_list_reverse.extend(['-o', output_root + 'bw/reverse.bw'])
    os.system( ' '.join(cmd_list_forward) )
    os.system( ' '.join(cmd_list_reverse) )

  def feature_assign(self, forward_bw=None, reverse_bw=None, gtf=None, output_root=None):
    cmd_list = ['python', self.scripts + 'feature_attrs.py']
    if forward_bw and self._check_para('--forward_bw', forward_bw, str, isFile=True):
      cmd_list.extend(['--forward_bw', forward_bw])
    if reverse_bw and self._check_para('--reverse_bw', reverse_bw, str, isFile=True):
      cmd_list.extend(['--reverse_bw', reverse_bw])
    if gtf and self._check_para('--gtf', gtf, str, isFile=True):
      cmd_list.extend(['--gtf', gtf])
    if not output_root.endswith('/'): output_root = output_root + '/'
    self._build_project_path(output_root)
    cmd_list.extend(['--output_root', output_root])

    os.system( ' '.join(cmd_list) )

  def pausing_sites(self, forward_bw=None, reverse_bw=None, output_root=None, cores=1):
    cmd_list = ['python', self.scripts + 'pausing_sites.py']
    if forward_bw and self._check_para('--forward_bw', forward_bw, str, isFile=True):
      cmd_list.extend(['--forward_bw', forward_bw])
    if reverse_bw and self._check_para('--reverse_bw', reverse_bw, str, isFile=True):
      cmd_list.extend(['--reverse_bw', reverse_bw])
    if not output_root.endswith('/'): output_root = output_root + '/'
    self._build_project_path(output_root)
    cmd_list.extend(['--output_root', output_root])
    if cores:
      cur_cores = self._get_cores(cores)
      cmd_list.extend(['--cores', str(cur_cores)])

    os.system( ' '.join(cmd_list) )

  def network_analysis(self, regulatory_source=None, attribute_file=None, output_root=None ):
    try:
      import networkx as nx
    except:
      print( 'import networkx error.')
      print( 'you need to install networkx with the command "pip install networkx"')
      os.sys.exit(1)

    try:
      from community import community_louvain
    except:
      print( 'import community error.' )
      print( 'you need to install community with the command "pip install python-louvain community"')
      os.sys.exit(1)

    try:
      import hvplot.networkx as hvnx
    except:
      print( 'import hvplot error.' )
      print( 'you need to install hvplot with the command "pip install hvplot"')
      os.sys.exit(1)


    cmd_list = ['python', self.scripts + 'network_analysis.py']
    if regulatory_source and self._check_para('--regulatory_source', regulatory_source, str, isFile=True):
      cmd_list.extend(['--regulatory_source', regulatory_source])
    if attribute_file and self._check_para('--attribute_file', attribute_file, str, isFile=True):
      cmd_list.extend(['--attribute_file', attribute_file])
    if not output_root.endswith('/'): output_root = output_root + '/'
    self._build_project_path(output_root)
    cmd_list.extend(['--output_root', output_root])

    os.system( ' '.join(cmd_list) )

def main():
  fire.Fire(Nasap)

if __name__ == '__main__':
  main()