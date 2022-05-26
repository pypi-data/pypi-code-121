import numpy as np
from numpy import linalg as LA
from scipy.optimize import minimize_scalar

from apacepy.control import InterventionAffectingContacts


class ContactModel:

    def __init__(self, par_base_contact_matrix):

        self.parBaseContactMatrix = par_base_contact_matrix
        self.contactMatrix = self.parBaseContactMatrix.value
        self.nGroups = len(self.contactMatrix)

    def update_contact_rates(self, interventions_in_effect):

        self.contactMatrix = self.parBaseContactMatrix.value
        for i in interventions_in_effect:
            if isinstance(i, InterventionAffectingContacts):
                all1 = np.ones((self.nGroups, self.nGroups))
                ratio = all1 + i.parPercChangeInContactMatrix.value
                self.contactMatrix = np.multiply(self.contactMatrix, ratio)

        return self.contactMatrix


class FOIModel:

    def __init__(self, par_base_contact_matrix, compartments):
        """
        :param par_base_contact_matrix: (Parameter) contact matrix under no intervention
        :param compartments: (list) of model compartments
        """

        self.contactModel = ContactModel(par_base_contact_matrix=par_base_contact_matrix)
        self.nOfMixingGroups = par_base_contact_matrix.value.shape[0]
        self.compartments = compartments
        self.comparts_with_epi_dep_events = []
        for c in self.compartments:
            if len(c.epiDepEvents) > 0:
                self.comparts_with_epi_dep_events.append(c)

    def update_transmission_rates(self, interventions_in_effect):
        """ updates transmission rates of epidemic-dependent events"""

        # find the population size of mixing groups
        size_of_mixing_groups = [0] * self.nOfMixingGroups
        for c in self.compartments:
            size_of_mixing_groups[c.idxContactMatrix] += c.size

        # calculate the contact matrix depending on which intervention is in effect
        contact_matrix = self.contactModel.update_contact_rates(interventions_in_effect=interventions_in_effect)

        # go over all compartments with an active epidemic dependent event
        for receiving in self.comparts_with_epi_dep_events:
            if receiving.size == 0:
                continue

            for e in receiving.epiDepEvents:

                # find susceptibility of this compartment
                try:
                    susceptibility = receiving.susParams[e.generatingPathogen].value
                except IndexError:
                    raise IndexError("If modeling more than 1 pathogen, for the compartment '{}', "
                                     "either provide the number of pathogens "
                                     "or the list of susceptibility parameters "
                                     "(length of this list should be equal to the number of pathogens).".format(receiving.name))

                # find transmission rate out of this compartment
                rate = 0
                for j in range(len(self.compartments)):

                    # find the infectivity of this (potentially) infecting compartment
                    infecting = self.compartments[j]
                    if infecting.size > 0:
                        try:
                            infectivity = infecting.infParams[e.generatingPathogen].value
                        except IndexError:
                            raise IndexError("If modeling more than 1 pathogen, for the compartment '{}', "
                                             "either provide the number of pathogens "
                                             "or the list of infectivity parameters.".format(infecting.name))

                        if infectivity > 0:
                            # contact rate between the susceptibles and infecting compartments
                            contact = contact_matrix[receiving.idxContactMatrix][infecting.idxContactMatrix]

                            # transmission rate upon contact
                            sus_contact_inf = susceptibility * contact * infectivity

                            # transmission rate
                            if sus_contact_inf > 0:
                                rate += sus_contact_inf * infecting.size / \
                                        size_of_mixing_groups[infecting.idxContactMatrix]

                e.set_rate(value=rate)


def get_waifw(contact_matrix, susceptibilities, infectivities):
    """
    :param contact_matrix: (list of lists) contact rates [C_ij], where
        C_ij is the rate at which a susceptible person in group i comes into contact with an infectious
        person in group j
    :param susceptibilities: (list) of susceptibility values [sucp_i]
    :param infectivities: (list) of infectivity values [inf_j]
    :returns: the Who Acquired Infection From Whom matrix [a_ij] = [susp_i * C_ij * inf_j]
    """

    waifw = []
    for i, row in enumerate(contact_matrix):
        waifw_row = []
        for j in range(len(row)):
            waifw_row.append(susceptibilities[i] * contact_matrix[i][j] * infectivities[j])
        waifw.append(waifw_row)

    return waifw


