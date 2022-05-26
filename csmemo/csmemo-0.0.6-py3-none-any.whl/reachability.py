import re
import warnings
import pandas as pd
import logging
from cobra.core import Reaction
from cobra.core import DictList
from pyfastcore import Fastcore


class InfeasibleProblemError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class MetabolicTaskException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class AlreadyRegisteredError(MetabolicTaskException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class TaskRegisterError(MetabolicTaskException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def find_gene_knockout_reactions(model):
    gene_ko_reactions = {}
    for g in model.genes:
        gene_ko_reactions[g.id] = []
    
    for r in model.reactions:
        if r.gpr is None or len(r.gene_reaction_rule) == 0:
            continue
        for g in r.genes:
            if r.gpr.eval([g]):
                gene_ko_reactions[g.id].append(r.id)

    return gene_ko_reactions


class ReachabilityTester:

    def __init__(self, cobra_model, target_products,
                 epsilon=1e-4, tolerance=1e-7, 
                 flux_bound=999999., level=logging.INFO):

        self._model = cobra_model.copy()
        self._var_mapping = {}
        self._epsilon = epsilon
        self._tolerance = tolerance
        self._demands_dict = {}
        self._product_to_demands_dict = {}
        self._original_bound = {}
        self._not_reachable_products = []

        self._gene_knockout_reactions = find_gene_knockout_reactions(self._model)

        assert len(target_products) > 0

        logging.basicConfig(level=level)
        logging.info("- Creating CSMBuilder")

        
        logging.info("===========================================================")
        logging.info("Initializing Reachability Tester using")
        logging.info("Model: %s" % cobra_model.id)

        logging.info("- Nº of reactions: %i" % len(self._model.reactions))
        logging.info("- Nº of metabolites: %i" % len(self._model.metabolites))
        logging.info("- Nº of target products: %i" % len(target_products))

        if hasattr(target_products[0], 'id'):
            target_products = [m.id for m in target_products]

        for r in self._model.reactions:
            self._original_bound[r.id] = r.bounds
            if r.upper_bound > 0:
                r.upper_bound = flux_bound
            if r.lower_bound < 0:
                r.lower_bound = -flux_bound

        for m in target_products:
            m = self._model.metabolites.get_by_id(m)
            try:
                demand = self._model.add_boundary(m, type='demand')
            except (KeyError, ValueError) as e:
                demand_id = re.sub(r"^[^']*'([^']*)'.*", r"\1", e.args[0])
                demand = self._model.reactions.get_by_id(demand_id)

            self._demands_dict[demand.id] = m
            self._product_to_demands_dict[m.id] = demand.id

        self.__init_lp_problems()


        not_reachable_targets = self.test_target_products()
        if len(not_reachable_targets) > 0:
            logging.warning(" - The following target products cannot be reached")
            print(" ".join(not_reachable_targets))
            logging.warning(" - Removing compounds form the list of target products")
            for i in not_reachable_targets:
                demand = self._product_to_demands_dict[i]
                del self._demands_dict[demand]

            logging.info("Updating LP models")
            self.__init_lp_problems()

    @property
    def model(self):
        return self._model

    @property
    def epsilon(self):
        return self._epsilon

    @property
    def tolerance(self):
        return self._tolerance

    def __init_lp_problems(self):

        self._var_mapping = {}
        self._lp7 = None
        self._fva = None

        demands = list(self._demands_dict.keys())
        self._lp7 = Fastcore.create_optlang_lp7(self._model, demands, epsilon=self.epsilon)
        self._fva = Fastcore.create_optlang_fba(self._model)

        for rxn, met in self._demands_dict.items():
            z_var_id = Fastcore.AUXILIARY_VAR_PREFIX + rxn
            z_var = self._lp7.variables.get(z_var_id)
            self._var_mapping[z_var] = met

    def __run_lp7_reachability(self, reactions_to_block):
        not_produced = []
        variables_to_block = {}

        if len(reactions_to_block) > 0:
            if hasattr(reactions_to_block[0], 'id'):
                reactions_to_block = [r.id for r in reactions_to_block]

            for r in reactions_to_block:
                var = self._lp7.variables.get(r)
                variables_to_block[var] = (var.lb, var.ub)
                var.lb = 0
                var.ub = 0

        self._lp7.optimize()
        eps = 0.99 * self.epsilon
        for z_var, met in self._var_mapping.items():
            if z_var.primal - eps > self.tolerance:
                continue
            not_produced.append(met.id)

        for r in reactions_to_block:
            var = self._lp7.variables.get(r)
            (var.lb, var.ub) = variables_to_block[var]

        return not_produced

    def __run_fva_reachability(self, reactions_to_block):
        lp_model = self._fva
        not_produced = []
        if len(reactions_to_block) > 0:
            if hasattr(reactions_to_block[0], 'id'):
                reactions_to_block = [r.id for r in reactions_to_block]

        bounds_dict = {}
        for r in reactions_to_block:
            var = lp_model.variables.get(r)
            bounds_dict[var] = var.lb, var.ub
            var.lb = 0
            var.ub = 0

        objective_coefficients = {v: 0 for v in lp_model.variables}
        for r, m in self._demands_dict.items():
            var = lp_model.variables.get(r)
            objective_coefficients[var] = 1
            lp_model.objective.set_linear_coefficients(objective_coefficients)
            lp_model.update()
            lp_model.optimize()
            objective_coefficients[var] = 0

            if lp_model.status == 'infeasible':
                warnings.warn("Infeasible solution for %s" % m)

            if var.primal < self._tolerance:
                not_produced.append(m.id)

        for r in reactions_to_block:
            var = lp_model.variables.get(r)
            var.lb = bounds_dict[var][0]
            var.ub = bounds_dict[var][1]

        return not_produced

    def run_reactions_reachability(self, reactions_to_block, method='lp7'):

        if method == 'lp7':
            return self.__run_lp7_reachability(reactions_to_block)
        elif method == 'fva':
            return self.__run_fva_reachability(reactions_to_block)
        else:
            raise NotImplementedError

    def single_gene_reachability(self, gene_list=[], method='lp7', rxn_str_sep='|'):

        if len(gene_list) == 0:
            gene_list = [g.id for g in self._model.genes]

        if hasattr(gene_list[0], 'id'):
            gene_list = [g.id for g in gene_list]

    
        logging.info(f"Running reachability for {len(gene_list)} genes")
        data = []
        for g in gene_list:

            reactions_to_block = self._gene_knockout_reactions[g]
            if len(reactions_to_block) == 0:
                continue

            not_produced = self.run_reactions_reachability(reactions_to_block, method=method)
            if len(not_produced) == 0:
                continue

            reactions_strn = rxn_str_sep.join([r for r in reactions_to_block])
            for m in not_produced:
                m = self._model.metabolites.get_by_id(m)
                data.append([g, m.id, m.name, reactions_strn])

        columns = ['gene_id', 'compound_id', 'compound_name', 'reactions']
        df_reachability = pd.DataFrame(columns=columns, data=data)
        df_reachability.index.name = 'idx'

        return df_reachability

    def single_reaction_reachability(self, reaction_list=[], method='lp7', find_ums=False):

        if len(reaction_list) == 0:
            reaction_list = [r.id for r in self._model.reactions]

        if hasattr(reaction_list[0], 'id'):
            reaction_list = [r.id for r in reaction_list]

        data = []
        for r in reaction_list:

            not_produced = self.run_reactions_reachability([r], method=method)
            if len(not_produced) == 0:
                continue

            r = self._model.reactions.get_by_id(r)
            for m in not_produced:
                m = self._model.metabolites.get_by_id(m)
                data.append([r.id, m.id, m.name, r.gene_reaction_rule])

        columns = ['reaction_id', 'compound_id', 'compound_name', 'gpr']
        df_reachability = pd.DataFrame(columns=columns, data=data)
        df_reachability.index.name = 'idx'

        return df_reachability

    def test_target_products(self):
        self._not_reachable_products = self.__run_lp7_reachability([])
        return self._not_reachable_products

    @staticmethod
    def to_square_form(df, gene_col='gene_id', task_col='compound_id', value_col=None):
        if value_col is None:
            value_col = "values"
            df[value_col] = 1
            
        df_square = df.pivot_table(index=task_col, columns=gene_col, values=value_col, fill_value=0.0)

        return df_square


class TaskTester(object):

    AUXILIARY_VAR_PREFIX = "Y_var_task"
    AUXILIARY_CONS_PREFIX = "Y_const_task"

    def __init__(self, cobra_model, task_list, zero_tolerance=1e-9, info_level=logging.INFO, debug=False):

        assert len(task_list) > 0
        logging.basicConfig(level=info_level)

        self._model = cobra_model.copy()
        self._debug = debug

        logging.info("- Model: %s" % cobra_model.id)
        logging.info(f"\t|Reactions|={len(self._model.reactions)}")
        logging.info(f"\t|Metabolites|={len(self._model.metabolites)}")
        logging.info(f"\t|Genes|={len(self._model.genes)}")

        self._original_bounds = {r.id: r.bounds for r in self._model.reactions}

        for r in self._model.exchanges:
            r.bounds = (0, 0)
        
        self._tasks = DictList(task_list)
        self._solver = None
        self._sources = {}
        self._demands = {}
        self._zero_tolerance = zero_tolerance
        self._infeasible_tasks = []

        self._gene_knockout_reactions = find_gene_knockout_reactions(self._model)

        logging.info("- Creating Metabolic Task Tester")

        self.__initialize_tester()
        self.__init_lp_solver()

        logging.info(f"- Testing infeasible metabolic tasks")
        tested_taks = self.test_all_tasks()
        
        for task_id, success in tested_taks.items():
            if success:
                continue
            else:
                task = self.tasks.get_by_id(task_id)
                self._infeasible_tasks.append(task)
                self._tasks.remove(task)
        
        if len(self._infeasible_tasks) > 0:
            logging.warning(f"- {len(self._infeasible_tasks)} tasks failed test, skiping them.")

    @property
    def tasks(self):
        return self._tasks

    @property
    def infeasible_tasks(self):
        return self._infeasible_tasks

    @property
    def solver(self):
        return self._solver

    def __initialize_tester(self):
        logging.info("- Initializing steps")
        logging.info("- Registering metabolic tasks")
        logging.info(f"\t|Metabolic tasks|={len(self.tasks)}")
        fail_to_register = []
        for task in self.tasks:
            try:
                self.__register_task(task)
            except TaskRegisterError as e:
                logging.warning(f"- Cant' register task {task.id}: " + str(e))
                fail_to_register.append(task)
        
        if len(fail_to_register) > 0:
            logging.warning(f"- Removing {len(fail_to_register)} incompatible tasks from the list")
            for task in fail_to_register:
                self._tasks.remove(task)

    def __add_sink(self, metabolite, type='input'):
            if type=='input':
                sink_id = f"TASK_INPUTt_{metabolite.id}"
                coefficient = 1
            elif type == 'output':
                sink_id = f"TASK_OUTPUT_{metabolite.id}"
                coefficient = -1
            else:
                raise TaskRegisterError(f"Unknown sink type {type}")
            if sink_id in self._model.reactions:
                return sink_id
            sink = Reaction(id=sink_id, name=sink_id, lower_bound=0, upper_bound=0)
            sink.add_metabolites({metabolite: coefficient})
            self._model.add_reaction(sink)
            return sink_id
 
    def __register_task(self, task):
        logging.info(f"\tRegistering Task {task.id}")
        for m in task.inputs:
            if m not in self._model.metabolites:
                raise TaskRegisterError(f"Metabolite {m} not found in model")
            if m in self._sources:
                continue
            metabolite = self._model.metabolites.get_by_id(m)
            source_id = self.__add_sink(metabolite, type='input')
            self._sources[m] = source_id

        for m in task.outputs:
            if m not in self._model.metabolites:
                raise TaskRegisterError(f"Metabolite {m} not found in model")
            if m in self._demands:
                continue
            metabolite = self._model.metabolites.get_by_id(m)
            demand_id = self.__add_sink(metabolite, type='output')
            self._demands[m] = demand_id

    def __init_lp_solver(self):
        logging.info("- Initializing LP solver")
        self._solver = self._model.solver
        self._solver.name = 'Task Testing LP 1'
        self._objective_coefficients = {v: 0.0 for v in self._solver.variables}
        self._solver.objective.set_linear_coefficients(self._objective_coefficients)
        self._solver.objective.direction = 'max'
        self._solver.update()

    def __activate_task(self, task, activate=True):
        for m in task.inputs:
            objective_coefficients = {v: 0.0 for v in self._solver.variables}
            source_id = self._sources[m]
            var = self._solver.variables.get(source_id)
            if activate:
                var.ub = task.inputs[m][1]
                var.lb = task.inputs[m][0]
                objective_coefficients[var] = 1
            else:
                var.lb = 0.0
                var.ub = 0.0
                objective_coefficients[var] = 0.0

        for m in task.outputs:
            demand_id = self._demands[m]
            var = self._solver.variables.get(demand_id)
            if activate:
                var.ub = task.outputs[m][1]
                var.lb = task.outputs[m][0]
                objective_coefficients[var] = 1
            else:
                var.lb = 0.0
                var.ub = 0.0
                objective_coefficients[var] = 0.0
        
        self._solver.objective.set_linear_coefficients(self._objective_coefficients)
        self._solver.update()

    def test_single_task(self, task):
        if hasattr(task, 'id'):
            task = task.id
        task = self.tasks.get_by_id(task)
        self.__activate_task(task)
        self._solver.optimize()
        self.__activate_task(task, activate=False)
        return self._solver.status


    def test_all_tasks(self):
        result = {}
        for task in self.tasks:
            status = self.test_single_task(task)
            if status == 'optimal':
                result[task.id] = True
            else:
                 result[task.id] = False
        return result

    def single_gene_deletion(self, gene_list=[], rxn_str_sep='|'):

        if len(gene_list) == 0:
            gene_list = [g.id for g in self._model.genes]
        if hasattr(gene_list[0], 'id'):
            gene_list = [g.id for g in gene_list]
    
        logging.info(f"Running single gene deletion for {len(gene_list)} genes on {len(self.tasks)} tasks")
        data = []
        for g in gene_list:
            
            if self._debug:
                logging.info(f"Testing gene {g}")

            reactions_to_block = self._gene_knockout_reactions[g]
            if len(reactions_to_block) == 0:
                continue

            if self._debug:
                logging.info(f"Disbling reactons: {reactions_to_block}")

            bounds = {}
            for r in reactions_to_block:
                var = self._solver.variables.get(r)
                bounds[r] = (var.lb, var.ub)
                var.lb = 0.0
                var.ub = 0.0          
            self._solver.update()

            result = self.test_all_tasks()

            for r in reactions_to_block:
                var = self._solver.variables.get(r)
                var.ub = bounds[r][1] 
                var.lb = bounds[r][0]
            self._solver.update()

            failed_task = [k for k,v in result.items() if not v]

            if len(failed_task) == 0:
                continue

            reactions_strn = rxn_str_sep.join([r for r in reactions_to_block])
            for t_id in failed_task:
                task = self.tasks.get_by_id(t_id)
                data.append([g, task.id, task.system, task.subsystem, reactions_strn])

        columns = ['gene_id', 'task_id', 'system', 'subsystem', 'reactions']
        df_reachability = pd.DataFrame(columns=columns, data=data)
        df_reachability.index.name = 'idx'

        return df_reachability

    def __init_milp(self):
        logging.info("- Initializing MILP model")
        optlang_interface = self._model.solver.interface
        self._milp_model = Fastcore.create_optlang_fba(self._model)
        self._milp_model.name = 'Task Testing MILP 1'

        self._objective_coefficients = {v: 0.0 for v in self._milp_model.variables}
        const_to_add = []
        for task in self.task_list:
            y_var_id = f"{TaskTester.AUXILIARY_VAR_PREFIX}_{task.id}"
            y_var = optlang_interface.Variable(y_var_id, lb=0, ub=1, type='binary')
            self._milp_model.add(y_var)
            self._objective_coefficients[y_var] = 1.0
            self._task2vars[task.id] = y_var

            for m, source in task.sources.items():
                lb, ub = task.get_bounds(m)
                v_var = self._milp_model.variables.get(source.id)
                v_var.lb = 0.0
                v_var.ub = 1000.0

                y_constraint_id = f"{TaskTester.AUXILIARY_CONS_PREFIX}_{task.id}_{source.id}_LHS"
                constraint = optlang_interface.Constraint(v_var - y_var * lb, lb=0, name=y_constraint_id)
                const_to_add.append(constraint)

                y_constraint_id = f"{TaskTester.AUXILIARY_CONS_PREFIX}_{task.id}_{source.id}_RHS"
                constraint = optlang_interface.Constraint(y_var * ub - v_var, lb=0, name=y_constraint_id)
                const_to_add.append(constraint)
            
            for m, demand in task.demands.items():
                lb, ub = task.get_bounds(m)
                v_var = self._milp_model.variables.get(demand.id)
                v_var.lb = 0.0
                v_var.ub = 1000.0

                y_constraint_id = f"{TaskTester.AUXILIARY_CONS_PREFIX}_{task.id}_{demand.id}_LHS"
                constraint = optlang_interface.Constraint(v_var - y_var * lb, lb=0, name=y_constraint_id)
                const_to_add.append(constraint)

                y_constraint_id = f"{TaskTester.AUXILIARY_CONS_PREFIX}_{task.id}_{demand.id}_RHS"
                constraint = optlang_interface.Constraint(y_var * ub - v_var, lb=0, name=y_constraint_id)
                const_to_add.append(constraint)
        
        self._milp_model.add(const_to_add)
        self._milp_model.objective.set_linear_coefficients(self._objective_coefficients)
        self._milp_model.objective.direction = 'max'
        self._milp_model.update()
    def __evaluate_tasks_milp(self, task_list):
        milp_model = self._milp_model
        if len(task_list) == 0:
            return
        # Setting objective coefficients to zero
        self._objective_coefficients = {x: 0.0 for x in milp_model.variables}
        
        # Setting coefficients of binary var correspondint to the tested tasks to one
        for task in task_list:
            y_var = self._task2vars[task.id]
            self._objective_coefficients[y_var] = 1.0
        
        # Updating milp model
        milp_model.objective.set_linear_coefficients(self._objective_coefficients)
        milp_model.update()

        task_dict = {task.id: task for task in task_list}
        succeed_tasks = set()
        failed_tasks = set()
        untested_taks = set([task.id for task in task_list])
        while len(untested_taks) > 0:
            milp_model.optimize()
            if milp_model.status == 'infeasible':
                raise InfeasibleProblemError()

            for task_id in untested_taks:
                y_var = self._task2vars[task_id]
                if  abs(1 - y_var.primal) < self.zero_tolerance:
                    succeed_tasks |= set( [task_id] )
                    
            if len(untested_taks & succeed_tasks) > 0:
                untested_taks -= succeed_tasks
            else:
                failed_tasks = untested_taks
                untested_taks = set()
        
        return [task_dict[i] for i in failed_tasks]
    


class MetabolicTask(object):

    TASK_PREIX = "TASK"
    
    def __init__(self, id, inputs, outputs, system="", subsystem="", 
                 description="", annotations={}, should_fail=False):
        
        self._id = str(id)
        self._system = system
        self._subsystem = subsystem
        self._description = description
        self._annotations = annotations
        self._inputs = inputs 
        self._outputs = outputs

        self._should_fail = should_fail
        self._model = None
        self._sources = None
        self._demands = None

        self._original_objective = {}
        
    @property
    def id(self):
        return self._id
        
    @property
    def system(self):
        return self._system
    
    @property
    def subsystem(self):
        return self._subsystem

    @property
    def inputs(self):
        return self._inputs
    
    @property
    def outputs(self):
        return self._outputs

    @property
    def sources(self):
        return self._sources
    
    @property
    def demands(self):
        return self._demands

    @property
    def is_registered(self):
        return self._model is not None

    def get_bounds(self, m_id):
        if m_id in self._inputs:
            return self._inputs[m_id]
        if m_id in self._outputs:
            return self._outputs[m_id]
        else:
            return None
           
    def to_dict(self):
        return {
                "id": self._id,
                "inputs": self._inputs,
                "outputs": self._outputs,
                "should_fail": self._should_fail,
                "system": self._system,
                "subsystem": self._subsystem,
                "description": self._description,
                "annotations": self._annotations
            }
    
    def to_frame(self):
        
        columns = ["id", "metabolite",  "lower_bound", "upper_bound", "is_output",
                   "should_fail", "system", "subsystem", "description", "annotations"]    
        
        data = []
        for m_id in self.inputs:
            row = {}
            row["id"] = self._id
            row["metabolite"] = m_id
            row["lower_bound"] = self.inputs[m_id][0]
            row["upper_bound"] = self.inputs[m_id][1]
            row["is_output"] = False
            row["should_fail"] = self._should_fail
            row["system"] = self._system
            row["subsystem"] = self._subsystem
            row["description"] = self._description
            for k,v in self._annotations.items():
                row[k.lower()] = v
            data.append(row)
        for m_id in self.outputs:
            row = {}
            row["id"] = self._id
            row["metabolite"] = m_id
            row["lower_bound"] = self.outputs[m_id][0]
            row["upper_bound"] = self.outputs[m_id][1]
            row["is_output"] = True
            row["should_fail"] = self._should_fail
            row["system"] = self._system
            row["subsystem"] = self._subsystem
            row["description"] = self._description
            for k,v in self._annotations.items():
                row[k.lower()] = v
            data.append(row)
        
        columns = list(row.keys())
        
        df = pd.DataFrame(data, columns=columns, )
        return df.set_index(['id', 'metabolite'])



    def remove(self):
        if self._model is None:
            return
        self._model.remove_reactions([r for r in self._sources])
        self._sources = None
        self._model.remove_reactions([r for r in self._demands])
        self._demands = None
        self._model = None

    def activate(self):
        if not self.is_registered:
            return

        self._original_objective = {}
        for r in self._model.reactions:
            self._original_objective[r.id] = r.objective_coefficient
            if r.objective_coefficient == 0:
                continue
            r.objective_coefficient = 0
        
        for m in self.inputs:
            self.sources[m].bounds = self.inputs[m]
            self.sources[m].objective_coefficient = 1
        
        for m in self.outputs:
            self.demands[m].bounds = self.outputs[m]
            self.demands[m].objective_coefficient = 1

    def deactivate(self):
        if not self.is_registered:
            return
        for m in self.inputs:
            self.sources[m].bounds = (0.0, 0.0)
        for m in self.outputs:
            self.demands[m].bounds = (0.0, 0.0)
        
        for r in self._original_objective:
            rxn = self._model.reactions.get_by_id(r)
            rxn.objective_coefficient = self._original_objective[r]