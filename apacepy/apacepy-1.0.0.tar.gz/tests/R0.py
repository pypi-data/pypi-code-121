from apacepy.Transmission import *


if __name__ == '__main__':

    # calculating R0 using a next generation matrix
    ngm = [[2.18, 0.61],
           [2.43, 2.43]]
    r0 = get_r_nut_from_ngm(next_gen_matrix=ngm)
    print('R0 using next generation matrix:', r0)

    # # calculating R0 using the matrix of who acquired infection from whom
    # waifw = [[1.8e-8, 5.02e-9], [5.02e-9, 5.02e-9]]
    # pop_size = [11e6, 44e6]
    # dur_inf = 11
    # r0 = get_r_nut_from_waifw(waifw=waifw, pop_sizes=pop_size, inf_dur=dur_inf)
    # print('R0 using next generation matrix:', r0)

    # calculating R0 using contact matrix
    contact_matrix = [
        [40, 9],  # between children and [children, adults]
        [9, 15]]  # between adults and [children, adults]
    susceptibilities = [1, 1.5]     # assuming adults are more susceptible
    infectivities = [3, 3]          # assuming children and adults are equally susceptible
    pop_size = [1000, 2000]
    inf_dur = 5 / 364
    r0 = get_r_nut_from_contact_matrix(contact_matrix=contact_matrix,
                                       susceptibilities=susceptibilities,
                                       infectivities=infectivities,
                                       pop_sizes=pop_size, inf_duration=inf_dur)
    print('R0 using contact matrix:', r0)

    estimated_inf = get_infectivity_from_r_nut(r0=r0,
                                               contact_matrix=contact_matrix,
                                               susceptibilities=susceptibilities,
                                               pop_sizes=pop_size, inf_dur=inf_dur)

    print('Estimated infectivity: ', estimated_inf)


    # debugging COVID
    contact_matrix = [[1]*6]*6
    susceptibilities = [1, 1, 1, 1, 1, 1]
    pop_size = [100]*6
    inf_dur = 0.024186191222571034
    R0 = 1.8
    infectivity = R0 / inf_dur

    infectivities = [infectivity]*len(pop_size)
    est_r0 = get_r_nut_from_contact_matrix(contact_matrix=contact_matrix, susceptibilities=susceptibilities,
                                           infectivities=infectivities, pop_sizes=pop_size,
                                           inf_duration=inf_dur)

    inf1 = R0 / inf_dur
    inf2 = get_infectivity_from_r_nut(r0=r0,
                                      contact_matrix=contact_matrix,
                                      susceptibilities=susceptibilities,
                                      pop_sizes=pop_size, inf_dur=inf_dur)

    print(inf1)
    print(inf2)