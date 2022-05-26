import os
import unittest
import logging
import datetime
from thompcoutils.cron_time import CronTime
from thompcoutils.test_utils import assert_test
from thompcoutils.config_utils import ConfigManager, EmailConnectionConfig, HiLow, CellNumberConfig
import thompcoutils.email_utils as email_utils
from thompcoutils.cell_phone import CellPhone

test_path = 'test_ini_files'
if not os.path.exists(test_path):
    os.mkdir(test_path)
log_configuration_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.ini')
logging.config.fileConfig(log_configuration_file)


def test_replace(filename, old_string, new_string):
    # Safely read the input filename using 'with'
    try:
        with open(filename) as f:
            s = f.read()
            if old_string not in s:
                print('"{old_string}" not found in {filename}.'.format(**locals()))
                return

        # Safely write the changed content, if found in the file
        with open(filename, 'w') as f:
            print('Changing "{old_string}" to "{new_string}" in {filename}'.format(**locals()))
            s = s.replace(old_string, new_string)
            f.write(s)
    except Exception as e:
        raise e


def test_hi_low_vals(file_name, section, value):
    hi_low = HiLow(file_name=file_name, value_type=float)
    hi_value = value
    places = 10
    hi_low.write_value(entry=section, value=value)
    values = hi_low.read_values(entry=section)
    assert_test(values[HiLow.direction_tag] == HiLow.Direction.Up, "Should be moving Up")
    assert_test(values[HiLow.hi_tag] == value, "value should match")
    assert_test(values[HiLow.last_tag] == value, "value should match")
    assert_test(values[HiLow.change_amount_tag] > 1, "value should be large")

    diff = 1
    value -= diff
    hi_low.write_value(entry=section, value=value)
    values = hi_low.read_values(entry=section)
    assert_test(values[HiLow.direction_tag] == HiLow.Direction.Down, "Should be moving Down")
    assert_test(values[HiLow.low_tag] == value, "value should match")
    assert_test(values[HiLow.hi_tag] == hi_value, "value should match")
    assert_test(values[HiLow.last_tag] == value, "value should match")
    assert_test(round(values[HiLow.change_amount_tag], places) == diff, "value should be {}".format(diff))

    hi_low.write_value(entry=section, value=value)
    values = hi_low.read_values(entry=section)
    assert_test(values[HiLow.direction_tag] == HiLow.Direction.NoChange, "Should not be moving")
    assert_test(values[HiLow.low_tag] == value, "value should match")
    assert_test(values[HiLow.hi_tag] == hi_value, "value should match")
    assert_test(values[HiLow.last_tag] == value, "value should match")
    assert_test(values[HiLow.change_amount_tag] == 0, "value has not changed")

    diff = 2
    value += diff
    values = hi_low.write_value(entry=section, value=value)
    assert_test(values[HiLow.direction_tag] == HiLow.Direction.Up, "Should be moving Up")
    assert_test(values[HiLow.hi_tag] == value, "value should match")
    assert_test(values[HiLow.last_tag] == value, "value should match")
    assert_test(round(values[HiLow.change_amount_tag], places) == diff, "value should be {}".format(diff))

    diff = 1.1
    value += diff
    hi_low.write_value(entry=section, value=value)
    values = hi_low.read_values(entry=section)
    assert_test(values[HiLow.direction_tag] == HiLow.Direction.Up, "Should be moving Up")
    assert_test(values[HiLow.hi_tag] == value, "value should match")
    assert_test(values[HiLow.last_tag] == value, "value should match")
    assert_test(round(values[HiLow.change_amount_tag], places) == diff, "value should be {}".format(diff))

    diff = 10.1
    value -= diff
    hi_low.write_value(entry=section, value=value)
    values = hi_low.read_values(entry=section)
    assert_test(values[HiLow.direction_tag] == HiLow.Direction.Down, "Should be moving Down")
    assert_test(values[HiLow.low_tag] == value, "value should match")
    assert_test(values[HiLow.last_tag] == value, "value should match")
    assert_test(round(values[HiLow.change_amount_tag], places) == diff, "value should be {}".format(diff))

    value = 14
    vals = hi_low.write_value(entry=section, value=value)
    values = hi_low.read_values(entry=section)
    assert_test(vals == values, "values should match")


