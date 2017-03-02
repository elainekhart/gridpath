#!/usr/bin/env python
# Copyright 2017 Blue Marble Analytics LLC. All rights reserved.

"""
Describes the relationships among timepoints in the optimization
"""

import os.path

from pyomo.environ import Set, Param, NonNegativeIntegers, NonNegativeReals


def add_model_components(m, d):
    """

    :param m:
    :param d:
    :return:
    """
    m.HORIZONS = Set(within=NonNegativeIntegers, ordered=True)
    m.boundary = Param(m.HORIZONS)
    m.horizon_weight = Param(m.HORIZONS, within=NonNegativeReals)

    m.horizon = Param(m.TIMEPOINTS, within=m.HORIZONS)

    m.TIMEPOINTS_ON_HORIZON = \
        Set(m.HORIZONS, ordered=True,
            initialize=lambda mod, h:
            set(tmp for tmp in mod.TIMEPOINTS if mod.horizon[tmp] == h))

    # TODO: is there are a better way to do this than relying on min and max?
    m.first_horizon_timepoint = \
        Param(m.HORIZONS,
              initialize=
              lambda mod, h: min(tmp for tmp in mod.TIMEPOINTS_ON_HORIZON[h]))

    m.last_horizon_timepoint = \
        Param(m.HORIZONS,
              initialize=
              lambda mod, h: max(tmp for tmp in mod.TIMEPOINTS_ON_HORIZON[h]))

    def previous_timepoint_init(mod, tmp):
        prev_tmp_dict = {}
        for tmp in mod.TIMEPOINTS:
            if tmp == mod.first_horizon_timepoint[mod.horizon[tmp]]:
                if mod.boundary[mod.horizon[tmp]] == "circular":
                    prev_tmp_dict[tmp] = \
                        mod.last_horizon_timepoint[mod.horizon[tmp]]
                elif mod.boundary[mod.horizon[tmp]] == "linear":
                    prev_tmp_dict[tmp] = None
                else:
                    raise ValueError(
                        "Invalid boundary value '{}' for horizon '{}'".
                        format(
                            mod.boundary[mod.horizon[tmp]], mod.horizon[tmp])
                        + "\n" +
                        "Horizon boundary must be either 'circular' or 'linear'"
                    )
            else:
                prev_tmp_dict[tmp] = tmp-1

        return prev_tmp_dict

    m.previous_timepoint = \
        Param(m.TIMEPOINTS,
              initialize=previous_timepoint_init)


def load_model_data(m, d, data_portal, scenario_directory, horizon, stage):
    """
    """
    data_portal.load(filename=os.path.join(scenario_directory, horizon,
                                           "inputs", "horizons.tab"),
                     select=("HORIZONS", "boundary", "horizon_weight"),
                     index=m.HORIZONS,
                     param=(m.boundary, m.horizon_weight)
                     )

    data_portal.load(filename=os.path.join(scenario_directory, horizon, stage,
                                           "inputs", "timepoints.tab"),
                     select=("TIMEPOINTS","horizon"),
                     index=m.TIMEPOINTS,
                     param=m.horizon
                     )