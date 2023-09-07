"""Jpylyzer configuration settings that are shared between sub-modules."""
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import sys

VALIDATION_FORMAT = 'jp2'
OUTPUT_VERBOSE_FLAG = False
OUTPUT_PACKET_MARKERS_FLAG = False
EXTRACT_NULL_TERMINATED_XML_FLAG = False
INPUT_RECURSIVE_FLAG = False
INPUT_WRAPPER_FLAG = False
NO_PRETTY_XML_FLAG = False
LEGACY_XML_FLAG = False
MIX_FLAG = 0
ERR_CODE_NO_IMAGES = -7
UTF8_ENCODING = "UTF-8"
PLATFORM = sys.platform
PYTHON_VERSION = sys.version
