# from context import BASEDIR
from webform.prportal.i5562 import F5562
from webform.prportal.i5406 import F5406
from webform.prportal.i5669 import F5669
from webform.prportal.i0008 import F0008
from webform.prportal.login import Login
from webform.models.prmodel import PrModel
from webform.prportal.application import Application
import json, dotenv, os, argparse
from termcolor import colored
from docxtpl import DocxTemplate
import os,sys

# Get project's home directory, 
BASEDIR=os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# All data directory
DATADIR=os.path.abspath(os.path.join(BASEDIR,'data'))


def login_prportal(rcic: str):
    # login
    path = os.path.abspath(os.path.join(os.path.expanduser("~"), ".prportalenv"))
    config = dotenv.dotenv_values(path)
    rcic_account = {
        "account": config.get(rcic + "_prportal_account"),
        "password": config.get(rcic + "_prportal_password"),
    }
    if not rcic_account["account"] or not rcic_account["password"]:
        print(
            colored(
                f"{rcic}'s prportal account and/or password is not existed. Check the .prportalenv file in your home directory and add your profile",
                "red",
            )
        )
        exit(1)

    rcic_obj = Login(rcic_account)
    return rcic_obj.login()


def output(args, actions):
    if args.to:
        with open(args.to, "w") as f:
            json.dump(actions, f, indent=3, default=str)
            print(colored(f"{args.to} is created", "green"))
    else:
        print(json.dumps(actions, indent=3, default=str))

def makeDocx(persons,docx_file):
    document=DocxTemplate(DATADIR+"/word/pr-appendix.docx")
    document.render(persons)
    document.save(docx_file)
    print(colored(f"{docx_file} saved","green"))


def main():
    parser = argparse.ArgumentParser(
        description="Used for generating data for webform filling."
    )
    # input source excel files for pa, sp, and dp
    parser.add_argument(
        "-pa",
        "--principal_applicant",
        help="Input principal applicant's excel file name",
    )
    parser.add_argument("-sp", "--spouse", help="Input spouse's excel file name")
    parser.add_argument(
        "-dp",
        "--dependants",
        help="Input dependants' excel file names, can be multiple.",
        nargs="+",
    )
    # get which rcic
    parser.add_argument("-r", "--rcic", help="Input rcic's name")
    # generate data for filling all, or specific form
    parser.add_argument(
        "-f",
        "--forms",
        help="Specify generating which form. Exp: -f 5669 5562 0008 5406. Without -f, the app will generate all forms' data ",
        nargs="+",
    )
    # generate 0008 pa's data
    parser.add_argument(
        "-f0008pa", "--f0008pa", help="Generate imm0008 pa's data", action="store_true"
    )
    # generate 0008 dps' data
    parser.add_argument(
        "-f0008dp", "--f0008dp", help="Generate imm0008 dps' data", action="store_true"
    )
    # save to file
    parser.add_argument("-t", "--to", help="Input the output json file name")
    
    # make an additional appendix docx file including all information
    parser.add_argument("-a", "--appendix", help="Input the appendix file name")
    
    args = parser.parse_args()

    # get pa, sp, and dps object
    if args.principal_applicant:
        pa = PrModel([args.principal_applicant])
    else:
        print(
            colored(
                "You didn't input principal applicant's excel file. Please use -pa excel.xlsl",
                "red",
            )
        )
        return

    if args.spouse:
        sp = PrModel([args.spouse])
    else:
        sp = None

    dps = []
    if args.dependants:
        for excel in args.dependants:
            dps.append(PrModel([excel]))

    # make appendix doc file
    if args.appendix:
        dps_above_18=[dp.dict() for dp in dps if dp.personal.age>=18]
        sp=[sp.dict()] if sp else []
        makeDocx({"persons":[pa.dict(),*sp,*dps_above_18]},args.appendix)
        return
    # actions container
    actions = []
    # login
    if not args.rcic:
        print(
            colored(
                "You did not speficy using which rcic's portal. Please use -r rcic name",
                "red",
            )
        )
        return
    actions += login_prportal(args.rcic)
    # determine create a new applicatoin or pick an existing application. 现在创建还是手工创建算了。
    # pick an application
    app = Application(pa)
    actions += app.pick()

    if args.f0008pa:
        f0008 = F0008(pa, sp, dps)
        actions += f0008.fill_pa()
        output(args, actions)
        return
    if args.f0008dp:
        f0008 = F0008(pa, sp, dps)
        actions += f0008.fill_dp()
        output(args, actions)
        return


    # if args.form exists, then loop the form and generate them, else generate all forms
    if args.forms:
        a5406 = a5562 = a5669 = a0008 = []
        for form in args.forms:
            match form:
                case "5406":
                    f5406 = F5406(pa, sp, dps)
                    a5406 = f5406.fill()
                case "5562":
                    f5562 = F5562(pa, sp, dps)
                    a5562 = f5562.fill()
                case "5669":
                    f5669 = F5669(pa, sp, dps)
                    a5669 = f5669.fill()
                case "0008":
                    f0008 = F0008(pa, sp, dps)
                    a0008 = f0008.fill()
                case _:
                    print(
                        colored(
                            f"{form} is not a valid form number in '5562','5406','5669','0008'",
                            "red",
                        )
                    )
                    return
        actions += a5406 + a5562 + a5669 + a0008
        output(args, actions)
        return
    else:
        f5406 = F5406(pa, sp, dps)
        actions += f5406.fill()
        f5562 = F5562(pa, sp, dps)
        actions += f5562.fill()
        f5669 = F5669(pa, sp, dps)
        actions += f5669.fill()
        f0008 = F0008(pa, sp, dps)
        actions += f0008.fill()
        output(args, actions)
        return

    
        

if __name__ == "__main__":
    main()