def get_r_nut_from_ngm(next_gen_matrix):
    """
    :param next_gen_matrix: (list of lists) next generation matrix
    :returns:  R0 calculated from a next generation matrix
    """

    w, v = LA.eig(np.array(next_gen_matrix))
    # R0 is the dominant eigen value
    max_w = max(w)

    try:
        max_w = max_w.real
    except AttributeError:
        max_w = max_w

    return max_w


def get_next_generation_matrix(waifw, pop_sizes, inf_dur):
    """
    :param waifw: (list of lists) the Who Acquired Infection From Whom matrix
    :param pop_sizes: (list) size of each group
    :param inf_dur: (float) duration of infectiousness
    :return: (np.array) the next generation matrix
        https://www.sciencedirect.com/science/article/pii/S2468042717300209
    """

    F = []
    for i, row in enumerate(waifw):
        F_row = []
        for j in range(len(row)):
            F_row.append(waifw[i][j] * pop_sizes[i]/pop_sizes[j])
        F.append(F_row)

    V = np.diag(v=[1/inf_dur]*len(pop_sizes))
    V_inv = np.linalg.inv(V)
    
    return np.matmul(np.array(F), V_inv)


def get_r_nut_from_waifw(waifw, pop_sizes, inf_dur):
    """
    :param waifw: (list of list) who acquires infection from whom
    :param pop_sizes: (list) size of each group
    :param inf_dur: (float) duration of infectiousness
    :returns: R0 calculated from the matrix of who acquires infection from whom
    """

    next_gen_matrix = get_next_generation_matrix(waifw=waifw, pop_sizes=pop_sizes, inf_dur=inf_dur)
    return get_r_nut_from_ngm(next_gen_matrix=next_gen_matrix)


def get_r_nut_from_contact_matrix(contact_matrix, susceptibilities, infectivities, pop_sizes, inf_duration):
    """
    :param contact_matrix: (list of lists) contact rates
    :param susceptibilities: (list) of susceptibility values
    :param infectivities: (list) of infectivity values
    :param pop_sizes: (list) size of each group
    :param inf_duration: (float) duration of infectiousness
    :returns:  R0 calculated from the contact matrix
    """

    waifw = get_waifw(contact_matrix=contact_matrix,
                      susceptibilities=susceptibilities,
                      infectivities=infectivities)
    return get_r_nut_from_waifw(
        waifw=waifw,
        pop_sizes=pop_sizes,
        inf_dur=inf_duration)


def __get_error_r_nut(infectivity, r_0, contact_matrix, susceptibilities, pop_sizes, inf_dur):
    """ :returns: the (R0 - R0_hat)^2, where R0_hat is estimated for the provided infectivity value  """

    # estimated r0
    r_0_hat = get_r_nut_from_contact_matrix(
        contact_matrix=contact_matrix,
        susceptibilities=susceptibilities,
        infectivities=[infectivity]*len(pop_sizes),
        pop_sizes=pop_sizes,
        inf_duration=inf_dur)

    return pow(r_0 - r_0_hat, 2)


def get_infectivity_from_r_nut(r0, contact_matrix, susceptibilities, pop_sizes, inf_dur):
    """
    :param r0: (float) R0
    :param contact_matrix: (list of lists) contact rates [C_ij], where
        C_ij is the rate at which a susceptible person in group i comes into contact with an infectious
        person in group j
    :param susceptibilities: (list) of susceptibility values [sucp_i]
    :param pop_sizes: (list) size of each group
    :param inf_dur: (float) duration of infectiousness
    :return: the estimated infectivity (assumes that same infectivity for all groups)
    """
    res = minimize_scalar(fun=__get_error_r_nut,
                          args=(r0, contact_matrix, susceptibilities, pop_sizes, inf_dur),
                          bounds=(0, float('inf')))
    return res.x
