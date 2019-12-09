# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create an Infiltration object that can be used to create a ProgramType or be
assigned directly to a Room.
-

    Args:
        _name_: Text string for the infiltration definition name. If None, a unique
            name will be generated.
        _flow_per_ext_area: A numerical value for the intensity of infiltration
            in m3/s per square meter of exterior surface area. Typical values for
            this property are as follows (note all values are at typical building
            pressures of ~4 Pa):
                * 0.0001 (m3/s per m2 facade) - Tight building
                * 0.0003 (m3/s per m2 facade) - Average building
                * 0.0006 (m3/s per m2 facade) - Leaky building
        _schedule_: A fractional schedule for the infiltration over the course
            of the year. The fractional values will get multiplied by the
            flow_per_exterior_area to yield a complete infiltration profile.
            Default: 'Always On'
    
    Returns:
        infil: An Infiltration object that can be used to create a ProgramType or
            be assigned directly to a Room.
"""

ghenv.Component.Name = "HB Infiltration"
ghenv.Component.NickName = 'Infiltration'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "Energy"
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import uuid

try:
    from honeybee_energy.load.infiltration import Infiltration
    from honeybee_energy.lib.schedules import schedule_by_name
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # make a default Infiltration name if none is provided
    if _name_ is None:
        _name_ = "Infiltration_{}".format(uuid.uuid4())
    
    # get the schedule
    _schedule_ = _schedule_ if _schedule_ is not None else 'Always On'
    if isinstance(_schedule_, str):
        _schedule_ = schedule_by_name(_schedule_)
    
    # create the Infiltration object
    infil = Infiltration(_name_, _flow_per_ext_area, _schedule_)