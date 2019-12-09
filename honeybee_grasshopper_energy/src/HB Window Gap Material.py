# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a window gas gap material that corresponds to a layer in a window construction.
This material can be plugged into the "HB Window Construction" component.
-

    Args:
        _name: Text string for material name.
        _thickness_: Number for the thickness of the air gap layer [m].
            Default: 0.0125
        _gas_types_: A list of text describing the types of gas in the gap.
            Text must be one of the following: 'Air', 'Argon', 'Krypton', 'Xenon'.
            Default: ['Air']
        _gas_ratios_: A list of text describing the volumetric fractions of gas
            types in the mixture.  This list must align with the gas_types
            input list. Default: Equal amout of gases for each type.
    
    Returns:
        mat: A window gas gap material that describes a layer in a window construction
            and can be assigned to a Honeybee Window construction.
"""

ghenv.Component.Name = "HB Window Gap Material"
ghenv.Component.NickName = 'GapMat'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "Energy"
ghenv.Component.SubCategory = "1 :: Construction"
ghenv.Component.AdditionalHelpFromDocStrings = "5"


try:  # import the honeybee-energy dependencies
    from honeybee_energy.material.gas import EnergyWindowMaterialGas, \
        EnergyWindowMaterialGasMixture
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))
try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set the default material properties
    _thickness_ = 0.0125 if _thickness_ is None else _thickness_
    _gas_types_ = ['Air'] if len(_gas_types_) == 0 else _gas_types_
    _gas_ratios_ = [1 / len(_gas_types_)] * len(_gas_types_) if \
        len(_gas_ratios_) == 0 else _gas_ratios_
    assert len(_gas_types_) == len(_gas_ratios_), \
        'Length of _gas_types_ does not equal length of _gas_ratios_.'
    
    # create the material
    if len(_gas_types_) == 1:
        mat = EnergyWindowMaterialGas(_name, _thickness_, _gas_types_[0])
    else:
        mat = EnergyWindowMaterialGasMixture(
            _name, _thickness_, _gas_types_, _gas_ratios_)