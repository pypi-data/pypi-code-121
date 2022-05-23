from sqlite3 import paramstyle
import pandas as pd
import re


str_output_len = "env.m"
str_prefix_for_return_parameter = "out_"


def check_if_output_parameter( str_cparam):
    is_output_parameter = False

    if str_prefix_for_return_parameter in str_cparam and "out_env" not in str_cparam: is_output_parameter = True

    return is_output_parameter

def add_to_return_statement( param, str_return):
    if str_return == "":
        str_return = str_return + param + "np"
    else:
        str_return = str_return + ", " + param + "np"
    return str_return


def prepare_parameter_for_c_function_call( str_cfunc, has_env, param_count, param_type, param_name, str_return):
    param_name = param_name.replace( "*", "")
    this_param = param_name
    
    str_cffi = ""

    # handle pointers
    if "*" in param_type:
        if "int" in param_type:
            this_param  = "p" + this_param
            if str_prefix_for_return_parameter not in this_param:
                # convert to CFFI
                str_cffi = "    " + this_param + "np" + ", " + this_param + " = " + "convert_py_int_to_cffi( " + param_name + ")"
            else:
                # allocate numpy array
                str_cffi = "    " + this_param + "np" + ", " + this_param + " = " + "create_intc_zeros_as_CFFI_int( " + str_output_len + ")"    
                str_return = add_to_return_statement( this_param, str_return)
        elif "double" in param_type:
            this_param  = "p" + this_param
            if str_prefix_for_return_parameter not in this_param:
                # convert to CFFI
                str_cffi = "    " + this_param + "np" + ", " + this_param + " = " + "convert_py_float_to_cffi( " + param_name + ")"
            else:
                str_cffi = "    " + this_param + "np" + ", " + this_param + " = " + "create_float_zeros_as_CFFI_double( " + str_output_len + ")"    
                str_return = add_to_return_statement( this_param, str_return)
        elif "int_64" in param_type:
            str_cffi = ""   
        elif "struct_fm_env_sparse" in param_type:
            str_cffi = ""
            str_return = this_param
        elif "struct_fm_env" in param_type:
            str_cffi = ""
        else:
            print( "unknown parameter type: ", param_type, "in c function: ", str_cfunc)
    
    if param_count > 0:
        this_param = ", " + this_param
        
    return this_param, str_cffi, str_return


# generate python wrapper code for one C function
# input:  C function 
# output: python wrapper code
def gen_py_code_for_c_function( str_cfunc):
    py_func_code = []
    py_test_code = []
    py_func_calls_to_convert_data = []
    str_return = ""
    has_env = False
    if "env" in str_cfunc: has_env = True
    
    # check for python keywords used in c function
    str_cfunc = str_cfunc.replace( "lambda", "lambdax")
    
    # scan function and generate tokens
    # tokens[0]: return type
    # tokens[1]: function name
    # tokens[2]: parameter 1 type
    # tokens[3]: parameter 2 type
    # ...
    temp = str_cfunc.replace( "(", " ").replace( ")", "").replace( ",", "")
    temp = re.sub( r"[ ]+", " ", temp)
    tokens = re.split( ",| ", temp)
    # print( "tokens: ", tokens)
        
    # initial comment
    str_wrapper_func = str_cfunc.replace( "py_", "")
    str_in_comment = "#    " + str_cfunc.replace( "struct_", "struct ")
    py_func_code.append( "# Generated python wrapper for:")
    py_func_code.append( str_in_comment)
    # print( str_in_comment)
        
    # function header
    token_iter = iter( tokens) 
    return_type = next( token_iter)
    func_name = next( token_iter).replace( "py_", "")
    str_py_header = "def " + func_name + "("
    param_count = 0
    c_params = ""
    while True:
        try:
            param_type = next( token_iter)
            param_name = next( token_iter)
            output = check_if_output_parameter( param_name)
            if param_count == 0 and output == False: 
                str_py_header += param_name
            elif param_count > 0 and output == False:
                str_py_header += ", " + param_name
            this_param, str_cffi, str_return = prepare_parameter_for_c_function_call( str_cfunc, has_env, param_count, param_type, param_name, str_return)
            c_params += this_param.replace( "*", "")
            if str_cffi: py_func_calls_to_convert_data.append( str_cffi)
            if output == False: param_count += 1
        except StopIteration:
            str_py_header += "):"
            break
    py_func_code.append( str_py_header)

    # Test code
    py_test_code.append( "# Test wrapper for:")
    py_test_code.append( str_in_comment)
    py_test_code.append( "# pyw." + str_py_header.replace( "def", "").replace( ":", "").strip())
 
    # print( str_py_header)
        
    # trace
    str_trace = "    trace( " + '"' + str_cfunc.replace( "struct_", "struct ") + '"' + ")" 
    py_func_code.append( str_trace)
    # print( str_trace)
    
    # prepare parameters for C function call
    py_func_code.extend( py_func_calls_to_convert_data)
        
    # C function call and return statement
    if "void" in return_type: 
        # Ignore the result of the C function call
        str_c_func_call = "    fm.py_" + func_name + "( " + c_params + ")";
    else:
        # The result of the C function call is the return value
        str_c_func_call = "    yy = fm.py_" + func_name + "( " + c_params + ")";
        str_return = "yy"
    str_return = "    return " + str_return
    py_func_code.append( str_c_func_call)
    if str_return: py_func_code.append( str_return)    

    return py_func_code, py_test_code





list_of_c_functions = "list_of_c_functions.txt" 
generated_py_code = "generated_py_code.py"


py_wrapper_code = []
py_test_code = []
with open( list_of_c_functions, 'r') as fh_read:
    for line in fh_read:
        # remove whitespaces and ";"
        aline = line.strip().replace( ";", "").replace( "struct ", "struct_")
        wrapper_code, test_code = gen_py_code_for_c_function( aline)
        py_wrapper_code.extend( wrapper_code)
        py_test_code.extend( test_code)
        # add empty lines
        py_wrapper_code.append( "\n")
        py_test_code.append( "\n")
        

fh_write = open( generated_py_code, 'w')
fh_write.writelines( "%s\n" % l for l in py_wrapper_code)

fh_write.writelines( "%s\n" % l for l in py_test_code)


# the end
