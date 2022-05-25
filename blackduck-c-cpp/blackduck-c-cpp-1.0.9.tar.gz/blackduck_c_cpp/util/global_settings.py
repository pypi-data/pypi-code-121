import re

# all_h_ptrn_emit = re.compile(r"\/.+\.hxx\.\S+|\/.+\.hxx|\/.+\.hpp\.\S+|\/.+\.hpp|\/.+\.h\.\S+|\/.+\.h", re.IGNORECASE)
src_emit_pttrn = re.compile(
    r"\/.+\.hxx\.\S+|\/.+\.hxx|\/.+\.hpp\.\S+|\/.+\.hpp|\/.+\.h\.\S+|\/.+\.h|\/.+\.cxx\.\S+|\/.+\.cxx|\/.+\.cppm\.\S+|\/.+\.cppm|\/.+\.cpp\.\S+|\/.+\.cpp|\/.+\.c\+\+\.\S+|\/.+\.c\+\+|\/.+\.cp\.\S+|\/.+\.cp|\/.+\.cc\.\S+|\/.+\.cc|\/.+\.c\.\S+|\/.+\.c|\/.+\.ixx\.\S+|\/.+\.ixx",
    re.IGNORECASE)

# all_h_ptrn_emit_win = re.compile(
#    r"[A-Z]\:\/.+\.hxx\.\S+|[A-Z]\:\/.+\.hxx|[A-Z]\:\/.+\.hpp\.\S+|[A-Z]\:\/.+\.hpp|[A-Z]\:\/.+\.h\.\S+|[A-Z]\:\/.+\.h")
src_emit_pttrn_win = re.compile(
    r"[A-Z]\:\/.+\.hxx\.\S+|[A-Z]\:\/.+\.hxx|[A-Z]\:\/.+\.hpp\.\S+|[A-Z]\:\/.+\.hpp|[A-Z]\:\/.+\.h\.\S+|[A-Z]\:\/.+\.h|[A-Z]\:\/.+\.cxx\.\S+|[A-Z]\:\/.+\.cxx|[A-Z]\:\/.+\.cppm\.\S+|[A-Z]\:\/.+\.cppm|[A-Z]\:\/.+\.cpp\.\S+|[A-Z]\:\/.+\.cpp|[A-Z]\:\/.+\.c\+\+\.\S+|[A-Z]\:\/.+\.c\+\+|[A-Z]\:\/.+\.cp\.\S+|[A-Z]\:\/.+\.cp|[A-Z]\:\/.+\.cc\.\S+|[A-Z]\:\/.+\.cc|[A-Z]\:\/.+\.c\.\S+|[A-Z]\:\/.+\.c|[A-Z]\:\/.+\.ixx\.\S+|[A-Z]\:\/.+\.ixx",
    re.IGNORECASE)

so_pattern = re.compile(r"(?i).*\.so\..+$|.*\.so$")
a_pattern = re.compile(r"(?i).*\.a\..+$|.*\.a$")
o_pattern = re.compile(r"(?i).*\.o\..+$|.*\.o$")
obj_pattern = re.compile(r"(?i).*\.obj\..+$|.*\.obj$")

cpp_pattern = re.compile(r"(?i).*\.cpp\..+$|.*\.cpp$")
c_pattern = re.compile(r"(?i).*\.c\..+$|.*\.c$")
cxx_pattern = re.compile(r"(?i).*\.cxx\..+$|.*\.cxx$")
cc_pattern = re.compile(r"(?i).*\.cc\..+$|.*\.cc$")
cp_pattern = re.compile(r"(?i).*\.cp\..+$|.*\.cp$")
cplus_pattern = re.compile(r"(?i).*\.c\+\+\..+$|.*\.c\+\+$")
cppm_pattern = re.compile(r"(?i).*\.cppm\..+$|.*\.cppm$")
ixx_pattern = re.compile(r"(?i).*\.ixx\..+$|.*\.ixx$")


hpp_pattern = re.compile(r"(?i).*\.hpp\..+$|.*\.hpp$")
h_pattern = re.compile(r"(?i).*\.h\..+$|.*\.h$")
hxx_pattern = re.compile(r"(?i).*\.hxx\..+$|.*\.hxx$")

dll_pattern = re.compile(r"(?i).*\.dll\..+$|.*\.dll$")
lib_pattern = re.compile(r"(?i).*\.lib\..+$|.*\.lib$")

cplusplus_pattern = re.compile(r".*EXECUTING: .*\Sc\+\+ ")
gplusplus_pattern = re.compile(r".*EXECUTING: .*\Sg\+\+ ")
cc_pattern = re.compile(r".*EXECUTING: .*\Scc ")
gcc_pattern = re.compile(r".*EXECUTING: .*\Sgcc ")
ld_pattern = re.compile(r".*EXECUTING: .*\Sld ")
mvsc_link_pattern = re.compile(r".*EXECUTING: LINK", re.IGNORECASE)
mvsc_cl_pattern = re.compile(r".*EXECUTING: CL", re.IGNORECASE)
compl_non_mtch_ptrn_1 = re.compile(r".* -c .*")
compl_non_mtch_ptrn_2 = re.compile(r".* -E .*")

snippet_match = 'snippet'
darwin_pltfrm = 'darwin'
macos_pltfrm = 'macos'
