from data_reader import read
from output_writer import write_update, write_best_result
from utils import get_input_production_line, assigner, output_generator
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

    betas_t = [0, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500]
    betas_c = [0, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500]
    betas_b = [0, 10, 100, 1000, 10000, 100000]

    all_combinations = []
    for beta_t in betas_t:
        for beta_c in betas_c:
            for beta_b in betas_b:
                all_combinations.append((beta_t, beta_c, beta_b))

    temporary_results = {}
    minimum_total_cost = float("inf")
    pf_of_best = [[]]
    nuf_of_best = [[]]
    nue_of_best = [[[]]]
    nr_of_best = [[]]
    buy_cost_of_best = 0
    production_cost_of_best = 0
    transport_cost_of_best = 0
    time_of_best = 0
    n_improvement = 0

    # input production line
    # TODO: (possible improvement) adapt input production line with corrector
    input_production_line = get_input_production_line(N, TP, PL)
    if debug:
        print("Production_line:")
        for n_site, n_product_type in input_production_line:
            print(f"Site:{n_site}\tProduct: {n_product_type}\t(Limit: {PL[n_site][n_product_type]})")

    for betas in all_combinations:
        beta_t = betas[0]
        beta_c = betas[1]
        beta_b = betas[2]

        # assigner
        to_buy, to_produce = assigner(input_production_line, F, D, PL, Cap, CostF, alpha, CR, beta_t, beta_c, beta_b)

        # output generator
        pf, nuf, nue, nr, buy_cost, production_cost, transport_cost = \
            output_generator(to_produce, to_buy, F, TP, N, H, D, PL, Cap, CostF, CostT, alpha, CR)
        total_cost = production_cost + transport_cost + buy_cost  # total cost

        temporary_results[betas] = total_cost

        if total_cost < minimum_total_cost:
            minimum_total_cost = total_cost
            pf_of_best = pf
            nuf_of_best = nuf
            nue_of_best = nue
            nr_of_best = nr
            buy_cost_of_best = buy_cost
            production_cost_of_best = production_cost
            transport_cost_of_best = transport_cost
            time_of_best = time() - start
            write_update(minimum_total_cost, time_of_best, out, n_improvement, debug=debug, overwrite=True)
            n_improvement += 1

    if debug:
        print(f"Production cost:\t{production_cost_of_best}")
        print(f"Transport cost: \t{transport_cost_of_best}")
        print(f"Buy cost:       \t{buy_cost_of_best}")
        print("-----------------------------------------")
        print(f"Total cost:     \t{minimum_total_cost}")

    # write output
    if os.path.isfile(out) and not force:
        print(f"The output file {out} already exists, no changes will be saved. If you want to overwrite old results "
              f"with the new ones, use the 'force' parameter ('-f' or '--force').")
    else:
        write_best_result(minimum_total_cost, time_of_best, out, n_improvement,
                          pf_of_best, nuf_of_best, nue_of_best, nr_of_best, debug=debug)
    return minimum_total_cost


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
