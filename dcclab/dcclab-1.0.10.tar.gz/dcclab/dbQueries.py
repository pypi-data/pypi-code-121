from dcclab import Database
import os


if __name__ == '__main__':
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, 'database', 'mtp.bd')
    database = Database(path)
    database.connect()

    print('Proceeding to the query : "mCher"')
    select = database.select('cziChannels', 'channel_id', 'channel_name="mCher"')
    with open(os.path.join(directory, 'tests', 'query_mCher.csv'), 'w', encoding='UTF-8') as file:
        for line in select:
            file.write('{}\n'.format(line['channel_id']))

    print('Proceeding to the query : "DAPI"')
    select = database.select('cziChannels', 'channel_id', 'channel_name="DAPI"')
    with open(os.path.join(directory, 'tests', 'query_dapi.csv'), 'w', encoding='UTF-8') as file:
        for line in select:
            file.write('{}\n'.format(line['channel_id']))

    print('Proceeding to the query : "EGFP"')
    select = database.select('cziChannels', 'channel_id', 'channel_name="EGFP"')
    with open(os.path.join(directory, 'tests', 'query_egfp.csv'), 'w', encoding='UTF-8') as file:
        for line in select:
            file.write('{}\n'.format(line['channel_id']))
    print('Done!')
