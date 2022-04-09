import argparse
import os

files_consolidated_count = 0
folders_created_count = 0

def top_level_move_files(base_path):
    for f in os.listdir(base_path):
        if not os.path.isfile(base_path + "/" + f):
            recursive_move_files(base_path, f, "/")

def recursive_move_files(base_path, chunk_dir, curr_dir):
    old_path = base_path + "/" + chunk_dir + "/" + curr_dir + "/"
    new_path = base_path + "/__merged__/" + curr_dir + "/"
    for f in os.listdir(old_path):
        old_name = old_path + f
        if os.path.isfile(old_name):
                global files_consolidated_count
                files_consolidated_count += 1
                new_name = new_path + f
                if args.force:
                    os.rename(old_name, new_name)
                print("\033[1;37;40mrenamed " + old_name + " to " + new_name)
        else:
            new_dir = new_path + f
            exists = os.path.exists(new_dir)
            if not exists:
                # Create a new directory because it does not exist
                if args.force:
                    os.makedirs(new_dir)
                global folders_created_count
                folders_created_count += 1
                print("The new directory " + new_dir + " is created!")
            recursive_move_files(base_path, chunk_dir, curr_dir + "/" + f)

parser = argparse.ArgumentParser(description='Given the absolute path of a base directory containing a bunch of numbered directories representing chunks of the same folder on Google drive, merges all files or pictures into a common folder, maintaining the same directory structure')
parser.add_argument('directory', metavar='Dir', type=str, nargs=1,
                    help='absolute path of base photo directory.  Must contain raw and unprocessed subdirectories')
parser.add_argument("-f", "--force", help="enables changes to be written.  Defaults to false for preview mode. Cannot be undone",
                    action="store_true")

args = parser.parse_args()

if args.force:
    print("Force flag detected. Changes will be made.")
else:
    print("The force flag was not set using '-f', so no changes will be made.  Preview mode.")

base_dir = args.directory[0]
top_level_move_files(base_dir)
print("\033[1;36;40m" + str(files_consolidated_count) + " files consolidated and " + str(folders_created_count) + " folders created!")
if args.force:
    print("Force flag detected. Changes were made.")
else:
    print("The force flag was not set using '-f', so no changes were made.  Preview mode.")
