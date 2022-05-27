#!/usr/bin/env python
# generatePlots.py -- generate plots of component numbers as a function of time in the ITkPD

import logging

import sys, os
from collections import Counter
from itkdb.utilities import colouredLogger
from itkdb.core import Session

logging.setLoggerClass(colouredLogger)
log = logging.getLogger('generatePlots')
log.setLevel(logging.INFO)


class PlotMaker(object):
    def __init__(self, session):
        self.session = session

    # Define our function for applying cuts (from a list of choices or a boolean value)
    def __cutOnValue(self, component, allowedValues, keywords):

        try:

            # Get value at the level of the first keyword
            value = component[keywords[0]]

            # If there are multiple keywords, continue to update value (note, the order of the keywords should match the order in the uuComponent object)
            for keyword in keywords[1:]:
                value = value[keyword]

            # If the value passes the cut, return True
            if value in allowedValues:
                return True

            # If the value fails the cut, return False
            else:
                log.debug(
                    'Component \'%s\' failed at \'%s\' cut: \'%s\' = %s'
                    % (component['code'], keywords[0], keywords[0], value)
                )
                return False

        # If the keywords do not actually exist for the object, return False too
        except KeyError as error:
            log.warning(
                'Component \'%s\' failed due to KeyError: %s'
                % (component['code'], error)
            )
            return False

    # Define our function for applying cuts using a mathematical (in)equality operator
    def __cutOnValueWithOperator(self, component, operator, cutValue, keywords):

        try:

            # Get value at the level of the first keyword
            value = component[keywords[0]]

            # If there are multiple keywords, continue to update value (note, the order of the keywords should match the order in the uuComponent object)
            for keyword in keywords[1:]:
                if ':' in keyword:
                    index1, index2 = [int(item) for item in keyword.split(':')]
                    value = value[index1:index2]
                else:
                    value = value[keyword]

            # If the value passes the cut, return True, else return False (note: we have to check each case for the operator to be used)
            if operator == '<':
                if value < cutValue:
                    return True
                else:
                    log.debug(
                        'Component \'%s\' failed at \'%s\' cut: \'%s\' = %s'
                        % (component['code'], keywords[0], keywords[0], value)
                    )
                    return False
            elif operator == '>':
                if value > cutValue:
                    return True
                else:
                    log.debug(
                        'Component \'%s\' failed at \'%s\' cut: \'%s\' = %s'
                        % (component['code'], keywords[0], keywords[0], value)
                    )
                    return False
            elif operator == '<=':
                if value <= cutValue:
                    return True
                else:
                    log.debug(
                        'Component \'%s\' failed at \'%s\' cut: \'%s\' = %s'
                        % (component['code'], keywords[0], keywords[0], value)
                    )
                    return False
            elif operator == '>=':
                if value >= cutValue:
                    return True
                else:
                    log.debug(
                        'Component \'%s\' failed at \'%s\' cut: \'%s\' = %s'
                        % (component['code'], keywords[0], keywords[0], value)
                    )
                    return False
            elif operator == '==':
                if value == cutValue:
                    return True
                else:
                    log.debug(
                        'Component \'%s\' failed at \'%s\' cut: \'%s\' = %s'
                        % (component['code'], keywords[0], keywords[0], value)
                    )
                    return False
            elif operator == '!=':
                if value != cutValue:
                    return True
                else:
                    log.debug(
                        'Component \'%s\' failed at \'%s\' cut: \'%s\' = %s'
                        % (component['code'], keywords[0], keywords[0], value)
                    )
                    return False

        # If the keywords do not actually exist for the object, return False too
        except KeyError as error:
            log.warning(
                'Component \'%s\' failed due to KeyError: %s'
                % (component['code'], error)
            )
            return False

    # Define a function for adding a single cutOnValue
    def __addCutOnValue(self, cuts, cutName, allowedValues, keywords):

        # Check if allowedValues is a list and doesn't equal a list of None
        # If this passes, we add the cut
        if isinstance(allowedValues, list) and allowedValues != [None]:
            log.debug('Adding cut \'%s\'...' % cutName)
            cuts[cutName] = lambda component: self.__cutOnValue(
                component, allowedValues=allowedValues, keywords=keywords
            )

        # Check if allowedValues is not a list and doesn't equal None
        # If this passes, we add the cut
        elif not isinstance(allowedValues, list) and allowedValues != None:
            log.debug('Adding cut \'%s\'...' % cutName)
            cuts[cutName] = lambda component: self.__cutOnValue(
                component, allowedValues=allowedValues, keywords=keywords
            )

        # Else, don't add the cut
        else:
            pass

    # Define a function for adding all of our cuts from our kwargs
    def __getCuts(self, **kwargs):

        log.debug('Adding cuts...')

        # Initialize our cut list
        cuts = {}

        # Add our cuts, one at a time
        self.__addCutOnValue(
            cuts,
            'currentLocation',
            allowedValues=kwargs['currentLocation'],
            keywords=['currentLocation', 'code'],
        )
        self.__addCutOnValue(
            cuts,
            'institution',
            allowedValues=kwargs['institution'],
            keywords=['institution', 'code'],
        )
        self.__addCutOnValue(
            cuts,
            'currentGrade',
            allowedValues=kwargs['currentGrade'],
            keywords=['currentGrade'],
        )
        self.__addCutOnValue(
            cuts, 'qaState', allowedValues=kwargs['qaState'], keywords=['qaState']
        )

        # Add our lower date cut
        if kwargs['lowerDate'] != None:
            log.debug('Adding cut \'lowerDate\'...')
            cuts['lowerDate'] = lambda component: self.__cutOnValueWithOperator(
                component, '>=', kwargs['lowerDate'], ['cts', '0:10']
            )

        # Add our upper date cut
        if kwargs['upperDate'] != None:
            log.debug('Adding cut \'upperDate\'...')
            cuts['upperDate'] = lambda component: not self.__cutOnValueWithOperator(
                component['cts'], '>=', kwargs['upper'], []
            )

        # Add the remaining cuts
        self.__addCutOnValue(
            cuts, 'trashed', allowedValues=kwargs['trashed'], keywords=['trashed']
        )
        self.__addCutOnValue(
            cuts, 'dummy', allowedValues=kwargs['dummy'], keywords=['dummy']
        )
        self.__addCutOnValue(
            cuts, 'assembled', allowedValues=kwargs['assembled'], keywords=['assembled']
        )
        self.__addCutOnValue(
            cuts, 'reworked', allowedValues=kwargs['reworked'], keywords=['reworked']
        )
        self.__addCutOnValue(
            cuts, 'qaTested', allowedValues=kwargs['qaTested'], keywords=['qaTested']
        )

        # Return the cuts
        log.debug('All cuts successfully added.')
        return cuts

    # Define a function for applying every cut in cuts to a component
    def __applyCuts(self, component, cuts):

        # Iterate through our cuts
        for cut in cuts.values():

            # If the cut fails (i.e., returns False), return False to indicate that the component did not pass
            if not cut(component):
                return False

        # Else, return True is everything passes
        log.debug('Component \'%s\' passed all cuts.' % component['code'])
        return True

    def __addToCounter(self, component, counter, split):
        date = component['cts'][0:10]
        counter['total'].append(date)
        if split:
            try:
                splitType = component[split]['code']
            except TypeError as error:
                log.warning(
                    'Component \'%s\' failed to be added to counter due to TypeError: %s'
                    % (component['code'], error)
                )
                return counter
            except KeyError as error:
                log.warning(
                    'Component \'%s\' failed to be added to counter due to KeyError: %s'
                    % (component['code'], error)
                )
                return counter
            if splitType in counter.keys():
                counter[splitType].append(date)
            else:
                counter[splitType] = [date]
        log.debug('Component \'%s\' successfully added to counter.' % component['code'])
        return counter

    def __addToCounterWithStages(self, component, counter, **kwargs):
        try:
            for i, stage in enumerate(component['stages']):
                date = stage['dateTime'][0:10]
                if stage in counter.keys():
                    if i == 0:
                        counter[stage].append(date)
                    else:
                        counter[stage].append(date)
                        counter[component['stages'][i - 1]].append('-' + date)
                else:
                    if i == 0:
                        counter[stage].append(date)
                    else:
                        counter[stage].append(date)
                        counter[component['stages'][i - 1]].append('-' + date)
        except TypeError as error:
            log.warning(
                'Component \'%s\' failed due to TypeError: %s'
                % (component['code'], error)
            )
            return counter
        except KeyError as error:
            log.warning(
                'Component \'%s\' failed due to KeyError: %s'
                % (component['code'], error)
            )
            return counter

    # Define a function for finalizing our counter (i.e., performing a cumulative sum and organizing by date)
    def __finalizeCounter(self, counter, **kwargs):

        # Define a small function for performing the cumulative sum of a list
        def accumulate(list):
            total = 0
            for count in list:
                total += count
                yield total

        # Iterate through the keys ('total' and any 'split' keys) of our counter
        for key in counter.keys():

            # Turn each iterable into a Counter object
            counter[key] = Counter(counter[key])

            # Sort the dates
            dates = sorted(counter[key].keys())

            # Perform a cumulative sum of our counts in the order of dates
            counts = list(accumulate([counter[key][date] for date in dates]))

            # Redefine two new keys for the current key of counts we are examining:
            # dates := time ordered list of dates
            # counts := cumulative sum of counts in order of dates
            counter[key] = {'dates': dates, 'counts': counts}

        # Get the earliest and latest dates from counter['total']
        earliest_date = (
            kwargs['lowerDate']
            if kwargs['lowerDate'] != None
            else counter['total']['dates'][0]
        )
        latest_date = (
            kwargs['upperDate']
            if kwargs['upperDate'] != None
            else counter['total']['dates'][-1]
        )

        # Iterate through our keys, inserting the earliest and latest dates from 'total'
        # (and keeping the number of counts the same as the 2nd earliest/latest date)
        for key in counter.keys():
            if counter[key]['dates'][0] != earliest_date:
                counter[key]['dates'].insert(0, earliest_date)
                counter[key]['counts'].insert(0, counter[key]['counts'][0])
            if counter[key]['dates'][-1] != latest_date:
                counter[key]['dates'].append(latest_date)
                counter[key]['counts'].append(counter[key]['counts'][-1])

        # Return our counter
        return counter

    def __finalizeCounterWithStages(self, counter, **kwargs):

        # Define a small function for performing the cumulative sum of a list
        def accumulate(list):
            total = 0
            for count in list:
                total += count
                yield total

        counter['total'] = []
        for dates in counter.values():
            counter['total'] += dates

        # Iterate through the keys of our counter
        for key in counter.keys():

            # Turn each iterable into a Counter object
            counter[key] = Counter(counter[key])

            # Sort the dates
            dates = sorted(counter[key].keys())

            for date in dates:
                if date[0] == '-':
                    counter[key][date[1:]] -= counter[key][date]
                    del counter[date]
                else:
                    break

            # Perform a cumulative sum of our counts in the order of dates
            counts = list(accumulate([counter[key][date] for date in dates]))

            # Redefine two new keys for the current key of counts we are examining:
            # dates := time ordered list of dates
            # counts := cumulative sum of counts in order of dates
            counter[key] = {'dates': dates, 'counts': counts}

        # Get the earliest and latest dates from counter['total']
        earliest_date = counter['total']['dates'][0]
        latest_date = counter['total']['dates'][-1]

        # Iterate through our keys, inserting the earliest and latest dates from 'total'
        # (and keeping the number of counts the same as the 2nd earliest/latest date)
        for key in counter.keys():
            if counter[key]['dates'][0] != earliest_date:
                counter[key]['dates'].insert(0, earliest_date)
                counter[key]['counts'].insert(0, counter[key]['counts'][0])
            if counter[key]['dates'][-1] != latest_date:
                counter[key]['dates'].append(latest_date)
                counter[key]['counts'].append(counter[key]['counts'][-1])

        # Return our counter
        return counter

    def __drawPlots(self, counter, **kwargs):

        import datetime

        if kwargs['rrulewrapperFrequency'] == 'DAILY':
            rrulewrapperFrequency = DAILY
        elif kwargs['rrulewrapperFrequency'] == 'MONTHLY':
            rrulewrapperFrequency = MONTHLY
        elif kwargs['rrulewrapperFrequency'] == 'YEARLY':
            rrulewrapperFrequency = YEARLY

        rule = rrulewrapper(
            rrulewrapperFrequency, interval=kwargs['rrulewrapperInterval']
        )
        loc = RRuleLocator(rule)
        formatter = DateFormatter('%Y/%m/%d')

        plt.style.use("seaborn-whitegrid")
        fig, ax = plt.subplots()

        keys = counter.keys()
        if len(keys) == 1:
            dates = [
                datetime.date(*[int(item) for item in date.split('-')])
                for date in counter['total']['dates']
            ]
            counts = counter['total']['counts']
            plt.plot_date(dates, counts, linestyle='-', label='total')

        else:
            if kwargs['includeTotal']:
                dates = [
                    datetime.date(*[int(item) for item in date.split('-')])
                    for date in counter['total']['dates']
                ]
                counts = counter['total']['counts']
                plt.plot_date(dates, counts, linestyle='-', label='total')
            for key in sorted(keys):
                if key == 'total':
                    continue
                dates = [
                    datetime.date(*[int(item) for item in date.split('-')])
                    for date in counter[key]['dates']
                ]
                counts = counter[key]['counts']
                plt.plot_date(dates, counts, linestyle='-', label=key)

        plt.title(
            'project = \'%s\', componentType = \'%s\' -- Generated on %s'
            % (kwargs['project'], kwargs['componentType'], kwargs['startTime'])
        )
        plt.xlabel('Date [a.u.]')
        plt.ylabel('Frequency [a.u.]')
        plt.legend()

        ax.xaxis.set_major_locator(loc)
        ax.xaxis.set_major_formatter(formatter)

        # if kwargs['lowerDate'] != None:
        #     plt.gca().set_xlim(left = datetime.date(*[int(item) for item in kwargs['lowerDate'].split('-')]))
        # if kwargs['upperDate'] != None:
        #     plt.gca().set_xlim(right = datetime.date(*[int(item) for item in kwargs['upperDate'].split('-')]))

        if kwargs['savePath'][-4:] == '.pdf':
            plt.savefig(kwargs['savePath'])
        elif kwargs['savePath'][-4:] == '.png':
            plt.savefig(kwargs['savePath'], dpi=150)
        if kwargs['saveJson']:
            counter['kwargs'] = kwargs
            import json

            with open(kwargs['savePath'][0:-4] + '.json', 'w') as file:
                json.dump(
                    counter, file, sort_keys=True, indent=4, separators=(',', ': ')
                )

    # Define our main makePlots function
    def makePlots(self, **kwargs):

        # Get our keys for kwargs
        keys = kwargs.keys()

        # Define a general error class
        class Error(Exception):
            def __init__(self, message):
                self.message = message

        # Perform some argument checking
        # Note, this does not check every required argument for makePlot() is present in kwargs
        ########################################################################################################
        # This is bad of me, it should be fixed in the future if this class is to be used outside of this file #
        ########################################################################################################
        log.debug('Peforming argument checking...')
        try:
            if 'project' not in keys:
                raise Error(
                    'Keyword argument \'project\' is required by PlotMaker.makePlots().'
                )
            if 'componentType' not in keys:
                raise Error(
                    'Keyword argument \'componentType\' is required by PlotMaker.makePlots().'
                )
            if 'savePath' not in keys:
                raise Error(
                    'Keyword argument \'savePath\' is required by PlotMaker.makePlots().'
                )
            if kwargs['savePath'][-4:] != '.pdf' and kwargs['savePath'][-4:] != '.png':
                raise Error(
                    '--savePath must have suffix \'.pdf\' or \'.png\'": --savePath = %s'
                    % kwargs['savePath']
                )
            if not os.path.exists(os.path.dirname(kwargs['savePath'])):
                raise Error(
                    'Parent directory does not exist: %s'
                    % os.path.dirname(kwargs['savePath'])
                )
            if (
                kwargs['type'] != None
                or kwargs['currentStage'] != None
                or kwargs['split'] in ['type', 'currentStage']
            ):
                componentTypeJson = self.session.get(
                    'getComponentTypeByCode',
                    json={
                        'project': kwargs['project'],
                        'code': kwargs['componentType'],
                    },
                )
                if componentTypeJson['types'] == [] and (
                    kwargs['split'] == 'type' or kwargs['type'] != []
                ):
                    raise Error(
                        'Component type \'%s\' does not have any types and so it does not make sense to split/filter by type.'
                        % kwargs['componentType']
                    )
                if kwargs['type'] != None:
                    unknownTypes = [
                        type
                        for type in kwargs['type']
                        if type
                        not in [type2['code'] for type2 in componentTypeJson['types']]
                    ]
                    if unknownTypes != []:
                        raise Error(
                            'Unknown type code(s) for component type \'%s\': [\'%s\']'
                            % (kwargs['componentType'], '\', \''.join(unknownTypes))
                        )
                if componentTypeJson['stages'] == [] and (
                    kwargs['split'] == 'currentStage' or kwargs['currentStage'] != []
                ):
                    raise Error(
                        'Component type \'%s\' does not have any types and so it does not make sense to split/filter by the current stage.'
                        % kwargs['componentType']
                    )
                if kwargs['currentStage'] != None:
                    unknownStages = [
                        stage
                        for stage in kwargs['currentStage']
                        if stage
                        not in [
                            stage2['code'] for stage2 in componentTypeJson['stages']
                        ]
                    ]
                    if unknownStages != []:
                        raise Error(
                            'Unknown stage code(s) for component type \'%s\': [\'%s\']'
                            % (kwargs['componentType'], '\', \''.join(unknownStages))
                        )
            if kwargs['currentLocation'] != None or kwargs['institution'] != None:
                institutionsJson = self.session.get('listInstitutions')
                if kwargs['currentLocation'] != None:
                    unknownCurrentLocations = [
                        currentLocation
                        for currentLocation in kwargs['currentLocation']
                        if currentLocation
                        not in [
                            currentLocation2['code']
                            for currentLocation2 in institutionsJson
                        ]
                    ]
                    if unknownCurrentLocations != []:
                        raise Error(
                            'Unknown current location code(s): [\'%s\']'
                            % '\', \''.join(unknownCurrentLocations)
                        )
                if kwargs['institution'] != None:
                    unknownInstitutions = [
                        institution
                        for institution in kwargs['institution']
                        if institution
                        not in [
                            institution2['code'] for institution2 in institutionsJson
                        ]
                    ]
                    if unknownInstitutions != []:
                        raise Error(
                            'Unknown institution code(s): [\'%s\']'
                            % '\', \''.join(unknownInstitutions)
                        )
        except Error as e:
            log.error(e.message)
            sys.exit(1)
        log.debug('Argument checking passed.')

        # Get our initial list of components from the DB
        data = {'project': kwargs['project'], 'componentType': kwargs['componentType']}
        if kwargs['type'] != None:
            data['type'] = kwargs['type']
        if kwargs['currentStage'] != None:
            data['currentStage'] = kwargs['currentStage']
        log.info(
            'Fetching a list of components filtered by project/componentType/type/currentStage from the ITkPD...'
        )
        components = self.session.get('listComponents', json=data)['pageItemList']
        log.info(
            'List of components successfully fetched (%s entries).' % len(components)
        )

        # Get our cuts
        cuts = self.__getCuts(**kwargs)

        # Apply our cuts to each component and keep only the components which pass all cuts
        log.info('Applying cuts to the list of components and generating counter...')
        if kwargs['currentStage'] != None or kwargs['split'] == 'currentStage':
            addToCounter = self.__addToCounterWithStages
            finalizeCounter = lambda counter: self.__finalizeCounterWithStages(
                counter, **kwargs
            )
        else:
            addToCounter = self.__addToCounter
            finalizeCounter = lambda counter: self.__finalizeCounter(counter, **kwargs)
        split = kwargs['split']
        passedComponents = 0
        counter = {'total': []}
        for component in components:
            if self.__applyCuts(component, cuts):
                passedComponents += 1
                addToCounter(component, counter, split)

        if [0 for value in counter.values() if value == []] != []:
            log.info('Cuts successfully applied to list of components (0 entries).')
            log.warning('No components passed the cuts -- no plot to be generated.')

        else:

            # Finalize the counter and delete our old reference to components
            finalizeCounter(counter)
            del components
            log.info(
                'Cuts successfully applied to list of components (%s entries).'
                % passedComponents
            )

            self.__drawPlots(counter, **kwargs)


