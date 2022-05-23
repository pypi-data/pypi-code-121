import PySimpleGUI as sg
from wiliot.wiliot_testers.tester_utils import *
from wiliot.cloud_apis.management.management import ManagementClient
from math import ceil
from queue import Queue, Empty

BATCH_SIZE = 50
MAX_NUM_TAGS = 6000
MAX_NUM_WORKERS = 50
MAX_RETRIALS = 10
MIN_DELAY_BETWEEN_BATCHES = 0
ENV = ''  # Leave empty for prod


def get_files_path():
    """
    opens GUI for selecting a file and returns it
    """
    # Define the window's contents
    layout = [[sg.Text('choose run_data file that you want to upload:'), sg.Input(),
               sg.FileBrowse(key="run_data_file")],
              [sg.Text('choose tags_data file that you want to upload:'), sg.Input(),
               sg.FileBrowse(key="tags_data_file")],
              [sg.Text('would you like to serialize those tags?'),
               sg.InputCombo(('Yes', 'No'), default_value="Yes", key='serialize')],
              [sg.Text('would you like to upload those files?'),
               sg.InputCombo(('Yes', 'No'), default_value="Yes", key='upload')],
              [sg.Button('Select')]]

    # Create the window
    window = sg.Window('upload and serialize', layout)

    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == 'Select' and (values['run_data_file'] != '' or values['tags_data_file'] != ''):
        window.close()
        return values
    else:
        window.close()
        return None


