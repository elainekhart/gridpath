#!/usr/bin/env python

import os

from reserve_requirements import add_generic_reserve_components


def add_model_components(m):
    add_generic_reserve_components(
        m,
        reserve_violation_variable="Regulation_Down_Violation",
        reserve_violation_penalty_param="regulation_down_violation_penalty",
        reserve_requirement_param="regulation_down_requirement",
        reserve_generator_set="REGULATION_DOWN_GENERATORS",
        generator_reserve_provision_variable="Provide_Regulation_Down",
        total_reserve_provision_variable="Regulation_Down_Provision",
        meet_reserve_constraint="Meet_Regulation_Down_Constraint",
        objective_function_reserve_penalty_cost_component=
        "Regulation_Down_Penalty_Cost"
        )


def load_model_data(m, data_portal, inputs_directory):
    data_portal.load(filename=os.path.join(inputs_directory,
                                           "regulation_down_requirement.tab"),
                     param=m.regulation_down_requirement

                     )


def export_results(scenario, m):
    for z in getattr(m, "LOAD_ZONES"):
        for tmp in getattr(m, "TIMEPOINTS"):
            print("Regulation_Down_Violation[" + str(z) + ", "
                  + str(tmp) + "]: "
                  + str(m.Regulation_Down_Violation[z, tmp].value)
                  )