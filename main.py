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

    beta_t = 0
    beta_c = 1
    beta_b = 0

    # input production line
    # TODO: (possible improvement) adapt input production line with corrector
    input_production_line = get_input_production_line(N, TP, PL)
    if debug:
        print("Production_line:")
        for n_site, n_product_type in input_production_line:
            print(f"Site:{n_site}\tProduct: {n_product_type}\t(Limit: {PL[n_site][n_product_type]})")

    # assigner
    to_buy, to_produce = assigner(input_production_line, F, D, PL, Cap, CostF, alpha, CR, beta_t, beta_c, beta_b)
    if debug and to_buy:
        print("To buy:")
        for n_site, n_product_type in to_buy:
            print(f"Site:{n_site}\tProduct: {n_product_type}")
    if debug and to_produce:
        print("To produce:")
        for n_line in range(len(to_produce)):
            print(f"Line: {n_line}")
            for n_site, n_product_type, time_ in to_produce[n_line]:
                print(f"\tSite:{n_site}\tProduct: {n_product_type}\tTime: {time_}")

    # output generator
    pf, nuf, nue, nr, buy_cost, production_cost, transport_cost = \
        output_generator(to_produce, to_buy, F, TP, N, H, D, PL, Cap, CostF, CostT, alpha, CR)
    total_cost = production_cost + transport_cost + buy_cost  # total cost
    if debug:
        print("*** pf ***")
        for line in pf:
            print(f"\t{[n_product_type + 1 for n_product_type in line]}")
        print("*** nuf ***")
        for line in nuf:
            print(f"\t{line}")
        print("*** nue ***")
        for n_site in range(len(nue)):
            print(f"\tSite {n_site}")
            for n_product_type in range(len(nue[n_site])):
                print(f"\t\t{nue[n_site][n_product_type]}")
        print("*** nr ***")
        for site in nr:
            print(f"\t{site}")
        print(f"Production cost:\t{production_cost}")
        print(f"Transport cost: \t{transport_cost}")
        print(f"Buy cost:       \t{buy_cost}")
        print("-----------------------------------------")
        print(f"Total cost:     \t{total_cost}")
    total_time = time() - start

    # write output
    n_improvement = 0
    if os.path.isfile(out) and not force:
        print(f"The output file {out} already exists, no changes will be saved. If you want to overwrite old results "
              f"with the new ones, use the 'force' parameter ('-f' or '--force').")
    else:
        write_update(total_cost, total_time, out, n_improvement, debug=debug, overwrite=True)
        write_best_result(total_cost, total_time, out, n_improvement, pf, nuf, nue, nr, debug=debug)
    return total_cost


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
