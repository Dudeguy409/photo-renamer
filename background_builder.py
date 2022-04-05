import argparse
import os
import shutil

existing_photos_found = {}
delete_count = 0
add_count = 0
left_alone_count = 0

# 1 - make a map of all files that currently exist to bool if they are found
# 2 - trawl through all directories and either copy the file over or mark it as true in the map if it exists.
# 3 - delete all existing files not marked true

def recursive_build(curr_path, base_path):
    global existing_photos_found
    global add_count
    global left_alone_count
    for f in os.listdir(curr_path):
        new_path = curr_path + "/" + f
        if os.path.isfile(new_path):
            if new_path.endswith(".jpg") or new_path.endswith(".JPG") :
                if f in existing_photos_found:
                    existing_photos_found[f] = True
                    left_alone_count += 1
                    print("\033[1;37;40m left the following file alone: " + f )
                else:
                    if args.force:
                        shutil.copyfile(curr_path + "/" + f, base_path + "/" + f)
                    add_count += 1
                    print("\033[1;37;40m added " + f )
        else:
            recursive_build(new_path, base_path)

def determine_existing_photos(base_path):
    global existing_photos_found
    for f in os.listdir(base_path):
        abs_path = base_path + "/" + f
        if os.path.isfile(abs_path):
            existing_photos_found[f]= False

def delete_stray_photos(base_path):
    global existing_photos_found
    global delete_count
    for f, found in existing_photos_found.items():
        if not found:
            print("\033[1;37;40mdeleted " + f)
            delete_count += 1
            if args.force:
                os.remove(base_path+"/"+f)

parser = argparse.ArgumentParser(description='Given a directory of backgrounds, copies all photos in nested subdirectories to the top level.')
parser.add_argument('directory', metavar='Dir', type=str, nargs='?', const='~/Pictures/Backgrounds/',
                    help='absolute path of the base background directory.  Defaults to "~/Pictures/Backgrounds/"')
parser.add_argument("-f", "--force", help="enables changes to be written.  Defaults to false for preview mode. Cannot be undone",
                    action="store_true")

args = parser.parse_args()

if args.force:
    print("Force flag detected. Changes will be made.")
else:
    print("The force flag was not set using '-f', so no changes will be made.  Preview mode.")

base_dir = "/Users/davidsonac/Pictures/Backgrounds"
if args.directory is not None:
    base_dir = args.directory[0]

determine_existing_photos(base_dir)

recursive_build(base_dir, base_dir)

delete_stray_photos(base_dir)

print("\033[1;36;40m" + str(left_alone_count) + " files left alone, " + str(add_count) + " files added, and " + str(delete_count) + " files deleted.")
if args.force:
    print("Force flag was detected. Changes were made.")
else:
    print("The force flag was not set using '-f', so no changes were made.  Preview mode.")
