import enum
import re
import logging
import boolean
import numpy as np
import pandas as pd
from cobra.core.gene import GPR
from cobra.manipulation import remove_genes

from pyfastcore import Fastcore

from ast import (
    And,
    BoolOp,
    Expression,
    Name,
    Or,
)



GPR_LOGIC_OR_MAP = ('max', 'sum')
ME_METHODS = ('fastcore', )


def _get_enzymes_recursive(expression, or_operator="|", and_operator="&"):
    list_of_enzymes = []
    if expression.isliteral:
        list_of_enzymes.append(str(expression))
    else:
        expression = expression.simplify()
        if expression.operator == or_operator:
            for arg in expression.args:
                if arg.isliteral:
                    list_of_enzymes.append([str(arg)])
                else:
                    enzymes = _get_enzymes_recursive(arg)
                    list_of_enzymes.extend(enzymes)
        elif expression.operator == and_operator:
            enzymes = []
            simple = True
            for arg in expression.args:
                subunits = _get_enzymes_recursive(arg)
                if len(subunits) > 1:
                    simple = False
                    enzymes = [enzymes + s for s in subunits]
                else:
                    enzymes.append(subunits[0])
            if simple:
                list_of_enzymes.append(enzymes)
            else:
                list_of_enzymes.extend(enzymes)
        else:
            raise Exception("ERROR IN EXPRESSION: Unknown operator/literar:", str(expression))

    return list_of_enzymes


def get_enzymes(gene_reaction_rule):
    dash_found = False
    if re.search("-", gene_reaction_rule):
        gene_reaction_rule = re.sub("-", "_", gene_reaction_rule)
        dash_found = True

    algebra = boolean.BooleanAlgebra()
    expression = algebra.parse(gene_reaction_rule, simplify=True)
    if expression.isliteral:
        list_of_enzymes = [[str(expression)]]
    else:
        expression = expression.simplify()
        list_of_enzymes = _get_enzymes_recursive(expression)
        for enzyme in list_of_enzymes:
            wrong_parse = False
            for subunit in enzyme:
                if isinstance(subunit, str):
                    continue
                wrong_parse = True
                break
        if wrong_parse:
            expression = expression.distributive()
            list_of_enzymes = _get_enzymes_recursive(expression)
    if dash_found:
        for enzyme in list_of_enzymes:
            for i,gene in enumerate(enzyme):
                enzyme[i] = re.sub("_", "-", gene)           
    list_of_enzymes = tuple([tuple(sorted(i)) for i in list_of_enzymes])
    return list_of_enzymes


def rename_element_ids(model, rename_dict, type='reaction'):
    if type == 'reaction':
        element_list = model.reactions
    for id_old, id_new in rename_dict.items():
        if id_old not in element_list:
            continue
        el = element_list.get_by_id(id_old)
        el.id = id_new
    model.repair()
    return model


class UnsupportedGPROperator(Exception):
    def __init__(self, message="Supported operators for GPR logic \"or\" are \"max\" or \"sum\""):
        self.message = message
        super().__init__(self.message)


class UnknownMEMethod(Exception):
    message = "Supported ME methods include:", " ".join(ME_METHODS)
    def __init__(self, message=message):
        self.message = message
        super().__init__(self.message)


