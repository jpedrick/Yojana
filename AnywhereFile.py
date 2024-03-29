"""
  Copyright notice:
  This file is part of Cursed.
  Cursed is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  Cursed is also covered by GNU Affero General Public License with the 
  following permission under the GNU Affero GPL version 3 section 7:
      If you modify this Program, or any covered work, by linking or
      combining it with other code, such other code is not for that reason
      alone subject to any of the requirements of the GNU Affero GPL
      version 3.

  Cursed is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with Cursed.  If not, see <https://www.gnu.org/licenses/>.

  You should also have received a copy of the GNU Affero General Public License
  along with Cursed.  If not, see <https://www.gnu.org/licenses/>.
"""
import urllib
import io

class AnywhereFile:
    def __init__(self, path):
        if path.startswith('https://'):
            with urllib.request.urlopen( path ) as data:
                self.data = io.BytesIO( data.read() ) 
        else:
            with open( path, "rb" ) as data:
                self.data = io.BytesIO( data.read() ) 
