"""
This module helps to plug a VSCode debugger with the following configuration::

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
