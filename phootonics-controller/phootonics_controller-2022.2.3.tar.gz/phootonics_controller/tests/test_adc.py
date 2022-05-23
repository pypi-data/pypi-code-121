import logging

from phootonics_controller.utils.ADC_converter import ADS1263

ADC = ADS1263.ADS1263()
ADC_CHANNEL = 0
REF = 5.08


def initialise_adc():
    if ADC.ADS1263_init() == -1:
        raise Exception('ADC not ininitalized')


def read_adc_detector():
    try:
        adc_value = ADC.ADS1263_GetAll()
        print(adc_value)
        if adc_value[ADC_CHANNEL] >> 31 == 1:
            value = REF * 2 - adc_value[ADC_CHANNEL] * REF / 0x80000000
        else:
            value = adc_value[ADC_CHANNEL] * REF / 0x7fffffff  # 32bit
        return value
    except Exception as e:
        logging.error('could not read ADC value {}'.format(e))
        ADC.ADS1263_Exit()



if __name__ == '__main__':
    initialise_adc()
    value = read_adc_detector()
    print(value)