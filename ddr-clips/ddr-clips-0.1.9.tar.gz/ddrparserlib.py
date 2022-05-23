from pprint import pprint as pp
import copy
import clips


##############################################################################
#
#
# show_and_assert_fact - execute a show command, parse the show command output,
#            and assert a fact based on the output
#            return "success" on success else return error string
#
# Example of parsed data from a show command created by a "genie_parser"
# This example shows state information for LISP instances.
# The data for the instance is a "sub_dictionary" contained in the "per_instance_dict"
# The genie_parser generates this dictionary structure
#
#            {'lisp_instance':
#               {'per_instance_dict':
#                 {'instance_id': 4100, 'lisp_id': 0, 'reg_timer': '00:02:49'}
#               }
#            }
#
# This is the FACT definition used to process the data returned by the parser
#
#  {"fact_type": "show_and_assert",
#     "command": 'show processes memory platform sorted',
#     "device": "cat9k-24",
#     "genie_parser": "ShowLispInstanceId",
#     "assert_fact_for_each_item_in": "lisp_instance",
#     "protofact": {"template": "lisp-instance",
#                                "slots": {"device": "device",
#                                          "instance": "$",
#                                          "instance-id": "$+instance_id",
#                                          "lisp-id": "$+lisp_id",
#                                          "reg-timer": "$+reg_timer"}}}

#############################################################################
def test_show_and_assert_fact(env, template, fact, response):
    print("\n********** Parsed response data translated into dictionary **************\n")
    try:
        #
        # use the parsed output of a show command that will be in the form of a python dictionary
        # The "fact" dictionary includes a field indentifying what part of the parsed data
        # to use to generated the CLIPs FACT
        #
        parsed_genie_output = response
        sub_dictionary_list = test_find(fact["assert_fact_for_each_item_in"], parsed_genie_output)
        import copy
        #
        # If there are multiple sets of data in the parsed response, each will be in a sub_dictionary
        # A FACT is generated for each sub_dictionary
        #
        for sub_dictionary in sub_dictionary_list:
            print(f"\nsub_dictionary: {sub_dictionary}\n")
            #
            # Each "item" in the sub_dictionary is
            # Addeded to a dictionary in the form required to generate a CLIPs FACT
            #
            for item in sub_dictionary:
                protofact = copy.deepcopy(fact["protofact"])
                for slot in protofact["slots"]:
                    value = protofact["slots"][slot]
                    #
                    # insert the device name into the fact
                    #
                    if value == "device":
                        protofact["slots"][slot] = value.replace("device", fact["device"])
                    elif type(value) == str and "$" in value:
                        protofact["slots"][slot] = value.replace("$", item)

                test_assert_template_fact(env, template, protofact, sub_dictionary)
    except Exception as e:
        print("\n&&&& show_and_assert exception: \n" + str(e))


#     self.print_log("%%%% EMRE Error: Exception in show_and_assert_fact: " + str(e))
#     return


##############################################################################
#
# find - return nested dictionary value given a dictionary (j) and a string
#		 element (element) in the form of "Garden.Flowers.White"
#
#############################################################################
def test_find(element, j):
    try:
        if element == "":
            return j
        keys = element.split('+')
        rv = j
        for i, key in enumerate(keys):
            if key == '*':
                new_list = []
                new_keys = copy.deepcopy(keys[i + 1:])  # all the keys past the * entry
                for entry in rv:  # for each entry in the * dictionary
                    new_rv = copy.deepcopy(rv[entry])
                    for new_key in new_keys:
                        new_rv = new_rv[new_key]
                    for e in new_rv:
                        new_rv[e]["upper_value"] = entry
                    new_list.append(new_rv)
                return new_list
            else:
                # normal stepping through dictionary
                try:
                   rv = rv[key]
                except Exception as e:
                    print(">> find exception: key: ", str(e), key)
                    return
        return [rv]
    except Exception as e:
        print("\n&&&& find exception: \n", str(e), element, j)


##############################################################################
#
# assert_template_fact - given a protofact, assert the fact into the clips system
# 						 protofact examples:
# protofact = {"template": "person-template", "slots": {"name": "Leeroy", "surname": "Jenkins", "age": 23.1}}
# protofact2 = {"template": "person-template", "slots": {"name": "Leeroy", "surname": "Jenkins", "age": "Leeroy.age"}}
#						 in protofact2, the age is unknown, but can be looked up in a sub_dictionary
#						 sub_dictionary example:
# sub_dictionary = {"Leeroy: {"age": 23.1, "height": 182, "gender": "M"},
#				    "Maria": {"age": 32.5, "height": 160, "gender": "F"}}
#
#############################################################################
def test_assert_template_fact(env, template, protofact, sub_dictionary):
        try:
            template = env.find_template(template)
            fact1 = {}
            for slot, value in protofact["slots"].items():
    #
    # If the "value" is in a subdirectory, look up the final value in the sub_dictionary
    #
                try:
#                    print("\n>> value, type: ", value, type(value))
                    if type(value) is str and "+" in value:
                        value = test_find(value, sub_dictionary)[0]

                    if isinstance(value, int):
                        fact1[slot] = int(value)
                    else:
                        fact1[slot] = str(value)
                except Exception as e:
                    print("%%%% DDR Exception: incorrect fact definition: " + str(value))

    #
    # Assert the FACT defined by a Python dictionary
    #
            try:
                template.assert_fact(**fact1)
            except Exception as e:
                print("%%%% DDR Exception: assert_template_fact: " + str(e))
        except Exception as e:
            print("%%%% DDR Error: Exception assert_template_fact: " + str(e))

