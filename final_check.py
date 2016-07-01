# This script tells you:
# - if the directory <student/blatt-xx> exists
# - if the directory is cleaned (no .o files or files without ending)
# - if erfahrungen.txt was uploaded
# - if a Makefile was uploaded
# - if a feedback-tutor.txt file was created
# - if points were given (nothing of the form "/xx" or "/x")
# - if the sum of points was computed correctly
# - how many points the student got (xx/20 or x/20)
# - if there have been any changes since the last commit

from subprocess import call, Popen, PIPE
import os
import sys
import re
from correction_script import Correction


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
c = Correction()

def get_total_points(path):
    if os.path.exists(path + "feedback-tutor.txt"):
        with open(path + "feedback-tutor.txt") as file:
            lines = file.readlines()
            for line in lines:
                # Check whether the sum of the points was computed correctly
                points_match = re.match(r"^([\d\.]+)/20", line, re.MULTILINE)
                if points_match:
                    return float(points_match.group(1))
    return -1


def final_check_student(student, sheet_num):
    path_to_sheet = PATH + student + "/blatt-" + sheet_num + "/"

    print(HEADER + "\n" + "*"*80 + ENDC)
    print(OKBLUE + BOLD + "Checking student %s..." % student + ENDC)

    if os.path.isdir(path_to_sheet):   
        # Check whether the directory was cleaned properly
        files = c.is_dir_clean(path_to_sheet)
        for file in files:
            print(WARNING + "Should the file %s be here?" % file + ENDC)

        # Check whether erfahrungen.txt, Makefile and feedback-tutor.txt exist
        files = c.is_file_in_dir(path_to_sheet, ["erfahrungen.txt", "Makefile", "feedback-tutor.txt"])
        for file in files:
            print(WARNING + "Student %s doesn't have a %s in his repository." % (student, file) + ENDC)

        # Check whether files in the directory have been changed since last update
        changed_files = c.run_svn_diff(path_to_sheet)
        if changed_files:
            print(WARNING + "There have been some changes:" + ENDC)
            for i in range(len(changed_files)):
                print(BOLD + "    In %s:" % changed_files[i][0] + ENDC)
                for change in changed_files[i][1]:
                    print("    %s" % change)
                    
        # Check whether points were given correctly in the feedback-tutor.txt file
        errors = c.check_assigned_points(path_to_sheet)
        for err in errors:
            print(FAIL + "Seems like you haven't assigned the points correctly: %s" % err + ENDC)

        # Print out total points
        points = get_total_points(path_to_sheet)
        print(OKGREEN + "%s got %.1fP" % (student, points) + ENDC)

    else:
        print(FAIL + "Student %s doesn't have a directory blatt-%s in his repository." % (student, sheet_num) + ENDC)


def final_check_all_students(directories, sheet_num):
    print(OKBLUE + BOLD + "\n" + "#"*80 + ENDC)
    print(OKBLUE + BOLD + "#"*80 + ENDC)
    print(OKBLUE + """    Before we start: I promise you, nothing bad will happen.\n
    All I'm doing is check and print.\n
    I will not make any changes to any files nor will I create any new files.\n
    Don't worry.""" + ENDC)
    print(OKBLUE + BOLD + "#"*80 + ENDC)
    print(OKBLUE + BOLD + "#"*80 + ENDC)

    print(OKBLUE + BOLD + "Path to be checked: %s" % PATH)

    for dirc in directories:
        if "." not in dirc:
            final_check_student(dirc, sheet_num)


def main():
    # Exit if a wrong number of command line arguments is given
    arguments = sys.argv
    if len(arguments) != 2:
        print(WARNING + "Usage: python ./final_check.py <sheet number>" + ENDC)
        exit()

    sheet_num = arguments[1].zfill(2)
    directories = os.listdir(PATH)
    directories.sort()

    # Print a warning if the number of directories isn't 25
    if (len(directories) != 25):
        print(WARNING + "Strange number of directories. Please check:" + ENDC)
        print(directories)

    final_check_all_students(directories, sheet_num)


if __name__ == "__main__":
    main()