#!/usr/bin/env python
# Copyright 2017 Blue Marble Analytics LLC. All rights reserved.

import csv
import os.path
import pandas as pd
from pyomo.environ import Set, Param, Var, Constraint, Expression, \
    NonNegativeReals, value

from gridpath.auxiliary.auxiliary import make_project_time_var_df, is_number
from gridpath.auxiliary.dynamic_components import \
    capacity_type_operational_period_sets


def add_module_specific_components(m, d):
    """

    """
    m.EXISTING_LINEAR_ECON_RETRMNT_GENERATORS_OPERATIONAL_PERIODS = \
        Set(dimen=2)

    # Add to list of sets we'll join to get the final
    # PROJECT_OPERATIONAL_PERIODS set
    getattr(d, capacity_type_operational_period_sets).append(
        "EXISTING_LINEAR_ECON_RETRMNT_GENERATORS_OPERATIONAL_PERIODS",
    )

    m.existing_lin_econ_ret_capacity_mw = \
        Param(m.EXISTING_LINEAR_ECON_RETRMNT_GENERATORS_OPERATIONAL_PERIODS,
              within=NonNegativeReals)
    m.existing_lin_econ_ret_fixed_cost_per_mw_yr = \
        Param(m.EXISTING_LINEAR_ECON_RETRMNT_GENERATORS_OPERATIONAL_PERIODS,
              within=NonNegativeReals)

    def retire_capacity_bounds(mod, g, p):
        """
        Shouldn't be able to retire more than available capacity
        :param mod:
        :param g:
        :param p:
        :return:
        """
        return 0, mod.existing_lin_econ_ret_capacity_mw[g, p]

    # Retire capacity variable
    m.Retire_MW = Var(
        m.EXISTING_LINEAR_ECON_RETRMNT_GENERATORS_OPERATIONAL_PERIODS,
        bounds=retire_capacity_bounds
    )

    # Existing capacity minus retirements
    def existing_existing_econ_ret_capacity_rule(mod, g, p):
        """

        :param mod:
        :param g:
        :param p:
        :return:
        """
        return mod.existing_lin_econ_ret_capacity_mw[g, p] \
            - mod.Retire_MW[g, p]
    m.Existing_Linear_Econ_Ret_Capacity_MW = \
        Expression(
            m.EXISTING_LINEAR_ECON_RETRMNT_GENERATORS_OPERATIONAL_PERIODS,
            rule=existing_existing_econ_ret_capacity_rule
        )
                   
    def retire_forever_rule(mod, g, p):
        """
        Once retired, capacity cannot be brought back (i.e. in the current 
        period, total capacity (after retirement) must be less than or equal 
        what it was in the last period
        :param mod: 
        :param g: 
        :param p: 
        :return: 
        """
        if p == mod.first_period:
            return Constraint.Skip
        return mod.Existing_Linear_Econ_Ret_Capacity_MW[g, p] \
            <= \
            mod.Existing_Linear_Econ_Ret_Capacity_MW[g, mod.previous_period[p]]
    m.Retire_Forever_Constraint = Constraint(
        m.EXISTING_LINEAR_ECON_RETRMNT_GENERATORS_OPERATIONAL_PERIODS
    )
        

def capacity_rule(mod, g, p):
    return mod.Existing_Linear_Econ_Ret_Capacity_MW[g, p]


# TODO: give the option to add an exogenous param here instead of 0
def capacity_cost_rule(mod, g, p):
    """
    Capacity cost for existing capacity generators with no economic retirements
    is 0
    :param mod:
    :return:
    """
    return mod.Existing_Linear_Econ_Ret_Capacity_MW[g, p] \
        * mod.existing_lin_econ_ret_fixed_cost_per_mw_yr[g, p]


