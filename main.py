from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import requests, zipfile
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
            text="Launcher:", 
            bg=self.bg_darker,
            fg=self.fg_color,
            font=("Arial", 10, "bold"),
            anchor="w",
            padx=5
        )
        
        self.toplabel.grid(row=0, column=0, pady=(10, 5), sticky="ew", columnspan=2, padx=10)
        
        self.launcherframe = tk.Frame(self.topframe,bg=self.bg_dark)
        self.launcherframe.grid(row=1,column=0,sticky="ew",columnspan=2,padx=10)
        self.launcherframe.columnconfigure(1, weight=1)
        
        tk.Label(self.launcherframe,text="Launcher :", bg=self.bg_dark, fg=self.fg_color).grid(
            row=0,column=0,sticky="w",padx=5,pady=5)
        
        self.launcher_combo = ttk.Combobox(
            self.launcherframe,
            values=self.launcher_names,
            state="readonly",
            width=15
        )
        self.launcher_combo.grid(row=0,column=1,sticky="ew",padx=5,pady=5)
        
        self.launcher_combo.bind("<<ComboboxSelected>>", self.on_select_launcher)
        
        tk.Label(self.launcherframe,text="Instance :", bg=self.bg_dark, fg=self.fg_color).grid(
            row=1,column=0,sticky="w",padx=5,pady=5)
        
        self.instance_combo = ttk.Combobox(
            self.launcherframe,
            state="readonly",
            width=15
        )
        self.instance_combo.grid(row=1,column=1,sticky="ew",padx=5,pady=5)
        self.instance_combo.bind("<<ComboboxSelected>>", self.find_mod)
        
        self.update_button = tk.Button(
            self.topframe,
            text="Update",
            bg=self.accent_color,
            fg="white",
            font=("Arial", 11, "bold"),
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
            font=("Arial", 9, "bold"),
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
        
        self.log("Parakeet Launcher initialized")
        self.log("Ready to launch...")

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
            "CurseForge": homepath / "curseforge"/ "minecraft" / "Instances"
        }
    
        for name,path in location.items():
            if path.exists():
                yield (name,path)
                
    def on_select_launcher(self,event):
        selected_launcher_name = self.launcher_combo.get()
        
        for name,path in self.launcher_path:
            if name == selected_launcher_name:
                self.selected_launcher_path = (name,path)
                self.log(f"{name} and {path}")
                break
        else:
            self.log("bzamsdas")
            return
            
        self.instance_path = list(self.find_instance(self.selected_launcher_path))

        
        self.instance_map = {path.name : path for _,path in self.instance_path}
        self.instance_name = list(self.instance_map.keys())
        self.instance_combo['values'] = self.instance_name

    def find_instance(self,selected_launcher_path,):
        
        label, paths = selected_launcher_path
    
        for path in paths.iterdir():
            if path.is_dir():
                yield label, path
                
    def find_mod(self,event):
        
        selected_name = self.instance_combo.get()
        if not selected_name:
            return None
    
        # Use the instance_map to get the full path
        path = self.instance_map[selected_name]
        label, _ = self.selected_launcher_path  # ty:ignore[not-iterable]
        
        if label == "PrismLauncher":
            target_dir = path / "minecraft" / "mods"
        elif label =="CurseForge":
            target_dir = path / "mods"
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
        
        url = "https://raw.githubusercontent.com/aeaver/parakeet/refs/heads/main/manifest.json"
    
        try:
            with requests.Session() as session:
                json_request = session.get(url)
                json_request.raise_for_status()
                manifest = json_request.json()
                
                mod_list = manifest["target_mod"]
                file_download_url = manifest["download_url"]
                
                destination_filename = "mods.zip"
                download_location = self.mod_folder / destination_filename #ty:ignore
                
                self.log(f"Downloading mods...")
                self.root.update()
                
                get_download = session.get(file_download_url, stream=True)
                
                total_size = int(get_download.headers.get('content-length', 0))
                downloaded = 0
                
                if get_download.status_code == 200:
                    with open(download_location, "wb") as f:
                        for chunk in get_download.iter_content(chunk_size=8192):
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
                for old_mod in self.mod_folder.glob(pattern): #ty:ignore
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
        except requests.RequestException as e:
            self.log(f"Failed to get manifest: {e}")
        except Exception as e:
            self.log(f"Unexpected error: {e}")
            
        self.log("Update completed, Close the damn thing now")
        
        
    def run(self):
        self.root.mainloop()
        
if __name__ == "__main__":
    app = ParakeetUI()
    app.run()