class CSMBuilder:
    
    def __init__(self, cobra_model, gene_expression, gene_thredholds, csm_id=None,
                 me_method='fastcore', gpr_or='max', fill_missing_gene=0.0, copy_model=True,
                 global_lb_q_threshold=0.25, global_ub_q_threshold=0.7, base_core=[],
                 penalty_weights={0.75:0, 0.5:-1, 0.25:-10, 0.1:-100}, epsilon=1e-7,
                 level=logging.INFO, init_me_solver=True, **kwargs):
        """

        Parameters
        ----------
        cobra_model : cobra Model 
            A model to be use as universal or reference
        gene_expression: dict 
            A dictionarywith gene IDs (present in the model) and expression values
        gene_thredholds: dict
            A dictionary with gene IDs (present in the model) and thresholds to binarize the expression
        fill_missing_gene: float
            Default expression to assign to genes with unknown values
        me_method: String
            The model extraction method used to create a context-specific model
        """

        logging.basicConfig(level=level)
        logging.info("- Creating CSMBuilder")

        if me_method not in ME_METHODS:
            raise UnknownMEMethod("")
        self._me_method = me_method

        if gpr_or not in GPR_LOGIC_OR_MAP:
            raise UnsupportedGPROperator()
        self._gpr_or = gpr_or

        if copy_model:
            self._model = cobra_model.copy()
        else:
            self._model = cobra_model

        self._original_bounds = {}
        for r in self._model.reactions:
            self._original_bounds[r.id] = r.bounds

        self._csm_id = csm_id
        if self._csm_id is None:
            self._csm_id = self._model.id

        assert fill_missing_gene >= 0
        self._fill_missing_gene = fill_missing_gene

        self._gene_expression = dict()
        self.__consolidate_genes(gene_expression)

        assert global_lb_q_threshold >= 0.0
        assert global_lb_q_threshold <= 1.0 
        assert global_ub_q_threshold >= 0.0
        assert global_ub_q_threshold <= 1.0
        assert global_lb_q_threshold < global_ub_q_threshold
        
        self._global_lb_threshold = 0.0
        self._global_lb_threshold = max(gene_expression.values())
        
        self.__calculate_global_thresholds(global_lb_q_threshold, global_ub_q_threshold)

        self._gene_thresholds = dict()
        self.__consolidate_thresholds(gene_thredholds)

        self._gene_confidences = {}
        self.__binarize_gene_expression()

        self._reaction_expression = {}
        self.__map_gene_expression()

        self._base_core = []
        self.__consolidate_base_core(base_core)

        self._inferred_core = []
        self.__calculate_reaction_core()

        self._penalty_weights = penalty_weights
        self._penalties = {}
        self.__calculate_penalties()

        self._epsilon = epsilon

        self._kwargs = kwargs
        
        self._consistent_subnetwork = []
        self._cs_model = None

        self._me_solver = None
        if init_me_solver:
            self.__init_me_solver()

    #############
    # Properties
    #############

    @property
    def model(self):
        return self._model

    @property
    def csm_id(self):
        return self._csm_id
    
    @csm_id.setter
    def csm_id(self, csm_id):
        self._csm_id = csm_id

    @property
    def gene_expression(self):
        return self._gene_expression

    @property
    def gene_thresholds(self):
        return self._gene_thresholds

    @property
    def gene_confidences(self):
        return self._gene_confidences
    
    @property
    def reaction_expression(self):
        return self._reaction_expression

    @property
    def gpr_or(self):
        return self._gpr_or

    @property
    def base_core(self):
        return self._base_core

    @property
    def inferred_core(self):
        return self._inferred_core

    @property
    def core_reactions(self):
        core_reactions = self.base_core + self.inferred_core
        return frozenset(core_reactions)

    @property
    def penalties(self):
        return self._penalties

    @property
    def epsilon(self):
        return self._epsilon

    @property
    def cs_model(self):
        if self._cs_model is None:
            logging.warning("- CS models has not been built. First run CSMBuilder.build_csm()")
        return self._cs_model


    ##################
    # Private methods
    ##################

    def __consolidate_genes(self, gene_expression):
        """
        Find genes from the model that are  not present in the gene expression dict
        and fill the expression values of missing using the fill_missing_gene parameter
        """
        logging.info("* Consolidating genes")
        logging.info(f"\t- Total genes in model: {len(self._model.genes)}")
        missing = 0
        for g in self.model.genes:
            if g.id in gene_expression:
                self._gene_expression[g.id] = gene_expression[g.id]
            else:
                self._gene_expression[g.id] = self._fill_missing_gene
                missing += 1
        logging.info(f"\t- Total missing genes found: {missing}")
        logging.info(f"\t- Filling missing genes with: {self._fill_missing_gene}")
    
    def __calculate_global_thresholds(self, lb_quantile, ub_quantile):
        s = pd.Series(self._gene_expression)
        logging.info(f"* Calculating global lb and lb threshold using quantiles {lb_quantile} and {ub_quantile} on gene expression")
        global_lb_thr = s[s>0].quantile(lb_quantile)
        self._global_lb_threshold = global_lb_thr
        logging.info(f"\t- Global lb threshold value: {global_lb_thr}")
        global_ub_thr = s[s>0].quantile(ub_quantile)
        self._global_ub_threshold = global_ub_thr
        logging.info(f"\t- Global ub threshold value: {global_ub_thr}")
        
    def __consolidate_thresholds(self, gene_thredholds):
        """
        Find threshold from the model that are not present in the gene threshold dict
        and fill the expression values of missing using the fill_missing_gene parameter
        """
        logging.info("* Consolidating thresholds")
        logging.info(f"\t- Total genes in model: {len(self.model.genes)}")
        missing = 0
        for g in self.model.genes:
            if g.id in gene_thredholds:
                if gene_thredholds[g.id] < self._global_lb_threshold:
                    self._gene_thresholds[g.id] = self._global_lb_threshold
                elif gene_thredholds[g.id] > self._global_ub_threshold:
                    self._gene_thresholds[g.id] = self._global_ub_threshold
                else:
                    self._gene_thresholds[g.id] = gene_thredholds[g.id]
            else:
                self._gene_thresholds[g.id] = self._global_lb_threshold
                missing += 1
        logging.info(f"\t- Total missing genes found: {missing}")
        logging.info(f"\t- Filling missing genes with: {self._fill_missing_gene}")

    def __binarize_gene_expression(self):
        """
        Binarize gene expression values into {0,1} appling gene specific thredholds
        """
        logging.info("* Binarizing gene expression")
        total_active = 0
        total_inactive = 0
        for g in self._model.genes:
            confidence = self._gene_expression[g.id] >= self._gene_thresholds[g.id]
            self._gene_confidences[g.id] = confidence
            if confidence:
                total_active += 1
            else:
                total_inactive += 1

        logging.info(f"\t- Total genes {len(self._model.genes)}")
        logging.info(f"\t- Total active genes {total_active}")
        logging.info(f"\t- Total inactive genes {total_inactive}")

    def __map_gene_expression(self):
        """
        Map gene expression (continous) values thruoug GPRs into reaction expression values
        """
        aux_dict = {}
        for r in self.model.reactions:
            if r.gpr is None or len(r.gene_reaction_rule) == 0:
                self._reaction_expression[r.id] = np.nan
                continue
            if r.gene_reaction_rule not in aux_dict:
                values_dict = {g.id:self.gene_expression[g.id] for g in r.genes}
                result = self.safe_eval_gpr(r.gpr.body, values_dict, or_func=self.gpr_or)
                aux_dict[r.gene_reaction_rule] = result
            self._reaction_expression[r.id] = aux_dict[r.gene_reaction_rule]

    def __consolidate_base_core(self, base_core):
        logging.info("* Consolidating user provided core")
        if type(base_core) is str:
            base_core = [base_core]
        
        total_excluded = 0
        for r in base_core:
            if r in self._model.reactions:
                self._base_core.append(r)
            else:
                total_excluded += 1
                logging.warning(f"\t- User provided base core reaction {r} not in model.")
        if total_excluded > 0:
            logging.warning(f"\t- Excluding {len(r)} user provided base core reactions not founded in model {self._model.id}.")
        logging.info(f"\t- Base core size: {len(self.base_core)} reactions")

    def __calculate_reaction_core(self):
        logging.info("* Calculating gene inferred core reactions")
        for r in self.model.reactions:
            if r.gpr is None or len(r.gene_reaction_rule) == 0:
                continue
            inactive_genes = {g.id for g in r.genes if not self._gene_confidences[g.id]}
            if r.gpr.eval(inactive_genes):
                self._inferred_core.append(r.id)
        logging.info(f"\t- Inferred core size: {len(self.inferred_core)} reactions")
           
    def __calculate_penalties(self):
        logging.info(f"* Calculating reaction penalties using quantiles")
        reaction_expression = pd.Series(self._reaction_expression)
        non_zero_expression = reaction_expression[reaction_expression>0]
        self._penalties = pd.Series(0.0, index=reaction_expression.index)
        for q,p in self._penalty_weights.items():
            thr = non_zero_expression.quantile(q)
            mask = reaction_expression < thr
            self._penalties[mask] = p
        self.penalties[self.core_reactions] = 0.0

    def __init_me_solver(self):
        if self._me_method == 'fastcore':
            self._me_solver = Fastcore(self.model, self.core_reactions, penalties=self.penalties, copy_model=False, **self._kwargs)
        else:
            raise UnknownMEMethod()

    def __correct_thresholds(self, lp_fname=None):
        if self._cs_model is None:
            return False

        logging.info(f"* Consolidating gene activity for non-core reactions")
        consistent_subnetwork = set(self._consistent_subnetwork)
        non_core_reactions = consistent_subnetwork - self.core_reactions
        gene_list = []
        gpr_list = []
        for r in non_core_reactions:
            r = self._cs_model.reactions.get_by_id(r)
            if r.gpr is None or len(r.gene_reaction_rule) == 0:
                continue
            gpr_list.append(r.gene_reaction_rule)
            gene_list.extend([g.id for g in r.genes])
        
        logging.info(f"\t- {len(gpr_list)} non-core reaction requires an update in their gene context.")
        gpr_list = set(gpr_list)
        gene_list = set(gene_list)

        logging.info(f"\t- Processing {len(gpr_list)} unique GPR containing {len(gene_list)} genes.")

        gene_weights = {}
        for g in gene_list:
            weight = self.gene_thresholds[g] - self.gene_expression[g] 
            gene_weights[g] = weight
        
        optlang_interface = self.cs_model.solver.interface
        logging.info(f"\t- Creating MinGene MILP problem")
        logging.info(f"\t- Finding minimal gene context compatible with the non-core-reactions")
        milp_model = CSMBuilder.create_mingene_milp(optlang_interface, gpr_list, gene_weights=gene_weights)
        if lp_fname is not None:
            with open(str(lp_fname), 'w') as fh:
                fh.write(milp_model.to_lp())
        
        milp_model.optimize()
        if milp_model.status != 'optimal':
            logging.warning(f"\t- Min Gene problem could not")
            return False

        logging.info(f"\t- Optimal solution found for MinGene problem!")
        new_active_genes = [k for k,v in milp_model.primal_values.items() 
                                if v >= 0.9999 and k in gene_list]
        logging.info(f"\t- Context adjustment requires to change the status of {len(new_active_genes)} genes to active")
        logging.info(f"\t- Adjusting context be reducing gene thresholds")
        for g in new_active_genes:
            # Skiping already active genes
            if self._gene_confidences[g]:
                continue
            if self._gene_expression[g] >= self._gene_thresholds[g]:
                continue
            relaxed_threshold = self._gene_expression[g] - self.epsilon
            relaxed_threshold = max(0, relaxed_threshold)
            self._gene_thresholds[g] = relaxed_threshold
            self._gene_confidences[g] = True
        self.__binarize_gene_expression()
        
        return True

    ################
    # Pulic methods
    ################

    def run_me_solver(self):
        self._cs_model = None
        self._consistent_subnetwork = []
        if self._me_method == 'fastcore':
            logging.info(f"Running {self._me_method} model extraction method")
            self._me_solver.fast_core()
            self._consistent_subnetwork = self._me_solver.consistent_subnetwork
        else:
            raise UnknownMEMethod("")
        logging.info(f"Model extraction method finish!")
    
    def build_csm(self, consolidate_genes=True, save_mingene=None):
        
        if len(self._consistent_subnetwork) == 0:
            logging.warning("ME solver has not be run, running it now")
            self.run_me_solver()
        
        logging.info(f"Creating context-model")
        self._cs_model = self._model.copy()
        self._cs_model.id = self.csm_id
        to_remove = []
        for r in self._cs_model.reactions:
            if r.id in self._consistent_subnetwork:
                continue
            to_remove.append(r.id)
        self._cs_model.remove_reactions(to_remove)

        inactive_metabolites = [m for m in self._cs_model.metabolites if len(m.reactions) == 0]
        self._cs_model.remove_metabolites(inactive_metabolites)
        self._cs_model.repair()

        # Restoring de original bounds (Fastcore relax them)
        for r in self._cs_model.reactions:
            r.bounds = self._original_bounds[r.id]
        
        if consolidate_genes:
            self.__correct_thresholds(lp_fname=save_mingene)
            genes_to_remove = [g for g,conf in self.gene_confidences.items() 
                                        if conf == False and g in self._cs_model.genes]
            genes_to_remove = list(set(genes_to_remove))
            
            # Fix needed to avoid the error that cobra.manipulation.remove_genes raises when trying 
            # to remove a gene which has the same ID than a reactions (e.g. 'ADA', 'AGPAT1', 'RPE')
            # The fix consists in temporary renaming conflicting reactions before removing the genes
            # and then restor the original reaction's ID back.
            rename_fix_dict = {}
            rename_restore_dict = {}
            for r in self._cs_model.reactions:
                if r.id not in self._cs_model.genes:
                    continue
                fixed_r_id = "FIXED_" + r.id
                rename_fix_dict[r.id] = fixed_r_id
                rename_restore_dict[fixed_r_id] = r.id

            rename_element_ids(self._cs_model, rename_fix_dict)
            logging.info(f"\t- Pruning {len(genes_to_remove)} inactive genes from the context-specific model")
            remove_genes(self._cs_model, genes_to_remove)
            self._cs_model.repair()
            rename_element_ids(self._cs_model, rename_restore_dict)

        return self._cs_model


    @staticmethod
    def create_mingene_milp(optlang_interface, gpr_list, gene_weights={}, default_weight=1.0):
        """
        Create an optlang MILP problem for finding a subset of genes that minimize a linear 
        cost function on the genes, subject to a set of MILP constraints constructed from
        the set of boolean expression that represent Gene-Protein-Reaction rules (gpr_list)
        
        Parameters
        ----------
        optlang_interface: module
            an optlang interface used to create the Model
        gpr_list: list
            a list of strings representing gene-protein-rules as boolean
            expression such as ['(A and B) or (A and C)', 'A', 'A or C', 'E and D']
        gene_weights: dict, optional
            a dict of gene ids and the weights used to create the objective function
        default_weight: float, optional
            defulat value to use as the objective coefficinet of genes not found in gene_weights 

        """

        gene_list = []
        complex_list = []
        grp_enzymes_dict = {}
        for gpr in gpr_list:
            enzyme_list = get_enzymes(gpr)
            grp_enzymes_dict[gpr] = enzyme_list
            for enzyme in enzyme_list:
                gene_list.extend(enzyme)
                if len(enzyme) > 1:
                    complex_list.append(enzyme)

        gene_list = sorted(set(gene_list))
        complex_list = sorted(set(complex_list), key=lambda x: len(x))

        if len(gene_weights) != len(gene_list):
            for g in gene_list:
                if g in gene_weights:
                    continue
                gene_weights[g] = default_weight

        lp_model = optlang_interface.Model()
        lp_model.name = 'MinGene'
        var_dict = {}

        # Adding gene variables
        for g in gene_list:
            x_var = optlang_interface.Variable(g, lb=0, ub=1, type='continuous')
            var_dict[g] = x_var
            lp_model.add(x_var)
        lp_model.update()

        # Adding enzyme complex binary variables and constraints
        for i,enzyme in enumerate(complex_list):
            c_id = f"Complex_{i+1}"
            y_var = optlang_interface.Variable(c_id, lb=0, ub=1, type='binary')
            var_dict[enzyme] = y_var
            lp_model.add(y_var)
            expr = None
            for g in enzyme:
                x_var = var_dict[g]
                if expr is None:
                    expr = x_var
                else:
                    expr += x_var
            expr -= len(enzyme) * y_var
            constr = optlang_interface.Constraint(expr, lb=0, ub=len(enzyme))
            lp_model.add(constr)
        lp_model.update()

        # Adding GPR constraints
        for gpr, enzyme_list in grp_enzymes_dict.items():
            expr = None
            for enzyme in enzyme_list:
                if len(enzyme) == 1:
                    enzyme = enzyme[0]
                var = var_dict[enzyme]
                if expr is None:
                    expr = var
                else:
                    expr += var
            cons_name = gpr.replace(" ","")
            cons_name = cons_name.replace("and","&")
            cons_name = cons_name.replace("or","|")    
            constr = optlang_interface.Constraint(expr, lb=1)
            lp_model.add(constr)
        lp_model.update()

        objective_coefficients = {lp_model.variables.get(g): gene_weights[g]
                                  for g in gene_list}

        lp_model.objective.set_linear_coefficients(objective_coefficients)
        lp_model.objective.direction = 'min'
        lp_model.update()
        return lp_model

    @staticmethod
    def safe_eval_gpr(expr, values_dict, or_func='max'):
        if isinstance(expr, Expression):
            return CSMBuilder.safe_eval_gpr(expr.body, values_dict)
        elif isinstance(expr, Name):
            fgid = expr.id
            if fgid not in values_dict:
                return 0
            return values_dict[fgid]
        elif isinstance(expr, BoolOp):
            op = expr.op
            if isinstance(op, Or):
                if or_func == 'max':
                    return max(CSMBuilder.safe_eval_gpr(i, values_dict) for i in expr.values)
                elif or_func == 'sum':
                    return sum(CSMBuilder.safe_eval_gpr(i, values_dict) for i in expr.values)
                else:
                    raise UnsupportedGPROperator
            elif isinstance(op, And):
                return min(CSMBuilder.safe_eval_gpr(i, values_dict) for i in expr.values)
            else:
                raise TypeError("unsupported operation " + op.__class__.__name__)
        elif expr is None:
            return 0
        else:
            raise TypeError("unsupported operation  " + repr(expr))

    

    
