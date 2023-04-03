import argparse
import os

photo_idx = 1
orig_names_to_mod_names = {}
orig_names_matched = {}
delete_count = 0
renamed_jpg_count = 0
renamed_raw_count = 0
raw_found = False
unprocessed_found = False
unmatched_raw_count = 0
unmatched_unprocessed_count = 0
duplicate_unprocessed_count = 0

def recursive_add_mapping(curr_path, curr_name):
    timestamps_to_orig_names = {}
    for f in os.listdir(curr_path):
        old_path = curr_path + "/" + f
        if os.path.isfile(old_path):
            timestamp = os.path.getmtime(old_path)
            mapping = timestamps_to_orig_names.get(str(timestamp))
            if mapping:
                timestamps_to_orig_names[str(timestamp)] = mapping + [f]
            else:
                timestamps_to_orig_names[str(timestamp)] = [f]
        else:
            recursive_add_mapping(old_path, curr_name + "_" + f)
    sorted_timestamps = dict(sorted(timestamps_to_orig_names.items()))
    global photo_idx
    global orig_names_to_mod_names
    tmp_names_to_new_names = {}
    global orig_names_matched
    global raw_found
    global duplicate_unprocessed_count
    for ts, files in sorted_timestamps.items():
        for f in files:
            filename = f.split(".")[0]
            fileext = f.split(".")[1]
            if filename != "" :
                new_name = curr_name + "_" + str(photo_idx)
                photo_idx += 1
                already_found = orig_names_to_mod_names.get(filename)
                if raw_found and already_found:
                    duplicate_unprocessed_count += 1
                    print("\033[1;31;40m found duplicate unprocessed file " + filename + ", full file path: " + f)
                orig_names_to_mod_names[filename]= new_name
                orig_names_matched[filename]= False
                global renamed_jpg_count
                renamed_jpg_count += 1
                old_path = curr_path + "/" + f
                new_path = curr_path + "/" + new_name + "." + fileext
                tmp_path = curr_path + "/" + new_name + "__tmp__." + fileext
                tmp_names_to_new_names[tmp_path] = new_path
                if args.rename:
                    if args.force:
                        os.rename(old_path, tmp_path)
                    if args.verbose:
                        print("\033[1;37;40mrenamed " + old_path + " to " + tmp_path)
    for tmp_path, new_path in tmp_names_to_new_names.items():
        if args.rename:
            if args.force:
                os.rename(tmp_path, new_path)
            if args.verbose:
                print("\033[1;37;40mrenamed " + tmp_path + " to " + new_path)


def clean_up_raw_folder(raw_path, base_dir_name):
    global raw_found
    if not raw_found:
        return
    global unprocessed_found
    if not unprocessed_found:
        rename_raw_photos(raw_path, base_dir_name)
        return
    tmp_names_to_new_names = {}
    global renamed_raw_count
    global unmatched_raw_count
    global orig_names_matched
    for f in os.listdir(raw_path):
        filename = f.split(".")[0]
        fileext = f.split(".")[1]
        if filename != "":
            mapping = orig_names_to_mod_names.get(filename)
            old_path = raw_path + "/" + f
            if mapping and mapping != "":
                tmp_path = raw_path + "/" + mapping + "__tmp__." + fileext
                new_path = raw_path + "/" + mapping + "." + fileext
                tmp_names_to_new_names[tmp_path] = new_path
                orig_names_matched[filename] = True
                if args.rename:
                    if args.force:
                        os.rename(old_path, tmp_path)
                    renamed_raw_count += 1
                    if args.verbose:
                        print("\033[1;37;40mrenamed " + old_path + " to " + tmp_path)
            else:
                if args.clean:
                    if args.force:
                        os.remove(old_path)
                    global delete_count
                    delete_count += 1
                    print("\033[1;31;40mdeleted " + old_path)
                else:
                    print("\033[1;31;40mfailed to match raw file " + old_path)
                    unmatched_raw_count += 1
    for tmp_path, new_path in tmp_names_to_new_names.items():
        if args.rename:
            if args.force:
                os.rename(tmp_path, new_path)
            if args.verbose:
                print("\033[1;37;40mrenamed " + tmp_path + " to " + new_path)

def print_unmatched_unprocessed():
    global raw_found
    global orig_names_matched
    global unmatched_unprocessed_count
    if raw_found:
        for fname, found in orig_names_matched.items():
            if not found:
                print("\033[1;31;40mfailed to match unprocessed file " + fname)
                unmatched_unprocessed_count += 1


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
        if args.rename:
            if args.force:
                os.rename(old_path, tmp_path)
            renamed_raw_count += 1
            if args.verbose:
                print("\033[1;37;40mrenamed " + old_path + " to " + tmp_path)
    for tmp_path, new_path in tmp_names_to_new_names.items():
        if args.rename:
            if args.force:
                os.rename(tmp_path, new_path)
            if args.verbose:
                print("\033[1;37;40mrenamed " + tmp_path + " to " + new_path)

parser = argparse.ArgumentParser(description='Given the absolute path of a base directory containing images sorted into "raw" and "unprocessed" folders, renames the raw photos after the structure of subdirectories in unprocessed, deleting RAW files whose jpgs were deleted. Also renames the jpgs.')
parser.add_argument('directory', metavar='Dir', type=str, nargs=1,
                    help='absolute path of base photo directory.  Must contain raw and unprocessed subdirectories')
parser.add_argument("-f", "--force", help="enables changes to be written.  Defaults to false for preview mode. Cannot be undone",
                    action="store_true")
parser.add_argument("-c", "--clean", help="deletes raw files that don't have an accompanying unprocessed jpg in any of the subfolders.  Only makes changes when used with the '-f' or '--force' flag as well.  Useful when sorting through and deleting unprocessed jpgs.  Defaults to false. Cannot be undone",
                    action="store_true")
parser.add_argument("-r", "--rename", help="renames jpg and/or raw files according to their folder structure.  Only makes changes when used with the '-f' or '--force' flag as well.  It is best to only use this flag BEFORE backing up pictures to the cloud, since using this flag after deleting some photos locally will cause the local file names and cloud file names to no longer match.  Defaults to false. Cannot be undone",
                    action="store_true")
parser.add_argument("-v", "--verbose", help="prints verbose debug information for what each files was renamed to.  Defaults to false.",
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
raw_dir = base_dir + "/raw"
if os.path.exists(raw_dir):
    raw_found = True
if os.path.exists(unprocessed_dir):
    unprocessed_found =  True
    recursive_add_mapping(unprocessed_dir, base_dir_name)
clean_up_raw_folder(raw_dir, base_dir_name)
print_unmatched_unprocessed()
print("\033[1;36;40m" + str(renamed_jpg_count) + " jpg files renamed, " + str(renamed_raw_count) + " raw files renamed, " + str(delete_count) + " raw files deleted, " + str(unmatched_unprocessed_count) + " umatched unprocessed files, " +str(unmatched_raw_count) + " unmatched raw files, and " + str(duplicate_unprocessed_count) + " duplicate unprocessed file names.")

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
