import os


def check_syntax(folder_name):
    for home, dirs, files in os.walk(folder_name):
        for file_name in files:
            if file_name.endswith(".py") and file_name != "__init__.py":
                os.system("pyflakes " + home + "/" + file_name)


def check_style(folder_name):
    for home, dirs, files in os.walk(folder_name):
        for file_name in files:
            if file_name.endswith(".py"):
                os.system("pycodestyle " + home + "/" + file_name)


check_syntax("Connector")
check_style("Connector")
