# Copyright 2021 (c) Crown Copyright, GC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Zones where carbon tax enforced; these can be different from the load
zones and other balancing areas.
"""

import csv
import os.path
from pyomo.environ import Set


def add_model_components(m, d, scenario_directory, subproblem, stage):
    """

    :param m:
    :param d:
    :param scenario_directory:
    :param subproblem:
    :param stage:
    :return:
    """

    m.CARBON_TAX_ZONES = Set()


def load_model_data(m, d, data_portal, scenario_directory, subproblem, stage):
    """

    :param m:
    :param d:
    :param data_portal:
    :param scenario_directory:
    :param subproblem:
    :param stage:
    :return:
    """
    data_portal.load(
        filename=os.path.join(
            scenario_directory,
            str(subproblem),
            str(stage),
            "inputs",
            "carbon_tax_zones.tab",
        ),
        set=m.CARBON_TAX_ZONES,
    )


def get_inputs_from_database(scenario_id, subscenarios, subproblem, stage, conn):
    """
    :param subscenarios: SubScenarios object with all subscenario info
    :param subproblem:
    :param stage:
    :param conn: database connection
    :return:
    """
    subproblem = 1 if subproblem == "" else subproblem
    stage = 1 if stage == "" else stage
    c = conn.cursor()
    carbon_tax_zone = c.execute(
        """SELECT carbon_tax_zone
        FROM inputs_geography_carbon_tax_zones
        WHERE carbon_tax_zone_scenario_id = {};
        """.format(
            subscenarios.CARBON_TAX_ZONE_SCENARIO_ID
        )
    )

    return carbon_tax_zone


def validate_inputs(scenario_id, subscenarios, subproblem, stage, conn):
    """
    Get inputs from database and validate the inputs
    :param subscenarios: SubScenarios object with all subscenario info
    :param subproblem:
    :param stage:
    :param conn: database connection
    :return:
    """
    pass
    # Validation to be added
    # carbon_tax_zone = get_inputs_from_database(
    #     scenario_id, subscenarios, subproblem, stage, conn)


def write_model_inputs(
    scenario_directory, scenario_id, subscenarios, subproblem, stage, conn
):
    """
    Get inputs from database and write out the model input
    carbon_tax_zones.tab file.
    :param scenario_directory: string, the scenario directory
    :param subscenarios: SubScenarios object with all subscenario info
    :param subproblem:
    :param stage:
    :param conn: database connection
    :return:
    """

    carbon_tax_zone = get_inputs_from_database(
        scenario_id, subscenarios, subproblem, stage, conn
    )

    with open(
        os.path.join(
            scenario_directory,
            str(subproblem),
            str(stage),
            "inputs",
            "carbon_tax_zones.tab",
        ),
        "w",
        newline="",
    ) as carbon_tax_zones_file:
        writer = csv.writer(carbon_tax_zones_file, delimiter="\t", lineterminator="\n")

        # Write header
        writer.writerow(["carbon_tax_zone"])

        for row in carbon_tax_zone:
            writer.writerow(row)
