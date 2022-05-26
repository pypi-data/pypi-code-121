# from context import BASEDIR
from webform.bcpnp.register import Register
from webform.models.bcpnpmodel_app import BcpnpEEModelApp, BcpnpModelApp
from webform.models.bcpnpmodel_reg import BcpnpModelReg, BcpnpEEModelReg
from webform.bcpnp.login import Login
from webform.bcpnp.registrant import Registrant
from webform.bcpnp.education_reg import Education
from webform.bcpnp.employment import Employment
from webform.bcpnp.joboffer_reg import Joboffer
from webform.bcpnp.language import Language
from webform.bcpnp.submit import Submit
from webform.bcpnp.applicant import Applicant
from webform.bcpnp.education_app import EducationApp
from webform.bcpnp.workexperience import WorkExperience
from webform.bcpnp.family import Family
from webform.bcpnp.joboffer_app import JobofferApp


import json, argparse, os
from termcolor import colored


def save(actions, filename):
    with open(filename, "w") as fp:
        json.dump(actions, fp, indent=3, default=str)
    print(colored(f"{filename} has been saved.", "green"))


def main():
    parser = argparse.ArgumentParser(
        description="used for generating bcpnp form filling data"
    )
    # commands
    parser.add_argument("-e", "--excel", help="input bcpnp excel file. Will create one if the excel issn't exsited")
    parser.add_argument(
        "-t", "--task", help="tasks for p: profile, r: register a: application"
    )
    parser.add_argument("-j", "--json", help="output json file name")

    # flags
    parser.add_argument(
        "-i",
        "--initial",
        help="indicator stands for it is initial time for creating a stream to fill",
        action="store_true",
    )
    parser.add_argument(
        "-ee",
        "--express_entry",
        help="indicator stnads for it is Enpress Entry or not",
        action="store_true",
    )

    args = parser.parse_args()

    if not args.task:
        print(
            colored(
                "You must indicate which task to do by type -t plus p, r, or a. ", "red"
            )
        )
        return
    
    if not args.excel:
        print(
            colored(
                "You must indicate which task to do by type -t plus p, r, or a. ", "red"
            )
        )
        return
    
    if args.excel and not os.path.exists(args.excel):
        print(colored(f"{args.excel} is not existed. ", "red"))
        match args.task:
            case "p" | "r":
                client = (
                BcpnpEEModelReg(output_excel_file=args.excel)
                if args.express_entry
                else BcpnpModelReg(output_excel_file=args.excel)
                )
                print(colored(f"{args.excel} has been created. ", "green"))
            case "a":
                client = (
                BcpnpEEModelApp(output_excel_file=args.excel)
                if args.express_entry
                else BcpnpModelApp(output_excel_file=args.excel)
                )
                print(colored(f"{args.excel} has been created. ", "green"))
        return
    
    # actions container
    actions = []

    # excute tasks
    match args.task:
        case "p":  # profile
            client = (
                BcpnpEEModelReg(excels=[args.excel])
                if args.express_entry
                else BcpnpModelReg(excels=[args.excel])
            )
            # register
            register = Register(client)
            actions += register.register()
        case "r":  # registration
            client = (
                BcpnpEEModelReg(excels=[args.excel])
                if args.express_entry
                else BcpnpModelReg(excels=[args.excel])
            )
            # signing in, pick skill immigration, select stream and confirm
            actions += Login(client).login(initial=True if args.initial else False)
            # Registrant
            actions += Registrant(client).fill()
            # Education
            actions += Education(client).fill()
            # Employment
            actions += Employment(client).fill()
            # Job offer
            actions += Joboffer(client).fill()
            # Language
            actions += Language(client).fill()
            # Submit
            actions += Submit(client).fill()
        case "a":  # application
            client = (
                BcpnpEEModelApp(excels=[args.excel])
                if args.express_entry
                else BcpnpModelApp(excels=[args.excel])
            )
            # login
            # signing in, pick skill immigration, select stream and confirm
            actions += Login(client).login(initial=False)
            # Applicant
            actions += Applicant(client).fill()
            # Education
            actions += EducationApp(client).fill()
            # Employment
            actions += WorkExperience(client).fill()
            # Family
            actions += Family(client).fill()
            # Job offer
            actions += JobofferApp(client).fill()
            # Submit
            actions += Submit(client).fill()
        case _:  # profile
            print(
                colored(
                    f"{args.task} is wrong indicator. There are 3 types, in which p stands for profile, r for register, and a for application.",
                    "reg",
                )
            )
            return
    save(actions, args.json) if args.json else print(
        json.dumps(actions, indent=3, default=str)
    )


if __name__ == "__main__":
    main()
