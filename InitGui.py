# SPDX-License-Identifier: LGPL-2.1-or-later
"""FreeCAD Jewelry Workbench loader."""

import os
import sys

# Ensure package directory is in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import and register Lapidary workbench (faceting)
try:
    import freecad.lapidary.init_gui
except Exception as e:
    pass

# Import and register Jewelry workbench
try:
    import freecad.jewelry.init_gui
except Exception as e:
    pass
