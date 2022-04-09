import argparse
import os

photo_idx = 1
orig_names_to_mod_names = {}
delete_count = 0
renamed_jpg_count = 0
renamed_raw_count = 0

def recursive_add_mapping(curr_path, curr_name):
    tmp_names_to_new_names = {}
    for f in os.listdir(curr_path):
        old_path = curr_path + "/" + f
        if os.path.isfile(old_path):
            if old_path.endswith(".jpg") or old_path.endswith(".JPG") :
                global photo_idx
                global orig_names_to_mod_names
                filename = f.split(".")[0]
                fileext = f.split(".")[1]
                new_name = curr_name + "_" + str(photo_idx)
                photo_idx += 1
                orig_names_to_mod_names[filename]= new_name
                global renamed_jpg_count
                renamed_jpg_count += 1
                new_path = curr_path + "/" + new_name + "." + fileext
                tmp_path = curr_path + "/" + new_name + "__tmp__." + fileext
                tmp_names_to_new_names[tmp_path] = new_path
                if args.force:
                    os.rename(old_path, tmp_path)
                print("\033[1;37;40mrenamed " + old_path + " to " + tmp_path)
        else:
            recursive_add_mapping(old_path, curr_name+"_"+f)
    for tmp_path, new_path in tmp_names_to_new_names.items():
        if args.force:
            os.rename(tmp_path, new_path)
        print("\033[1;37;40mrenamed " + tmp_path + " to " + new_path)


def clean_up_raw_folder(raw_path):
    tmp_names_to_new_names = {}
    global renamed_raw_count
    for f in os.listdir(raw_path):
        filename = f.split(".")[0]
        fileext = f.split(".")[1]
        mapping = orig_names_to_mod_names.get(filename)
        old_path = raw_path + "/" + f
        if mapping and mapping != "":
            tmp_path = raw_path + "/" + mapping + "__tmp__." + fileext
            new_path = raw_path + "/" + mapping + "." + fileext
            tmp_names_to_new_names[tmp_path] = new_path
            if args.force:
                os.rename(old_path, tmp_path)
            renamed_raw_count += 1
            print("\033[1;37;40mrenamed " + old_path + " to " + tmp_path)
        else:
            if args.force:
                os.remove(old_path)
            global delete_count
            delete_count += 1
            print("\033[1;31;40mdeleted " + old_path)
    for tmp_path, new_path in tmp_names_to_new_names.items():
        if args.force:
            os.rename(tmp_path, new_path)
        print("\033[1;37;40mrenamed " + tmp_path + " to " + new_path)

parser = argparse.ArgumentParser(description='Given the absolute path of a base directory containing images sorted into "raw" and "unprocessed" folders, renames the raw photos after the structure of subdirectories in unprocessed, deleting RAW files whose jpgs were deleted. Also renames the jpgs.')
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
dir_names = base_dir.split("/")
base_dir_name = dir_names[-1]
if base_dir_name == '':
    base_dir_name = dir_names[-2]
recursive_add_mapping(base_dir+"/unprocessed", base_dir_name)
clean_up_raw_folder(base_dir+"/raw")
print("\033[1;36;40m" + str(renamed_jpg_count) + " jpg files renamed, " + str(renamed_raw_count) + " raw files renamed, and " + str(delete_count) + " deleted.")
if args.force:
    print("Force flag detected. Changes were made.")
else:
    print("The force flag was not set using '-f', so no changes were made.  Preview mode.")
