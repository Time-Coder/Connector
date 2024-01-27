import os


def check_syntax(folder_name):
    for home, dirs, files in os.walk(folder_name):
        for filename in files:
            if filename.endswith(".py") and filename != "__init__.py":
                os.system("pyflakes " + home + "/" + filename)


def check_style(folder_name):
    for home, dirs, files in os.walk(folder_name):
        for filename in files:
            if filename.endswith(".py"):
                os.system("pycodestyle " + home + "/" + filename)


check_syntax("Connector")
check_style("Connector")
