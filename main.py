from data_reader import read
from output_writer import write_update, write_best_result, clear_file
from utils import get_input_production_line, assigner, output_generator
from time import time
import argparse
import os
import random
import math


# folders
INPUT_FOLDER = "my_inputs"
OUTPUT_FOLDER = "my_outputs"
DEBUG_FOLDER = "debug_outputs"

TOTAL_TIME = 300
MAXIMUM_PRODUCTION_LINE_SWAPS = 0.5  # in (0, 1)
MAXIMUM_NEXT_BEST_PROBABILITY = 0.8  # in (0, 1)


def main(inp, out, debug=False, force=False):
    # prepare files
    inp = os.path.join(INPUT_FOLDER, inp)
    if debug:
        print("DEBUG MODE - results may not be accurate...")
        out = os.path.join(DEBUG_FOLDER, out)
    else:
        out = os.path.join(OUTPUT_FOLDER, out)

    # write output
    if os.path.isfile(out):
        if force:
            clear_file(out)
        else:
            print(f"The output file {out} already exists, no changes will be saved. If you want to overwrite old "
                  f"results with the new ones, use the 'force' parameter ('-f' or '--force').")
            return

    start = time()  # start timer

    F, TP, N, H, D, PL, Cap, CostF, CostT, alpha, CR = read(inp)  # reading input

    # initialize betas
    betas_constants = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    betas_orders = [0.001, 0.01, 0.1, 1, 10, 100]
    betas = [0]
    for order in betas_orders:
        betas += list(map((lambda x: x*order), betas_constants))

    # initialize deltas
    deltas_constants = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    deltas_orders = [1000, 10000, 100000]
    deltas = [0]
    for order in deltas_orders:
        deltas += list(map((lambda x: x*order), deltas_constants))

    # initialize info for best run
    best_betas = []
    best_deltas = []
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

    # STEP 1: find most suitable betas and deltas
    if debug: print(f"STEP 1")

    # input production line
    input_production_line = get_input_production_line(N, TP, PL)

    for beta in betas:
        for delta in deltas:
            # assigner
            to_buy, to_produce = assigner(input_production_line, F, D, PL, Cap, CostF, alpha, CR, beta, delta)

            # output generator
            pf, nuf, nue, nr, buy_cost, production_cost, transport_cost = \
                output_generator(to_produce, to_buy, F, TP, N, H, D, PL, Cap, CostF, CostT, alpha, CR)
            total_cost = production_cost + transport_cost + buy_cost  # total cost
            if abs(total_cost - minimum_total_cost) < 1.e-8:
                best_betas.append(beta)
                best_deltas.append(delta)
            elif total_cost < minimum_total_cost:
                best_betas = [beta]
                best_deltas = [delta]
                minimum_total_cost = total_cost
                pf_of_best = pf
                nuf_of_best = nuf
                nue_of_best = nue
                nr_of_best = nr
                buy_cost_of_best = buy_cost
                production_cost_of_best = production_cost
                transport_cost_of_best = transport_cost
                time_of_best = time() - start
                write_update(minimum_total_cost, time_of_best, out, n_improvement, debug=debug, overwrite=False)
                n_improvement += 1
                if debug:
                    print(f"Beta: {'%.1f'%beta}\tDelta: {'%.1f'%delta}\tScore: {'%.1f'%minimum_total_cost}"
                          f"\t(in {time_of_best} s)")
                else:
                    print(f"{minimum_total_cost}\t{time_of_best}")

    # STEP 2: randomize
    if debug: print(f"STEP 2")
    beta_range = (min(best_betas) * 0.1, max(best_betas) * 1.9)
    delta_range = (min(best_deltas) * 0.1, max(best_deltas) * 1.9)
    while time() - start < TOTAL_TIME:
        beta = random.uniform(beta_range[0], beta_range[1])
        delta = random.uniform(delta_range[0], delta_range[1])
        production_line_swaps = random.randint(0, int(math.floor(MAXIMUM_PRODUCTION_LINE_SWAPS *
                                                                 len(input_production_line))))
        next_best_probability = random.uniform(0, MAXIMUM_NEXT_BEST_PROBABILITY)

        # input production line
        input_production_line = get_input_production_line(N, TP, PL, swaps=production_line_swaps)

        # assigner
        to_buy, to_produce = assigner(input_production_line, F, D, PL, Cap, CostF, alpha, CR, beta, delta,
                                      jump_p=next_best_probability)

        # output generator
        pf, nuf, nue, nr, buy_cost, production_cost, transport_cost = \
            output_generator(to_produce, to_buy, F, TP, N, H, D, PL, Cap, CostF, CostT, alpha, CR)
        total_cost = production_cost + transport_cost + buy_cost  # total cost

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
            write_update(minimum_total_cost, time_of_best, out, n_improvement, debug=debug, overwrite=False)
            n_improvement += 1
            if debug:
                print(f"Beta: {'%.1f'%beta}\tDelta: {'%.1f'%delta}\tScore: {'%.1f'%minimum_total_cost}"
                      f"\t(in {time_of_best} s)")
            else:
                print(f"{minimum_total_cost}\t{time_of_best}")

    # finished
    if debug:
        print(f"Production cost:\t{production_cost_of_best}")
        print(f"Transport cost: \t{transport_cost_of_best}")
        print(f"Buy cost:       \t{buy_cost_of_best}")
        print("-----------------------------------------")
        print(f"Total cost:     \t{minimum_total_cost}")
    else:
        print(n_improvement)
        print(f"{minimum_total_cost}\t{time_of_best}")

    # write output
    write_best_result(minimum_total_cost, time_of_best, out, n_improvement, pf_of_best, nuf_of_best, nue_of_best,
                      nr_of_best, debug=debug)
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
