# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Write a honeybee Model to an IDF file and run them through EnergyPlus.

-
    Args:
        model: A honeybee model object possessing all geometry and corresponding
            energy simulation properties.
        _epw_ile: Path to an .epw file on your system as a text string.
        _ddy_file_: An optional path to a .ddy file on your system, which contains
            information about the design days used to size the hvac system. If None,
            this component will look for a .ddy file next to the .epw and extract
            all 99.6% and 0.4% design days.
        _sim_par_: A honeybee Energy SimulationParameter object that describes all
            of the setting for the simulation. If None, some default simulation
            parameters will automatically be used.
        add_str_: THIS OPTION IS JUST FOR ADVANCED USERS OF ENERGYPLUS.
            You can input additional text strings here that you would like
            written into the IDF.  The strings input here should be complete
            EnergyPlus objects that are correctly formatted. This input can be used to
            write objects into the IDF that are not currently supported by Honeybee.
        _folder_: An optional folder on your system, into which your IDF and result
            files will be written.  NOTE THAT DIRECTORIES INPUT HERE SHOULD NOT HAVE
            ANY SPACES OR UNDERSCORES IN THE FILE PATH.
        _write: Set to "True" to translate the model to an IDF file.
            The file path of the resulting file will appear in the idf output of
            this component.  Note that only setting this to "True" and not setting
            run_ to "True" will not automatically run the IDF through EnergyPlus.
        run_: Set to "True" to run your IDF through EnergyPlus once it is written.
            This will ensure that result files appear in their respective outputs.
    
    Returns:
        report: Check here to see a report of the EnergyPlus run.
        idf: The file path of the IDF file that has been generated on your machine.
        sql: The file path of the SQL result file that has been generated on your
            machine. This will be None unless run_ is set to True.
        eio:  The file path of the EIO file that has been generated on your machine.
            This file contains information about the sizes of all HVAC equipment
            from the simulation.
        rdd: The file path of the Result Data Dictionary (.rdd) file that is
            generated after running the file through EnergyPlus.  This file
            contains all possible outputs that can be requested from the EnergyPlus
            model.  Use the Read Result Dictionary component to see what outputs
            can be requested.
        html: The HTML file path of the Summary Reports. Note that this will be None
            unless the input _sim_par_ denotes that an HTML report is requested and
            run_ is set to True.
"""

ghenv.Component.Name = "HB Model to IDF"
ghenv.Component.NickName = 'ModelToIDF'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "Energy"
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import os

try:
    from ladybug.designday import DDY
    from ladybug.futil import write_to_file_by_name, nukedir
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee_energy.simulationparameter import SimulationParameter
    from honeybee_energy.run import run_idf
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def orphaned_warning(object_type):
    """Generate an error message for orphaned Faces, Apertures, or Doors."""
    return 'Input _model contains orphaned {}s. These are not permitted in ' \
        'Models for energy simulation.\nIf you have geometry that is not a ' \
        'part of a Room boundary that you want included in the energy simulation, ' \
        'it should be added as shades.'.format(object_type)


if all_required_inputs(ghenv.Component) and _write:
    # process the design days
    if _ddy_file_ is None:
        folder, epw_file_name = os.path.split(_epw_file)
        ddy_file = os.path.join(folder, epw_file_name.replace('.epw', '.ddy'))
        if os.path.isfile(ddy_file):
            ddy_obj = DDY.from_ddy_file(ddy_file)
            ddy_strs = [ddy.ep_style_string for ddy in ddy_obj.design_days if
                        '99.6%' in ddy.name or '.4%' in ddy.name]
        else:
            raise ValueError('No _ddy_file_ has been input and no .ddy file was '
                             'found next to the _epw_file.')
    else:
        ddy_obj = DDY.from_ddy_file(_ddy_file_)
        ddy_strs = [ddy.ep_style_string for ddy in ddy_obj.design_days]
    
    # process the simulation parameters
    if _sim_par_ is None:
        _sim_par_ = SimulationParameter()
        _sim_par_.output.add_zone_energy_use()
    
    # process the additional strings
    add_str = '/n'.join(add_str_) if add_str_ is not None else ''
    
    # process the simulation folder name and the directory
    if _folder_ is None:
        _folder_ = os.path.join(os.environ['USERPROFILE'], 'honeybee')
    directory = os.path.join(_folder_, _model.name, 'EnergyPlus')
    sch_directory = os.path.join(directory, 'schedules')
    
    # check the model to be sure there are no orphaned faces, apertures, or doors
    assert len(_model.orphaned_faces) == 0, orphaned_warning('Face')
    assert len(_model.orphaned_apertures) == 0, orphaned_warning('Aperture')
    assert len(_model.orphaned_doors) == 0, orphaned_warning('Door')
    
    # scale the model if the Rhino units are not meters
    meters_conversion = conversion_to_meters()
    if meters_conversion != 1:
        _model = _model.duplicate()  # duplicate model to avoid scaling the input
        _model.scale(meters_conversion)
    
    # create the strings for simulation paramters and model
    sim_par_str = _sim_par_.to_idf()
    model_str = _model.to.idf(_model, schedule_directory=sch_directory,
                              solar_distribution=_sim_par_.shadow_calculation.solar_distribution)
    idf_str = '\n\n'.join([sim_par_str, '\n\n'.join(ddy_strs), model_str, add_str])
    
    # delete any existing files in the directory
    nukedir(directory)
    
    # write the final string into an IDF.
    idf = os.path.join(directory, 'in.idf')
    write_to_file_by_name(directory, 'in.idf', idf_str, True)
    
    if run_:
        # TODO: Get the ep_path from a honeybee_energy.config module once it exists
        ep_path = 'C:/openstudio-2.8.0/EnergyPlus/'
        sql, eio, rdd, html = run_idf(idf, _epw_file, ep_path)