if __name__ == '__main__':

    try:

        # Get our start time of the script
        from time import strftime

        startTime = strftime('%Y/%m/%d-%H:%M:%S')
        startTime4SavePath = (
            ''.join(startTime.split('-')[0].split('/'))
            + '-'
            + ''.join(startTime.split('-')[1].split(':'))
        )

        # Define our parser
        import argparse

        parser = argparse.ArgumentParser(
            description='Generate plots of component numbers as a function of time in the ITkPD',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        parser._action_groups.pop()

        # Define our required arguments
        required = parser.add_argument_group('required arguments')
        required.add_argument(
            '-p',
            '--project',
            dest='project',
            type=str,
            choices=['S', 'P', 'CM', 'CE'],
            default='S',
            help='project code for a component type',
        )
        required.add_argument(
            '-c',
            '--componentType',
            dest='componentType',
            type=str,
            required=True,
            help='component type code',
        )
        required.add_argument(
            '-S',
            '--savePath',
            dest='savePath',
            type=str,
            default='{0}/ITkPDProdPlot_{1}.pdf'.format(os.getcwd(), startTime4SavePath),
            help='save path for the plot (choose suffix [\'.pdf\'|\'.png\'])',
        )

        # Define an argparse type for converting str to bool
        # See: https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
        def str2bool(arg):
            if arg.lower() in ('yes', 'true', 't', 'y', '1'):
                return True
            elif arg.lower() in ('no', 'false', 'f', 'n', '0'):
                return False
            else:
                raise argparse.ArgumentTypeError('Boolean value expected.')

        # Define an argparse type for checking the str formatting of the date(s)
        from datetime import datetime

        def str2date(arg):
            try:
                datetime.strptime(arg, '%Y-%m-%d')
                return arg
            except ValueError:
                try:
                    datetime.strptime(arg, '%Y/%m/%d')
                    return '-'.join(arg.split('/'))
                except ValueError:
                    try:
                        datetime.strptime(arg, '%Y.%m.%d')
                        return '-'.join(arg.split('.'))
                    except ValueError:
                        try:
                            datetime.strptime(arg, '%Y%m%d')
                            return arg[0:4] + '-' + arg[4:6] + '-' + arg[6:8]
                        except ValueError:
                            raise argparse.ArgumentTypeError(
                                'Date must be formatted one of [\'YYYY-MM-DD\'|\'YYYY/MM/DD\'|\'YYYY.MM.DD\'|\'YYYYMMDD\'].'
                            )

        # Define our optional arguments
        optional = parser.add_argument_group('optional arguments')
        order_choices = [
            'currentLocation',
            'institution',
            'currentGrade',
            'qaState',
            'trashed',
            'dummy',
            'assembled',
            'reworked',
            'qaTested',
        ]
        optional.add_argument(
            '-t',
            '--type',
            dest='type',
            type=str,
            nargs='*',
            help='space-separated list of type codes of the component type',
        )
        optional.add_argument(
            '-s',
            '--currentStage',
            dest='currentStage',
            type=str,
            nargs='*',
            help='space-separated list of current stage codes',
        )
        optional.add_argument(
            '-l',
            '--currentLocation',
            dest='currentLocation',
            type=str,
            nargs='*',
            help='space-separated list of current location codes',
        )
        optional.add_argument(
            '-i',
            '--institution',
            dest='institution',
            type=str,
            nargs='*',
            help='space-separated list of institution codes',
        )
        optional.add_argument(
            '-g',
            '--currentGrade',
            dest='currentGrade',
            type=int,
            nargs='*',
            help='space-separated list of current grades',
        )
        optional.add_argument(
            '-q',
            '--qaState',
            dest='qaState',
            type=str,
            nargs='*',
            help='space-separated list of QA state codes',
        )
        optional.add_argument(
            '-L',
            '--lowerDate',
            dest='lowerDate',
            type=str2date,
            help='lower date range to filter components by',
        )
        optional.add_argument(
            '-U',
            '--upperDate',
            dest='upperDate',
            type=str2date,
            help='upper date range to filter components by',
        )
        optional.add_argument(
            '-T',
            '--trashed',
            dest='trashed',
            type=str2bool,
            nargs='*',
            help='trashed status (True|False)',
        )
        optional.add_argument(
            '-D',
            '--dummy',
            dest='dummy',
            type=str2bool,
            nargs='*',
            help='dummy status (True|False)',
        )
        optional.add_argument(
            '-A',
            '--assembled',
            dest='assembled',
            type=str2bool,
            nargs='*',
            help='assembled status (True|False)',
        )
        optional.add_argument(
            '-R',
            '--reworked',
            dest='reworked',
            type=str2bool,
            nargs='*',
            help='reworked status (True|False)',
        )
        optional.add_argument(
            '-Q',
            '--qaTested',
            dest='qaTested',
            type=str2bool,
            nargs='*',
            help='QA tested status (True|False)',
        )
        optional.add_argument(
            '-x',
            '--split',
            dest='split',
            type=str,
            choices=[None, 'type', 'currentStage', 'currentLocation', 'institution'],
            default=None,
            help='',
        )
        optional.add_argument(
            '-v',
            '--verbose',
            dest='verbose',
            action='store_true',
            help='enable detailed printout',
        )
        optional.add_argument(
            '--rrulewrapperFrequency',
            dest='rrulewrapperFrequency',
            type=str,
            choices=['DAILY', 'MONTHLY', 'YEARLY'],
            default='MONTHLY',
            help='frequency for the intervals on the plot',
        )
        optional.add_argument(
            '--rrulewrapperInterval',
            dest='rrulewrapperInterval',
            type=int,
            default=2,
            help='number of steps to take in frequency per major tick on the plot',
        )
        optional.add_argument(
            '--includeTotal',
            dest='includeTotal',
            action='store_true',
            help='show the total number of component counts when --split != None',
        )
        optional.add_argument(
            '--saveJson',
            dest='saveJson',
            action='store_true',
            help='save the json associated the plot (same filename with suffix == \'.json\')',
        )

        # Fetch our args and generate our kwargs dict
        args = parser.parse_args()
        kwargs = {
            'startTime': startTime,
            'project': args.project.upper(),
            'savePath': args.savePath,
            'componentType': args.componentType.upper(),
            'type': [arg.upper() for arg in args.type] if args.type != None else None,
            'currentStage': [arg.upper() for arg in args.currentStage]
            if args.currentStage != None
            else None,
            'currentLocation': [arg.upper() for arg in args.currentLocation]
            if args.currentLocation != None
            else None,
            'institution': [arg.upper() for arg in args.institution]
            if args.institution != None
            else None,
            'currentGrade': args.currentGrade,
            'qaState': args.qaState,
            'lowerDate': args.lowerDate,
            'upperDate': args.upperDate,
            'trashed': args.trashed,
            'dummy': args.dummy,
            'assembled': args.assembled,
            'reworked': args.reworked,
            'qaTested': args.qaTested,
            'split': args.split,
            'rrulewrapperFrequency': args.rrulewrapperFrequency,
            'rrulewrapperInterval': args.rrulewrapperInterval,
            'includeTotal': args.includeTotal,
            'saveJson': args.saveJson,
        }

        if args.verbose:
            log.setLevel(logging.DEBUG)

        log.info('*** generatePlots.py ***')

        # Try to import matplotlib
        try:
            global matplotlib
            import matplotlib.pyplot as plt
            from matplotlib.dates import (
                DAILY,
                MONTHLY,
                YEARLY,
                DateFormatter,
                rrulewrapper,
                RRuleLocator,
            )
        except ImportError:
            log.error('Python module \'matplotlib\' is not installed.')
            log.info(
                'To install, please type \'sudo apt-get install python-matplotlib\' for Python 2.'
            )
            log.info('For Python 3, type \'sudo apt-get install python3-matplotlib\'.')
            sys.exit(1)

        # Generate our PlotMaker object and make our plots
        plotMaker = PlotMaker(Session())
        plotMaker = plotMaker.makePlots(**kwargs)
        log.debug('Finished successfully.')
        sys.exit(0)

    # In the case of a keyboard interrupt, quit with error
    except KeyboardInterrupt:
        print('')
        log.error('Exectution terminated.')
        sys.exit(1)
