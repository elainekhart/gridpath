#!/usr/bin/env python

from pyomo.environ import Expression, Objective, minimize


def add_model_components(m, d, scenario_directory, horizon, stage):
    """
    Aggregate costs and components to objective function.
    :param m:
    :param d:
    :param scenario_directory:
    :param horizon:
    :param stage:
    :return:
    """

    # Define objective function
    def total_cost_rule(mod):

        return sum(getattr(mod, c)
                   for c in d.total_cost_components)

    m.Total_Cost = Objective(rule=total_cost_rule, sense=minimize)