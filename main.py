from data_reader import read
from output_writer import write_update, write_best_result
from time import time
import argparse
import os


# folders
INPUT_FOLDER = "my_inputs"
OUTPUT_FOLDER = "my_outputs"
DEBUG_FOLDER = "debug_outputs"


def main(inp, out, debug=False, force=False):
    # prepare files
    inp = os.path.join(INPUT_FOLDER, inp)
    if debug:
        print("DEBUG MODE - results may not be accurate...")
        out = os.path.join(DEBUG_FOLDER, out)
    else:
        out = os.path.join(OUTPUT_FOLDER, out)

    start = time()  # start timer
    F, TP, N, H, D, PL, Cap, CostF, CostT, alpha, CR = read(inp)  # reading input
    lines_unavailability = [0] * F  # preparing production line

    # preparing output
    pf = [[] for i in range(F)]
    nuf = [[] for i in range(F)]
    nue = [[[0] * H for j in range(TP)] for i in range(N)]
    nr = [[0] * TP for i in range(N)]

    # where costs will cumulatively be stored
    total_cost = 0
    production_cost = 0
    transport_cost = 0
    other_cost = 0

    # production management
    for n_site in range(N):
        for n_product_type in range(TP):
            # we check that this product for this site needs to be produced
            if not PL[n_site][n_product_type]:
                continue
            free_line_found = False
            for n_line in range(F):
                # check if this product can be produced in this line
                if not Cap[n_line][n_product_type]:
                    continue
                # how long would the production take on this line
                full_time = D[n_site][n_product_type] // Cap[n_line][n_product_type]  # full production time
                extra_quantity = D[n_site][n_product_type] % Cap[n_line][n_product_type]
                production_time = full_time + (extra_quantity > 0)
                # we check if this line can produce the product on time
                if lines_unavailability[n_line] + production_time > PL[n_site][n_product_type]:
                    continue
                # update total cost
                # production
                total_cost += CostF[n_line][n_product_type] * D[n_site][n_product_type]
                production_cost += CostF[n_line][n_product_type] * D[n_site][n_product_type]  # for debugging
                # transport: only if there is no other product (from another line) that is already being transported
                # to the same site, in this same instant
                reuse_transport = False
                for rt_n_product_type in range(N):
                    if nue[n_site][rt_n_product_type][lines_unavailability[n_line] + production_time - 1] != 0:
                        reuse_transport = True
                if not reuse_transport:
                    total_cost += CostT[n_site]
                    transport_cost += CostT[n_site]  # for debugging
                # update output
                pf[n_line] += [n_product_type] * production_time
                nuf[n_line] += [Cap[n_line][n_product_type]] * full_time
                nuf[n_line] += [extra_quantity] * (extra_quantity > 0)
                nue[n_site][n_product_type][lines_unavailability[n_line] + production_time - 1] = \
                    D[n_site][n_product_type]
                # update availability
                lines_unavailability[n_line] += production_time
                free_line_found = True
                break
            # check if a production line was already found
            if free_line_found:
                continue
            # update total cost
            total_cost += CR[n_site][n_product_type] * (D[n_site][n_product_type] ** alpha)
            other_cost += CR[n_site][n_product_type] * (D[n_site][n_product_type] ** alpha)  # for debugging
            # update output
            nr[n_site][n_product_type] = D[n_site][n_product_type]
    if debug:
        print(f"production:\t{production_cost}")
        print(f"transport:\t{transport_cost}")
        print(f"other:  \t{other_cost}")
        print(f"TOTAL:  \t{total_cost}")
    # complete pf and nuf output with unused instants
    for line in pf:
        line += [-1] * (H - len(line))
    for line in nuf:
        line += [0] * (H - len(line))
    total_time = time() - start

    # write output
    n_improvement = 0
    if os.path.isfile(out) and not force:
        print(f"The output file {out} already exists, no changes will be saved. If you want to overwrite old results "
              f"with the new ones, use the 'force' parameter ('-f' or '--force').")
    else:
        write_update(total_cost, total_time, out, n_improvement, debug=debug, overwrite=True)
        write_best_result(total_cost, total_time, out, n_improvement, pf, nuf, nue, nr, debug=debug)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file", help="path to the input file")
    parser.add_argument("-o", "--output_file", help="path to the output file")
    parser.add_argument("-f", "--force", default=False, action='store_true',
                        help="if set to True and output file already exists, it overwrites with new results")
    parser.add_argument("-d", "--debug", default=False, action='store_true',
                        help="useful insights on what the program is doing, and an output that is easier to read. "
                             "CAREFUL: the output will no longer be valid if this parameter is used.")
    args = parser.parse_args()
    all_requirements = True
    if not args.input_file:
        print("ERROR: input_file is required as argument.")
        all_requirements = False
    if not args.output_file:
        print("ERROR: output_file is required as argument.")
        all_requirements = False
    if all_requirements:
        main(args.input_file, args.output_file, debug=args.debug, force=args.force)
    else:
        print("\nNot all requirements were met. Closing...")