def serialize_data_from_file():
    values = get_files_path()
    if values is None:
        print('user exited the program')
        return False
    tags_df = {}
    if values['run_data_file'] != '' and not values['run_data_file'].endswith('.csv'):
        print('run_data file format is not csv, please insert a csv file')
        return False
    if values['tags_data_file'] != '' and not values['tags_data_file'].endswith('.csv'):
        print('tags_data file format is not csv, please insert a csv file')
        return False

    batch_name, run_data_csv_name, tags_data_csv_name = None, None, None

    if values['run_data_file'] != '':
        batch_name = values['run_data_file'][:(len(values['run_data_file']) -
                                               len(values['run_data_file'].split("/")[-1]))]
        run_data_csv_name = values['run_data_file'].split('/')[-1]
    if values['tags_data_file'] != '':
        batch_name = values['tags_data_file'][:(len(values['tags_data_file']) -
                                                len(values['tags_data_file'].split("/")[-1]))]
        tags_data_csv_name = values['tags_data_file'].split('/')[-1]
    if batch_name is None:
        print('no files were selected, will exit the program')
        return False

    file_path, user_name, password, owner_id, is_successful = check_user_config_is_ok()

    if values['upload'] == 'Yes':
        upload_to_cloud_api(batch_name=batch_name, tester_type='offline', run_data_csv_name=run_data_csv_name,
                            tags_data_csv_name=tags_data_csv_name, to_logging=False, env='prod', logger_=logging.getLogger().name,
                            is_batch_name_inside_logs_folder=False)

    try:
        tags_df = pd.read_csv(values['tags_data_file'])

    except Exception:
        print('unable to get data from csv')
        return False


    if values['serialize'] == 'Yes':
        batch_num_queued = 0
        management_client = ManagementClient(oauth_username=user_name, oauth_password = password,owner_id = owner_id, env =ENV)
        refresh_thread = refreshTokenPeriodically(security_client = management_client.auth_obj, dt = 14400)
        try:
            # make it to list
            adv_address = []
            packet = []
            serialization_threads_working = []
            next_batch_to_serialization = {'response': '', 'upload_data': []}
            failed_batches = []
            get_new_token = False

            pre_ser_batch_q  = Queue()
            post_ser_batch_q = Queue()
            failed_tags_q    = Queue()

            num_tags = len(tags_df['advAddress'])
            if MAX_NUM_TAGS != 0 and num_tags > MAX_NUM_TAGS:
                num_tags = MAX_NUM_TAGS

            num_batches = ceil(num_tags/BATCH_SIZE)

            num_workers = min(MAX_NUM_WORKERS,ceil(num_batches/5))
            for i in range(num_workers):
                serialization_threads_working.append(serializationWorker( management_client = management_client, input_q = pre_ser_batch_q, output_q = post_ser_batch_q,failed_tags_q = failed_tags_q, max_retrials = MAX_RETRIALS))
                serialization_threads_working[-1].start()
            # serialization part
            failed_tags_counter = 0
            failed_tags_list =[]
            for tag in range(num_tags):
                if tags_df['status'][tag] == 'Failed':
                    failed_tags_list.append(tags_df['externalId'][tag])
                    failed_tags_counter+=1
                    continue
                external_id_tmp = tags_df['externalId'][tag]
                packet_tmp = tags_df['rawData'][tag].split('"')[5]

                adv_address.append(external_id_tmp)
                packet.append(packet_tmp)

                if len(next_batch_to_serialization['upload_data']) == 0:
                    next_batch_to_serialization = {'response': '',
                                                   'upload_data': [{"payload": packet_tmp[16:74],
                                                                    "tagId": external_id_tmp}],
                                                   'writing_lock': threading.Lock()}
                else:
                    next_batch_to_serialization['upload_data'].append({"payload": packet_tmp[16:74],
                                                                       "tagId": external_id_tmp})

                # tag_idx = tag + 1
                if tag % BATCH_SIZE == 0 or tag == num_tags-1:
                    print("Batch {} has Added {} tags for serialization, upload data {}".format(str(batch_num_queued + 1),len(next_batch_to_serialization['upload_data']),next_batch_to_serialization['upload_data']))
                    pre_ser_batch_q.put(next_batch_to_serialization)
                    batch_num_queued += 1
                    next_batch_to_serialization = {'response': '', 'upload_data': []}


            #Status prints:
            max_iterations = 10*num_tags/(BATCH_SIZE*num_workers)
            idle_time = 10
            iter_num = 0
            while post_ser_batch_q.qsize() < batch_num_queued and iter_num<max_iterations:
                time.sleep(10)
                print("After {} seconds: finished {} batches out of {} ({}%)".format(iter_num*idle_time,post_ser_batch_q.qsize(),batch_num_queued,100*post_ser_batch_q.qsize()/batch_num_queued))
                iter_num +=1

        except Exception as e:
            raise ValueError ("Failed serialization with exception {}".format(str(e)))

        finally:
            refresh_thread.stop()
            for i in range(num_workers):
                serialization_threads_working[i].stop()
            #wait for the thread to really stop- sample the event every sample_timeout_dt seconds
            #TODO: change to Q event
            time.sleep(serialization_threads_working[-1].sample_timeout_dt)

            num_ser_batches = 0
            num_ser_tags = 0
            while not post_ser_batch_q.empty():
                curr_batch = post_ser_batch_q.get(timeout = 10) #Should happen...
                num_ser_batches +=1
                num_ser_tags += len(curr_batch["upload_data"])

            # print("Failed to serialize after {} retrials. Error: {}  Upload data:\n {}".format(curr_batch['retrials'],curr_batch['response'],curr_batch['upload_data'] ))
            expected_ser_tags = num_tags-failed_tags_counter
            # pre_ser_batch_q.join() #Wait for all to finish..
            print("Finish serializing {} tags out of {} expected tags (skipped serialization of {} bad tags)\n  Num batches: {} batches (expected {} batches)" \
                  .format(num_ser_tags,expected_ser_tags,failed_tags_counter, num_ser_batches,batch_num_queued ))
            print('Bad tags:')
            print(failed_tags_list)
            success = False
            if num_ser_tags == expected_ser_tags and num_ser_batches == batch_num_queued and failed_tags_q.empty():
                success = True

            else:
                if not failed_tags_q.empty():
                    print(" The following {} tags failed serialization process at the cloud:".format(failed_tags_q.qsize()))
                    while not failed_tags_q.empty():
                        failed_tag = failed_tags_q.get()
                        print(failed_tag)
                if num_ser_tags != expected_ser_tags:
                    print("Error: serialization succeed on all batches, but only {} tags were serialized out of expected {}!!".format(num_ser_tags,expected_ser_tags))
                if num_ser_batches != batch_num_queued:
                    print("Some batches failed to be processed by the cloud:")
                    while not pre_ser_batch_q.empty():
                        curr_batch = pre_ser_batch_q.get()
                        print("Failed to serialize after {} retrials. Error: {}  Upload data:\n {}".format(curr_batch['retrials'],curr_batch['response'],curr_batch['upload_data'] ))
            if not success:
                print("Serialization Failed!! See above errors!!")
            else:
                print("\n\nSerialization of {} tags succeed!!!".format(num_ser_tags))
                
if __name__ == '__main__':
    serialize_data_from_file()
    print("upload_and_serialize_csv_manually is done\n")
