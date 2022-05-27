#!/usr/bin/env python
# registerComponent.py -- interface for registering components in the ITk Production Database from the command line

import logging
import json
import sys
import click
from itkdb.utilities import colours, colouredLogger
from itkdb.core import Session

logging.setLoggerClass(colouredLogger)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Define an exception for raising during &CANCEL calls
class Cancel(Exception):
    pass


# Define an exception for raising during &BACK calls
class GoBack(Exception):
    pass


# Define our registration interface
class RegistrationInterface(object):

    # institutions will contain the list of institutions returned by the DB, always_print will always print available code options
    # json will contain the json for the current component to be registered and stage will contain the code of the component's stage
    def __init__(self, session):
        self._session = session
        self.always_print = False
        self.json = {}
        self.stage = None

    # Print a list of names and codes in list (assuming it has those keys) with nice printing
    def __printNamesAndCodes(self, list):
        log.info(
            '    {0}{1}{2:<60} {3:<20}{4}'.format(
                colours.BOLD_SEQ, colours.WHITE, 'Name:', 'Code:', colours.RESET_SEQ
            )
        )
        for item in list:
            log.info('    {0:<60} {1:<20}'.format(item['name'], item['code']))

    # Define a function to provide a prompt to the user and have them select from options
    # Used to get codes from the user, so options includes all possible codes for the current parameter
    def __askForSomething(self, prompt, options):

        # Generate our list of codes
        codes = [item['code'] for item in options]
        log.info(prompt)

        # If always_print, print the available options for the code
        if self.always_print:
            log.info('Printing options:')
            self.__printNamesAndCodes(options)

        while True:

            # Get our user input
            response = click.prompt('Please enter a code from above').upper().strip()

            # If nothing, do nothing
            if response == '':
                continue

            # Escape code &PRINT -- print the available options
            elif response == '&PRINT':
                log.info('Printing options:')
                self.__printNamesAndCodes(options)
                log.info('Please enter a code from above:')

            # Escape code &JSON -- print JSON to show what has already been selected
            elif response == '&JSON':
                log.info('Printing JSON:')
                log.info(json.dumps(self.json, indent=4))
                log.info('Please enter a code:')

            # Escape code &CANCEL -- raise our Cancel exception
            elif response == '&CANCEL':
                log.warning('Registration cancelled.')
                raise Cancel

            # If the user enters a valid code, return that code and its index
            elif response in codes:
                i = codes.index(response)
                log.info('Using code: {0} ({1})'.format(response, options[i]['name']))
                return i, response

            # Else the input is invalid
            else:
                log.info('Invalid input, please try again:')
                continue

    # Define a function for getting the serial number from the user
    def __askForSerialNumber(self, first_part_of_sn):

        log.info('Serial number is required to be manually entered the component type.')

        while True:

            # Get our user input
            response = click.prompt(
                'Enter the last 7 digits of the component\'s serial number'
            ).strip()

            # If nothing, do nothing
            if response == '':
                continue

            # Escape code &JSON -- print JSON to show what has already been selected
            elif response == '&JSON':
                log.info('Printing JSON:')
                log.info(json.dumps(self.json, indent=4))
                log.info('Please enter a serial number:')

            # Escape code &CANCEL -- raise our Cancel exception
            elif response == '&CANCEL':
                log.warning('Registration cancelled.')
                raise Cancel

            # If the user enters a valid serial number, return that number (string)
            elif len(response) == 7 and response.isdigit():
                serial_number = first_part_of_sn + response
                log.info('Using serial number: ' + serial_number)
                return serial_number

            # Else the input is invalid
            else:
                log.info('Invalid input, please enter a 7 digit serial number:')
                continue

    # Print the code, name, data type, required, and description for a component's property
    def __printProperty(self, property):
        keys = property.keys()
        if 'code' in keys:
            log.info(
                '    {0}{1}Code{2}:        '.format(
                    colours.WHITE, colours.BOLD_SEQ, colours.RESET_SEQ
                )
                + '%s' % property['code']
            )
        if 'name' in keys:
            log.info(
                '    {0}{1}Name{2}:        '.format(
                    colours.WHITE, colours.BOLD_SEQ, colours.RESET_SEQ
                )
                + '%s' % property['name']
            )
        if 'dataType' in keys:
            log.info(
                '    {0}{1}Data Type{2}:   '.format(
                    colours.WHITE, colours.BOLD_SEQ, colours.RESET_SEQ
                )
                + '%s' % property['dataType']
            )
        if 'required' in keys:
            log.info(
                '    {0}{1}Required{2}:    '.format(
                    colours.WHITE, colours.BOLD_SEQ, colours.RESET_SEQ
                )
                + '%s' % property['required']
            )
        if 'default' in keys:
            log.info(
                '    {0}{1}Default{2}:     '.format(
                    colours.WHITE, colours.BOLD_SEQ, colours.RESET_SEQ
                )
                + '%s' % property['default']
            )
        if 'unique' in keys:
            log.info(
                '    {0}{1}Unique{2}:      '.format(
                    colours.WHITE, colours.BOLD_SEQ, colours.RESET_SEQ
                )
                + '%s' % property['unique']
            )
        if 'snPosition' in keys:
            log.info(
                '    {0}{1}SN Positon{2}:  '.format(
                    colours.WHITE, colours.BOLD_SEQ, colours.RESET_SEQ
                )
                + '%s' % property['snPosition']
            )
        if 'description' in keys:
            log.info(
                '    {0}{1}Description{2}: '.format(
                    colours.WHITE, colours.BOLD_SEQ, colours.RESET_SEQ
                )
                + '%s' % property['description']
            )
        if property['dataType'] == 'codeTable':
            log.info(
                '    {0}{1}Code Table{2}:'.format(
                    colours.WHITE, colours.BOLD_SEQ, colours.RESET_SEQ
                )
            )
            row_format = '        {:<15}{:<15}'
            header = ['Code', 'Value']
            log.info(
                colours.WHITE
                + colours.BOLD_SEQ
                + row_format.format(*header)
                + colours.RESET_SEQ
            )
            code_table = {item['code']: item['value'] for item in property['codeTable']}
            for code in code_table.keys():
                row = [code, code_table[code]]
                log.info(row_format.format(*row))

    # Convert reponse to specific type
    def __convertToType(self, response, type):

        # If the wrong input is provided, the code will throw a ValueError
        if type == 'string':
            return str(response)
        elif type == 'float':
            return float(response)
        elif type == 'integer':
            return int(response)

        # For boolean, we'll require specific inputs or else throw a ValueError
        elif type == 'boolean':
            if response.lower() in ['1', 'true', 't']:
                return True
            elif response.lower() in ['0', 'False', 'f']:
                return False
            else:
                raise ValueError

        # For a code table, we'll require keys or values to be enter or else throw a ValueError
        elif type[0] == 'codeTable':
            code_table = {item['code']: item['value'] for item in type[1]}
            if response in code_table.keys():
                return response
            else:
                raise ValueError

        return None

    # Give the user a prompt to enter a value for a property indexed by i
    def __getProperty(self, prompt, property, i):

        # Print the relevant info for that property
        self.__printProperty(property)

        while True:

            # Get our input
            response = click.prompt(prompt).strip()

            # If nothng, do nothing
            if response == '':
                continue

            # Escape code &JSON -- print JSON to show what has already been selected
            elif response.upper() == '&JSON':
                log.info('Printing JSON:')
                log.info(json.dumps(self.json, indent=4))
                log.info('Please enter a value for the property:')

            # Escape code &SKIP -- skip the current property if it's not required
            elif response.upper() == '&SKIP':

                # Check if it's required
                if property['required']:
                    log.warning('Property is required and cannot be skipped.')
                    log.info('Please enter a value:')
                    continue
                else:
                    log.info(
                        'Skipping property: {0} ({1}).'.format(
                            property['code'], property['name']
                        )
                    )

                    # Increment i to move onto the next property, and return None for the current property's value
                    return i + 1, None

            # Escape code &BACK -- go back to edit the previous property by raising Back exception
            elif response.upper() == '&BACK':
                log.info('Going back.')
                raise GoBack

            # Escape code &CANCEL -- raise our Cancel exception
            elif response.upper() == '&CANCEL':
                log.warning('Registration cancelled.')
                raise Cancel

            # Else, we assume the user enter a property value
            else:
                try:

                    # Try to convert the input string to its correct data type
                    if property['dataType'] == 'codeTable':
                        property['dataType'] = ['codeTable', property['codeTable']]
                    response_converted = self.__convertToType(
                        response, property['dataType']
                    )
                    log.info(
                        'Using property: {0} ({1}) = {2}'.format(
                            property['code'], property['name'], response
                        )
                    )

                    # Return i + 1 to move onto the next property and return our converted property value
                    return i + 1, response_converted

                # Catch our ValueErrors for invalid input
                except ValueError:
                    log.info('Invalid input, please try again:')
                    continue

    # Define a function to ask the user a prompt and get a yes or no response
    def __getYesOrNo(self, prompt):
        while True:

            # Get our input
            response = click.prompt(prompt).strip().lower()

            # Skip empty inputs
            if response == '':
                continue

            # If yes, return True
            elif response in ['y', 'yes', '1']:
                return True

            # If no, return False
            elif response in ['n', 'no', '0']:
                return False

            # Else the input is invalid and ask again
            else:
                del response
                log.info('Invalid input. Please enter \'y/Y\', or \'n/N\':')
                continue

    # Define a function for opening and running the registration interface.
    def openInterface(self):

        # Fetch our list of institutions if it's empty
        log.info('Running ITk Production Database component registration interface.')
        institutions = self._session.get('listInstitutions')['pageItemList']

        # Get a value for always_print
        self.always_print = self.__getYesOrNo(
            'To always print the available input options for codes, please type \'y/Y\' or type \'n/N\' to suppress this output'
        )
        log.info(
            'Use escape codes &PRINT to print the available options, &JSON to print the current JSON for your component, or &CANCEL to cancel the registration at any time.'
        )

        # The first while loops iterates over registration sessions for multiple components
        while True:

            # The second while loop iterates over a single registration session (I use break statements when &CANCEL codes are entered)
            while True:

                # Reset JSON and stage
                self.json = {}
                self.stage = None

                try:

                    # Get our institution code from the listing in institutions
                    # Here, i (j, k, etc.) refer to the selected element in the list of options
                    i, self.json['institution'] = self.__askForSomething(
                        'Enter your institution code', institutions
                    )

                    # Only fetch the projects associated with that institution
                    projects = institutions[i]['componentType']

                    # If no projects, break
                    if len(projects) == 0:
                        log.warning(
                            'Project: there are no projects associated with institution code \'{0}\'.'.format(
                                self.json['institution']
                            )
                        )
                        log.info(
                            'Please contact the Production Database team to get the appropriate rights.'
                        )
                        break

                    # If only one project, fetch it without prompt
                    elif len(projects) == 1:
                        log.warning('Project: only one option available.')
                        log.info(
                            'Using code: {0} ({1})'.format(
                                projects[0]['code'], projects[0]['name']
                            )
                        )

                        # Here, we are directly adding the code to JSON
                        j, self.json['project'] = 0, projects[0]['code']

                    # Else, have the user enter the project code
                    else:
                        j, self.json['project'] = self.__askForSomething(
                            'Enter a project code associated with your institution',
                            projects,
                        )

                    # Only fetch the component types associated with that project
                    component_types = projects[j]['itemList']

                    # Repeat the same procedure as above for the component type
                    if len(component_types) == 0:
                        log.warning(
                            'Component type: there are no component types associated project code \'{0}\' at your institution.'.format(
                                self.json['project']
                            )
                        )
                        log.info(
                            'Please contact the Production Database team to get the appropriate rights.'
                        )
                        break
                    elif len(component_types) == 1:
                        log.warning('Component type: only one option available.')
                        log.info(
                            'Using code: {0} ({1})'.format(
                                component_types[0]['code'], component_types[0]['name']
                            )
                        )
                        k, self.json['componentType'] = 0, component_types[0]['code']
                    else:
                        k, self.json['componentType'] = self.__askForSomething(
                            'Enter a component type code associated with your project',
                            component_types,
                        )

                    # Fetch all of the remaining info about that component type by ID
                    component = self._session.get(
                        'getComponentType', data={'id': component_types[k]['id']}
                    )

                    # Only get the types (e.g., for ABC, ABC130 or ABC*) that are associated with that particular component type
                    types = component['types']

                    # Repeat the same procedure as above for the type
                    if len(types) == 0:
                        log.warning(
                            'Type: there are no types associated with component type code \'{0}\' at your institution.'.format(
                                self.json['componentType']
                            )
                        )
                        log.info(
                            'Please contact the Production Database team to get the appropriate rights.'
                        )
                        break
                    elif len(types) == 1:
                        log.info('Type: only one option available.')
                        log.info(
                            'Using code: {0} ({1})'.format(
                                types[0]['code'], types[0]['name']
                            )
                        )
                        ii, self.json['type'] = 0, types[0]['code']
                    else:
                        ii, self.json['type'] = self.__askForSomething(
                            'Enter a type code associated with your component type',
                            types,
                        )

                    # Only fetch the subprojects associated with that type
                    subprojects = types[ii]['subprojects']

                    # Repeat the same procedure as above for the subproject (likely will always default to the elif statment)
                    if len(subprojects) == 0:
                        log.warning(
                            'Subproject: there are no subprojects associated with type code \'{0}\' at your institution.'.format(
                                self.json['type']
                            )
                        )
                        log.info(
                            'Please contact the Production Database team to get the appropriate rights.'
                        )
                        break
                    elif len(subprojects) == 1:
                        log.warning('Subproject: only one option available.')
                        log.info(
                            'Using code: {0} ({1})'.format(
                                subprojects[0]['code'], subprojects[0]['name']
                            )
                        )
                        jj, self.json['subproject'] = 0, subprojects[0]['code']
                    else:
                        jj, self.json['subproject'] = self.__askForSomething(
                            'Enter a subproject code associated with your type',
                            subprojects,
                        )

                    # Fetch the stages associated with our component type
                    stages = component['stages']

                    # Repeat the same procedure as above for the stage (but instead we output this result to stage)
                    if stages == None:
                        log.warning(
                            'Stage: there are no stages associated with component type code \'{0}\' -- skipping.'.format(
                                self.json['componentType']
                            )
                        )
                    elif len(stages) == 1:
                        log.warning('Stage: only one option available.')
                        log.info(
                            'Using code: {0} ({1})'.format(
                                stages[0]['code'], stages[0]['name']
                            )
                        )
                        kk, self.stage = 0, stages[0]['code']
                    else:
                        kk, self.stage = self.__askForSomething(
                            'Enter a stage code associated with your component type',
                            stages,
                        )

                    # If the SN is required, ask the user to enter it manually
                    try:
                        snAutomatically = component['snAutomatically']
                    except KeyError:
                        snAutomatically = False
                    try:
                        snRequired = component['snRequired']
                    except KeyError:
                        snRequired = False
                    if snAutomatically or not snRequired:
                        pass
                    else:
                        if component['snComponentIdentifier'] == '':
                            for type in component['types']:
                                if (
                                    type['code'] == self.json['type']
                                    and type['existing']
                                ):
                                    first_part_of_sn = (
                                        '20U'
                                        + self.json['subproject']
                                        + type['snComponentIdentifier']
                                    )
                        else:
                            first_part_of_sn = (
                                '20U'
                                + self.json['subproject']
                                + component['snComponentIdentifier']
                            )
                        serial_number = self.__askForSerialNumber(first_part_of_sn)
                        self.json['serialNumber'] = serial_number

                # Catch our &CANCEL responses from __askForSomething
                except Cancel:
                    break

                # Print what is currently selected
                log.info(
                    'Using: institution = {institution}, project = {project}, componentType = {componentType}, type = {type}, subproject = {subproject}'.format(
                        **self.json
                    )
                )
                log.info('Now adding properties.')
                log.info(
                    'Use escape codes &JSON to print the current JSON, &SKIP to skip a property which is not required, &BACK to make a correction, or &CANCEL to cancel the registration.'
                )

                # Get the properties associated with our component type
                properties = component['properties']
                self.json['properties'] = {}

                # i now refers to which property in properties we are considering
                i = 0

                # If not properties to add, skip
                if properties == []:
                    log.warning('No properties to add -- skipping.')

                # Else iterate over our properties
                else:
                    try:

                        # This while loop iterates over the properties
                        while True:

                            # If i reaches the end of the length of properties, we know we have added all and can break
                            if i == len(properties):
                                log.info('All properties added.')
                                break

                            # If we try to go &BACK below 0, set i to 0
                            elif i < 0:
                                log.warning('Can\'t go back any further.')
                                i = 0
                                continue

                            # Else ask for a property and update json['properties']
                            else:
                                try:
                                    i, value = self.__getProperty(
                                        'Please entry an appropriate value for the above property',
                                        properties[i],
                                        i,
                                    )
                                    self.json['properties'][
                                        properties[i - 1]['code']
                                    ] = value
                                except GoBack:
                                    i -= 1
                                    continue

                    # Catch our Cancels in the case of &CANCEL
                    except Cancel:
                        break

                # Show the user what is to be registered
                log.info('Your component will be registered using JSON:')
                log.info(json.dumps(self.json, indent=4))
                log.info('With stage:')
                log.info(
                    '    {0}{1}Stage{2} = {3}'.format(
                        colours.WHITE, colours.BOLD_SEQ, colours.RESET_SEQ, self.stage
                    )
                )

                # Ask the user if they want to upload the above
                if self.__getYesOrNo(
                    'Please type \'y/Y\' to confirm the registration or \'n/N\' to cancel'
                ):

                    # If yes, register the component and grab its component code
                    component_code = self.registerComponent(self.json)['component'][
                        'code'
                    ]

                    # If the component has stages, use that component code to set the stage for that component
                    if self.stage != None:
                        self.setStage(component=component_code, stage=self.stage)
                    log.info('Registered successfully.')
                    break

                # Else, the registration is cancelled
                else:
                    log.warning('Registration cancelled.')
                    break

            # Ask the user if they want to register another component
            log.info('Session finished.')
            if self.__getYesOrNo(
                'Please type \'y/Y\' to register another component or type \'n/N\' to quit'
            ):
                continue

            # Else quit
            else:
                log.info("Finished successfully.")
                sys.exit(0)

    # Register a component in the DB and return the JSON for that component
    def registerComponent(self, data):
        component = self._session.post('registerComponent', json=data)
        return component

    # Set the stage for registered component
    def setStage(self, component=None, stage=None):
        self._session.post(
            'setComponentStage', json={'component': component, 'stage': stage}
        )


if __name__ == "__main__":
    interface = RegistrationInterface(Session())
    interface.openInterface()
    sys.exit(0)
