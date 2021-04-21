# What is Multiple Builder?
This project is useful to update and build projects that use Git and Maven.

The main feature is execute some default commands used by developer in theirs work days for a lot Git projects. That way, with a unique command a bunch of projects can be reset and update by Git command and built by Maven, as well.

## What is required?
This is a Python 3 script implemented by Object-Oriented paradigm that has been refactored using the Clean Code best practices.

Then, to run it just the Python3 interpreter is necessary, thats can be downloaded at: [Python Downloads](https://www.python.org/downloads/). **Note:** During the Python installation setup don't forget to add Python path to your System Operation Path.

## How to use it?
When the script has executed a Common Line Interface - CLI can be shown with some options that will modify the reset, update and the build process for the multiple Git repositories that already been clonned.
Thus, the projects that you want to build by Multiple Builder thats be cloned in a root path for it, e.g.: C:/my_repositories.

See below the parameters you can pass before to run the script, thats will allow to build yours projects in different ways:

Check the script menu:
> python multiple_builder.py -h

Execute the script in the same path of the cloned Git repositories:
> python multiple_builder.py

Execute the script for a specific folder with the cloned Git repositories:
> python multiple_builder.py -d C:/my_repositories

Execute the script passing the flag to delete all the user's .m2 folders:
> python multiple_builder.py -c

Execute the script automatically for the all Git repositories:
> python multiple_builder.py -b

Execute the script picking the respositories and skipping the menu options:
> python multiple_builder.py -sm

**Note:** don't forget you can combine the differents parameters:
> python multiple_builder.py -c -sm -d C:/my_repositories

