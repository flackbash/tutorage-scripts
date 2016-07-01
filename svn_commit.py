from subprocess import call, Popen, PIPE
import os
import sys
import re


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


def run_svn_diff(path):
    """Checks whether files in the given directory were changed since the last
    update.
    Returns a list of lists of the changed files and their changes.

    Arguments:
    path - A string. Path to the blatt-xx directory of the student.
    """
    p = Popen(["svn", "diff", path], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()
    lines = output.split("\n")
    changed_files = []
    for line in lines:
        changed_file = re.match(r"^\+\+\+\s(.*)\t", line, re.MULTILINE)
        if changed_file:
            changed_files.append((changed_file.group(1), []))
        change = re.match(r"^([\+\-][^\+\-].*)$", line, re.MULTILINE)
        if change:
            print(change.group(1))
            changed_files[-1][1].append(change.group(1))
    return changed_files


def commit_student(student, sheet_num):
    print(HEADER + "\n" + "*"*80 + ENDC)
    print(OKBLUE + BOLD + "Checking student %s" % student + ENDC)

    path_to_sheet = PATH + student + "/blatt-" + sheet_num + "/"
    path_to_student = PATH + student + "/"

    # Show differences since last update
    changed_files = run_svn_diff(path_to_student)
    if changed_files:
        print(WARNING + "Wait a second! There have been some changes:" + ENDC)
        for i in range(len(changed_files)):
            print(BOLD + "    In %s:" % changed_files[i][0] + ENDC)
            for change in changed_files[i][1]:
                print("    %s" % change)
            print("")

    # Add files not yet under version control
    # TODO(np76): Will prolly have to change that to add only new files
    call(["svn", "add", path_to_sheet])
    call(["svn", "add", path_to_sheet + "feedback-tutor.txt"])
    
    # Show svn status
    print(WARNING + "svn status in directory %s" % path_to_student + ENDC)
    call(["svn", "stat", path_to_student])

    # Let the user check everything before commiting changes
    user_input = raw_input(OKGREEN + "Press ENTER to continue " + ENDC)

    if user_input == "recheck":
        # Show differences since last update
        call(["svn", "diff", path_to_student])
        # Show svn status
        call(["svn", "stat", path_to_student])
    elif user_input == "skip":
        pass
    elif user_input == "quit":
        exit()
    else:
        call(["svn", "commit", path_to_sheet, "-m", "Added feedback"])

    user_input = raw_input(OKGREEN + "All good? " + ENDC)


def commit_all_students(directories, sheet_num):
    print(OKBLUE + BOLD + "\n" + "#"*80 + ENDC)
    print(OKBLUE + """What I will do:\n
    - Show svn differences\n
    - Add unversioned files\n
    - Show the svn status\n
    - Commit the changes if you're fine with it""" + ENDC)
    print(OKBLUE + BOLD + "#"*80 + ENDC)

    print(OKBLUE + BOLD + "Path to be commited: %s" % PATH + ENDC)

    for dirc in directories:
        if "." not in dirc:
            commit_student(dirc, sheet_num)

def main():
    # Exit if a wrong number of command line arguments is given
    arguments = sys.argv
    if len(arguments) != 2:
        print(WARNING + "Usage: python ./svn_commit.py <sheet number>" + ENDC)
        exit()

    sheet_num = arguments[1].zfill(2)
    directories = os.listdir(PATH)
    directories.sort()

    # Print a warning if the number of directories isn't 25
    if (len(directories) != 25):
        print(WARNING + "Strange number of directories. Please check:" + ENDC)
        print(directories)

    commit_all_students(directories, sheet_num)


if __name__ == "__main__":
    main()