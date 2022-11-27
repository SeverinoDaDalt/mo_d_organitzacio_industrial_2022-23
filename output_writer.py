def write_update(total_cost, total_time, out, n_improvement, debug=False, overwrite=False):
    """
    Updates output file with the new best result.
    INPUT:
    - total_cost: new best cost result
    - total_time: time spent finding this solution
    - out: path to the output file
    - n_improvement: the number of improvements currently achieved
    - debug: (default False) for debugging. If this is set to True, the output will be easier to read but not the
      required format for evaluation.
    OUTPUT: None
    """
    with open(out, "w" if overwrite else "a") as o_file:
        if debug:
            o_file.write(f"*** f_{n_improvement} & t_{n_improvement} ***\n")
        o_file.write(f"{total_cost}*{total_time}\n")


def write_best_result(total_cost, total_time, out, n_improvement, pf, nuf, nue, nr, debug=False):
    """
    Updates output file with the best result and its process.
    INPUT:
    - total_cost: the best cost result found
    - total_time: time spent finding this solution
    - out: path to the output file
    - n_improvement: the number of improvements achieved
    - pf[i][t]: tipo de producto a fabricar en la línea '𝑖' en el periodo '𝑡'. Si no se produce, pf[i][t] = 0
    - nuf[i][t]: número de unidades a fabricar en la línea '𝑖' en el periodo '𝑡'. Si no se produce, nuf[i][t] = 0
    - nue[j][p][t]: número de unidades a enviar a la obra '𝑗' del producto '𝑝' que salen de fábrica al final del
      periodo '𝑡'
    - nr[j][p]: número de unidades compradas para la obra 'j' de producto 'p'
    - debug: (default False) for debugging. If this is set to True, the output will be easier to read but not the
      required format for evaluation.
    OUTPUT: None
    """
    with open(out, "a") as o_file:
        # n_improvement
        if debug:
            o_file.write(f"*** n "
                         f"improvements ***\n")
        o_file.write(f"{n_improvement}\n")

        # f_T & t_T
        if debug:
            o_file.write(f"*** f_{n_improvement} & t_{n_improvement} ***\n")
        o_file.write(f"{total_cost}*{total_time}\n")

        # pf
        if debug:
            o_file.write(f"*** pf ***\n")
        for line in pf:
            to_print = ""
            for p_in_instant in line:
                to_print += f"{p_in_instant + 1}*"
            to_print = to_print[:-1] + "\n"
            o_file.write(to_print)

        # nuf
        if debug:
            o_file.write(f"*** nuf ***\n")
        for line in nuf:
            to_print = ""
            for nu_in_instant in line:
                to_print += f"{nu_in_instant}*"
            to_print = to_print[:-1] + "\n"
            o_file.write(to_print)

        # nue
        if debug:
            o_file.write(f"*** nue ***\n")
        for site in nue:
            for product_type in site:
                to_print = ""
                for nu_in_instant in product_type:
                    to_print += f"{nu_in_instant}*"
                to_print = to_print[:-1] + "\n"
                o_file.write(to_print)

        # nr
        if debug:
            o_file.write(f"*** nr ***\n")
        for n_site in nr:
            to_print = ""
            for nu_in_product_type in n_site:
                to_print += f"{nu_in_product_type}*"
            to_print = to_print[:-1] + "\n"
            o_file.write(to_print)
