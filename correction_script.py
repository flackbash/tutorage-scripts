from subprocess import call, Popen, PIPE
import os
import sys
import re
import time
import getopt


# Color schemes
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

class Correction:

    def __init__(self):
        # Absolute path to the working directory
        self.directory_path = "/home/natalie/tutorat/abgaben/"
        # Absolute path to the solutions
        self.solution_path = "/home/natalie/tutorat/solutions/"
        # quick version: open only feedback, don't open terminal, don't run make
        self.quick_version = False
        self.only_feedback = False
        self.no_terminal = False
        self.no_solution = False
        self.no_make = False
        self.sheet_num = ''
        self.open_makefile = False
        self.curr_index = 0
        self.next_index = 0
        self.directories = []
        self.exit = False


    def create_feedback(self, path):
        """Creates a feedback-tutor.txt file if it doesn't exist.
        Returns True if a file was created.

        Arguments:
        path - A string. Path to the blatt-xx directory of the student.
        """
        created = False
        if not os.path.exists(path + "feedback-tutor.txt"):
            call(["cp", "/home/natalie/tutorat/feedback-tutor.txt", path])
            created = True
        return created


    def open_student_files(self, path, open_only_feedback=False):
        """Opens the directory <path> and the contained files in sublime.

        Arguments:
        path - A string. Path to the blatt-xx directory of the student.
        open_only_feedback - A boolean. Opens only feedback files if true.
        """
        path_to_student = re.sub(r"blatt-\d\d.*", "", path)
        call(["subl", "-b", path_to_student])
        # os.system("subl --command toggle_full_screen")
        for file in os.listdir(path):
            if open_only_feedback:
                if file == "feedback-tutor.txt":
                    call(["subl", "-b", path + file])
            elif self.open_makefile or file != "Makefile":
                call(["subl", "-b", path + file])


    def open_solution(self, path):
        """Opens the solution and common-mistakes.txt using a double vertical
        layout.

        Arguments:
        path - A string. Path to the solution directory for sheet-xx.
        """
        dic = '{"cols": [0, 0.5, 1],"rows": [0, 1],"cells": [[0, 0, 1, 1], [1, 0, 2, 1]]}'
        os.system("subl --command 'set_layout " + dic + "'")
        if os.path.isdir(path):
            for file in os.listdir(path):
                if self.open_makefile or file != "Makefile":
                    call(["subl", "-b", path + file])
        # Open common-mistakes
        path_common_mistakes = "/home/natalie/tutorat/common-mistakes.txt"
        if os.path.exists(path_common_mistakes):
            call(["subl", "-b", path_common_mistakes])


    def run_make(self, path):
        """Runs make test, checkstyle compile and clean.

        Arguments:
        path - A string. Path to the blatt-xx directory of the student.
        """
        call(["make", "test", "checkstyle", "compile", "clean", "-C", path])


    def is_dir_clean(self, path):
        """Checks whether the directory was cleaned properly.

        Arguments:
        path - A string. Path to the blatt-xx directory of the student.
        """
        if not os.path.isdir(path):
            return []
        strange_files = []
        for file in os.listdir(path):
            if ".o" in file or "." not in file and "Makefile" != file:
                strange_files.append(file)
        return strange_files


    def print_is_dir_clean(self, path):
        strange_files = self.is_dir_clean(path)
        for file in strange_files:
            print(WARNING + "Should the file %s be here?" % file + ENDC)
        return (len(strange_files) != 0)


    def is_file_in_dir(self, path, file_list):
        """Checks whether the files in file_list exist in the given path.

        Arguments:
        path - A string. Path to the blatt-xx directory of the student.
        """
        missing_files = []
        for file in file_list:
            if not os.path.exists(path + file):
                missing_files.append(file)
        return missing_files


    def check_assigned_points(self, path):
        """Checks whether the points were assigned everywhere and the sum matches
        the total given points.

        Arguments:
        path - A string. Path to the blatt-xx directory of the student.
        """
        point_errors = []
        if os.path.exists(path + "feedback-tutor.txt"):
            with open(path + "feedback-tutor.txt") as file:
                lines = file.readlines()
                total_points = 0
                for line in lines:
                    if re.match(r"^/\d+", line, re.MULTILINE):
                        point_errors.append(line[:-1])
                    points_match = re.match(r"^([\d\.]+)/(\d+)", line, re.MULTILINE)
                    if points_match:
                        if points_match.group(2) != "20":
                            total_points += float(points_match.group(1))
                        elif total_points != float(points_match.group(1)):
                            point_errors.append("Expected: %.1f, Actual: %s" % (total_points, points_match.group(1)))
        else:
            point_errors.append("No feedback-tutor.txt")
        return point_errors


    def print_check_points(self, path):
        errors = self.check_assigned_points(path)
        for err in errors:
            print(FAIL + "Seems like you haven't assigned the points correctly: %s" % err + ENDC)
        return (len(errors) != 0)


    def run_svn_diff(self, path):
        """Checks whether files in the given directory were changed since the last
        update.
        Returns a list of lists of the changed files and their changes.

        Arguments:
        path - A string. Path to the blatt-xx directory of the student.
        """
        path_to_student = re.sub(r"blatt-\d\d.*", "", path)
        p = Popen(["svn", "diff", path_to_student], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        lines = output.split("\n")
        changed_files = []
        for line in lines:
            changed_file = re.match(r"^\+\+\+\s(.*)\t", line, re.MULTILINE)
            if changed_file:
                changed_files.append((changed_file.group(1), []))
            change = re.match(r"^([\+\-][^\+\-].*)$", line, re.MULTILINE)
            if change:
                changed_files[-1][1].append(change.group(1))
        return changed_files


    def print_svn_diff(self, path):
        changed_files = self.run_svn_diff(path)
        for i in range(len(changed_files)):
            print(WARNING + "Wait a second! There have been some changes." + ENDC)
            print(BOLD + "    In %s:" % changed_files[i][0] + ENDC)
            for change in changed_files[i][1]:
                print("    %s" % change)
        return (len(changed_files) != 0)

    def get_student_preferences(self, student):
        """Read student preferences out of file student_preferences.txt and return
        them.

        Arguments:
        student - username of the student
        """
        path = "/home/natalie/tutorat/student_preferences.txt"
        preferences = []
        if os.path.exists(path):
            with open(path) as file:
                lines = file.readlines()
                found_student = False
                for i, line in enumerate(lines):
                    if line[:3] == "---" and found_student:
                        return preferences
                    elif line.strip() == student:
                        found_student = True
                    elif found_student:
                        preferences.append(line.strip())
        return []


    def open_gnome_terminal(self, path):
        """Opens a new gnome-terminal tab.

        Arguments:
        path - A string. Path to the blatt-xx directory of the student.
        """
        call(["gnome-terminal", "--tab", "--working-directory=" + path])


    def process_user_input(self):
        """Waits for user input and processes input.
        back, recheck, restart, quit, a student name and Enter will exit the
        function.
        Other inputs will lead to another input prompt.
        """
        wait = True
        path_to_sheet = self.directory_path + self.directories[self.curr_index] + "/blatt-" + self.sheet_num + "/"

        while (wait):
            user_input = raw_input(OKGREEN + "User Input: " + ENDC)
            user_input.strip()

            # Options for which student to check next
            if user_input in self.directories:
               self.next_index = self.directories.index(user_input)
               wait = False
            elif user_input == "back":
               self.next_index = self.curr_index - 1
               wait = False
            elif user_input == "recheck":
                self.next_index = self.curr_index
                wait = False
            elif user_input == "restart":
                self.next_index = 0
                wait = False
            elif user_input == "quit":
                self.exit = True
                wait = False
            elif user_input == "":
                self.next_index = self.curr_index + 1
                wait = False

            # Options for the following corrections
            elif user_input == "only_feedback":
                self.only_feedback = True
            elif user_input == "!only_feedback":
                self.only_feedback = False
            elif user_input == "no_terminal":
                self.no_terminal = True
            elif user_input == "!no_terminal":
                self.no_terminal = False
            elif user_input == "no_solution":
                self.no_solution = True
            elif user_input == "!no_solution":
                self.no_solution = False
            elif user_input == "no_make":
                self.no_make = True
            elif user_input == "!no_make":
                self.no_make = False
            elif user_input == "reset":
                self.only_feedback = False
                self.no_terminal = False
                self.no_solution = False
                self.no_make = False
            elif user_input == "help":
                print(BOLD + "  Press ENTER to continue." + ENDC)
                print(BOLD + "  Options (proceed after input): back, recheck, restart, quit." + ENDC)
                print(BOLD + "  Options (wait after input): only_feedback, no_terminal, no_solution, no_make, reset, help." + ENDC)
                print(BOLD + "  Run commands: run_make, open_terminal, check." + ENDC)

            # Options for running commands
            elif user_input == "run_make":
                self.run_make(path_to_sheet)
            elif user_input == "open_terminal":
                self.open_gnome_terminal(path_to_sheet)
            elif user_input == "check":
                self.print_svn_diff(path_to_sheet)
                self.print_is_dir_clean(path_to_sheet)
                self.print_check_points(path_to_sheet)

            # Print a warning if the option is unknown
            else:
                print(WARNING + "Unknown Option." + ENDC)
                


    def check_student(self):
        student = self.directories[self.curr_index]
        path_to_solution = self.solution_path + "blatt-" + self.sheet_num + "/"
        path_to_sheet = self.directory_path + student + "/blatt-" + self.sheet_num + "/"

        print(HEADER + "\n" + "*"*80 + ENDC)
        print(OKBLUE + BOLD + "Checking student %s" % student + ENDC)

        if os.path.isdir(path_to_sheet):
            dir_exists = True

            # Print student preferences
            preferences = self.get_student_preferences(student)
            for preference in preferences:
                print(BOLD + preference + ENDC)

            # Create feedback-tutor.txt if it doesn't exist
            if self.create_feedback(path_to_sheet):
                print(OKGREEN + "Created feedback-tutor.txt." + ENDC)      

            # Open directory and the contained files for each student in sublime
            only_feedback = self.quick_version or self.only_feedback
            self.open_student_files(path_to_sheet, open_only_feedback=only_feedback)
            time.sleep(1)

            # Open the solution using a double vertical layout
            if (not self.quick_version and not self.no_solution):
                self.open_solution(path_to_solution)

            # Run make test, checkstyle compile and clean
            if (not self.quick_version and not self.no_make):
                self.run_make(path_to_sheet)
            
            # Check whether the directory was cleaned properly
            files = self.is_dir_clean(path_to_sheet)
            for file in files:
                print(WARNING + "Should the file %s be here?" % file + ENDC)

            # Check whether the student has uploaded a erfahrungen.txt and the Makefile file
            files = self.is_file_in_dir(path_to_sheet, ["erfahrungen.txt", "Makefile"])
            for file in files:
                print(WARNING + "Student %s doesn't have a %s in his repository." % (student, file) + ENDC)

            # Open a new gnome-terminal tab in the students blatt-xx directory
            if (not self.quick_version and not self.no_terminal):
                self.open_gnome_terminal(path_to_sheet)
        
        else:
            # If the directory doesn't exist, only open super-directory and wait for user input
            dir_exists = False
            print(FAIL + "Student %s doesn't have a directory blatt-%s in his repository." % (student, self.sheet_num) + ENDC)
            call(["subl", self.directory_path + student])

        # Process user_input. 
        self.process_user_input()

        if (dir_exists):
            # Check whether points were assigned correctly, if changes were made, if directory is clean.
            errors = self.print_check_points(path_to_sheet)
            errors = self.print_svn_diff(path_to_sheet) or errors
            errors = self.print_is_dir_clean(path_to_sheet) or errors
            if errors:
                self.process_user_input()

        # Close the sublime window
        call(["subl", "--command", "close_window"])
        time.sleep(1)


    def check_all_students(self):
        while self.curr_index < len(self.directories):
            if "." not in self.directories[self.curr_index]:
                self.check_student()
                if self.exit:
                    exit()
                self.curr_index = self.next_index
            else:
                self.curr_index += 1


    def print_usage_and_exit(self):
        print(WARNING + "Usage: python ./correction_script.py <sheet number> [arguments]" + ENDC)
        sys.exit(2)


    def main(self):
        options = "qftsmc:h"
        long_options = ["quick", "feedback_only", "no_terminal", "no_solution", "no_make", "check_student", "help"]
        try:
            opts, args = getopt.gnu_getopt(sys.argv, options, long_options)
        except getopt.GetoptError:
            print("There has been an error while parsing the command line arguments.")
            self.print_usage_and_exit()

        check_only_student = ""
        for opt, opt_args in opts:
            if opt == '-q' or opt == '--quick': self.quick_version = True
            elif opt == '-f' or opt == '--feedback_only': self.only_feedback = True
            elif opt == '-t' or opt == "--no_terminal": self.no_terminal = True
            elif opt == '-s' or opt == "--no_solution": self.no_solution = True
            elif opt == '-m' or opt == "--no_make": self.no_make = True
            elif opt == '-c' or opt == "--check_student": check_only_student = opt_args;
            elif opt == '-h' or opt == "--help":
                string = ("Usage: python ./correction_script.py <sheet number> [arguments]\n\n"
                          "Arguments:\n"
                          "-q, --quick\t\t" + "Run a quick version: open only feedback, don't open a terminal, don't run make.\n"
                          "-f, --feedback_only\t" + "Open only the tutor feedback file.\n"
                          "-t, --no_terminal\t" + "Don't open a new terminal.\n"
                          "-s, --no_solution\t" + "Don't open the solution.\n"
                          "-m, --no_make\t\t" + "Don't run make.\n"
                          "-h, --help\t\t" + "Show help options.\n")
                print(BOLD + string + ENDC)
                sys.exit(2)
            else:
                self.print_usage_and_exit()

        if len(args) != 2:
            self.print_usage_and_exit()

        self.sheet_num = args[1].zfill(2)
        self.directories = os.listdir(self.directory_path)
        self.directories.sort()

        # Print a warning if the number of directories isn't 25
        if (len(self.directories) != 25):
            print(WARNING + "Strange number of directories. Please check:" + ENDC)
            print(self.directories)

        if len(check_only_student) > 0:
            if check_only_student in self.directories:
                self.curr_index = self.directories.index(check_only_student)
                self.check_student()
            else:
                print("Student not known.")
                sys.exit(2)
        else:
            self.check_all_students()


if __name__ == "__main__":
    correction = Correction()
    correction.main()