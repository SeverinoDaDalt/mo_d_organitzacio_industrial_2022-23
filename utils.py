def quicksort(list_, comparator=(lambda x, y: x < y), reverse=False):
    """
    Uses quick sort algorithm to sort a list.
    :param comparator: function to compare the elements of the list. Default is <.
    :param list_: list -> the list to sort.
    :param reverse: bool -> whether to return the resulting list in reverse other. Default is False.
    :return: list
    """
    pivot = list_[-1]
    smaller = []
    bigger_or_equal = []
    for to_compare in list_[:-1]:
        if comparator(to_compare, pivot) ^ reverse:  # ^ is xor in python
            smaller.append(to_compare)
        else:
            bigger_or_equal.append(to_compare)
    if len(smaller) > 1:
        smaller = quicksort(smaller, comparator=comparator, reverse=reverse)
    if len(bigger_or_equal) > 1:
        bigger_or_equal = quicksort(bigger_or_equal, comparator=comparator, reverse=reverse)
    return smaller + [pivot] + bigger_or_equal


def get_input_production_line(N, TP, PL):
    input_production_line = []
    for n_site in range(N):
        for n_product_type in range(TP):
            # we check that this product for this site needs to be produced
            if not PL[n_site][n_product_type]:
                continue
            input_production_line.append((n_site, n_product_type))

    def sort_orders(order1, order2):
        return PL[order1[0]][order1[1]] < PL[order2[0]][order2[1]]

    return quicksort(input_production_line, comparator=sort_orders)


def assigner(input_production_line, F, D, PL, Cap, CostF, alpha, CR, beta_t, beta_c, beta_b):
    lines_unavailability = [0] * F  # preparing production lines
    to_buy = []  # store buy decisions
    to_produce = [[] for _ in range(F)]  # store line assignments
    for n_site, n_product_type in input_production_line:
        available_lines = [n_line for n_line in range(F)]
        # filter lines that cannot produce this item
        available_lines = [n_line for n_line in available_lines if Cap[n_line][n_product_type]]
        # lines speed
        lines_time = {}
        for n_line in available_lines:
            remaining_available_time = PL[n_site][n_product_type] - lines_unavailability[n_line]  # time available in this line
            # how long would the production take on this line
            full_time = D[n_site][n_product_type] // Cap[n_line][n_product_type]  # full production time
            extra_quantity = D[n_site][n_product_type] % Cap[n_line][n_product_type]  # units produces using a partial amount of time
            production_time = full_time + (extra_quantity > 0)  # total time spent
            # filter lines that cannot produce this item in time
            if remaining_available_time < production_time:
                continue
            lines_time[n_line] = production_time
        lines_cost = {}
        for n_line in lines_time:
            lines_cost[n_line] = CostF[n_line][n_product_type]
        # TODO: check if another transport can be used (now or in the future)
        # TODO: filter out those lines for which the production + transport (if any) cost is higher than buying it
        # priority
        lines_priority = {}  # TODO: remove, currently it has no use
        maximum_priority = float('-inf')
        maximum_priority_line = None
        for n_line in lines_time:
            line_priority = - beta_t * lines_time[n_line] - beta_c * lines_cost[n_line]
            lines_priority[n_line] = line_priority
            if line_priority > maximum_priority:
                maximum_priority_line = n_line
                maximum_priority = line_priority
        # if no line is available for this product, or buying it is cheaper (or worth it in any sense), buy it
        buying_cost = CR[n_site][n_product_type] * (D[n_site][n_product_type] ** alpha)
        if maximum_priority_line is None or lines_cost[maximum_priority_line] >= buying_cost - beta_b:
            to_buy.append((n_site, n_product_type))
            continue
        to_produce[maximum_priority_line].append((n_site, n_product_type, lines_unavailability[maximum_priority_line]))
        lines_unavailability[maximum_priority_line] += lines_time[maximum_priority_line]
    return to_buy, to_produce


def overlap(interval1, interval2):
    # check if overlap
    max_of_min = max(interval1[0], interval2[0])
    min_of_max = min(interval1[1], interval2[1])
    if max_of_min > min_of_max:
        return False
    return (max_of_min, min_of_max)


def delivery_optimizer(delivery_aux, TP, N, H, D, CostT):
    transport_cost = 0
    nue = [[[0] * H for _ in range(TP)] for _ in range(N)]
    for n_site in range(len(delivery_aux)):
        to_check = [i for i in range(len(delivery_aux[n_site])) if delivery_aux[n_site][i] is not None]
        current_n_products = []
        current_interval = None
        while to_check or current_interval or current_n_products:
            if current_interval is None:
                current_n_products.append(to_check[-1])
                current_interval = delivery_aux[n_site][to_check.pop()]
            no_overlap = True
            for n_product_type in to_check:
                overlap_ = overlap(current_interval, delivery_aux[n_site][n_product_type])
                if not overlap_:
                    continue
                current_interval = overlap_
                current_n_products.append(n_product_type)
                to_check.remove(n_product_type)
                no_overlap = False
                break
            if no_overlap:
                for n_product_type in current_n_products:
                    nue[n_site][n_product_type][current_interval[0]] = D[n_site][n_product_type]
                transport_cost += CostT[n_site]
                current_interval = None
                current_n_products = []
    return nue, transport_cost


def output_generator(to_produce, to_buy, F, TP, N, H, D, PL, Cap, CostF, CostT, alpha, CR):
    buy_cost = 0
    production_cost = 0
    pf = [[-1] * H for _ in range(F)]
    nuf = [[0] * H for _ in range(F)]
    delivery_aux = [[None for _ in range(TP)] for _ in range(N)]
    for n_line in range(len(to_produce)):
        for n_site, n_product_type, time_ in to_produce[n_line]:
            production_cost += CostF[n_line][n_product_type] * D[n_site][n_product_type]  # update production cost
            full_time = D[n_site][n_product_type] // Cap[n_line][n_product_type]  # full production time
            extra_quantity = D[n_site][n_product_type] % Cap[n_line][n_product_type]  # units produced using a partial amount of time
            production_time = full_time + (extra_quantity > 0)  # total time spent
            # pf
            for instant in range(time_, time_ + production_time):
                if pf[n_line][instant] != -1:
                    raise ValueError
                pf[n_line][instant] = n_product_type
            # nuf
            for instant in range(time_, time_ + full_time):
                nuf[n_line][instant] = Cap[n_line][n_product_type]
            if extra_quantity:
                nuf[n_line][time_ + full_time] = extra_quantity
            # delivery auxiliary
            delivery_aux[n_site][n_product_type] = (time_ + production_time - 1, PL[n_site][n_product_type])  # TODO: Possible error. This is just a friendly reminder to check here if tester does not like the solution.
    # nue
    nue, transport_cost = delivery_optimizer(delivery_aux, TP, N, H, D, CostT)
    # nr
    nr = [[0] * TP for _ in range(N)]
    for n_site, n_product_type in to_buy:
        nr[n_site][n_product_type] = D[n_site][n_product_type]
        buy_cost += CR[n_site][n_product_type] * (D[n_site][n_product_type] ** alpha)
    return pf, nuf, nue, nr, buy_cost, production_cost, transport_cost
