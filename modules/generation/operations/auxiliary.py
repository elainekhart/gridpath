#!/usr/bin/env python

"""
Various auxiliary functions used in operations module
"""


import pandas


def check_list_has_single_item(l, error_msg):
    if len(l) > 1:
        raise ValueError(error_msg)
    else:
        pass


def find_list_item_position(l, item):
    """

    :param l:
    :param item:
    :return:
    """
    return [i for i, element in enumerate(l) if element == item]


def check_list_items_are_unique(l):
    """

    :param l:
    :return:
    """
    for item in l:
        positions = find_list_item_position(l, item)
        check_list_has_single_item(
            l=positions,
            error_msg="Service " + str(item) + " is specified more than once" +
            " in generators.tab.")


def get_final_expression(x):
    """
    Check recursively if x has an "expr" attribute until it does not
    :param m:
    :param x:
    :return:
    """
    while hasattr(x, "expr"):
        x = getattr(x, "expr")

    return x


def get_value_of_var_or_expr(x):
    """
    If x has an "expr" attribute, check recursively if its expr attribute has
    an expr attribute until it does not, then return its "value" attribute
    :param x:
    :return:
    """
    if hasattr(x, "expr"):
        x = get_final_expression(x)
    else:
        pass

    try:
        return getattr(x, "value")
    except AttributeError:
        print(x + " does not have a 'value' attribute.")


def make_gen_tmp_var_df(m, gen_set, tmp_set, x, header):
    """

    :param m:
    :param gen_set:
    :param tmp_set:
    :param x:
    :param header:
    :return:
    """
    # Power

    dict_for_gen_df = {}
    generators = []
    timepoints = []
    gen_tmp = []
    for g in getattr(m, gen_set):
        dict_for_gen_df[g] = {}
        generators.append(g)
        for tmp in getattr(m, tmp_set):
            dict_for_gen_df[g][tmp] = \
                get_value_of_var_or_expr(getattr(m, x)[g, tmp])
            gen_tmp.append((g, tmp))

    # For each generator, create a dataframe with its x values
    for g, tmp in dict_for_gen_df.iteritems():
        timepoints.append(pandas.DataFrame.from_dict(tmp, orient='index'))

    # Concatenate all the individual generator dataframes into a final one
    final_df = pandas.DataFrame(pandas.concat(timepoints, keys=generators))
    final_df.index.names = ["generator", "timepoint"]
    final_df.columns = [header]

    return final_df