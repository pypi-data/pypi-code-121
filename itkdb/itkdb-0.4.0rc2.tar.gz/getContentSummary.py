#!/usr/bin/env python
# getContentSummary.py -- a class providing an interface for getting component counts summary info from the ITk Production Database

import logging
import sys, datetime
import click

from itkdb.utilities import colours, colouredLogger
from itkdb.core import Session

logging.setLoggerClass(colouredLogger)
log = logging.getLogger('getContentSummary')
log.setLevel(logging.INFO)

# Define our cancel exception for &CANCEL calls
class Cancel(Exception):
    pass


# Define our content summary interface
class ContentSummaryInferface(object):

    # _institutions will contain the list of institutions returned by the DB, _projects contains a list of all possible projects
    # and _always_print will print all available options at each prompt
    def __init__(self, session):
        self._institutions = []
        self._projects = []
        self._always_print = False
        self.session = session

    # Update our list of institutions if it's empty
    def __startUp(self):
        if self._institutions == [] or self._projects == []:
            log.info('Running ITk Production Database content summary interface.')
            log.info('Updating list of institutions and projects.')
            self._institutions = self.session.get('listInstitutions')['pageItemList']
            self._projects = self.session.get('listProjects')['itemList']

    # Quit our content summary interface
    def __quit(self):
        log.info('Finished successfully.')
        sys.exit(0)

    # Print a list of names and codes in list (assuming it has those keys) with nice printing
    def __printNamesAndCodes(self, list):
        print(
            '    {0}{1}{2:<60} {3:<20}{4}'.format(
                colours.BOLD_SEQ, colours.WHITE, 'Name:', 'Code:', colours.RESET_SEQ
            )
        )
        for item in list:
            print('    {0:<60} {1:<20}'.format(item['name'], item['code']))

    # Define a function to provide a prompt to the user and have them select from options
    # Used to get codes from the user, so options includes all possible codes for the current parameter
    def __askForSomething(self, prompt, options):

        # Generate our list of codes
        codes = [item['code'] for item in options]
        log.info(prompt)

        # If _always_print, print the available options for the code
        if self._always_print:
            log.info('Printing options:\n')
            self.__printNamesAndCodes(options)

        while True:

            # Get our user input
            response = click.prompt('Please enter a code from above:').upper().strip()

            # If nothing, do nothing
            if response == '':
                continue

            # Escape code &PRINT -- print the available options
            elif response == '&PRINT':
                log.info('Printing options:\n')
                self.__printNamesAndCodes(options)
                log.info('Please enter a code from above:')

            # Escape code &CANCEL -- raise Cancel exception
            elif response == '&CANCEL':
                log.warning('Session cancelled.')
                raise Cancel

            # If the user enters a valid code, return that code
            elif response in codes:
                i = codes.index(response)
                log.info('Using code: {0} ({1})'.format(response, options[i]['name']))
                return i, response

            # Else the input is invalid
            else:
                log.info('Invalid input, please try again:')
                continue

    # Define a function to ask for a list of codes
    def __askForMultipleThings(self, prompt, options):

        # Generate our list of codes
        codes = [item['code'] for item in options]
        log.info(prompt)

        # If _always_print, print the available options
        if self._always_print:
            log.info('Printing options:\n')
            self.__printNamesAndCodes(options)

        while True:

            # Get our user input
            response = (
                click.prompt('Please enter a space separated list of codes from above:')
                .strip()
                .upper()
                .split()
            )

            # If nothing, do nothing
            if response == []:
                continue

            # Escape code &PRINT -- print the available options
            elif response == ['&PRINT']:
                log.info('Printing options:\n')
                self.__printNamesAndCodes(options)
                log.info('Please enter a list of space separated codes from above:')
                continue

            # Escape code &ALL -- select all available options
            elif response == ['&ALL']:
                log.info('Using all options.')
                return codes

            # Escape code &CANCEL -- raise Cancel exception
            elif response == ['&CANCEL']:
                log.warning('Session cancelled.')
                raise Cancel

            # If the user enters a valid list of codes, return that code and its index
            not_allowed = [code for code in response if code not in codes]
            if not_allowed == []:
                return_list = []
                log.info('Using code(s):\n')
                for code in response:
                    i = codes.index(code)
                    return_list.append(code)
                    print('    {0} ({1})'.format(code, options[i]['name']))
                return return_list

            # Else the input is invalid
            else:
                log.warning('Invalid input, please try again:')
                continue

    # Define a function to ask the user a prompt and get a yes or no response
    def __getYesOrNo(self, prompt):

        while True:

            # Get our input
            response = click.prompt(prompt).strip()

            # Skip empty inputs
            if response == '':
                continue

            # If yes, return True
            elif response in ['y', 'Y', 'yes', 'Yes', 'YES', '1']:
                return True

            # If no, return False
            elif response in ['n', 'N', 'no', 'No', 'NO', '0']:
                return False

            # Else the input is invalid and ask again
            else:
                del response
                log.info('Invalid input. Please enter \'y/Y\', or \'n/N\':')
                continue

    # Define a function for getting the date from the user
    def __getDate(self, prompt):

        while True:

            # Get our input
            response = click.prompt(prompt).strip()

            # Skip empty inputs:
            if response == '':
                continue

            # Include the &CANCEL escape code
            if response == '&CANCEL':
                log.warning('Session cancelled.')
                raise Cancel

            # Validate the format of the inputted date
            # See: https://stackoverflow.com/questions/16870663/how-do-i-validate-a-date-string-format-in-python
            try:
                datetime.datetime.strptime(response, '%Y-%m-%d')
                if len(response.split('-')[1]) != 2 or len(response.split('-')[2]) != 2:
                    raise ValueError
            except ValueError:
                log.info('Invalid date format, please use YYYY-MM-DD and try again:')
                continue

            # Return our date
            return response

    # Define a function to filter _institutions by only institutions which have component_type associated with project
    def __filterInstitutions(self, project, component_type):

        # Define our return list of institutions
        institutions = []

        # Iterate over all institutions in _institutions
        for institution in self._institutions:

            # Ensure there are projects associated with that insitution
            if institution['componentType'] == []:
                continue

            # Iterate over the available projects at an institution
            for i in range(len(institution['componentType'])):

                # If the institution has the correct project, fetch the index i
                if project == institution['componentType'][i]['code']:
                    break

                # Else do nothing
                else:
                    pass

            # Ensure there are components associated with that project
            if institution['componentType'][i]['itemList'] == []:
                continue

            # Iterate over all the components associated with the project
            for component in institution['componentType'][i]['itemList']:

                # If we find our desired component type, append the current institution to our outputted list
                if component_type == component['code']:
                    institutions.append(institution)

                # Else do nothing
                else:
                    pass

        # Return our list of institutions
        return institutions

    # Define our main interface loop
    def openInterface(self):

        # Fetch our list of institutions
        self.__startUp()

        # Get a value for _always_print
        self._always_print = self.__getYesOrNo(
            'To always print the available input options for codes, please type \'y/Y\' or type \'n/N\' to suppress this output:'
        )
        log.info(
            'Use escape codes &PRINT to print the available options, &ALL to select all options when prompted for a list, or &CANCEL to cancel the session at any time.'
        )

        # The first while loops iterates over summary sessions for multiple component types
        while True:

            # The second while loop iterates over a single summary session (I use break statements when &CANCEL codes are entered)
            while True:

                try:

                    # Ask the user for a project code
                    i, project = self.__askForSomething(
                        'Enter a project code:', self._projects
                    )

                    # Get the component types associated with that project code
                    component_types = self.session.get(
                        'listComponentTypes', json={'project': project}
                    )['pageItemList']

                    # If more than one component type, ask the user to specify
                    if len(component_types) > 1:
                        j, component_type = self.__askForSomething(
                            'Enter a component code associated with your project:',
                            component_types,
                        )

                    # If only one component type, fetch it without prompt
                    elif len(component_type) == 1:
                        log.warning('Component type: only one option available.')
                        log.info(
                            'Using code: {0} ({1})'.format(
                                component_types[0]['code'], component_types[0]['name']
                            )
                        )
                        j, component_type = 0, component_types[0]['code']

                    # If there are no component types, break
                    elif len(component_types) == 0:
                        log.warning(
                            'Component type: there are no component types associated with project code \'{0}\'.'.format(
                                project
                            )
                        )
                        log.info(
                            'If you think there is an error, please contact the production database team.'
                        )
                        break

                    # Get the types (e.g., for ABC, ABC130 or ABC*) that are associated with that particular component type
                    # types_ALL means all possible types, while types will refer to only those selected by the user

                    component = self.session.get(
                        'getComponentType', json={'id': component_types[j]['id']}
                    )
                    types_ALL = component['types']

                    # Repeat the same procedure as above for the type
                    if len(types_ALL) > 1:
                        types = self.__askForMultipleThings(
                            'Enter a space separated list of type codes associated with your component type:',
                            types_ALL,
                        )
                    elif len(types_ALL) == 1:
                        log.info('Type(s): only one option available.')
                        log.info(
                            'Using code: {0} ({1})'.format(
                                types_ALL[0]['code'], types_ALL[0]['name']
                            )
                        )
                        types = [types_ALL[0]['code']]
                    elif len(types_ALL) == 0:
                        log.warning(
                            'Type(s): there are no types associated with component type code \'{0}\'.'.format(
                                component_type
                            )
                        )
                        log.info(
                            'If you think there is an error, please contact the production database team.'
                        )
                        break

                    # Get our institutions associated with a project and component type
                    institutions_ALL = self.__filterInstitutions(
                        project, component_type
                    )

                    # Repeat the same procedure as above for the institution
                    if len(institutions_ALL) > 1:
                        institutions = self.__askForMultipleThings(
                            'Enter a space separated list of institution codes associated with your project/component type:',
                            institutions_ALL,
                        )
                    elif len(institutions_ALL) == 1:
                        log.warning('Institution(s): only one option available.')
                        log.info(
                            'Using code: {0} ({1})'.format(
                                institutions_ALL[0]['code'], institutions_ALL[0]['name']
                            )
                        )
                        institutions = [institutions_ALL[0]['code']]
                    elif len(institutions_ALL) == 0:
                        log.warning(
                            'Institution(s): there are no institutions associated with component code \'{0}\'.'.format(
                                component_type
                            )
                        )
                        log.info(
                            'If you think there is an error, please contact the production database team.'
                        )
                        break

                    # Get our lower and upper date ranges
                    date_lower = self.__getDate(
                        'Please enter a lower bound for the date range to search for components in, using format YYYY-MM-DD:'
                    ).split('-')
                    date_upper = self.__getDate(
                        'Please enter a upper bound for the date range to search for components in, using format YYYY-MM-DD:'
                    ).split('-')

                # Catch our &CANCEL responses from __askForSomething/__askForMultipleThings
                except Cancel:
                    break

                # Report the specified parameters to the user
                log.info('Using:\n')
                print(
                    '    {0}{1}Project{2}        = {3}'.format(
                        colours.BOLD_SEQ, colours.WHITE, colours.RESET_SEQ, project
                    )
                )
                print(
                    '    {0}{1}Component type{2} = {3}'.format(
                        colours.BOLD_SEQ,
                        colours.WHITE,
                        colours.RESET_SEQ,
                        component_type,
                    )
                )
                print(
                    '    {0}{1}Types{2}          = {3}'.format(
                        colours.BOLD_SEQ,
                        colours.WHITE,
                        colours.RESET_SEQ,
                        ', '.join(types),
                    )
                )
                print(
                    '    {0}{1}Institutions{2}   = {3}'.format(
                        colours.BOLD_SEQ,
                        colours.WHITE,
                        colours.RESET_SEQ,
                        ', '.join(institutions),
                    )
                )
                print(
                    '    {0}{1}Lower date{2}     = {3}'.format(
                        colours.BOLD_SEQ,
                        colours.WHITE,
                        colours.RESET_SEQ,
                        '-'.join(date_lower),
                    )
                )
                print(
                    '    {0}{1}Upper date{2}     = {3}'.format(
                        colours.BOLD_SEQ,
                        colours.WHITE,
                        colours.RESET_SEQ,
                        '-'.join(date_upper),
                    )
                )
                log.info('Getting count information from the database.')

                # Check if the component has stages
                stages_DETAILED = component['stages']
                # get list of components from DB
                component_list_db = self.session.get(
                    'listComponents',
                    json={'project': project, 'componentType': component_type},
                )['pageItemList']

                if stages_DETAILED == None:
                    stages_DETAILED = []
                    try:

                        # Get all of the components associated with the project and component type and filter them by the creation time stamp (cts)
                        # (should be between lower and upper dates), whether they match one of the selected institutions, and whether they match one of the
                        # selected types
                        components = list(
                            filter(
                                lambda item: (
                                    item['institution']['code'] in institutions
                                    and item['type']['code'] in types
                                    and date_lower <= item['cts'][0:10].split('-')
                                    and item['cts'][0:10].split('-') <= date_upper
                                ),
                                component_list_db,
                            )
                        )

                    # Some components seem to not have insitution or more likely a type associated with them so you get a TypeError
                    # The below will sift through each individual component and skip it if we get a TypeError
                    except KeyError:

                        components = []
                        for item in component_list_db:
                            try:
                                if (
                                    item['institution']['code'] in institutions
                                    and item['type']['code'] in types
                                    and date_lower <= item['cts'][0:10].split('-')
                                    and item['cts'][0:10].split('-') <= date_upper
                                ):
                                    components.append(item)
                                else:
                                    pass
                            except KeyError:
                                continue

                    # Generate our dictionary of counts for each institution
                    component_counts = {
                        institution['code']: {'TOTAL': 0}
                        for institution in institutions_ALL
                    }
                    component_counts['TOTAL'] = {'TOTAL': 0}

                    # Increment our totals for each institution and overall by checking each of our filtered components
                    for component in components:
                        component_counts[component['institution']['code']]['TOTAL'] += 1
                        component_counts['TOTAL']['TOTAL'] += 1

                else:

                    try:

                        # We can't filter by cts as we don't know what the most recent component stage in the specified date range
                        components = list(
                            filter(
                                lambda item: item['institution']['code'] in institutions
                                and item['type']['code'] in types,
                                component_list_db,
                            )
                        )

                    # Some components seem to not have insitution or more likely a type associated with them so you get a TypeError
                    # The below will sift through each individual component and skip it if we get a TypeError
                    except TypeError:

                        components = []
                        for item in component_list_db:
                            try:
                                if (
                                    item['institution']['code'] in institutions
                                    and item['type']['code'] in types
                                ):
                                    components.append(item)
                                else:
                                    pass
                            except TypeError:
                                continue

                    # Get our list of stage codes
                    stages = [stage['code'] for stage in stages_DETAILED]

                    # Generate our dictionary of counts for each stage of the component at each institution
                    component_counts = {}
                    for institution in institutions_ALL:
                        component_counts[institution['code']] = {}
                        for stage in stages:
                            component_counts[institution['code']][stage] = 0
                        component_counts[institution['code']]['TOTAL'] = 0
                    component_counts['TOTAL'] = {}
                    for stage in stages:
                        component_counts['TOTAL'][stage] = 0
                    component_counts['TOTAL']['TOTAL'] = 0

                    # Iterate over each filtered component
                    for component in components:

                        # Fetch the component from the database
                        component_DETAILED = self.session.get(
                            'getComponent', json={'component': component['code']}
                        )

                        # Initialize date (so dateTime for a stage should certainly be <=)
                        date = ['0000', '00', '00']

                        # Initialize the most recent stage code for the component
                        stage_code = None

                        # Iterate over each of the stages of the component
                        for stage in component_DETAILED['stages']:

                            # Get the dateTime
                            date_temp = stage['dateTime'].split('-')

                            # If the dateTime is in our range of interest and more recent the previous dateTime in our range of interest,
                            # fetch it's dateTime and stage code
                            if (
                                date_lower <= date_temp
                                and date_temp <= date_upper
                                and date <= date_temp
                            ):
                                date = date_temp
                                stage_code = stage['code']

                        # If the stage code has not change from None, the component is not in our date range and we want to skip it
                        if not stage_code:
                            continue

                        # Increment our totals for each stage at each institution and overall
                        component_counts[component['institution']['code']][
                            stage_code
                        ] += 1
                        component_counts[component['institution']['code']]['TOTAL'] += 1
                        component_counts['TOTAL'][stage_code] += 1
                        component_counts['TOTAL']['TOTAL'] += 1

                log.info('Printing summary:\n')

                # Order our stages according to the DB (so {'1': <first stage>, '2': <second stage>, etc.})
                stage_order = {}
                for stage in stages_DETAILED:
                    stage_order[stage['order']] = stage['code']

                # Print the count info, using alphabetically order for institution codes
                for institution in sorted(component_counts.keys()):
                    if institution == 'TOTAL':
                        continue
                    print(
                        '    {0}{1}{2}{3}:'.format(
                            colours.BOLD_SEQ,
                            colours.WHITE,
                            institution,
                            colours.RESET_SEQ,
                        )
                    )

                    # When printing the counts at each stage, print the stage codes in the order determined by stage_order
                    for number in sorted(stage_order.keys(), key=int):
                        print(
                            '        {0:<15} = {1}'.format(
                                stage_order[number],
                                component_counts[institution][stage_order[number]],
                            )
                        )
                    print(
                        '        {0:<15} = {1}'.format(
                            'TOTAL', component_counts[institution]['TOTAL']
                        )
                    )

                # Print overall counts
                print(
                    '    {0}{1}{2}{3}:'.format(
                        colours.BOLD_SEQ, colours.WHITE, 'TOTAL', colours.RESET_SEQ
                    )
                )
                for number in sorted(stage_order.keys(), key=int):
                    print(
                        '        {0:<15} = {1}'.format(
                            stage_order[number],
                            component_counts['TOTAL'][stage_order[number]],
                        )
                    )
                print(
                    '        {0:<15} = {1}'.format(
                        'TOTAL', component_counts['TOTAL']['TOTAL']
                    )
                )

                # Break the current summary session
                break

            # Ask the user if they want to get info for another component
            log.info('Session finished.')
            if self.__getYesOrNo(
                'Please type \'y/Y\' to get the summary for another component or type \'n/N\' to quit:'
            ):
                continue

            # Else quit
            else:
                self.__quit()


if __name__ == '__main__':

    try:

        # Open summary interface and run it
        interface = ContentSummaryInferface(Session())
        interface.openInterface()

    # In the case of a keyboard interrupt, quit with error
    except KeyboardInterrupt:
        log.error('Exectution terminated.')
        sys.exit(1)
