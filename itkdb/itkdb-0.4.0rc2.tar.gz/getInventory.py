#!/usr/bin/env python
# getInventory.py -- get a list of components specific to an institution from the ITkPD

import argparse, sys, os, json, time
import logging
import click

from itkdb.utilities import colours, colouredLogger
from itkdb import Client

logging.setLoggerClass(colouredLogger)
log = logging.getLogger('getContentSummary')
log.setLevel(logging.INFO)

# Define our inventory object
class Inventory(object):

    # Read in our args
    def __init__(self, args, session):
        self.command = args.command
        self.project = args.project
        self.componentType = args.componentType if args.componentType != None else []
        self.institution = args.institution if args.institution != None else []
        self.savePath = args.savePath
        self.useCurrentLocation = args.useCurrentLocation
        self.includeTrashed = args.includeTrashed
        self.session = session

    # Save a dictionary to json
    def __save(self, data):
        log.info('Saving list to: ' + self.savePath)
        with open(self.savePath, 'w') as file:
            json.dump(data, file)

    # Print a list of names and codes for a dictionary obtained from the ITkPD
    def __printNamesAndCodes(self, list):
        print(
            u'    {0}{1}{2:<60} {3:<20}{4}'.format(
                colours.BOLD_SEQ, colours.WHITE, 'Name:', 'Code:', colours.RESET_SEQ
            )
        )
        for item in list:
            print(u'    {0:<60} {1:<20}'.format(item['name'], item['code']))

    # Generate a list of institutions (and save that list to json)
    def listInstitutions(self):
        log.info('Fetching a list of institutions from the ITkPD...')
        timestamp = time.strftime('%Y/%m/%d-%H:%M:%S')
        institutions = [
            {'name': institution['name'], 'code': institution['code']}
            for institution in self.session.get('listInstitutions')
        ]
        log.info('Printing list of institutions:\n')
        self.__printNamesAndCodes(institutions)
        if self.savePath != None:
            self.__save(
                {
                    'timestamp': timestamp,
                    'function': 'listInstitutions',
                    'args': {},
                    'content': institutions,
                }
            )

    # Generate a list of component types for a specific project code (and save that list to json)
    def listComponentTypes(self):
        log.info(
            'Fetching a list of component types associated with project code \'{0}\' from the ITkPD...'.format(
                self.project
            )
        )
        timestamp = time.strftime('%Y/%m/%d-%H:%M:%S')
        componentTypes = [
            {'name': componentType['name'], 'code': componentType['code']}
            for componentType in self.session.get(
                'listComponentTypes', json={'project': self.project}
            )
        ]
        log.info('Printing list of component types:\n'.format(self.project))
        self.__printNamesAndCodes(componentTypes)
        if self.savePath != None:
            self.__save(
                {
                    'timestamp': timestamp,
                    'function': 'listComponentTypes',
                    'args': {'project': self.project},
                    'content': componentTypes,
                }
            )

    # Generate an inventory list for a specific project, component type(s), and institution (and save that list to json)
    def listInventory(self):

        # Get our list of components filtered by project and component type
        if self.componentType is None or self.institution is None:
            log.error("listInventory needs componentType and institution")
            return

        log.info(
            'Fetching an inventory list associated with project code \'{0}\', component type(s) [\'{1}\'], and institution(s) [\'{2}\'] from the ITkPD...'.format(
                self.project,
                '\', \''.join(self.componentType),
                '\', \''.join(self.institution),
            )
        )
        timestamp = time.strftime('%Y/%m/%d-%H:%M:%S')
        components = self.session.get(
            'listComponents', json={'project': 'S', 'componentType': self.componentType}
        )

        # Filter the components by institution (or by current location)
        if self.useCurrentLocation:
            locationKey = 'currentLocation'
        else:
            locationKey = 'institution'
        if self.includeTrashed:
            filterFunction = (
                lambda component: component[locationKey].get('code') in self.institution
            )
        else:
            filterFunction = (
                lambda component: component[locationKey].get('code') in self.institution
                and not component['trashed']
            )

        # Preallocate our inventory dictionary
        inventory = {}
        for institution in self.institution:
            inventory[institution] = {}
            for componentType in self.componentType:
                inventory[institution][componentType] = []

        # Sort through our list of components and filter our the desired keys
        keys = [
            'dummy',
            'currentGrade',
            'reworked',
            'trashed',
            'assembled',
            'qaPassed',
            'qaState',
        ]
        KeyErrorCounter = 0
        TypeErrorCounter = 0
        for component in components:
            try:
                if filterFunction(component):
                    data = dict((key, component[key]) for key in keys)
                    data['type'] = component['type']['code']
                    data['currentStage'] = component['currentStage']['code']
                    data['code'] = (
                        component['serialNumber']
                        if component['serialNumber'] != None
                        else component['code']
                    )
                    inventory[component[locationKey]['code']][
                        component['componentType']['code']
                    ].append(data)
                else:
                    pass
            except TypeError as error:
                print(
                    u'Encountered TypeError %s for component \'%s\' -- skipping.'
                    % (error, component['code'])
                )
                TypeErrorCounter += 1

        if KeyErrorCounter > 1:
            log.warning('%s components skipped due to key errors.' % KeyErrorCounter)
        if TypeErrorCounter > 1:
            log.warning('%s components skipped due to type errors.' % TypeErrorCounter)

        # Print our inventory and save the associated json
        log.info('Printing inventory list:\n')
        header = {
            'code': 'Code/Serial Number',
            'type': 'Type',
            'currentStage': 'Current Stage',
            'dummy': 'Dummy',
            'currentGrade': 'Current Grade',
            'reworked': 'Reworked',
            'trashed': 'Trashed',
            'assembled': 'Assembled',
            'qaPassed': 'QA Passed',
            'qaState': 'QA State',
        }
        form = '        {code:<40}{type:<15}{currentStage:<20}{dummy:<15}{currentGrade:<20}{reworked:<15}{trashed:<15}{assembled:<15}{qaPassed:<15}{qaState:<15}'
        for institution, componentTypes in inventory.items():
            for componentType, components in componentTypes.items():
                print(
                    u'    {0}{1}{2} / {3} :{4}\n'.format(
                        colours.BOLD_SEQ,
                        colours.WHITE,
                        institution,
                        componentType,
                        colours.RESET_SEQ,
                    )
                )
                print(
                    colours.BOLD_SEQ
                    + colours.WHITE
                    + form.format(**header)
                    + colours.RESET_SEQ
                )
                for component in components:
                    print(form.format(**component))
        if self.savePath != None:
            self.__save(
                {
                    'timestamp': timestamp,
                    'function': 'listInventory',
                    'args': {
                        'project': self.project,
                        'componentType': self.componentType,
                        'institution': self.institution,
                        'useCurrentLocation': self.useCurrentLocation,
                        'includeTrashed': self.includeTrashed,
                    },
                    'content': inventory,
                }
            )

    # Define a function to ask the user a prompt and get a 'confirm' input or a 'quit' input
    def __getConfirm(self, prompt, confirm_msg, quit_msg):
        while True:
            response = click.prompt(prompt).strip()
            if response == '':
                continue
            elif response == confirm_msg:
                return True
            elif response == quit_msg:
                return False
            else:
                del response
                log.warning(
                    'Invalid input. Please enter \'{0}\' or \'{1}\':'.format(
                        confirm_msg, quit_msg
                    )
                )
                continue

    # Define a function for trashing ALL unassembled components at an institution
    # Currently, there is not support for selecting
    def trashUnassembled(self):
        # If using the command 'trashUnassembled', only allow a single institution to be include in the command call
        # This is for safety purposes
        if self.institution is None or len(self.institution) != 1:
            log.error(
                '-i [--institution] may only refer to a single institution code when using the command \'trashUnassembled\': %s'
                % self.institution
            )
            log.debug('Finished with error.')
            return 0  # sys.exit(1)

        # Get our list of components filtered by project and component type
        log.info(
            'Fetching an inventory list associated with project code \'{0}\', component type(s) [\'{1}\'], institution(s) [\'{2}\'], and \'assembled\' == False from the ITkPD...'.format(
                self.project,
                '\', \''.join(self.componentType),
                '\', \''.join(self.institution),
            )
        )
        timestamp = time.strftime('%Y/%m/%d-%H:%M:%S')
        components = self.session.get(
            'listComponents',
            json={'project': self.project, 'componentType': self.componentType},
        )

        # Filter the components by institution (or by current location) and if they are not assembled
        if self.useCurrentLocation:
            locationKey = 'currentLocation'
        else:
            locationKey = 'institution'
        components = list(
            filter(
                lambda component: component[locationKey]['code'] in self.institution
                and not component['assembled']
                and not component['trashed'],
                components,
            )
        )

        # Preallocate our inventory dictionary
        inventory = {}
        for institution in self.institution:
            inventory[institution] = {}
            for componentType in self.componentType:
                inventory[institution][componentType] = []

        # Sort through our list of components and filter our the desired keys
        keys = ['dummy', 'currentGrade', 'assembled', 'qaPassed', 'qaState']
        for component in components:
            data = dict((key, component[key]) for key in keys)
            data['type'] = component['type']['code']
            data['currentStage'] = component['currentStage']['code']
            data['code'] = (
                component['serialNumber']
                if component['serialNumber'] != None
                else component['code']
            )
            inventory[component[locationKey]['code']][
                component['componentType']['code']
            ].append(data)

        # Print the list of items to be trashed
        log.info('The following components will be trashed:\n')
        header = {
            'code': 'Code/Serial Number',
            'type': 'Type',
            'currentStage': 'Current Stage',
            'dummy': 'Dummy',
            'currentGrade': 'Current Grade',
            'assembled': 'Assembled',
            'qaPassed': 'QA Passed',
            'qaState': 'QA State',
        }
        form = '        {code:<40}{type:<15}{currentStage:<20}{dummy:<15}{currentGrade:<20}{assembled:<15}{qaPassed:<15}{qaState:<15}'
        for institution, componentTypes in inventory.items():
            for componentType, components in componentTypes.items():
                print(
                    u'    {0}{1}{2} / {3} :{4}\n'.format(
                        colours.BOLD_SEQ,
                        colours.WHITE,
                        institution,
                        componentType,
                        colours.RESET_SEQ,
                    )
                )
                print(
                    colours.BOLD_SEQ
                    + colours.WHITE
                    + form.format(**header)
                    + colours.RESET_SEQ
                )
                for component in components:
                    print(form.format(**component))

        # Confirm that the user wants to trash the filtered components
        if self.__getConfirm(
            'Please type \'confirm_trash\' to trash the above components or \'quit\' to cancel this action:',
            'confirm_trash',
            'quit',
        ):
            for institution, componentTypes in inventory.items():
                for componentType, components in componentTypes.items():
                    for i, component in enumerate(components):
                        log.info(
                            'Trashing component \'{0}\'...'.format(component['code'])
                        )
                        self.session.post(
                            'setComponentTrashed',
                            json={'component': component['code'], 'trashed': True},
                        )
                        inventory[institution][componentType][i]['trashed'] = True
        else:
            log.info('Trashing aborted.')
            return

        # Confirm that the user does not want to undo the previous action
        if self.__getConfirm(
            'Please type \'undo\' to undo the above action or \'confirm_trash\' to conclude the function:',
            'undo',
            'confirm_trash',
        ):
            for institution, componentTypes in inventory.items():
                for componentType, components in componentTypes.items():
                    for i, component in enumerate(components):
                        log.info(
                            'Un-trashing component \'{0}\'...'.format(component['code'])
                        )
                        self.session.post(
                            'setComponentTrashed',
                            json={'component': component['code'], 'trashed': False},
                        )
                        inventory[institution][componentType][i]['trashed'] = False
            return
        else:
            log.info('Trashing confirmed.')

        # Save the resulting json for the trashed components
        if self.savePath != None:
            self.__save(
                {
                    'timestamp': timestamp,
                    'function': 'listInventory',
                    'args': {
                        'project': self.project,
                        'componentType': self.componentType,
                        'institution': self.institution,
                        'useCurrentLocation': self.useCurrentLocation,
                    },
                    'content': inventory,
                }
            )

    # Define our main function to call the other member functions from
    def main(self):
        if self.command == 'listInventory':
            self.listInventory()
        elif self.command == 'trashUnassembled':
            self.trashUnassembled()
        elif self.command == 'listInstitutions':
            self.listInstitutions()
        elif self.command == 'listComponentTypes':
            self.listComponentTypes()
        return True


