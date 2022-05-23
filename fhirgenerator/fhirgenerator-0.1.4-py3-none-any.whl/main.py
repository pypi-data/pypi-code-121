'''Main entrypoint for package'''

from random import randint

from fhirgenerator.resources.r4.encounter import generateEncounter
from fhirgenerator.resources.r4.patient import generatePatient
from fhirgenerator.resources.r4.observation import generateObservation
from fhirgenerator.resources.r4.condition import generateCondition
from fhirgenerator.resources.r4.bundle import generateBundle
from fhirgenerator.resources.r4.medicationStatement import generateMedicationStatement
from fhirgenerator.resources.r4.procedure import generateProcedure
from fhirgenerator.resources.r4.location import generateLocation

from fhirgenerator.resources.uscore_r4.handleUSCore import handleUSCore
from fhirgenerator.resources.uscore_r4.usCorePatient import generateUSCorePatient


def generateResources(config_dict: dict, bundle_type: str = 'collection') -> dict:
    '''Main function for generating resources'''

    final_bundle_entries = []

    # Getting total numbers of each gender
    gender_totals = [round(value * config_dict['numberPatients'] * .01) for value in config_dict['genderMFOU']]
    if sum(gender_totals) > config_dict['numberPatients']:
        gender_totals[0] -= (sum(gender_totals) - config_dict['numberPatients'])
    elif sum(gender_totals) < config_dict['numberPatients']:
        gender_totals[2] += (config_dict['numberPatients'] - sum(gender_totals))

    gender_totals_list = []
    for i in range(0, gender_totals[0]):
        gender_totals_list.append('M')
    for i in range(0, gender_totals[1]):
        gender_totals_list.append('F')
    for i in range(0, gender_totals[2]):
        gender_totals_list.append('O')
    for i in range(0, gender_totals[3]):
        gender_totals_list.append('U')

    for j in range(0, config_dict['numberPatients']):

        patient_age = randint(config_dict['ageMin'], config_dict['ageMax'])
        patient_config = {
            "age": patient_age,
            "gender": gender_totals_list[j],
            "startDate": config_dict['startDate']
        }
        if 'usCorePatient' in config_dict and config_dict['usCorePatient'] is True:
            patient_resource = generateUSCorePatient(patient_config)
        else:
            patient_resource = generatePatient(patient_config)
        final_bundle_entries.append(patient_resource)

        for resource_detail in config_dict['resourceDetails']:
            bundle_entry_list = []
            num_of_cycles = round(resource_detail['cycleLengthInDays'] / config_dict['days'])
            num_of_resources = randint(resource_detail['minOccurrencesPerCycle'], resource_detail['maxOccurrencesPerCycle']) * num_of_cycles
            resource_type = resource_detail['fhirResource']

            if (resource_type.lower()[0:6]) == 'uscore':
                for k in range(0, num_of_resources):
                    bundle_entry_list.append(handleUSCore(resource_detail, patient_resource['id'], config_dict['startDate'], config_dict['days']))

            match resource_type:
                case 'Observation':
                    for k in range(0, num_of_resources):
                        bundle_entry_list.append(generateObservation(resource_detail, patient_resource['id'], config_dict['startDate'], config_dict['days']))
                case 'Condition':
                    for k in range(0, num_of_resources):
                        bundle_entry_list.append(generateCondition(resource_detail, patient_resource['id'], config_dict['startDate'], config_dict['days']))
                case 'Procedure':
                    for k in range(0, num_of_resources):
                        bundle_entry_list.append(generateProcedure(resource_detail, patient_resource['id'], config_dict['startDate'], config_dict['days']))
                case 'MedicationStatement':
                    for k in range(0, num_of_resources):
                        bundle_entry_list.append(generateMedicationStatement(resource_detail, patient_resource['id'], config_dict['startDate'], config_dict['days']))
                case 'Encounter':
                    for k in range(0, num_of_resources):
                        bundle_entry_list.append(generateEncounter(resource_detail, patient_resource['id'], config_dict['startDate'], config_dict['days']))
                case 'Location':
                    for k in range(0, num_of_resources):
                        bundle_entry_list.append(generateLocation())

            final_bundle_entries.extend(bundle_entry_list)

        print(f'Patient number {j+1} generated')

    if 'bundleType' in config_dict:
        bundle_type = config_dict['bundleType']

    final_bundle = generateBundle(final_bundle_entries, type=bundle_type)

    return final_bundle
