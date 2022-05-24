from miacag.utils.sql_utils import getDataFromDatabase
import seaborn as sns
import argparse
parser = argparse.ArgumentParser(
    description='Define data['inputs'] for building database.')
parser.add_argument(
            '--query', type=str,
            help='query for retrieving data',
            required=True)
parser.add_argument(
    '--database', type=str,
    help="database name")
parser.add_argument(
    '--username', type=str,
    help="username for database")
parser.add_argument(
    '--password', type=str,
    help="password for database")
parser.add_argument(
    '--host', type=str,
    help="host for database")
parser.add_argument(
    '--port', type=str,
    help="port for database")
parser.add_argument(
    '--table_name', type=str,
    help="table_name in database")



if __name__ == '__main__':
    args = parser.parse_args()

    sql_config = {'database':
                  args.database,
                  'username':
                  args.username,
                  'password':
                  args.password,
                  'host':
                  args.host,
                  'port':
                  args.port,
                  'table_name':
                  args.table_name,
                  'query':
                  args.query
                  }
    df, connection = getDataFromDatabase(sql_config)
    df = df[["PositionerPrimaryAngle", "PositionerSecondaryAngle", "DistanceSourceToPatient", "DistanceSourceToDetector", self.config["labels_names"]]]
    map_dict = {0: "LCA",
                1: "RCA"}
    df[self.config["labels_names"]] = df[self.config["labels_names"]].map(map_dict)
    g = sns.PairGrid(df, hue=self.config["labels_names"])
    g.map_diag(sns.histplot)
    g.map_offdiag(sns.scatterplot)
    g.add_legend()
    g.figure.savefig("output.png")

    sns.scatterplot(
        data=df,
        x="PositionerPrimaryAngle",
        y="PositionerSecondaryAngle",
        hue=self.config["labels_names"])
    g.figure.savefig("angles.png")