if __name__ == '__main__':

    try:

        log.info('*** getInventory.py ***')

        # Define our allowed commands and projects (there are only 4 projects, no sense looking in the ITkPD for what is allowed)
        allowedCommands = [
            'listInstitutions',
            'listComponentTypes',
            'listInventory',
            'trashUnassembled',
        ]
        allowedProjects = ['S', 'P', 'CM', 'CE']

        # Define our parser
        parser = argparse.ArgumentParser(
            description='Get an inventory of components in the ITkPD',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        parser._action_groups.pop()

        # Define our required arguments
        required = parser.add_argument_group('required arguments')
        required.add_argument(
            dest='command',
            type=str,
            default='listInventory',
            choices=allowedCommands,
            help='the ITkPD command to be executed',
        )
        required.add_argument(
            '-p',
            '--project',
            dest='project',
            type=str,
            default='S',
            choices=allowedProjects,
            help='the project to acquire an inventory for',
        )
        required.add_argument(
            '-c',
            '--componentType',
            dest='componentType',
            nargs='*',
            type=str,
            help='the component type(s) to be included in the inventory',
        )
        required.add_argument(
            '-i',
            '--institution',
            dest='institution',
            nargs='*',
            type=str,
            help='the institution(s) to fetch the inventory from',
        )

        # Define our optional arguments
        optional = parser.add_argument_group('optional arguments')
        optional.add_argument(
            '-s',
            '--savePath',
            dest='savePath',
            type=str,
            help='save path for the resulting content (suffix with .json)',
        )
        optional.add_argument(
            '--useCurrentLocation',
            dest='useCurrentLocation',
            action='store_true',
            help='filter by current location when using \'listInventory\'',
        )
        optional.add_argument(
            '--includeTrashed',
            dest='includeTrashed',
            action='store_true',
            help='include trashed components when using \'listInventory\'',
        )

        # Fetch our args
        args = parser.parse_args()

        # Check if our savepath already exists, if the parent directory doesn't exist, and if suffix is not .json
        # Raise an error and quit if any of these are true
        if args.savePath != None:
            if os.path.exists(args.savePath):
                log.error(
                    '-s [--savePath] already exists and cannot be overwritten: '
                    + args.savePath
                )
                log.debug('Finished with error')
                sys.exit(1)
            elif not os.path.exists(os.path.dirname(args.savePath)):
                log.error(
                    '-s [--savePath] parent directory does not exist: '
                    + os.path.dirname(args.savePath)
                )
                log.debug('Finished with error')
                sys.exit(1)
            elif args.savePath[-5:].lower() != '.json':
                log.error(
                    '-s [--savePath] does not end with \'.json\': ' + args.savePath
                )
                log.debug('Finished with error')
                sys.exit(1)

        # Generate our inventory object
        inventory = Inventory(args, Client())

        # Run main
        inventory.main()
        log.debug('Finished successfully')
        sys.exit(0)

    # In the case of a keyboard interrupt, quit with error
    except KeyboardInterrupt:
        log.error('Exectution terminated.')
        log.debug('Finished with error.')
        sys.exit(1)
