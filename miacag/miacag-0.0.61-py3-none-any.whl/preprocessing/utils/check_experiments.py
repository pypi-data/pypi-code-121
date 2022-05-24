import os


def checkExpExists(exp, output_folder):
    exp_exists_list = []
    runned_exps = os.listdir(output_folder)
    if "results.csv" in runned_exps:
        runned_exps.remove("results.csv")
    exp_basename = os.path.basename(exp)[:-5]
    for runned_exp in runned_exps:
        runned_exp_match = runned_exp.split("_SEP_")[0]
        if exp_basename == runned_exp_match:
            test_plot = os.path.join(
                output_folder,
                runned_exp,
                "plots/test")
            test_plot_exists = os.path.exists(test_plot)
            if test_plot_exists is True:
                if len(os.listdir((test_plot))) > 0:
                    exp_exists = True
                else:
                    exp_exists = False
            else:
                exp_exists = False
        else:
            exp_exists = False
        exp_exists_list.append((exp_exists))
    if True in exp_exists_list:
        return True
    else:
        return False


def checkCsvExists(output_folder):
    csv_path = os.path.join(output_folder, "results.csv")
    if os.path.exists(csv_path) is True:
        return True, csv_path
    else:
        return False, csv_path

if __name__ == '__main__':
    exp_folder = "/home/sauroman/angiography_data/runs/test"
    output_folder = "classification_config_angio_2"
    exp_name = "DILLERRERE"
    checkExpExists(exp_folder, exp_name)