class TestConfigUtils(unittest.TestCase):
    def test_config_mgr(self):
        file_name = os.path.join(test_path, "test_config.ini")
        for write in [True, False]:
            if write:
                if os.path.isfile(file_name):
                    os.remove(file_name)
            else:
                test_replace(file_name, "Rover", "Baily")
            cfg_mgr = ConfigManager(file_name,
                                    "This is the title of the ini file\n"
                                    "You can have multiple lines if you use line breaks", write)
            first = cfg_mgr.read_entry("User 1", "date_time", datetime.datetime.now())
            second = cfg_mgr.read_entry("User 1", "first name", "Joe", "This is the first name")
            last = cfg_mgr.read_entry("User 1", "last name", "Brown", "This is the last name")
            age = cfg_mgr.read_entry("User 1", "age", 12)
            is_male = cfg_mgr.read_entry("User 1", "male", True)
            weight = cfg_mgr.read_entry("User 1", "weight", 23.5)
            values = cfg_mgr.read_entry("User 1", "values", {"height": 7.5, "weight": 10, "name": "Fred"})
            weights = cfg_mgr.read_entry("User 1", "weights", [23.5, 22])
            names = cfg_mgr.read_entry("User 1", "names", ["Joe", "Fred"])
            cfg_mgr.write_entry("User 1", "male", False)
            cfg_mgr.write_entry("User 1", "parent", "Fred")
            cfg_mgr.write_entry("User 1", "date_time", datetime.datetime.now())
            cfg_mgr.write_entry("User 1", "cron_time", CronTime(day_of_month=1, hour=2, minute=3),
                                format_string='%d %H %M')
            # section = cfg_mgr.read_section("user 2", {"first name": "Sally",
            #                                           "last name": "Jones",
            #                                           "age": 15,
            #                                           "is_male": False,
            #                                           "weight": 41.3},
            #                                "You only get to add notes at the top of the section using this method")
            if write:
                test1 = cfg_mgr.read_entry("User 1", "dog name", "Rover")
                assert_test(test1 == "Rover", "value should be Rover")
            else:
                test1 = cfg_mgr.read_entry("User 1", "dog name", "Rover")
                assert_test(test1 == "Baily", "value should be Rover")
                test2 = cfg_mgr.read_entry("User 1", "cat name", "Tinkerbell", use_default_if_missing=False)
                assert_test(test2 is None, "missing value should be none")
                val = cfg_mgr.read_entry("User 1", "cron_time", CronTime(day_of_month=1, hour=2, minute=3))
                assert_test(val.day_of_month == 1)
                assert_test(val.day_of_week == 0)
                assert_test(val.month == 0)
                assert_test(val.hour == 2)
                assert_test(val.minute == 3)

            print(first)
            print(second)
            print(last)
            print(age)
            print(is_male)
            print(weight)
            print(values)
            print(weights)
            print(names)
            # print(section)
            if write:
                test_file = file_name
                cfg_mgr.write(out_file=test_file, overwrite=False, stop=False)
                contents = open(test_file, "r")
                print("File contents are:")
                print("====================================================")
                print(contents.read())
                print("====================================================")
                contents.close()

    def test_email_connection_config(self):
        file_name = os.path.join(test_path, "test_email.ini")
        for write in [True, False]:
            if write:
                if os.path.isfile(file_name):
                    os.remove(file_name)
            else:
                pass
            cfg_mgr = ConfigManager(file_name,
                                    "This is the title of the ini file\n"
                                    "You can have multiple lines if you use line breaks", write)
            email_connection = EmailConnectionConfig(cfg_mgr)
            print(email_connection.username)
            print(email_connection.password)
            print(email_connection.from_user)
            print(email_connection.smtp_host)
            print(email_connection.smtp_port)
            if write:
                test_file = file_name
                cfg_mgr.write(out_file=test_file, overwrite=True, stop=False)
                contents = open(test_file, "r")
                print("File contents are:")
                print("====================================================")
                print(contents.read())
                print("====================================================")
                contents.close()

    def test_hi_low(self):
        file_name = os.path.join(test_path, "test_hi_low.ini")
        if os.path.isfile(file_name):
            os.remove(file_name)
        value = 50
        test_hi_low_vals(file_name, "first", value)
        value = 60
        test_hi_low_vals(file_name, "second", value)
        value = 40
        test_hi_low_vals(file_name, "third", value)

    def test_cell_number(self):
        file_name = os.path.join(test_path, "test_cell_number.ini")
        for write in [True, False]:
            if write:
                if os.path.isfile(file_name):
                    os.remove(file_name)
            else:
                pass
            cfg_mgr = ConfigManager(file_name,
                                    "This is the title of the ini file\n"
                                    "You can have multiple lines if you use line breaks", write)
            cell_phone = CellNumberConfig(cfg_mgr, CellPhone(11111, CellPhone.Carrier.T_MOBILE))
            print(cell_phone.phone_number)
            print(cell_phone.carrier)
            if write:
                test_file = file_name
                cfg_mgr.write(out_file=test_file, overwrite=True, stop=False)
                contents = open(test_file, "r")
                print("File contents are:")
                print("====================================================")
                print(contents.read())
                print("====================================================")
                contents.close()



        file_name = os.path.join(test_path, "test_cell.ini")
        if os.path.isfile(file_name):
            os.remove(file_name)
        cell_number = 1234567890
        cell_carrier = email_utils.EmailSender.Carrier.ATT

    @staticmethod
    def remove_file(f):
        if os.path.exists(f):
            os.unlink(f)
