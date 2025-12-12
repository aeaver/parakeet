import zipfile, requests
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
            yield path

def find_mod(mod_path):

    prism = mod_path/ "minecraft" / "mods"
    if prism.exists():
        return prism

    curse = mod_path / "mods"
    if curse.exists():
        return curse

    if (mod_path/ "minecraft").exists():
        prism.mkdir(parents=True)
        return prism
    else:
        curse.mkdir(parents=True)
        return curse

def update_instance_mod(mod_folder_path, manifest, session):

    mod_list = manifest["target_mod"]
    file_download_url = manifest["download_url"]
    destination_filename = "mods.zip"
    print(f"Downloading mods...")
    get_download = session.get(file_download_url)
    download_location = mod_folder_path / destination_filename

    if get_download.status_code == 200:
        with open(download_location, "wb") as f:
            f.write(get_download.content)
        print("Download completed")
    else:
        print(f"Download failed. Status code : {get_download.status_code}")

    for pattern in mod_list:
        for old_mod in mod_folder_path.glob(pattern):
            try:
                old_mod.unlink()
                print(f"removed {old_mod}")
            except Exception as e:
                print(f" Failed to remove {old_mod}: {e}")

    try:
        with zipfile.ZipFile(download_location, 'r') as my_zip:
            my_zip.extractall(mod_folder_path)
        print("Files extracted successfully")
    except FileNotFoundError:
        print("archive not found")

    try:
        download_location.unlink()
        print("Deleting leftover file for cleanup")
    except FileNotFoundError:
        print("Mods.zip not found")

def main():
    #get Launcher
    available_path = list(find_path())
    
    print("Welcome to parakeet, before we proceed please make sure to make a minecraft instance in your launcher")
    print("Pick the number based on your minecraft launcher and your minecraft instance name")
    print("This program will automatically install the required mod to join the server\n")

    if not available_path:
        print("No Path to minecraft instance has been found")

    counter = 1
    for launcher,paths in available_path:
        print(f"[{counter}]. {launcher} : {paths}")
        counter+=1

    while True:
        try:
            chosenPathLauncher = int(input("\nSelect Your launcher (Enter number based on the list above and press enter to submit): \n"))
            if 1 <= chosenPathLauncher <= len(available_path):
                break
            print(f"Please enter number between 1 and {len(available_path)}")
        except ValueError:
            print("Bodoh ke? Numbers only")


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
            Chosen_Mod_Folder = int(input("\nPick Your minecraft instance (Enter number based on the list):"))
            if 1 <= Chosen_Mod_Folder <= len(ver_folder_path):
                break
            print(f"Please enter number between 1 and {len(ver_folder_path)}")
        except ValueError:
            print("Are you fucking stupid??? Numbers only")

    Choosed_Mod_Folder = ver_folder_path[Chosen_Mod_Folder-1]
    mod_path = Choosed_Mod_Folder

    mod_folder_path = find_mod(mod_path)

    url = "https://raw.githubusercontent.com/aeaver/parakeet/refs/heads/main/manifest.json"

    try:
        with requests.Session() as session:
            json_request = session.get(url)
            json_request.raise_for_status()
            manifest = json_request.json()
    except requests.RequestException as e:
        print(f" failed to get manifest : {e}")
        return

    update_instance_mod(mod_folder_path, manifest, session)
    print("Update complete")
    input("Press Enter to close...")

if __name__ == "__main__":
    main()
