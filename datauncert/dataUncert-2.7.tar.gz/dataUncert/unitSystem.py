import logging
logger = logging.getLogger(__name__)
import numpy as np


class _unitConversion():

    def __init__(self, scale, offset) -> None:
        self.scale = scale
        self.offset = offset

    def convertToSI(self, upper=True, isComposite=False):
        if upper:
            if isComposite:
                return [self.scale, 0]
            else:
                return [self.scale, self.offset]
        else:
            return self.convertFromSI(not upper, isComposite)

    def convertFromSI(self, upper=True, isComposite=False):
        if upper:
            if isComposite:
                return [1 / self.scale, 0]
            else:
                return [1 / self.scale, -self.offset / self.scale]
        else:
            return self.convertToSI(not upper, isComposite)


class unit():
    def __init__(self) -> None:

        unit = {
            '1': _unitConversion(1, 0),
            "": _unitConversion(1, 0)
        }

        force = {
            'N': _unitConversion(1, 0)
        }

        mass = {
            'g': _unitConversion(1 / 1000, 0)
        }

        energy = {
            'J': _unitConversion(1, 0),
        }

        power = {
            'W': _unitConversion(1, 0)
        }

        pressure = {
            'Pa': _unitConversion(1, 0),
            'bar': _unitConversion(1e5, 0)
        }

        temperature = {
            'K': _unitConversion(1, 0),
            'C': _unitConversion(1, 273.15),
            'F': _unitConversion(5 / 9, 273.15 - 32 * 5 / 9)
        }

        time = {
            's': _unitConversion(1, 0),
            'min': _unitConversion(60, 0),
            'h': _unitConversion(60 * 60, 0),
            'yr': _unitConversion(60 * 60 * 24 * 365, 0)
        }

        volume = {
            'm3': _unitConversion(1, 0),
            'L': _unitConversion(1 / 1000, 0)
        }

        length = {
            'm': _unitConversion(1, 0)
        }

        current = {
            'A': _unitConversion(1, 0)
        }

        voltage = {
            'V': _unitConversion(1, 0)
        }

        frequency = {
            'Hz', _unitConversion(1, 0)
        }

        self.units = {
            'kg-m/s2': force,
            'kg/m-s2': pressure,
            's': time,
            'K': temperature,
            'm3': volume,
            'm': length,
            'kg-m2/s2': energy,
            'kg-m2/s3': power,
            'kg': mass,
            'A': current,
            'V': voltage,
            '1': unit,
            'Hz': frequency
        }

        self.prefixes = {
            'µ': 1e-6,
            'm': 1e-3,
            'k': 1e3,
            'M': 1e6
        }

        logger.debug('Created new unit conversion object')

    def _isUnitKnown(self, unit):
        logger.debug(f'Determine if the unit {unit} is known within the unitsystem')

        upper, lower = self._splitCompositeUnit(unit)
        units = upper + lower
        logger.debug(f'The unit {unit} is split in to its parts of {units}')

        if len(units) > 1:
            logger.debug(f'There are more than one unit in {units}. Therefore it is determined if all these elements are known.')
            for unit in units:
                self._isUnitKnown(unit)
        else:
            unit = units[0]

        unitWithoutExponent, _ = self._removeExponentFromUnit(unit)
        logger.debug(f'The unit {unit} was reduced to {unitWithoutExponent} by removing the exponent')

        # search for the unit
        for _, unitDict in self.units.items():
            if unitWithoutExponent in unitDict:
                return

        # The unit was not found. This must be because the unit has a prefix
        prefix = unitWithoutExponent[0:1]
        unitWithoutExponent = unitWithoutExponent[1:]
        logger.debug('The unit was not known in the unitsytem. It was therefore split in to a prefix of {prefix} and a unit of {unit}')
        if prefix not in self.prefixes:
            logger.error(f'The unit ({prefix}{unitWithoutExponent}) was not found. Therefore it was interpreted as a prefix and a unit. However the prefix ({prefix}) was not found')
            raise ValueError(f'The unit ({prefix}{unitWithoutExponent}) was not found. Therefore it was interpreted as a prefix and a unit. However the prefix ({prefix}) was not found')

        # look for the unit without the prefix
        for _, unitDict in self.units.items():
            if unitWithoutExponent in unitDict:
                return

        # The unit was not found
        logger.error(f'The unit ({prefix}{unit}) was not found. Therefore it was interpreted as a prefix and a unit. However the unit ({unit}) was not found')
        raise ValueError(f'The unit ({prefix}{unit}) was not found. Therefore it was interpreted as a prefix and a unit. However the unit ({unit}) was not found')

    def convertToSI(self, value, unit, isUncert=False):
        """
        Function to convert a value to a unit in the SI unit system
            isComposite - is true if the unit is composed of multiple different units. This disables the offset ei from Celsius to Kelvin.
        """
        logger.debug(f'The value {value} is converted to the SI unit {unit}')

        upper, lower = self._splitCompositeUnit(unit)
        logger.debug(f'The unit {unit} is split in to its upper and lower parts: {upper}, {lower}')

        if isUncert:
            isComposite = True
            logger.debug(f'The value to convert is an uncertanty. Therefore the offset in the scaling to the SI unit system is disabled.')
        else:
            if (len(lower) == 0 and len(upper) == 1):
                isComposite = False
                logger.debug(f'The unit is not a composite unit. Therefore the offset in the scaling to the SI unit system is enabled.')
            else:
                isComposite = True
                logger.debug(f'The unit is a composite unit. Therefore the offset in the scaling to the SI unit system is disabled.')

        logger.debug('The SI unit is initialized as an empty list of upper and lower units')
        unitUpper = []
        unitLower = []

        logger.debug('The upper units are iterated over and their conversion to SI unit is used to scale the value')
        for unit in upper:
            conversion, u, exp = self._convert(unit, toSI=True, upper=True, isComposite=isComposite)
            logger.debug(f'The exponent of {exp} was removed from the unit {unit}')
            logger.debug(f'The unit {unit} is converted to the SI unit {u}. This is done with a linear scaling of {conversion[0]} and an offset of {conversion[1]}')

            logger.debug(f'The value of {value} will be scaled using the conversion {exp} times')
            for _ in range(exp):
                value = value * conversion[0] + conversion[1]
            logger.debug(f'The value was scaled to {value}')

            siUpper, siLower = self._splitCompositeUnit(u)
            logger.debug(f'The unit {u} is split in to an upper and a lower unit: {siUpper}, {siLower}')
            logger.debug(f'The upper and lower units of {u} is iterated over and the exponent is removed')
            for up in siUpper:
                u, siExp = self._removeExponentFromUnit(up)
                logger.debug(f'The upper unit {up} is split in to the unit {u} and the exponent {siExp}')
                logger.debug(f'The exponent {siExp} is scaled with the original exponent {exp} of the unit {unit}')
                upExp = siExp * exp
                if upExp != 1:
                    u += str(upExp)
                logger.debug(f'The unit and the exponent are combined in to {u}')

                unitUpper.append(u)
                logger.debug(f'The unit {u} is appended to the list of upper units: {unitUpper}')

            for low in siLower:
                u, siExp = self._removeExponentFromUnit(low)
                logger.debug(f'The lower unit {low} is split in to the unit {u} and the exponent {siExp}')
                logger.debug(f'The exponent {siExp} is scaled with the original exponent {exp} of the unit {unit}')
                lowExp = siExp * exp
                if lowExp != 1:
                    u += str(lowExp)
                logger.debug(f'The unit and the exponent are combined in to {u}')

                unitLower.append(u)
                logger.debug(f'The unit {u} is appended to the list of the lower units_ {unitLower}')

        logger.debug('The lower units are iterated over and their conversion to SI unit is used to scale the value')
        for unit in lower:
            conversion, u, exp = self._convert(unit, toSI=True, upper=False, isComposite=isComposite)
            logger.debug(f'The exponent of {exp} was removed from the unit {unit}')
            logger.debug(f'The unit {unit} is converted to the SI unit {u}. This is done with a linear scaling of {conversion[0]} and an offset of {conversion[1]}')

            logger.debug(f'The value of {value} will be scaled using the conversion {exp} times')
            for _ in range(exp):
                value = value * conversion[0] + conversion[1]
            logger.debug(f'The value was scaled to {value}')

            siUpper, siLower = self._splitCompositeUnit(u)
            logger.debug(f'The unit {u} is split in to an upper and a lower unit: {siUpper}, {siLower}')
            logger.debug(f'The upper and lower units of {u} is iterated over and the exponent is removed')
            for up in siUpper:
                u, siExp = self._removeExponentFromUnit(up)
                logger.debug(f'The upper unit {up} is split in to the unit {u} and the exponent {siExp}')
                logger.debug(f'The exponent {siExp} is scaled with the original exponent {exp} of the unit {unit}')
                upExp = siExp * exp
                if upExp != 1:
                    u += str(upExp)
                logger.debug(f'The unit and the exponent are combined in to {u}')

                unitLower.append(u)
                logger.debug(f'The unit {u} is appended to the list of lower units: {unitLower}')
            for low in siLower:
                u, siExp = self._removeExponentFromUnit(low)
                logger.debug(f'The lower unit {low} is split in to the unit {u} and the exponent {siExp}')
                logger.debug(f'The exponent {siExp} is scaled with the original exponent {exp} of the unit {unit}')
                lowExp = siExp * exp
                if lowExp != 1:
                    u += str(lowExp)
                logger.debug(f'The unit and the exponent are combined in to {u}')

                unitUpper.append(u)
                logger.debug(f'The unit {u} is appended to the list of the upper units: {unitUpper}')

        # cancle out upper and lower
        logger.debug(f'The combined upper and lower units are {unitUpper} and {unitLower}')
        unitUpper, unitLower = self._cancleUnits(unitUpper, unitLower)
        logger.debug(f'The upper and lower units are cancled with each other. They are now reduced to {unitUpper} and {unitLower}')

        # combine the upper and lower
        outUnit = self._combineUpperAndLower(unitUpper, unitLower)
        logger.debug(f'The upper and lower units are combined in to the output unit {outUnit}')

        logger.debug(f'The value of {value} and unit {unit} is returned')
        return value, outUnit

    def convertFromSI(self, value, unit, isUncert=False):
        """
        Function to convert a value from a unit in the SI unit system
            isComposite - is true if the unit is composed of multiple different units. This disables the offset ei from Celsius to Kelvin.
        """
        logger.debug(f'The value {value} is converted from SI to the unit {unit}')

        upper, lower = self._splitCompositeUnit(unit)
        logger.debug(f'The unit {unit} is split in to the upper and lower units {upper} and {lower}')

        if isUncert:
            isComposite = True
            logger.debug(f'The value to convert is an uncertanty. Therefore the offset in the scaling to the SI unit system is disabled.')
        else:
            if (len(lower) == 0 and len(upper) == 1):
                isComposite = False
                logger.debug(f'The unit is not a composite unit. Therefore the offset in the scaling to the SI unit system is enabled.')
            else:
                isComposite = True
                logger.debug(f'The unit is a composite unit. Therefore the offset in the scaling to the SI unit system is disabled.')

        logger.debug('The upper units are iterated over')
        for up in upper:
            conversion, u, exp = self._convert(up, toSI=False, upper=True, isComposite=isComposite)
            logger.debug(f'The exponent of {exp} was removed from the unit {up}')
            logger.debug(f'The unit {up} is converted to the SI unit {u}. This is done with a linear scaling of {conversion[0]} and an offset of {conversion[1]}')

            logger.debug(f'The value of {value} is converted {exp} times')
            for _ in range(exp):
                value = value * conversion[0] + conversion[1]
            logger.debug(f'The value was scaled to {value}')

        logger.debug('The lower units are iterated over')
        for low in lower:
            conversion, u, exp = self._convert(low, toSI=False, upper=False, isComposite=isComposite)
            logger.debug(f'The exponent of {exp} was removed from the unit {low}')
            logger.debug(f'The unit {low} is converted to the SI unit {u}. This is done with a linear scaling of {conversion[0]} and an offset of {conversion[1]}')

            logger.debug(f'The value of {value} is converted {exp} times')
            for _ in range(exp):
                value = value * conversion[0] + conversion[1]
            logger.debug(f'The value was scaled to {value}')

        logger.debug(f'The value {value} and the unit {unit} is returned')
        return value, unit

    def _splitCompositeUnit(self, compositeUnit):
        logger.debug(f'Splitting the unit {compositeUnit} in to its parts')

        logger.debug('Removing any illegal symbols')
        special_characters = """!@#$%^&*()+?_=.,<>\\"""
        if any(s in compositeUnit for s in special_characters):
            logger.error('The unit can only contain slashes (/), hyphens (-)')
            raise ValueError('The unit can only contain slashes (/), hyphens (-)')

        logger.debug('Removing any spaces')
        compositeUnit = compositeUnit.replace(' ', '')

        slash = '/'
        if slash in compositeUnit:
            logger.debug('A slash was found in the unit. This indicates that the unit has an upper and a lower part')
            index = compositeUnit.find(slash)
            upper = compositeUnit[0:index]
            lower = compositeUnit[index + 1:]

            # check for multiple slashes
            if slash in upper or slash in lower:
                logger.error('A unit can only have a single slash (/)')
                raise ValueError('A unit can only have a single slash (/)')

            upper = upper.split('-')
            lower = lower.split('-')
            logger.debug('Split the upper and lower based on hyphens (-). Upper is therefore {upper} and lower is {lower}')

        else:
            upper = compositeUnit.split('-')
            lower = []
            logger.debug(f'No slashes were found. This indicates that the unit has no denominator. The upper is therefore {upper} whereas the lower is an empty list')

        logger.debug(f'The unit {compositeUnit} was split in an upper and a lower unit: {upper} and {lower}')
        return upper, lower

    def _removeExponentFromUnit(self, unit):
        logger.debug(f'The exponent is removed from the unit {unit}')

        logger.debug(f'Finding any integers in the unit {unit}')
        num = []
        num_indexes = []
        for i, s in enumerate(unit):
            if s.isdigit():
                logger.debug(f'The integer {s} was found at index {i}')
                num.append(s)
                num_indexes.append(i)

        logger.debug(f'Determine if all integers are placed consequtively')
        for i in range(len(num_indexes) - 1):
            elem_curr = num_indexes[i]
            elem_next = num_indexes[i + 1]
            if not elem_next == elem_curr + 1:
                logger.error('All numbers in the unit has to be grouped together')
                raise ValueError('All numbers in the unit has to be grouped together')

        logger.debug(f'Determien if the last integer is placed at the end of the unit')
        if len(num) != 0:
            if max(num_indexes) != len(unit) - 1:
                logger.error('Any number has to be placed at the end of the unit')
                raise ValueError('Any number has to be placed at the end of the unit')

        logger.debug(f'Remove the inters from the unit')
        if len(num) != 0:
            for i in reversed(num_indexes):
                unit = unit[0:i] + unit[i + 1:]

        logger.debug('Combine the exponents')
        if len(num) != 0:
            exponent = int(''.join(num))
        else:
            exponent = 1

        logger.debug('Ensure that the entire use was not removed by removing the integers')
        if len(unit) == 0:
            logger.debug('No symbols are left after removing the integers')
            if exponent == 1:
                unit = '1'
                logger.debug('The integers removed was equal to 1. This is due to the unit THE unit')
            else:
                logger.error(f'The unit {unit} was stripped of all integers which left no symbols in the unit. This is normally due to the integers removed being equal to 1, as the unit is THE unit. Howver, the intergers removed was not equal to 1. The unit is therefore not known.')
                raise ValueError(
                    f'The unit {unit} was stripped of all integers which left no symbols in the unit. This is normally due to the integers removed being equal to 1, as the unit is THE unit. Howver, the intergers removed was not equal to 1. The unit is therefore not known.')

        logger.debug(f'Return the unit {unit} and the exponent {exponent}')
        return unit, exponent

    def _convert(self, unit, toSI=True, upper=True, isComposite=False):
        """
        Function to return the scaling to convert a unit to or from the SI unit system
            tiSI - is true if you are converting to the SI unit system
            upper - is true if the unit is in the numerator.
            isComposite - is true if the unit is composed of multiple different units. This disables the offset ei from Celsius to Kelvin.
        """

        if toSI:
            logger.debug(f'A conversion will be created in order to convert to SI units from the unit {unit} when the unit {unit} is {"on top of" if upper else "below of"} a fraction')
        else:
            logger.debug(f'A conversion will be created in order to convert from SI units from the unit {unit} when the unit {unit} is {"on top of" if upper else "below of"} a fraction')

        unit, exponent = self._removeExponentFromUnit(unit)
        logger.debug(f'The exponent {exponent} and {unit} was removed from each other')
        # search for the unit
        isFound = False
        for siUnit, unitDict in self.units.items():
            if unit in unitDict:
                conversion = unitDict[unit]
                isFound = True
                break

        if isFound:
            logger.debug('The unit is known')

            if toSI:
                out = conversion.convertToSI(upper, isComposite)
            else:
                out = conversion.convertFromSI(upper, isComposite)

            logger.debug(f'A conversion was found with scaling {out[0]} and offset {out[1]}')

            # the unt was found without looking for the prefix. Therefore the prefix must be 1
            prefix = 1
        else:
            logger.debug(f'The unit {unit} was not found. This must be because the unit has a prefix')

            prefix = unit[0:1]
            unit = unit[1:]
            if prefix not in self.prefixes:
                logger.error(f'The unit ({prefix}{unit}) was not found. Therefore it was interpreted as a prefix and a unit. However the prefix ({prefix}) was not found')
                raise ValueError(f'The unit ({prefix}{unit}) was not found. Therefore it was interpreted as a prefix and a unit. However the prefix ({prefix}) was not found')

            # look for the unit without the prefix
            isFound = False
            for siUnit, unitDict in self.units.items():
                if unit in unitDict:
                    conversion = unitDict[unit]
                    isFound = True
                    break

            # check if the unit was found
            if not isFound:
                logger.error(f'The unit ({prefix}{unit}) was not found. Therefore it was interpreted as a prefix and a unit. However the unit ({unit}) was not found')
                raise ValueError(f'The unit ({prefix}{unit}) was not found. Therefore it was interpreted as a prefix and a unit. However the unit ({unit}) was not found')

            # create the conversion
            if toSI:
                out = conversion.convertToSI(upper, isComposite)
            else:
                out = conversion.convertFromSI(upper, isComposite)

            logger.debug(f'A conversion was found with scaling {out[0]} and offset {out[1]}')

            # The prefix is inverted if the conversion is not to SI
            prefix = self.prefixes[prefix]
            if not upper:
                prefix = 1 / prefix
            if not toSI:
                prefix = 1 / prefix

        logger.debug(f'The scaling of the conversion is multied with the scaling of the prefix. The scaling is therefore increased from {out[0]} to {out[0]*prefix}')
        out[0] *= prefix

        logger.debug(f'The conversion of {out}, the corresponding SI unit of {siUnit} and the exponent {exponent} are returned')
        return out, siUnit, exponent

    def assertEqual(self, unit1, unit2):
        logger.info(f'Determine if the units {unit1} and {unit2} are equal')

        upperUnit1, lowerUnit1 = self._splitCompositeUnit(unit1)
        logger.debug(f'The unit {unit1} was split in to its upper and lower components: {upperUnit1} and {lowerUnit1}')

        upperUnit2, lowerUnit2 = self._splitCompositeUnit(unit2)
        logger.debug(f'The unit {unit2} was split in to its upper and lower components: {upperUnit2} and {lowerUnit2}')

        if set(upperUnit1) == set(upperUnit2) and set(lowerUnit1) == set(lowerUnit2):
            logger.debug(f'The units {unit1} and {unit2} are equal')
            return True
        else:
            logger.debug(f'The units {unit1} and {unit2} are equal')
            return False

    def _divide(self, unit1, unit2):
        logger.debug(f'Divide the unit {unit1} by the unit {unit2}')

        # determine the upper and lower units of unit 2
        upperUnit2, lowerUnit2 = self._splitCompositeUnit(unit2)
        logger.debug(f'The unit {unit2} was split in to its upper and lower components: {upperUnit2} and {lowerUnit2}')

        # flip unit 2
        lowerUnit2, upperUnit2 = upperUnit2, lowerUnit2

        unit2Flipped = ''
        if len(upperUnit2) != 0:
            unit2Flipped += '-'.join(upperUnit2)
        else:
            unit2Flipped += '1'

        if len(lowerUnit2) != 0:
            if len(lowerUnit2) == 1:
                if lowerUnit2[0] == '1':
                    pass
                else:
                    unit2Flipped += '/' + '-'.join(lowerUnit2)
            else:
                unit2Flipped += '/' + '-'.join(lowerUnit2)

        logger.debug(f'The upper and lower components of {unit2} are flipped and combined again to form the recibrocal of {unit2}: {unit2Flipped}')

        result = self._multiply(unit1, unit2Flipped)

        logger.debug(f'The unit {unit1} was divied by {unit2} resulting in the unit {result}')
        return result

    def _multiply(self, unit1, unit2):

        upperUnit1, lowerUnit1 = self._splitCompositeUnit(unit1)
        logger.debug(f'The unit {unit1} was split in to its upper and lower components: {upperUnit1} and {lowerUnit1}')

        upperUnit2, lowerUnit2 = self._splitCompositeUnit(unit2)
        logger.debug(f'The unit {unit2} was split in to its upper and lower components: {upperUnit2} and {lowerUnit2}')

        upper = upperUnit1 + upperUnit2
        lower = lowerUnit1 + lowerUnit2
        logger.debug(f'The upper and lower of the units {unit1} and {unit2} are combined in to {upper} and {lower}')

        upper, lower = self._cancleUnits(upper, lower)
        logger.debug(f'Units are cancled in the upper and lower: {upper} and {lower}')

        u = self._combineUpperAndLower(upper, lower)
        logger.debug(f'The upper and lower are combined: {u}')
        return u

    def _power(self, unit1, power):
        logger.debug(f'The unit {unit1} is raise to the power of {power}')

        if not isinstance(power, int):
            if not power.is_integer():
                logger.error('The power has to be an integer')
                raise ValueError('The power has to be an integer')

        upperUnit1, lowerUnit1 = self._splitCompositeUnit(unit1)
        logger.debug(f'The unit {unit1} was split in to its upper and lower components: {upperUnit1} and {lowerUnit1}')

        logger.debug(f'The upper units are iterated through: {upperUnit1}')
        if upperUnit1[0] != '1':
            for i in range(len(upperUnit1)):
                up = upperUnit1[i]
                u, exponent = self._removeExponentFromUnit(up)
                logger.debug(f'The unit {up} was split in to the unit {u} and the exponent {exponent}')
                exponent *= power
                logger.debug(f'The exponent {exponent} was scaled by the power {power}')
                if exponent != 1:
                    if exponent == 0:
                        upperUnit1[i] = '1'
                        logger.debug(f'The exponent was equal to 0. Therefore the unit "1" was added to the upper units: {upperUnit1}')
                    else:
                        u = u + str(int(exponent))
                        upperUnit1[i] = u
                        logger.debug(f'The unit {u} was added to the upper units: {upperUnit1}')
                else:
                    logger.debug(f'The exponent was equal to 1. The unit {u} was added to the upper units: {upperUnit1}')
                    upperUnit1[i] = u

        logger.debug(f'The lower units are iterated through: {lowerUnit1}')
        for i in range(len(lowerUnit1)):
            low = lowerUnit1[i]
            u, exponent = self._removeExponentFromUnit(low)
            logger.debug(f'The unit {low} was split in to the unit {u} and the exponent {exponent}')
            exponent *= power
            logger.debug(f'The exponent {exponent} was scaled by the power {power}')
            if exponent != 1:
                if exponent == 0:
                    lowerUnit1[i] = '1'
                    logger.debug(f'The exponent was equal to 0. Therefore the unit "1" was added to the lower units: {lowerUnit1}')
                else:
                    u = u + str(int(exponent))
                    lowerUnit1[i] = u
                    logger.debug(f'The unit {u} was added to the upper units: {upperUnit1}')
            else:
                logger.debug(f'The exponent was equal to 1. The unit {u} was added to the lower units: {lowerUnit1}')
                upperUnit1[i] = u

        # combine the upper and lower
        u = self._combineUpperAndLower(upperUnit1, lowerUnit1)
        logger.debug(f'The upper {upperUnit1} and lower {lowerUnit1} was combined in to the unit {u}')
        return u

    def _cancleUnits(self, upper, lower):
        logger.debug(f'The upper {upper} and lower {lower} units will be cancled')

        logger.debug(f'The upper units with exponents will be replaced by multiple occurences of the unit')
        unitsToRemove = []
        unitsToAdd = []
        for up in upper:
            u, e = self._removeExponentFromUnit(up)
            if e != 1:
                unitsToRemove.append(up)
                unitsToAdd += [u] * e
        logger.debug(f'The units to remove are {unitsToRemove}. These are replaced by the following units {unitsToAdd}')
        for u in unitsToRemove:
            upper.remove(u)
        for u in unitsToAdd:
            upper.append(u)
        logger.debug(f'The upper units has been modified as follows {upper}')

        logger.debug(f'The lower units with exponents will be replaced by multiple occurences of the unit')
        unitsToRemove = []
        unitsToAdd = []
        for low in lower:
            u, e = self._removeExponentFromUnit(low)
            if e != 1:
                unitsToRemove.append(low)
                unitsToAdd += [u] * e
        logger.debug(f'The units to remove are {unitsToRemove}. These are replaced by the following units {unitsToAdd}')
        for u in unitsToRemove:
            lower.remove(u)
        for u in unitsToAdd:
            lower.append(u)
        logger.debug(f'The lower units has been modified as follows {upper}')

        # cancle the upper and lower units
        unitsToRemove = []
        done = False
        while not done:
            done = True
            for low in lower:
                if low in upper:
                    upper.remove(low)
                    lower.remove(low)
                    logger.debug(f'The unit {low} was found in both the upper and the lower units. This is removed from both.')
                    done = False
            if done:
                break
        logger.debug(f'The upper and lower units are reduced to {upper} and {lower}')

        # remove '1'
        if len(upper) > 1:
            if '1' in upper:
                upper.remove('1')
                logger.debug(f'The unit "1" was removed from the upper units: {upper}')
        if len(lower) > 1:
            if '1' in lower:
                lower.remove('1')
                logger.debug(f'The unit "1" was removed from the lower units: {lower}')

        logger.debug('The exponent is determined for the upper units')
        upperWithExponents = []
        if len(upper) != 0:
            done = False
            while not done:
                up = upper[0]
                exponent = upper.count(up)
                upper = list(filter((up).__ne__, upper))
                logger.debug(f'The unit {up} was found a total of {exponent} times')
                if exponent != 1:
                    up = up + str(exponent)
                upperWithExponents.append(up)
                logger.debug(f'The unit {up} was added to the list of upper units with exponents')
                if len(upper) == 0:
                    done = True
        logger.debug(f'The upper units has been converted in to the following {upperWithExponents}')

        logger.debug('The exponent is determined for the lower units')
        lowerWithExponents = []
        if len(lower) != 0:
            done = False
            while not done:
                low = lower[0]
                exponent = lower.count(low)
                lower = list(filter((low).__ne__, lower))
                logger.debug(f'The unit {low} was found a total of {exponent} times')
                if exponent != 1:
                    low = low + str(exponent)
                lowerWithExponents.append(low)
                logger.debug(f'The unit {low} was added to the list of upper units with exponents')
                if len(lower) == 0:
                    done = True
        logger.debug(f'The lower units has been converted in to the following {lowerWithExponents}')

        return upperWithExponents, lowerWithExponents

    def _combineUpperAndLower(self, upper, lower):

        logger.debug(f'The unit is initialized as an empty string')
        u = ''
        if len(upper) != 0:
            u += '-'.join(upper)
            logger.debug(f'The upper units are added: {u}')
        else:
            u += '1'
            logger.debug('The upper units are empty. Therefore the upper must be a "1"')

        if len(lower) != 0:
            if len(lower) == 1:
                if lower[0] == '1':
                    logger.debug(f'The lower units include a single unit {lower[0]}. Therefore the upper units is returned: {u}')
                    pass
                else:
                    u += '/' + '-'.join(lower)
                    logger.debug(f'The lower units include a single unit {lower[0]}. Therefore a division line and the lower units are added to the unit: {u}')
            else:
                u += '/' + '-'.join(lower)
                logger.debug(f'The lower units include multiple units. Therefore a division line and the lower units are added to the unit {u}')
        else:
            logger.debug(f'The lower units are empty. Therefore the upper units is returned: {u}')
        return u

    def assertUnitsSI(self, unit1, unit2):
        logger.debug(f'It will be determined if the units {unit1} and {unit2} can be converted in to the same SI unit')

        # split the units
        upper1, lower1 = self._splitCompositeUnit(unit1)
        upper2, lower2 = self._splitCompositeUnit(unit2)
        logger.debug(f'The unit {unit1} was split in to the upper {upper1} and lower {lower1}')
        logger.debug(f'The unit {unit2} was split in to the upper {upper2} and lower {lower2}')

        logger.debug(f'The upper of {unit1}, {upper1}, is converted in to SI')
        upper1SI = []
        for u in upper1:
            _, uSI, exponent = self._convert(u, toSI=True, upper=True, isComposite=False)
            logger.debug(f'The unit {u} was converted in to the SI unit {uSI} and the exponent {exponent}')
            uSI, exp = self._removeExponentFromUnit(uSI)
            logger.debug(f'The SI unit of {u} was split in to the unit {uSI} and the exponent {exp}')
            exponent *= exp
            logger.debug(f'The exponent of the unit {u}, {exponent}, was scaled by the exponent of the unit {uSI}, {exp}')
            if exponent != 1:
                uSI += str(exponent)
            upper1SI.append(uSI)
            logger.debug(f'The unit {uSI} was added to the list of upper units of {unit1} in SI')
        logger.debug(f'The upper units of {unit1} in SI is {upper1SI}')

        logger.debug(f'The lower of {unit1}, {lower1}, is converted in to SI')
        lower1SI = []
        for l in lower1:
            _, lSI, exponent = self._convert(l, toSI=True, upper=False, isComposite=False)
            logger.debug(f'The unit {l} was converted in to the SI unit {lSI} and the exponent {exponent}')
            lSI, exp = self._removeExponentFromUnit(lSI)
            logger.debug(f'The SI unit of {u} was split in to the unit {lSI} and the exponent {exp}')
            exponent *= exp
            logger.debug(f'The exponent of the unit {u}, {exponent}, was scaled by the exponent of the unit {lSI}, {exp}')
            if exponent != 1:
                lSI += str(exponent)
            lower1SI.append(lSI)
            logger.debug(f'The unit {lSI} was added to the list of lower units of {lower1} in SI')
        logger.debug(f'The lower units of {unit1} in SI is {lower1SI}')

        logger.debug(f'The upper of {unit2}, {upper2}, is converted in to SI')
        upper2SI = []
        for u in upper2:
            _, uSI, exponent = self._convert(u, toSI=True, upper=True, isComposite=False)
            logger.debug(f'The unit {u} was converted in to the SI unit {uSI} and the exponent {exponent}')
            uSI, exp = self._removeExponentFromUnit(uSI)
            logger.debug(f'The SI unit of {u} was split in to the unit {uSI} and the exponent {exp}')
            exponent *= exp
            logger.debug(f'The exponent of the unit {u}, {exponent}, was scaled by the exponent of the unit {uSI}, {exp}')
            if exponent != 1:
                uSI += str(exponent)
            upper2SI.append(uSI)
            logger.debug(f'The unit {uSI} was added to the list of upper units of {unit2} in SI')
        logger.debug(f'The upper units of {unit2} in SI is {upper2SI}')

        logger.debug(f'The lower of {unit2}, {lower2}, is converted in to SI')
        lower2SI = []
        for l in lower2:
            _, lSI, exponent = self._convert(l, toSI=True, upper=False, isComposite=False)
            logger.debug(f'The unit {l} was converted in to the SI unit {lSI} and the exponent {exponent}')
            lSI, exp = self._removeExponentFromUnit(lSI)
            logger.debug(f'The SI unit of {u} was split in to the unit {lSI} and the exponent {exp}')
            exponent *= exp
            logger.debug(f'The exponent of the unit {u}, {exponent}, was scaled by the exponent of the unit {lSI}, {exp}')
            if exponent != 1:
                lSI += str(exponent)
            lower2SI.append(lSI)
            logger.debug(f'The unit {lSI} was added to the list of lower units of {lower2} in SI')
        logger.debug(f'The lower units of {unit2} in SI is {lower2SI}')

        upper1SI, lower1SI = self._cancleUnits(upper1SI, lower1SI)
        upper2SI, lower2SI = self._cancleUnits(upper2SI, lower2SI)
        logger.debug(f'The upper and lower units in SI of {unit1} has been cancled to {upper1SI} and {lower1SI}')
        logger.debug(f'The upper and lower units in SI of {unit1} has been cancled to {upper1SI} and {lower1SI}')

        if upper1SI == upper2SI and lower1SI == lower2SI:
            logger.debug(f'The upper and lower of {unit1} are equal to the upper and lower of {unit2}')
            return True
        else:
            logger.debug(f'The upper and lower of {unit1} are not equal to the upper and lower of {unit2}')
            return False

    def _nRoot(self, unit, power):

        upper, lower = self._splitCompositeUnit(unit)
        logger.debug(f'The unit {unit} is split in to the upper {upper} and lower {lower}')

        def isCloseToInteger(a, rel_tol=1e-9, abs_tol=0.0):
            b = np.around(a)
            return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

        # Test if the exponent of all units is divisible by the power
        for elem in upper + lower:
            elem, exp = self._removeExponentFromUnit(elem)
            if not isCloseToInteger(exp * power):
                logger.error(f'You can not raise a variable with the unit {unit} to the power of {power}')
                raise ValueError(f'You can not raise a variable with the unit {unit} to the power of {power}')

        logger.debug('The new exponent is determined for all the upper units')
        for i, up in enumerate(upper):
            u, exp = self._removeExponentFromUnit(up)
            logger.debug(f'The unit {up} was split in to the unit {u} and the exponent {exp}')
            exp *= power
            exp = int(np.around(exp))
            logger.debug(f'The exponenet {exp} was scaled by the power {power}.')
            if exp != 1:
                u += str(exp)
            upper[i] = u
            logger.debug(f'The unit {u} was added to the upper units')

        logger.debug('The new exponent is determined for all the lower units')
        for i, low in enumerate(lower):
            l, exp = self._removeExponentFromUnit(low)
            logger.debug(f'The unit {up} was split in to the unit {u} and the exponent {exp}')
            exp *= power
            exp = int(np.around(exp))
            logger.debug(f'The exponenet {exp} was scaled by the power {power}.')
            if exp != 1:
                l += str(exp)
            lower[i] = l
            logger.debug(f'The unit {l} was added to the lower units')

        unit = self._combineUpperAndLower(upper, lower)
        logger.debug(f'The upper {upper} and the lower {lower} units are combined in to the unit {unit}')
        return unit
