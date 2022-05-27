import requests
import traceback
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
import datetime
import json
import time
from time import mktime
import sys


class Zermelo():
    # For documentation see: https://wartburg.zportal.nl/static/swagger/ & https://zermelo.atlassian.net/wiki/display/DEV/API+Entities
    def __init__(self, customer, token, storage_location, initial_zermelo_extract=False, extract_cancelled=True):
        """
        Extracts data from source based on the entered parameters
        :param customer: indicates the customer
        :param token: gives access to customer data
        :param storage_location: indicates the location where the extracted data file is saved
        :param initial_zermelo_extract: store the extract as a delta file (true) or not (false)
        :param cancelled_appointments: doesn't get the cancelled appointments by default. Can be changed to an empty string to get the cancelled appointments
        """
        api_version = 3
        self.url = 'https://{0}.zportal.nl/api/v{1}/'.format(customer, api_version)
        self.access_token = token
        self.storage_location = storage_location
        self.initial_zermelo_extract = initial_zermelo_extract
        if extract_cancelled:
            self.cancelled_appointments = ''
        else:
            self.cancelled_appointments = '&cancelled=false'

    def run_all_extracts(self):
        # The following endpoints are delivering such huge amounts of data, that these one should be splitted in seperate schoolyears
        start_of_data = datetime.date(year=datetime.datetime.today().year, month=8, day=1).timetuple()
        # end_of_data = datetime.date.today().timetuple()
        end_of_data = datetime.date(year=datetime.datetime.today().year + 2, month=8, day=1).timetuple()
        if self.initial_zermelo_extract:
            for i in range(1, 7):
                start_of_data = datetime.date(year=datetime.datetime.today().year - i, month=8, day=1).timetuple()
                end_of_data = datetime.date(year=datetime.datetime.today().year - i + 1, month=7, day=31).timetuple()
                # self.get_zermelo_substituded_lessons(endpoint='substitutedlessons', fields=['contract', 'employee', 'appointment', 'start', 'end', 'changeDescription', 'appointmentInstance'],
                #                                      startdate=start_of_data, enddate=end_of_data)
                self.get_zermelo_appointments(endpoint='appointments', fields=['id', 'start', 'end', 'type', 'remark', 'valid', 'cancelled', 'modified',
                                                                               'moved', 'changeDescription', 'branch', 'branchOfSchool', 'created', 'lastModified',
                                                                               'hidden', 'appointmentInstance', 'new', 'teachers', 'students', 'subjects', 'groups',
                                                                               'locations', 'locationsOfBranch', 'groupsInDepartments'],
                                              startdate=start_of_data, enddate=end_of_data)
        elif datetime.datetime.today().month <= 7:
            start_of_data = datetime.date(year=datetime.datetime.today().year - 1, month=8, day=1).timetuple()
            # end_of_data = datetime.date.today().timetuple()
            end_of_data = datetime.date(year=datetime.datetime.today().year + 1, month=8, day=1).timetuple()
            # self.get_zermelo_substituded_lessons(endpoint='substitutedlessons', fields=['contract', 'employee', 'appointment', 'start', 'end', 'changeDescription', 'appointmentInstance'],
            #                                      startdate=start_of_data, enddate=end_of_data)
            self.get_zermelo_appointments(endpoint='appointments', fields=['id', 'start', 'end', 'type', 'remark', 'valid', 'cancelled', 'modified',
                                                                           'moved', 'changeDescription', 'branch', 'branchOfSchool', 'created', 'lastModified',
                                                                           'hidden', 'appointmentInstance', 'new', 'teachers', 'students', 'subjects', 'groups',
                                                                           'locations', 'locationsOfBranch', 'groupsInDepartments'],
                                          startdate=start_of_data, enddate=end_of_data)
        else:
            # self.get_zermelo_substituded_lessons(endpoint='substitutedlessons', fields=['contract', 'employee', 'appointment', 'start', 'end', 'changeDescription', 'appointmentInstance'],
            #                                      startdate=start_of_data, enddate=end_of_data)
            self.get_zermelo_appointments(endpoint='appointments', fields=['id', 'start', 'end', 'type', 'remark', 'valid', 'cancelled', 'modified',
                                                                           'moved', 'changeDescription', 'branch', 'branchOfSchool', 'created', 'lastModified',
                                                                           'hidden', 'appointmentInstance', 'new', 'teachers', 'students', 'subjects', 'groups',
                                                                           'locations', 'locationsOfBranch', 'groupsInDepartments'],
                                          startdate=start_of_data, enddate=end_of_data)

        self.get_zermelo(endpoint='branches', fields=['code', 'name'])
        self.get_zermelo(endpoint='branchesofschools', fields=['id', 'schoolInSchoolYear', 'branch', 'name'])
        self.get_zermelo(endpoint='choosableindepartments', fields=['id', 'subject', 'departmentOfBranch', 'departmentOfBranchCode', 'sectionOfBranch', 'clockHoursPerLesson', 'teachingLevelManually',
                                                                    'teachingLevel', 'subjectType', 'subjectCode', 'subjectName', 'scheduleCode', 'subjectScheduleCode', 'lessonDemand', 'lessonHoursInClassPeriods'],
                         nested=True, nested_fields=['lessonHoursInClassPeriods'])
        self.get_zermelo(endpoint='classperiods', fields=['id', 'name', 'schoolInSchoolYear', 'weeks'], nested=True, nested_fields=['weeks'])
        self.get_zermelo(endpoint='contracts', fields=['id', 'start', 'end', 'employee', 'defaultFunctionCategory', 'teacherTeam', 'clockHoursGeneralTasks', 'clockHoursGeneralTasksManually',
                                                       'clockHoursTasks', 'clockHoursProfessionalDevelopmentManually', 'clockHoursProfessionalDevelopment', 'clockHoursNet', 'lessonsMax', 'type',
                                                       'yearFraction', 'fteYearLeave', 'ftePermanent', 'fteTemporary', 'fteNet', 'clockHoursGross', 'clockHoursBalance', 'clockHoursLessonsMax',
                                                       'lessonReducingTasks', 'taskSpace', 'taskBalance', 'lessonSpace', 'mainBranchOfSchool', 'school', 'schoolName', 'schoolYear', 'firstName',
                                                       'lastName', 'prefix', 'clockHoursLessons'])
        self.get_zermelo(endpoint='departmentsofbranches', fields=['id', 'code', 'yearOfEducation', 'branchOfSchool', 'clockHoursPerLesson', 'schoolInSchoolYearId', 'schoolInSchoolYearName', 'studentCount', 'prognosticStudentCount'])
        self.get_zermelo(endpoint='employees', fields=['userCode', 'commencementTeaching', 'commencementSchool', 'prefix', 'gender', 'dateOfBirth', 'firstName', 'lastName', 'street', 'houseNumber', 'postalCode', 'city'])
        self.get_zermelo(endpoint='groups', fields=['id', 'code'])
        self.get_zermelo(endpoint='groupindepartments', fields=['id', 'departmentOfBranch', 'name', 'isMainGroup', 'isMentorGroup', 'extendedName'])
        self.get_zermelo(endpoint='holidays', fields=['id', 'schoolInSchoolYear', 'name', 'start', 'end'])
        self.get_zermelo(endpoint='jobs', fields=['id', 'contract', 'functionCategory', 'employmentType', 'start', 'end', 'fteReal', 'fteManually', 'fte', 'type', 'employee', 'clockHoursGross'])
        self.get_zermelo(endpoint='jobextensions', fields=['id', 'contract', 'start', 'end', 'fteReal', 'lessonsAndTasks', 'total', 'employee', 'fte', 'generalTasks', 'professionalDevelopment', 'personalBudget'])
        self.get_zermelo(endpoint='leaves', fields=['id', 'contract', 'leaveType', 'leaveTypeName', 'start', 'end', 'total', 'leaveApproved', 'employee', 'fteReal'])
        self.get_zermelo(endpoint='leavetypes', fields=['id', 'name', 'fixed', 'affectsPersonalBudget'])
        self.get_zermelo(endpoint='locations', fields=['code'])
        self.get_zermelo(endpoint='locationofbranches', fields=['id', 'name', 'parentteachernightCapacity', 'courseCapacity', 'branchOfSchool'])
        self.get_zermelo(endpoint='plannedlessons', fields=['id', 'clockHoursPerLesson', 'clockHoursPerLessonManually', 'plannedGroups', 'lessonDemand', 'branchOfSchool', 'departmentOfBranches',
                                                            'lessonHoursInClassPeriods', 'subjects', 'sectionOfBranches', 'maxTeachingLevel', 'regularTeachingAssignments',
                                                            'prognosticStudentsPerTeacherCount', 'expectedTeacherCount', 'privateComment', 'publicComment'],
                         nested=True, nested_fields=['plannedGroups', 'departmentOfBranches', 'subjects', 'sectionOfBranches', 'regularTeachingAssignments', 'lessonHoursInClassPeriods'])
        self.get_zermelo(endpoint='plannedgroups', fields=['id', 'choosableInDepartment', 'groupInDepartment', 'teachingLevel', 'subjectCode', 'groupInDepartmentName',
                                                           'groupInDepartmentIsMainGroup', 'groupInDepartmentIsMentorGroup', 'groupInDepartmentExtendedName', 'name', 'rank'])
        self.get_zermelo(endpoint='schools', fields=['id', 'name', 'brin'])
        self.get_zermelo(endpoint='schoolsinschoolyears', fields=['id', 'school', 'year', 'project', 'archived', 'projectName', 'schoolName', 'name'])
        self.get_zermelo(endpoint='sectionassignments', fields=['contract', 'id', 'lessonHoursFirstDegree', 'lessonHoursSecondDegree', 'sectionOfBranch'])
        self.get_zermelo_filtered(endpoint='selectedsubjects',
                                  fields=['id', 'subjectSelection', 'choosableInDepartment', 'alternativeChoosableInDepartment', 'manualLessonInvolvement',
                                                                       'exemption', 'studentInDepartment', 'subjectCode', 'subject', 'segmentCode', 'lessonInvolvement'],
                                  startdate=start_of_data,
                                  enddate=end_of_data)
        self.get_zermelo(endpoint='sections', fields=['id', 'abbreviation', 'name', 'sectionOfBranches'], nested=True, nested_fields=['sectionOfBranches'])
        self.get_zermelo(endpoint='students', fields=['dateOfBirth', 'email', 'street', 'houseNumber', 'postalCode', 'city', 'lastName', 'prefix',
                                                      'firstName', 'lwoo', 'userCode', 'studentInDepartments'], nested=True, nested_fields=['studentInDepartments'])
        self.get_zermelo(endpoint='studentsindepartments', fields=['id', 'student', 'departmentOfBranch', 'groupInDepartments', 'mainGroup'])
        self.get_zermelo(endpoint='subjectselections', fields=['id', 'selectedSubjects', 'studentCode', 'departmentOfBranch'])
        self.get_zermelo(endpoint='subjectselectionsubjects', fields=['id', 'code', 'name', 'scheduleCode'])
        self.get_zermelo(endpoint='taskassignments', fields=['branchOfSchool', 'contract', 'employee', 'contract', 'hours', 'hoursReplacement', 'taskGroup', 'taskInBranchOfSchool',
                                                             'type', 'start', 'end'])
        self.get_zermelo(endpoint='tasks', fields=['abbreviation', 'id', 'name', 'taskGroup', 'taskGroupAbbreviation'])
        self.get_zermelo(endpoint='taskgroups', fields=['abbreviation', 'description', 'id', 'name'])
        self.get_zermelo(endpoint='tasksinbranchofschool', fields=['branchOfSchool', 'clockHoursAssigned', 'clockHoursBalance', 'id', 'maxHours', 'task', 'taskAbbreviation'])
        self.get_zermelo(endpoint='teacherteams', fields=['id', 'name', 'branchOfSchool', 'departmentOfBranches'], nested=True, nested_fields=['departmentOfBranches'])
        self.get_zermelo(endpoint='teachingassignments', fields=['id', 'contract', 'plannedLesson', 'type', 'regular', 'lessonHoursInClassPeriodsManually', 'startWeek', 'endWeek',
                                                                 'employee', 'regularContract', 'teachingQualificationStatus', 'lessonHoursNet', 'clockHoursPerLesson', 'clockHoursTotal',
                                                                 'sectionOfBranches', 'publicComment', 'privateComment', 'clockHoursAlgorithm', 'replacements',
                                                                 'lessonHoursInClassPeriods', 'plannedGroups'],
                         nested=True, nested_fields=['lessonHoursInClassPeriods', 'plannedGroups', 'sectionOfBranches', 'replacements'])
        self.get_zermelo(endpoint='teachingqualifications', fields=['id', 'employee', 'choosable', 'startWeek', 'endWeek', 'diploma', 'teachingLevel', 'choosableAbbreviation', 'status', 'name'])
        self.get_zermelo(endpoint='workforceparameters', fields=['defaultclockhoursperlesson', 'id', 'schoolInSchoolYear'])

    def get_zermelo(self, endpoint, fields, nested=False, nested_fields=[], startdate=None, enddate=None):
        """
        Database in Zermelo is divided in different endpoints which consist of fields. Some fields are nested, which
        means that some data lines have a subdivision.
        :param endpoint: name of the endpoint. Not case-sensitive
        :param fields: make a selection of the desired fields. Selection of the field(s) is case-sensitive
        :param nested: field is nested or not
        :param nested_fields: select nested fields
        :return: returns error when extract didn't succeed
        """
        try:
            url_fields = ','.join(fields)
            url = '{0}{1}?access_token={2}&fields={3}'.format(self.url, endpoint, self.access_token, url_fields)

            if nested:
                # Get the response without any transformation
                response = requests.get(url).json()['response']['data']

                # From all the fields, hold only the meta_fields (the not nested fields)
                meta_fields = fields.copy()
                for nested_field in nested_fields:
                    meta_fields.remove(nested_field)

                # From the initial response, create a dataframe with only the meta_fields
                df = pd.DataFrame(response)
                df = df[meta_fields]

                # Set the columns in df as the same type as in the original df. Sometimes, an empty field will change the column type in df_temp
                # to object while the dtype in the original df is int or float. This will give an error when merging
                existing_field_types = dict(df.dtypes)
                for column in df:
                    if column in existing_field_types:
                        existing_dtype = existing_field_types[column]
                        if existing_dtype == 'int64' or existing_dtype == 'float64':
                            df[column] = df[column].fillna(0)
                            df[column] = df[column].astype(existing_dtype)

                # Loop through the nested_fields, create a dataframe for each nested field and join the result to the initial dataframe
                for nested_field in nested_fields:
                    # If the nested_field hold a key, value pair, then the record_prefix is usable. Only a value give a TypeError. Catch this error and rename the column
                    try:
                        df_temp = pd.io.json.json_normalize(data=response, meta=meta_fields, record_path=[nested_field], record_prefix='{}_'.format(nested_field))
                    except TypeError:
                        df_temp = pd.io.json.json_normalize(data=response, meta=meta_fields, record_path=[nested_field])
                        df_temp.rename(columns={0: nested_field}, inplace=True)
                    # Set the columns in df_temp as the same type as in the original df. Sometimes, an empty field will change the column type in df_temp
                    # to object while the dtype in the original df is int or float. This will give an error when merging
                    existing_field_types = dict(df.dtypes)
                    for column in df_temp:
                        if column in existing_field_types:
                            existing_dtype = existing_field_types[column]
                            if existing_dtype == 'int64' or existing_dtype == 'float64':
                                df_temp[column] = df_temp[column].fillna(0)
                                df_temp[column] = df_temp[column].astype(existing_dtype)
                    # Merge the initial dataframe and the new one
                    df = pd.merge(df, df_temp, how='left', on=meta_fields)
                data = df
            else:
                init_response = json.loads(requests.get(url).content)
                status = init_response['response']['status']
                if status == 200:
                    data = pd.DataFrame(init_response['response']['data'])

                    # Check each column if the column only holds integers. If yes, and the type is a Float, set type to float. Otherwise, this gives problems in QLik Sense (2 becomes 2.0)
                    for column in data.columns:
                        try:
                            if data.loc[:, column].dtype == np.float64 or data.loc[:, column].dtype == np.int64:
                                data.loc[:, column].fillna(0, inplace=True)
                            else:
                                data.loc[:, column].fillna('', inplace=True)
                            column_name = 'check_{}'.format(column)
                            data.loc[:, column_name] = data.apply(lambda x: 'int64' if x[column].is_integer() else 'float', axis=1)
                            if 'float' in data.loc[:, column_name].values:
                                pass
                            else:
                                data.loc[:, column] = data.loc[:, column].astype('int64')
                            del data[column_name]
                        except Exception as e:
                            continue

                else:
                    data = init_response['response']['message']
                    print(data)

            data.index.name = '{0}_id'.format(endpoint)
            file = '{0}{1}.csv'.format(self.storage_location, endpoint)
            data.to_csv(file, sep='|', decimal=',')
            print('{0} - {1} saved'.format(time.strftime('%H:%M:%S'), endpoint))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error = str(e)[:400].replace('\'', '').replace('\"', '') + ' | Line: {}'.format(exc_tb.tb_lineno)
            return error

    def get_zermelo_substituded_lessons(self, endpoint, fields, startdate, enddate):
        start = time.time()
        fields = ','.join(fields)

        # Loop through the data per 3 days (3600 seconds * 24 hours * 3 days) because the dataset is too big to receive in once. Start three years back
        df = pd.DataFrame()
        start_epoch = int(time.mktime(startdate))
        last_epoch = int(time.mktime(enddate))
        while start_epoch < last_epoch:
            try:
                if (start_epoch + (3600 * 24 * 7)) > last_epoch:
                    end_epoch = int(last_epoch)
                else:
                    end_epoch = int(start_epoch + (3600 * 24 * 7))

                url = '{0}{1}?access_token={2}&fields={3}&start={4}&end={5}'.format(self.url, endpoint, self.access_token, fields, start_epoch, end_epoch)
                data = requests.get(url).json()['response']['data']

                # checks if data is not empty list
                if data:
                    df_new = pd.DataFrame(data)
                    df_new['changeDescription'] = df_new['changeDescription'].str.replace('\n', '')
                    df_new['changeDescription'] = df_new['changeDescription'].str.replace('\r', '')
                    df = pd.concat([df, df_new])

                    print('Substituded: Start: {}, End: {}, Length: {}'.format(start_epoch, end_epoch, len(df_new)))

                start_epoch += (3600 * 24 * 7)

            except Exception as e:
                print('{} - Error at timestamp {}: {}'.format(time.strftime('%H:%M:%S'), start_epoch, e))
                start_epoch += (3600 * 24 * 7)

        # Store the total dataframe to a new csv file
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.index.name = '{0}_id'.format(endpoint)
        file = '{}{}_{}.csv'.format(self.storage_location, 'substituded_lessons', datetime.datetime.fromtimestamp(mktime(startdate)).strftime('%Y-%m-%d'))
        df.to_csv(file, sep='|', decimal=',')

        print('Done in {} seconds'.format(time.time() - start))

    def get_zermelo_appointments(self, endpoint, fields, startdate, enddate):
        start = time.time()
        fields = ','.join(fields)

        df = pd.DataFrame()

        start_epoch = int(time.mktime(startdate))
        last_epoch = int(time.mktime(enddate))
        while start_epoch < last_epoch:
            try:
                if (start_epoch + (3600 * 24 * 7)) > last_epoch:
                    end_epoch = int(last_epoch)
                else:
                    end_epoch = int(start_epoch + (3600 * 24 * 7))
                print(start_epoch, end_epoch)
                url = '{0}{1}?access_token={2}&fields={3}&start={4}&end={5}&includeHidden=True{6}&valid=True'.format(self.url, endpoint, self.access_token, fields, start_epoch, end_epoch, self.cancelled_appointments)
                data = requests.get(url).json()['response']['data']

                # checks if data is not empty list
                if data:
                    df_new = pd.DataFrame(data)
                    df_new['remark'] = df_new['remark'].str.replace('\n', '')
                    df_new['remark'] = df_new['remark'].str.replace('\r', '')
                    df = pd.concat([df, df_new])

                    print('Appointments: Start: {}, End: {}, Length: {}'.format(start_epoch, end_epoch, len(df_new)))
                # Add one week
                start_epoch += (3600 * 24 * 7)

            except Exception as e:
                print('{} - Error at timestamp {}: {}'.format(time.strftime('%H:%M:%S'), start_epoch, e))
                start_epoch += (3600 * 24 * 7)

        # During summer vacation, it can occur that no data call is executed. The df is empty in this case
        if len(df) > 0:
            # Reset some columns from Float to Int
            df.loc[:, 'branchOfSchool'].fillna(0, inplace=True)
            df.loc[:, 'branchOfSchool'] = df.loc[:, 'branchOfSchool'].astype('int64')
            df.reset_index(inplace=True, drop=True)

            # Subtract all the nested layers from the appointments and save to separate files
            self.appointments_create_lookup_table(df, 'students', 'userCode', startdate)
            self.appointments_create_lookup_table(df, 'teachers', 'userCode', startdate)
            self.appointments_create_lookup_table(df, 'subjects', 'scheduleCode', startdate)
            self.appointments_create_lookup_table(df, 'groups', 'code', startdate)
            self.appointments_create_lookup_table(df, 'locations', 'code', startdate)
            self.appointments_create_lookup_table(df, 'locationsOfBranch', 'id', startdate)
            self.appointments_create_lookup_table(df, 'groupsInDepartments', 'id', startdate)

            # Store the total dataframe to a new csv file
            df.drop(columns=['students', 'teachers', 'subjects', 'groups', 'locations', 'locationsOfBranch', 'groupsInDepartments'], inplace=True)
            df.index.name = '{0}_id'.format(endpoint)
            file = '{}{}_{}.csv'.format(self.storage_location, 'appointments', datetime.datetime.fromtimestamp(mktime(startdate)).strftime('%Y-%m-%d'))

            df.to_csv(file, sep='|', decimal=',')
            print('Done in {} seconds'.format(time.time() - start))

    def appointments_create_lookup_table(self, df, col_name, link_id, startdate):
        df = df[['id', col_name]]
        # Only hold rows whith filled arrays
        df = df[df[col_name].apply(len) > 0]
        appointments_lookup_df = []
        for index, row in df.iterrows():
            appointmentId = row['id']
            to_link = row[col_name]
            for item in to_link:
                appointments_lookup_df.append({'appointmentsId': appointmentId, link_id: item})
        df = pd.DataFrame(appointments_lookup_df)
        file = '{0}{1}.csv'.format(self.storage_location, 'appointments_{}_{}'.format(col_name, datetime.datetime.fromtimestamp(mktime(startdate)).strftime('%Y-%m-%d')))
        df.index.name = 'appointments_{0}_id'.format(col_name)
        df.to_csv(file, sep='|', decimal=',')

    def get_zermelo_filtered(self, endpoint, fields, startdate, enddate):
        start = time.time()
        fields = ','.join(fields)

        # Loop through the data per 3 days (3600 seconds * 24 hours * 3 days) because the dataset is too big to receive in once. Start three years back
        df = pd.DataFrame()
        start_epoch = int(time.mktime(startdate))
        last_epoch = int(time.mktime(enddate))
        while start_epoch < last_epoch:
            try:
                if (start_epoch + (3600 * 24 * 7)) > last_epoch:
                    end_epoch = int(last_epoch)
                else:
                    end_epoch = int(start_epoch + (3600 * 24 * 7))

                url = '{0}{1}?access_token={2}&fields={3}&start={4}&end={5}'.format(self.url, endpoint, self.access_token, fields, start_epoch, end_epoch)
                data = requests.get(url).json()['response']['data']

                # checks if data is not empty list
                if data:
                    df_new = pd.DataFrame(data)
                    df = pd.concat([df, df_new])

                    print(f'{endpoint}: Start: {start_epoch}, End: {end_epoch}, Length: {len(df_new)}')

                start_epoch += (3600 * 24 * 7)

            except Exception as e:
                print('{} - Error at timestamp {}: {}'.format(time.strftime('%H:%M:%S'), start_epoch, e))

        # Store the total dataframe to a new csv file
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.index.name = '{0}_id'.format(endpoint)
        file = '{0}{1}.csv'.format(self.storage_location, endpoint)
        df.to_csv(file, sep='|', decimal=',')
        print('{0} - {1} saved'.format(time.strftime('%H:%M:%S'), endpoint))
        print('Done in {} seconds'.format(time.time() - start))
