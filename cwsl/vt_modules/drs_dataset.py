"""

Copyright 2014 CSIRO

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Contains the VT module for a dataset created from a file pattern.

Copyright CSIRO 2014

"""

from vistrails.core.modules.basic_modules import List
from vistrails.core.modules.vistrails_module import Module, ModuleError, NotCacheable

from cwsl.configuration import configuration
from cwsl.core.pattern_dataset import PatternDataSet
from cwsl.core.constraint import Constraint


import logging
logger = logging.getLogger('cwsl.vtmodules.dataset')


class DataReferenceSyntax(NotCacheable, Module):
    """
    """

    # User defined constraints
    _input_ports = [('added_constraints', List,
                     {'defaults': ["[]"]})]

    _output_ports = [('out_dataset', '(csiro.au.cwsl:VtDataSet)')]

    def __init__(self, pattern, constraints=None):
        Module.__init__(self)
        self.pattern = pattern
        self.constraints = constraints

    def get_filepath_patterns(self):
        """
        Generate full filepath pattern using global configuration options
        and file pattern.

        TODO: determine with paths to use (user, auth or both)
        """
        if configuration.check('drs_basepath'):
            basepath = configuration.drs_basepath
        else:
            raise ModuleError(self,
                             ("No authorative path set"
                              " in the CWSL Configuration"))

        # TODO Check basepath add trailing '/'
        patterns = basepath + self.pattern
        return patterns

    def compute(self):

        # Determine file path
        patterns = self.get_filepath_patterns()
        logger.debug('Using pattern %s' % patterns)

        # Create constraints
        constraints = [Constraint(attribute, [values])
                       for attribute, values in self.constraints.iteritems()]

        # Add user contraints
        user_constraints = self.getInputFromPort("added_constraints")
        if user_constraints:
            constraints.extend(user_constraints)

        # Create dataset based on file search path and contraints
        dataset = PatternDataSet(patterns, constraints)

        self.setResult('out_dataset', dataset)


class RegionalClimateModel(DataReferenceSyntax):
    """
    File path search based on the CORDEX DRS (ref).

    Path structure: <path>/<mip>/<product>/<domain>/<institute>/<model>/<experiment>/<ensemble>/<RCMName>/<RCMVersionID>/<frequency>/<variable>/<filename>

      where:
          <path>: Configured via menu: Packages->CWSL->Configure: authorative_path 
          <filename>:  <variable>_<domain>_<model>_<experiment>_<ensemble>_<RCMName>_<RCMVersionID>_<frequency>_<time_span>

    """

    # CORDEX DATA REFERENCE SYNTAX
    pattern = '%product%/%activity%/%domain%/%institute%/%model%/%experiment%/%ensemble%/%RCMName%/%RCMVersionID%/%frequency%/%variable%/%variable%_%domain%_%model%_%experiment%_%ensemble%_%RCMName%_%RCMVersionID%_%frequency%_%time_span%.nc'

    # Restrict to RCM
    constraints = {'activity': 'RCM'}

    def __init__(self):
        super(RegionalClimateModel, self).__init__(self.pattern, self.constraints)


class GlobalClimateModel(DataReferenceSyntax):
    """
    File path search based on the CMIP5 GCM DRS (ref).

    Path structure: <path>/<mip>/<product>/<institute>/<model>/<experiment>/<frequency>/<realm>/<variable>/<ensemble>/<filename>
      where:
          <path>: Configured via menu: Packages->CWSL->Configure: authorative_path 
          <filename>:  <variable>_<mip_table>_<model>_<experiment>_<ensemble>_<time_span>
    """

    # DATA REFERENCE SYNTAX
    pattern = '%mip%/%product%/%institute%/%model%/%experiment%/%frequency%/%realm%/%variable%/%ensemble%/%variable%_%mip_table%_%model%_%experiment%_%ensemble%_%time_span%.nc'

    # Restrict to GCM
    constraints = {'activity': 'GCM'}

    def __init__(self):
        super(GlobalClimateModel, self).__init__(self.pattern, self.constraints)


class RegionalClimateModel_SDMa_NRM(RegionalClimateModel):
    """
    Creates a DataSet based on the CORDEX DRS.
    """

    constraints = {'mip': 'CMIP5',
                   'product': 'RCM',
                   'domain': 'AUS',
                   'RCMName': 'BOM-SDMa-NRM'}


class RegionalClimateModel_CCAM_NRM(RegionalClimateModel):
    """
    Creates a DataSet based on the CORDEX DRS.
    """

    constraints = {'mip': 'CMIP5',
                   'product': 'RCM',
                   'domain': 'global',
                   'RCMName': 'CSIRO-CCAM-NRM50'}