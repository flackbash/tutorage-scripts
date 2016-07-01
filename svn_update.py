from subprocess import call
import sys
import os


# Color schemes
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

# Absolute path to the working directory
PATH = "/home/natalie/tutorat/abgaben/"


def update_all_students(directories):
    print(OKBLUE + BOLD + "\n" + "#"*80 + ENDC)
    print(OKBLUE + BOLD + "#"*80 + ENDC)
    print(OKBLUE + "What I will do:\n- Update all student repositories" + ENDC)
    print(OKBLUE + BOLD + "#"*80 + ENDC)
    print(OKBLUE + BOLD + "#"*80 + ENDC)

    print(OKBLUE + BOLD + "Path to be updated: %s" % PATH + ENDC)

    for dirc in directories:
        if "." not in dirc:
            print(HEADER + "\n" + "*"*80 + ENDC)
            print(OKBLUE + BOLD + "Updating student %s" % dirc + ENDC)
            path_to_student = PATH + dirc + "/"
            call(["svn", "update", path_to_student])

    print(OKGREEN + "Updated all students." + ENDC)


def main():
    # Exit if a wrong number of command line arguments is given
    arguments = sys.argv
    if len(arguments) != 1:
        print(WARNING + "Usage: python ./svn_update.py" + ENDC)
        exit()

    directories = os.listdir(PATH)
    directories.sort()

    # Print a warning if the number of directories isn't 25
    if (len(directories) != 25):
        print(WARNING + "Strange number of directories. Please check:" + ENDC)
        print(directories)

    update_all_students(directories)


if __name__ == "__main__":
    main()