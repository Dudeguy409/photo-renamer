import argparse
import os

photo_idx = 1
orig_names_to_mod_names = {}
delete_count = 0
renamed_jpg_count = 0
renamed_raw_count = 0
raw_found = False
unprocessed_found = False

def recursive_add_mapping(curr_path, curr_name):
    timestamps_to_orig_names = {}
    for f in os.listdir(curr_path):
        old_path = curr_path + "/" + f
        if os.path.isfile(old_path):
            timestamp = os.path.getmtime(old_path)
            timestamps_to_orig_names[str(timestamp)] = f
        else:
            recursive_add_mapping(old_path, curr_name + "_" + f)
    sorted_timestamps = dict(sorted(timestamps_to_orig_names.items()))
    global photo_idx
    global orig_names_to_mod_names
    tmp_names_to_new_names = {}
    for ts, f in sorted_timestamps.items():
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
    for tmp_path, new_path in tmp_names_to_new_names.items():
        if args.force:
            os.rename(tmp_path, new_path)
        print("\033[1;37;40mrenamed " + tmp_path + " to " + new_path)


def clean_up_raw_folder(raw_path, base_dir_name):
    if not os.path.exists(raw_path):
        return
    global raw_found
    raw_found = True
    global unprocessed_found
    if not unprocessed_found:
        rename_raw_photos(raw_path, base_dir_name)
        return
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
            if args.clean:
                if args.force:
                    os.remove(old_path)
                global delete_count
                delete_count += 1
                print("\033[1;31;40mdeleted " + old_path)
    for tmp_path, new_path in tmp_names_to_new_names.items():
        if args.force:
            os.rename(tmp_path, new_path)
        print("\033[1;37;40mrenamed " + tmp_path + " to " + new_path)

def rename_raw_photos(raw_path, base_dir_name):
    global photo_idx
    global renamed_raw_count
    tmp_names_to_new_names = {}
    for f in os.listdir(raw_path):
        filename = f.split(".")[0]
        fileext = f.split(".")[1]
        old_path = raw_path + "/" + f
        new_name = base_dir_name + "_" + str(photo_idx)
        photo_idx += 1
        tmp_path = raw_path + "/" + new_name + "__tmp__." + fileext
        new_path = raw_path + "/" + new_name + "." + fileext
        tmp_names_to_new_names[tmp_path] = new_path
        if args.force:
            os.rename(old_path, tmp_path)
        renamed_raw_count += 1
        print("\033[1;37;40mrenamed " + old_path + " to " + tmp_path)
    for tmp_path, new_path in tmp_names_to_new_names.items():
        if args.force:
            os.rename(tmp_path, new_path)
        print("\033[1;37;40mrenamed " + tmp_path + " to " + new_path)

parser = argparse.ArgumentParser(description='Given the absolute path of a base directory containing images sorted into "raw" and "unprocessed" folders, renames the raw photos after the structure of subdirectories in unprocessed, deleting RAW files whose jpgs were deleted. Also renames the jpgs.')
parser.add_argument('directory', metavar='Dir', type=str, nargs=1,
                    help='absolute path of base photo directory.  Must contain raw and unprocessed subdirectories')
parser.add_argument("-f", "--force", help="enables changes to be written.  Defaults to false for preview mode. Cannot be undone",
                    action="store_true")
parser.add_argument("-c", "--clean", help="deletes raw files that don't have an accompanying unprocessed jpg in any of the subfolders.  Only makes changes when used with the '-f' or '--force' flag as well.  Useful when sorting through and deleting unprocessed jpgs.  Defaults to false. Cannot be undone",
                    action="store_true")

args = parser.parse_args()

if args.clean:
    print("Raw cleanup flag detected. Raw files without a matching unprocessed jpg will be deleted.")
else:
    print("The Raw cleanup flag was not set using '-c', so Raw files without a matching unprocessed jpg will NOT be deleted.")
if args.force:
    print("Force flag detected. Changes will be made.")
else:
    print("The force flag was not set using '-f', so no changes will be made.  Preview mode.")

base_dir = args.directory[0]
dir_names = base_dir.split("/")
base_dir_name = dir_names[-1]
if base_dir_name == '':
    base_dir_name = dir_names[-2]
unprocessed_dir = base_dir + "/unprocessed"
if os.path.exists(unprocessed_dir):
    unprocessed_found =  True
    recursive_add_mapping(unprocessed_dir, base_dir_name)
clean_up_raw_folder(base_dir+"/raw", base_dir_name)
print("\033[1;36;40m" + str(renamed_jpg_count) + " jpg files renamed, " + str(renamed_raw_count) + " raw files renamed, and " + str(delete_count) + " raw files deleted.")

if not unprocessed_found:
    print("\033[1;36;40m unprocessed jpg folder was not found and was skipped")
if not raw_found:
    print("\033[1;36;40m raw folder was not found and was skipped")
if args.clean:
    print("Raw cleanup flag detected. Raw files without a matching unprocessed jpg were deleted.")
else:
    print("The Raw cleanup flag was not set using '-c', so Raw files without a matching unprocessed jpg were NOT deleted.")
if args.force:
    print("Force flag detected. Changes were made.")
else:
    print("The force flag was not set using '-f', so no changes were made.  Preview mode.")
