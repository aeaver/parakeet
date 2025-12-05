import zipfile, requests, json, shutil
from pathlib import Path

def find_path():
    homepath = Path(r"C:\Users")

    for path in homepath.iterdir():
        if path.is_dir():

            prismpath = path / "AppData"/"Roaming"/"PrismLauncher"/"instances"
            cursepath = path / "curseforge"/ "minecraft" / "Instances"

            if prismpath.exists():
                yield ("PrismLauncher",prismpath)
            if cursepath.exists():
                yield ("CurseForge",cursepath)

def find_ver(launcher_choice_path):
    homepath = launcher_choice_path

    for path in homepath.iterdir():
        if path.is_dir():

            ver_dir = path

            if ver_dir.exists():
                yield ver_dir

def find_mod(mod_path):
    modpath = mod_path

    for path in modpath.iterdir():
        if path.is_dir():

            mod_folder = path / "mods"

            if mod_folder.exists():
                yield mod_folder

def find_jar(true_mod_folder, mod_list_manifest):

    for mods in mod_list_manifest:
        for jars in true_mod_folder.glob(mods):
            yield jars

def delete_old_jar(jarfile):
    try:
        for jar in jarfile:
            jar.unlink()
            print(f"deleted {jar} from dir")
    except FileNotFoundError:
        for jar in jarfile:
            print(f"{jar} not found")

def find_zip(true_mod_folder):

    filepath = true_mod_folder.rglob("*.zip")
    try:
        for zip in filepath:
            print(zip)
            return zip
    except FileNotFoundError:
        print("no zip fouind")


def main():
    #get Launcher
    available_path = list(find_path())

    if not available_path:
        print("No Path to minecraft instance has been found")

    counter = 1
    for launcher,paths in available_path:
        print(f"[{counter}]. {launcher} : {paths}")
        counter+=1

    while True:
        try:
            chosenPathLauncher = int(input("Select Your launcher: "))
        except ValueError:
            print("Numbers only")
        else:
            break

    selected_choice = available_path[chosenPathLauncher - 1]
    launcher_choice_path = selected_choice[1]

    #Get Version
    ver_folder_path = list(find_ver(launcher_choice_path))

    if not ver_folder_path:
        print("No Instances exists")

    counter = 1
    for paths in ver_folder_path:
        print(f"[{counter}]. {paths}")
        counter+=1

    while True:
        try:
            Chosen_Mod_Folder = int(input("Pick Your instance: "))
        except ValueError:
            print("Numbers only")
        else:
            break

    Choosed_Mod_Folder = ver_folder_path[Chosen_Mod_Folder-1]
    mod_path = Choosed_Mod_Folder

    mod_folder_path = list(find_mod(mod_path))

    for paths in mod_folder_path:
        print(paths)

    true_mod_folder = mod_folder_path[0]

    url = "https://raw.githubusercontent.com/aeaver/parakeet/refs/heads/main/manifest.json"

    json_request = requests.get(url)
    manifest = json_request.json()
    mod_list_manifest = manifest["target_mod"]
    download_url = manifest["download_url"]
    destination_filename = "mods.zip"
    true_mod_folder_path = true_mod_folder / destination_filename
    mod_manifest = requests.get(download_url)

    if mod_manifest.status_code == 200:
        with open(true_mod_folder_path, "wb") as f:
            f.write(mod_manifest.content)
        print("Download completed")
    else:
        print(f"Download failed. Status code : {mod_manifest.status_code}")

    jarfile = find_jar(true_mod_folder, mod_list_manifest)

    delete_old_jar(jarfile)

    zip_path = find_zip(true_mod_folder)

    try:
        with zipfile.ZipFile(zip_path, 'r') as my_zip:
            my_zip.extractall(true_mod_folder)
        print("Files extracted sakseufllly")
    except FileNotFoundError:
        print("archive not found")

    try:
        zip_path.unlink()
        print("Deleting leftover file for cleanup")
    except FileNotFoundError:
        print("Mods.zip not found")


if __name__ == "__main__":
    main()