def load_module_specific_data(
        m, data_portal, scenario_directory, horizon, stage
):
    """

    :param m:
    :param data_portal:
    :param scenario_directory:
    :param horizon:
    :param stage:
    :return:
    """
    def determine_existing_gen_linear_econ_ret_projects():
        """
        Find the existing_gen_linear_economic_retirement capacity type projects
        :return:
        """

        ex_gen_lin_econ_ret_projects = list()

        dynamic_components = \
            pd.read_csv(
                os.path.join(scenario_directory, "inputs", "projects.tab"),
                sep="\t", usecols=["project",
                                   "capacity_type"]
                )
        for row in zip(dynamic_components["project"],
                       dynamic_components["capacity_type"]):
            if row[1] == "existing_gen_linear_economic_retirement":
                ex_gen_lin_econ_ret_projects.append(row[0])
            else:
                pass

        return ex_gen_lin_econ_ret_projects

    def determine_period_params():
        """

        :return:
        """
        generators_list = determine_existing_gen_linear_econ_ret_projects()
        generator_period_list = list()
        existing_lin_econ_ret_capacity_mw_dict = dict()
        existing_lin_econ_ret_fixed_cost_per_mw_yr_dict = dict()
        dynamic_components = \
            pd.read_csv(
                os.path.join(scenario_directory, "inputs",
                             "existing_generation_period_params.tab"),
                sep="\t"
                )

        for row in zip(dynamic_components["GENERATORS"],
                       dynamic_components["PERIODS"],
                       dynamic_components["existing_capacity_mw"],
                       dynamic_components["fixed_cost_per_mw_yr"]):
            if row[0] in generators_list:
                generator_period_list.append((row[0], row[1]))
                existing_lin_econ_ret_capacity_mw_dict[(row[0], row[1])] = \
                    float(row[2])
                existing_lin_econ_ret_fixed_cost_per_mw_yr_dict[(row[0],
                                                                 row[1])] = \
                    float(row[3])
            else:
                pass

        return generator_period_list, \
               existing_lin_econ_ret_capacity_mw_dict, existing_lin_econ_ret_fixed_cost_per_mw_yr_dict

    data_portal.data()["EXISTING_LINEAR_ECON_RETRMNT_GENERATORS_OPERATIONAL_PERIODS"] = {
        None: determine_period_params()[0]
    }

    data_portal.data()["existing_lin_econ_ret_capacity_mw"] = \
        determine_period_params()[1]

    data_portal.data()["existing_lin_econ_ret_fixed_cost_per_mw_yr"] = \
        determine_period_params()[2]


def export_module_specific_results(scenario_directory, horizon, stage, m, d):
    """
    Export existing gen linear economic retirement results.
    :param scenario_directory:
    :param horizon:
    :param stage:
    :param m:
    :param d:
    :return:
    """
    with open(os.path.join(scenario_directory, horizon, stage, "results",
                           "capacity_existing_gen_linear_economic_retirement"
                           ".csv"), "w") as f:
        writer = csv.writer(f)
        writer.writerow(["project", "period", "technology", "load_zone",
                         "retire_mw"])
        for (prj, p) in \
                m.EXISTING_LINEAR_ECON_RETRMNT_GENERATORS_OPERATIONAL_PERIODS:
            writer.writerow([
                prj,
                p,
                m.technology[prj],
                m.load_zone[prj],
                value(m.Retire_MW[prj, p])
            ])


def summarize_module_specific_results(
    problem_directory, horizon, stage, summary_results_file
):
    """
    Summarize existing gen linear economic retirement capacity results.
    :param problem_directory:
    :param horizon:
    :param stage:
    :param summary_results_file:
    :return:
    """

    # Get the results CSV as dataframe
    capacity_results_df = \
        pd.read_csv(os.path.join(problem_directory, horizon, stage, "results",
                                 "capacity_existing_gen_linear_economic_"
                                 "retirement.csv")
                    )

    capacity_results_agg_df = \
        capacity_results_df.groupby(by=["load_zone", "technology",
                                        'period'],
                                    as_index=True
                                    ).sum()

    # Set the formatting of float to be readable
    pd.options.display.float_format = "{:,.0f}".format

    # Get all technologies with the new build capacity
    lin_retirement_df = pd.DataFrame(
        capacity_results_agg_df[
            capacity_results_agg_df["retire_mw"] > 0
        ]["retire_mw"]
    )

    lin_retirement_df.columns = ["Retired Capacity (MW)"]

    with open(summary_results_file, "a") as outfile:
        outfile.write("\n--> Retired Capacity <--\n")
        if lin_retirement_df.empty:
            outfile.write("No retirements.\n")
        else:
            lin_retirement_df.to_string(outfile)
            outfile.write("\n")
