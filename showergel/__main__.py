"""
This module is useful to plug a debugger.
Here is a useful VSCode debugger config::

    {
            "name": "Server showergel",
            "type": "python",
            "request": "launch",
            "program": "showergel",
            "args": [
                "${workspaceFolder}/test.ini"
            ],
            "console": "integratedTerminal"
        }

"""

from showergel import main

main()
