from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import httpx, zipfile
from typing import Optional

class ParakeetUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Parakeet")
        self.root.geometry("460x500")
        self.root.minsize(460,500)
        self.root.configure(bg="#202020")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.bg_dark = "#303030"
        self.bg_darker = "#232323"
        self.fg_color = "#FFFFFF"
        self.accent_color = "#4CAF50"

        self.server_mod = {"aeaver":"https://raw.githubusercontent.com/aeaver/parakeet/refs/heads/main/aeaver.json",
                            "krabu":"https://raw.githubusercontent.com/aeaver/parakeet/refs/heads/main/krabu.json"}
        self.launcher_path = list(self.find_path())
        self.launcher_names = [name for name, path in self.launcher_path]

        self.selected_launcher_path = None
        self.instance_path = []
        self.instance_names = []

        self.mod_folder:Optional[Path]=None

        self.setup_ui()

    def setup_ui(self):
        self.topframe = tk.Frame(self.root,bg=self.bg_dark)
        self.topframe.grid(row=0,column=0,sticky="nsew")
        self.topframe.rowconfigure(4,weight=1)
        self.topframe.columnconfigure(0,weight=1)


        self.toplabel = tk.Label(
            self.topframe,
            text="Parakeet",
            justify="right",
            bg=self.bg_darker,
            fg=self.fg_color,
            font=("Consolas", 15, "bold"),
            anchor="center",
            padx=5
        )

        self.toplabel.grid(row=0, column=0, pady=(10, 5), sticky="ew", columnspan=2, padx=10)

        self.launcherframe = tk.Frame(self.topframe,bg=self.bg_dark)
        self.launcherframe.grid(row=1,column=0,sticky="ew",columnspan=2,padx=10)
        self.launcherframe.columnconfigure(1, weight=1)

        # SERVER SELECTOR

        tk.Label(self.launcherframe,text="Server   :", bg=self.bg_dark, fg=self.fg_color, font=("Consolas",10)).grid(
            row=0,column=0,sticky="w",padx=5,pady=5)

        self.server_combo = ttk.Combobox(
            self.launcherframe,
            values=list(self.server_mod),
            state="readonly",
            width=15
        )
        self.server_combo.grid(row=0,column=1,sticky="ew",padx=5,pady=5)

        # LAUNCHER SELECTOR

        tk.Label(self.launcherframe,text="Launcher :", bg=self.bg_dark, fg=self.fg_color, font=("Consolas",10)).grid(
            row=1,column=0,sticky="w",padx=5,pady=5)

        self.launcher_combo = ttk.Combobox(
            self.launcherframe,
            values=self.launcher_names,
            state="readonly",
            width=15
        )
        self.launcher_combo.grid(row=1,column=1,sticky="ew",padx=5,pady=5)

        self.launcher_combo.bind("<<ComboboxSelected>>", self.on_select_launcher)

        # INSTANCE SELECTOR

        tk.Label(self.launcherframe,text="Instance :", bg=self.bg_dark, fg=self.fg_color,font=("Consolas",10) ).grid(
            row=2,column=0,sticky="w",padx=5,pady=5)

        self.instance_combo = ttk.Combobox(
            self.launcherframe,
            state="readonly",
            width=15
        )
        self.instance_combo.grid(row=2,column=1,sticky="ew",padx=5,pady=5)
        self.instance_combo.bind("<<ComboboxSelected>>", self.find_mod)

        self.update_button = tk.Button(
            self.topframe,
            text="Update",
            bg=self.accent_color,
            fg="white",
            font=("Consolas", 11, "bold"),
            command=self.update_instance_mod,
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=8
        )
        self.update_button.grid(row=2, column=0, pady=10, sticky="ew", columnspan=2, padx=10)

        self.midframe = tk.Frame(self.topframe,bg=self.bg_darker)
        self.midframe.grid(row=4,column=0,pady=(5,10), sticky="nsew", columnspan=2, padx=10)
        self.midframe.rowconfigure(1,weight=1)

        self.midlabel = tk.Label(
            self.midframe,
            text="Status/Log Area:",
            bg=self.bg_darker,
            fg=self.fg_color,
            font=("Consolas", 9, "bold"),
            anchor="w",
            padx=5
        )
        self.midlabel.grid(row=0, column=0, pady=(5, 5), sticky="ew", padx=5)

        text_frame = tk.Frame(self.midframe, bg=self.bg_darker)
        text_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.output_text = tk.Text(
            text_frame,
            height=12,
            bg="#1a1a1a",
            fg="#00FF00",
            font=("Consolas", 9),
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        self.output_text.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(text_frame, command=self.output_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.output_text.config(yscrollcommand=scrollbar.set)

        self.log("READ THIS PLEASE!!!!!!!!!!!!")
        self.log("Please select your launcher & instance")
        self.log("Select from dropbox above")

        self.output_text.config(state=tk.DISABLED)

    def log(self, message):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"> {message}\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def find_path(self):
        homepath = Path.home()
        location = {
            "PrismLauncher": homepath / "AppData"/"Roaming"/"PrismLauncher"/"instances",
            "CurseForge": homepath / "curseforge"/ "minecraft" / "Instances",
            "Legacy Launcher": homepath / "AppData"/ "Roaming" / ".tlauncher"
        }

        for name,path in location.items():
            if path.exists():
                yield (name,path)

    def on_select_launcher(self,event):
        selected_launcher_name = self.launcher_combo.get()

        for name,path in self.launcher_path:
            if name == selected_launcher_name:
                self.selected_launcher_path = (name,path)
                print(self.selected_launcher_path)
                break
        else:
            return

        if not self.selected_launcher_path[0] == "Legacy Launcher":
            self.instance_path = list(self.find_instance(self.selected_launcher_path))
            self.instance_map = {path.name : path for _,path in self.instance_path}
            self.instance_name = list(self.instance_map.keys())
            self.instance_combo['values'] = self.instance_name
        elif self.selected_launcher_path[0] == "Legacy Launcher":
            name,path = self.selected_launcher_path
            self.instance_map = {name : path}
            self.instance_name = list(self.instance_map.keys())
            self.instance_combo['values'] = self.instance_name
        else:
            self.log("error")

    def find_instance(self,selected_launcher_path,):

        label, paths = selected_launcher_path

        for path in paths.iterdir():
            if path.is_dir():
                yield label, path

    def find_mod(self,event):

        selected_name = self.instance_combo.get()
        print(selected_name)
        if not selected_name:
            return None

        # Use the instance_map to get the full path
        path = self.instance_map[selected_name]
        label, _ = self.selected_launcher_path  # ty:ignore[not-iterable]

        for paths in path.iterdir():
            if paths.is_dir():
                pass

        if label == "PrismLauncher":
            dot_minecraft = paths / ".minecraft"
            if dot_minecraft.exists() and dot_minecraft.is_dir():
                target_dir = dot_minecraft / "mods"
                print('hello')
            else:
                target_dir = path / "minecraft" / "mods"
        elif label =="CurseForge":
            target_dir = path / "mods"
        elif label =="Legacy Launcher":
            target_dir = path / "legacy" / "Minecraft" / "game" / "mods"
            print(path)
            print("this is targer dir : " ,target_dir)
        else:
            return None

        if not target_dir.exists():
            target_dir.mkdir(exist_ok=True,parents=True)
            print(f"Created : {target_dir}")

        self.mod_folder = target_dir
        return target_dir

    def update_instance_mod(self):
        if self.mod_folder is None:
            self.log("Please Select Instance first!")
            return

        if not self.server_combo.get():
            self.log("Please Select server first!")
            return

        if self.server_combo.get() == "aeaver":
            url = "https://raw.githubusercontent.com/aeaver/parakeet/refs/heads/main/aeaver.json"
        elif self.server_combo.get() == "krabu":
            url = "https://raw.githubusercontent.com/aeaver/parakeet/refs/heads/main/krabu.json"
        else:
            return None

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Parakeet/1.0'}

        self.update_button.config(state=tk.DISABLED, text="Updating...")

        try:
            with httpx.Client(headers=headers,timeout=15,follow_redirects=True) as session:
                json_request = session.get(url)
                json_request.raise_for_status()
                manifest = json_request.json()

                mod_list = manifest["target_mod"]
                file_download_url = manifest["download_url"]

                destination_filename = "mods.zip"
                download_location = self.mod_folder / destination_filename

                self.log(f"Downloading mods...")
                self.root.update()


                ##get_download = session.get(file_download_url, stream=True)
                with session.stream("GET",file_download_url) as get_download:
                    total_size = int(get_download.headers.get('content-length', 0))
                    downloaded = 0

                    if get_download.status_code == 200:
                        with open(download_location, "wb") as f:
                            for chunk in get_download.iter_bytes(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    if downloaded % (1024 * 1024) < 8192:
                                        mb_downloaded = downloaded / (1024 * 1024)
                                        self.log(f"Downloaded: {mb_downloaded:.1f} MB")
                                        self.root.update()
                            self.log("Download completed")
                    else:
                        self.log(f"Download failed. Status code : {get_download.status_code}")


            for pattern in mod_list:
                for old_mod in self.mod_folder.glob(pattern):
                    try:
                        old_mod.unlink()
                        self.log(f"removed {old_mod}")
                    except Exception as e:
                        self.log(f" Failed to remove {old_mod}: {e}")

            with zipfile.ZipFile(download_location, 'r') as my_zip:
                my_zip.extractall(self.mod_folder)
            self.log("Files extracted successfully")

            download_location.unlink()
            self.log("Deleting leftover file for cleanup")

        except zipfile.BadZipFile:
            self.log("Downloaded file is not a valid zip archive")
        except FileNotFoundError:
            self.log("Mod folder not found")
        except httpx.HTTPError as e:
            self.log(f"Failed to get manifest: {e}")
        except Exception as e:
            self.log(f"Unexpected error: {e}")

        self.log("Update completed, Close the damn thing now")

        self.update_button.config(text="Update",state=tk.NORMAL)


    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ParakeetUI()
    app.run()
