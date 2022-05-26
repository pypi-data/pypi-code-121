#!/usr/bin/python3
import argparse
from gitlab_ps_utils.api import GitLabApi
from gitlab_evaluate.migration_readiness.report_generator import ReportGenerator
from gitlab_evaluate.lib import api as api_helpers
import logging


def main():
  logging.basicConfig(filename='evaluate.log', level=logging.DEBUG)
  parser = argparse.ArgumentParser()
  parser.add_argument("-t", "--token", help="Personal Access Token: REQ'd")
  parser.add_argument("-s", "--source", help="Source URL: REQ'd")
  parser.add_argument("-f", "--filename", help="CSV Output File Name. If not set, will default to 'evaluate_output.csv'")
  parser.add_argument("-o", "--output", action='store_true', help="Output Per Project Stats to screen")
  parser.add_argument("-i", "--insecure", action='store_true', help="Set to ignore SSL warnings.")
  parser.add_argument("-p", "--processes", help="Number of processes. Defaults to number of CPU cores")

  args = parser.parse_args()

  if None not in (args.token, args.source):
    processes = args.processes if args.processes else None

    app_api_url = "/application/statistics"
    app_ver_url = "/version"
    source = args.source
    
    if args.insecure:
      gitlabApi = GitLabApi(ssl_verify=False)
      api_helpers.gl_api.ssl_verify=False
    else:
      gitlabApi = GitLabApi()

    rg = ReportGenerator(source, args.token, filename=args.filename, output_to_screen=args.output, api=gitlabApi, processes=processes)

    if resp := api_helpers.getApplicationInfo(source,args.token,app_api_url):
      rg.write_line_to_file('-' * 50)
      rg.write_line_to_file(f'Basic information from source: {source}')
      # print("Status code:", 
      rg.write_line_to_file(f"Total Merge Requests: {resp.get('merge_requests')}")
      rg.write_line_to_file(f"Total Projects: {resp.get('projects')}")
      rg.write_line_to_file(f"Total Archived Projects: {api_helpers.getArchivedProjectCount(source,args.token)}")
      rg.write_line_to_file(f"total Forks: {resp.get('forks')}")
      rg.write_line_to_file('-' * 50)
    else:
      print(f"Unable to pull application info from URL: {source}")

    if resp := api_helpers.getVersion(source, args.token , app_ver_url):
      rg.write_line_to_file('-' * 50)
      rg.write_line_to_file(f"GitLab Source Ver: {resp.get('version')}")
      rg.write_line_to_file('-' * 50)
    else:
      print(f"Unable to pull application info from URL: {source}")
    

    rg.handle_getting_data()
      
  else:
    parser.print_help()

