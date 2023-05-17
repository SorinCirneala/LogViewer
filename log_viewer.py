import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfile
import sys
import re
import os

class LogViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        # initialize variables
        self.keywords = ["version", "Start", "Finished"]
        py_version = f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}" 
        self.window_title = tk.StringVar(value=f"Log Viewer (Python {py_version})")
        self.kw_list = tk.StringVar(value=self.keywords)
        # TODO: remove default loaded file (for testing only)
        # self.log_path = tk.StringVar(value="general\\log_viewer\\log_samples\\a_navigation.log")
        self.log_path = tk.StringVar()
        self.last_log_path = tk.StringVar(value="")
        self.kw_path = tk.StringVar(value="")
        self.script_dir = sys.path[0]
        self.kw_locations = []
        self.case_sensitive = tk.BooleanVar(value=False)
        self.all_kw = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value="Log not loaded")
        self.search_string = tk.StringVar(value="service") # TODO: remove, for testing only
        self.string_locations = []
        self.current_loc = ('1.0', '1.0')
        # initialize UI
        self.init_container()
        self.init_left_frame()
        self.init_right_frame()
        self.init_status()

    def init_container(self):
        # configure main window 
        self.title(self.window_title.get())
        self.minsize(800, 600)
        self.geometry("1000x600+100+100")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # configure container frame
        self.container = tk.Frame(self)
        self.container.grid(row=0, column=0, sticky="NSEW")
        self.container.columnconfigure(1, weight=1)
        self.container.rowconfigure(0, weight=1)

    def init_left_frame(self):
        # configure and place frame
        left = tk.Frame(self.container, borderwidth=1, relief="groove")
        left.grid(row=0, column=0, sticky="NSEW", ipadx=5, ipady=5, padx=5, pady=5)
        left.columnconfigure((0,1,2,3), weight=1)
        # configure widgets
        open_btn = tk.Button(left, text="Select file", command=self.select_file)
        kw_label = tk.Label(left, text="Manage keywords", bg="#096e8d", fg="#ffe599")
        kw_add = tk.Button(left, text="Add KW", fg="#224c9b", command=self.add_kw)
        kw_remove = tk.Button(left, text="Del KW", fg="#224c9b", command=self.remove_kw)
        kw_load = tk.Button(left, text="Load", fg="green", command=self.load_kw)
        kw_save = tk.Button(left, text="Save", fg="green", command=self.save_kw)
        self.kw_box = tk.Listbox(left, listvariable=self.kw_list, selectmode="extended", width=35, height=14,
                        exportselection=False, selectbackground="#096e8d", selectforeground="#ffe599", 
                        activestyle="none")
        case_sensitive_chk = tk.Checkbutton(left, text="Case Sensitive", variable=self.case_sensitive)
        all_kw_chk = tk.Checkbutton(left, text="Apply ALL Selected", variable=self.all_kw)
        filter_log_btn = tk.Button(left, text="Filter log", command=self.filter_lines)
        clear_btn = tk.Button(left, text="Clear filters", command=self.clear_filters)
        export_bnt = tk.Button(left, text="Export results", command=self.export_logbox)
        search_label = tk.Label(left, text="Search within results", bg="#db504a", fg="#fff2cc" )
        search_entry = tk.Entry(left, textvariable=self.search_string)
        search_btn = tk.Button(left, text="Search", command=self.search)
        self.see_prev_btn = tk.Button(left, text="<<<", command=self.see_previous)
        self.see_prev_btn.configure(state="disabled")
        self.see_next_btn = tk.Button(left, text=">>>", command=self.see_next)
        self.see_next_btn.configure(state="disabled")

        # place widgets
        open_btn.grid(row=0, column=0, sticky="EW", pady=(0,10), columnspan=4)
        kw_label.grid(row=1, column=0, columnspan=4, ipadx=2, ipady=2, sticky="EW")
        kw_add.grid(row=2, column=0, sticky="EW")
        kw_remove.grid(row=2, column=1, sticky="EW")
        kw_save.grid(row=2, column=2, sticky="EW")
        kw_load.grid(row=2, column=3, sticky="EW")
        self.kw_box.grid(row=3, column=0, sticky="EW", columnspan=4)
        case_sensitive_chk.grid(row=4, column=0, sticky="W", pady=(5,0), columnspan=4)
        all_kw_chk.grid(row=5, column=0, sticky="W", pady=(5,5), columnspan=4)
        filter_log_btn.grid(row=6, column=0, sticky="EW", pady=(0,0), columnspan=2)
        clear_btn.grid(row=6, column=2, sticky="EW", pady=(0,0), columnspan=2)
        export_bnt.grid(row=7, column=0, sticky="EW", pady=(0,10), columnspan=4)
        search_label.grid(row=8, column=0, columnspan=4, ipadx=2, ipady=2, sticky="EW")
        search_entry.grid(row=9, column=0, sticky="EW", pady=(0,0), columnspan=4)
        search_btn.grid(row=10, column=0, sticky="EW", pady=(0,0), columnspan=4)
        self.see_prev_btn.grid(row=11, column=0, sticky="EW", pady=(5,0), columnspan=2)
        self.see_next_btn.grid(row=11, column=2, sticky="EW", pady=(5,0), columnspan=2)

    def init_right_frame(self): 
        # configure and place frame   
        right = tk.Frame(self.container, borderwidth=1, relief="groove")
        right.grid(row=0, column=1, sticky="NSEW", ipadx=5, ipady=5, padx=5, pady=5)
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)
        # configue and place widgets
        self.log_box = tk.Text(right, font=("Consolas", 10), exportselection=False)
        self.log_box.grid(row=0, column=0, sticky="NSEW", padx=5, pady=5)
        # lock the widget to prevent editing
        self.log_box.configure(state="disabled")
        # add vertical scrollbar
        box_scroll_y = tk.Scrollbar(right, orient="vertical", command=self.log_box.yview)
        box_scroll_y.grid(row=0, column=1, sticky="NS")
        self.log_box.configure(yscrollcommand=box_scroll_y.set)
        # add horizontal scrollbar
        box_scroll_x = tk.Scrollbar(right, orient="horizontal", command=self.log_box.xview)
        box_scroll_x.grid(row=1, column=0, sticky="EW")
        self.log_box.configure(xscrollcommand=box_scroll_x.set)

    def init_status(self):
        self.status_bar = tk.Label(self.container, textvariable=self.status, bd=1, relief="sunken", anchor="w")
        self.status_bar.grid(row=1, column=0, sticky="EW", columnspan=2, padx=5, pady=5)

    # handler methods
    def select_file(self):
        # unlocks the text widget, clears the previous text, inserts new text, locks the text widget
        self.log_box.configure(state="normal")
        self.log_box.delete(1.0, "end")
        self.set_status("Loading file...")
        if self.last_log_path.get() == "": # open the last path used for selecting logs
            self.log_path.set(askopenfilename(filetypes = [("All files", "*.*")]))
        else:
            self.log_path.set(askopenfilename(filetypes = [("All files", "*.*")], initialdir=self.last_log_path.get()))
        try:
            with open(self.log_path.get(), "r", errors="ignore") as fn:
                line_count = 0
                for line in fn.readlines():
                    self.log_box.insert("end", line)
                    line_count += 1
            self.log_box.configure(state="disabled")
            self.set_status(f"Loaded {line_count:,d} lines from {self.log_path.get()}")
            self.title(f"Log Viewer - {self.log_path.get()}")
        except FileNotFoundError:
            self.set_status("Log not loaded", "e")
        except UnicodeDecodeError as e:
            self.set_status(f"Unsupported character found: {str(e)}", "e")
        finally:
            folder_path = os.path.split(self.log_path.get())[0] # get the path from previously selected log
            self.last_log_path.set(folder_path) # store it to use when opening another log file

    def filter_lines(self):
        if self.log_path.get() == "":
            self.set_status("Load a log file to apply filter", "e")
            return
        # unlocks widget, clears the content, adds only the lines that match the filter, locks the widget
        try: 
            selected_kw = [self.keywords[i] for i in self.kw_box.curselection()]
            if not selected_kw:
                self.set_status("Select a keyword to apply a filter", "e")
                return
            status_line_counter = 0
            status_kw_counter = 0
            self.log_box.configure(state="normal") # unlock and clear the log_box
            self.log_box.delete(1.0, "end")
            with open(self.log_path.get(), "r", errors="ignore") as fn:
                found_kw = 0
                row_no = 1 # for Tkinter tag: row index, it starts from 1
                for line in fn.readlines(): # parse each log line
                    matches = []
                    for i, kw in enumerate(selected_kw): # check each kw using re.finditer()
                        if self.case_sensitive.get(): # use different match patterns when case-sensitive flag is ON/OFF
                            match_list = list(re.finditer(kw, line)) # finditer returns match obj. with start/end prop.
                        else:
                            match_list = list(re.finditer(kw, line, flags=re.IGNORECASE))
                        if len(match_list) > 0: # store match objects in the list of matches
                            matches.extend(match_list)
                            found_kw += 1
                    if self.all_kw.get(): # check all_kw Bool, use different condition to insert line to log_box
                        if len(matches) > 0 and len(selected_kw) == found_kw: # check matches list and how many found_kw
                            self.log_box.insert("end", line) # insert the line in log_box
                            for match in matches: # get the MO locations and store them to apply the color tag later
                                self.kw_locations.append((f"{row_no}.{match.start()}", f"{row_no}.{match.end()}"))
                                status_kw_counter += 1
                            status_line_counter += 1 
                            row_no += 1
                    else: # same actions as above, only the condition is different, TODO: create method to avoid repeat
                        if len(matches) > 0:
                            self.log_box.insert("end", line) 
                            for match in matches:
                                self.kw_locations.append((f"{row_no}.{match.start()}", f"{row_no}.{match.end()}"))
                                status_kw_counter += 1
                            status_line_counter += 1 
                            row_no += 1
                    found_kw = 0 # reset the number of found_kw after the line is parsed
            for location in self.kw_locations: # apply tag to each location
                self.set_tag("filter_kw", location[0], location[1])
            self.kw_locations.clear() # clear the kw locations to prepare for next filter
            self.log_box.configure(state="disabled") # lock the log_box
            self.set_status(f"Lines found: {status_line_counter}. Keywords found: {status_kw_counter}")
        except Exception as e:
            self.set_status(f"Error: {str(e)}", "e")

    def clear_filters(self):
        # unlocks widget, clear the content, display the original file, lock the widget
        try:
            self.log_box.configure(state="normal")
            self.log_box.delete(1.0, "end")
            with open(self.log_path.get(), "r", errors="ignore") as fn:
                for line in fn.readlines():
                    self.log_box.insert("end", line)
            self.log_box.configure(state="disabled")
            self.set_status("Filters cleared")
        except FileNotFoundError:
            self.set_status("Log not loaded", "e")

    def add_kw(self):
        popup = tk.Toplevel(self)
        popup.title("Enter filter text")
        popup.minsize(250, 80)
        popup.resizable(True, False)
        popup.focus()
        popup.attributes("-topmost", "true") # keep window on top
        # popup.configure(background="SlateGray1")
        popup.rowconfigure(0, weight=1)
        popup.columnconfigure(0, weight=1)
        popup.columnconfigure(1, weight=1)
        popup.grab_set() # popup grabs the focus

        new_kw = tk.StringVar(value="")
        
        def add(event=None): # event=None required to use method for both button and key binding
            if new_kw.get() == "":
                self.set_status("Empty keyword: cannot add", "e")
            elif new_kw.get() in self.keywords:
                self.set_status(f"Duplicate keyword: {new_kw.get()}", "e")
            else:
                self.keywords.append(new_kw.get())
                self.kw_list.set(self.keywords)
                popup.grab_release() # release focus before closing popup
                popup.destroy()
                self.set_status(f"Keyword added: {new_kw.get()}")

        def cancel(event=None):
            self.set_status("Add operation cancelled")
            popup.grab_release()
            popup.destroy()

        # bind events
        popup.bind("<Return>", add)
        popup.bind("<Escape>", cancel)

        # configure widgets
        field = tk.Entry(popup, textvariable=new_kw)
        field.focus() # places cursor in the entry field
        add_button = tk.Button(popup, text="Add", width=10, command=add)
        cancel_button = tk.Button(popup, text="Cancel", width=10, command=cancel)

        # place widgets
        field.grid(row=0, column=0, padx=10, pady=5, columnspan=2, sticky="EW")
        add_button.grid(row=1, column=0, padx=10, pady=5, sticky="EW")
        cancel_button.grid(row=1, column=1, padx=10, pady=5, sticky="EW")

    def remove_kw(self):
        selected_kw = [self.keywords[i] for i in self.kw_box.curselection()]
        if len(selected_kw) < 1:
            self.set_status("No keyword selected: cannot remove", "e")
        else:
            for kw in selected_kw:
                self.keywords.remove(kw)
                self.set_status(f"Keyword removed: {kw}")
            self.kw_list.set(self.keywords)
    
    def load_kw(self):
        self.kw_path.set(askopenfilename(filetypes = [("Keyword files", "*.kw")], initialfile="my_keywords.kw",
                    initialdir=self.script_dir))
        try: 
            with open(self.kw_path.get(), "r", errors="ignore") as fn:
                self.keywords.clear()
                for line in fn.readlines():
                    self.keywords.append(line.strip())
                self.kw_list.set(self.keywords)
            self.set_status(f"Keywords loaded: {self.kw_path.get()}")
        except FileNotFoundError:
            self.set_status("Keyword loading cancelled")

    def save_kw(self):
        out_file = asksaveasfile(mode="w", confirmoverwrite=True, title="Save current keywords", 
                    initialfile="my_keywords.kw", filetypes = [("Keyword files", "*.kw")], initialdir=self.script_dir)
        if out_file == None:
            self.set_status("Keyword saving cancelled")
        else:
            for kw in self.keywords:
                out_file.write(kw)
                out_file.write("\n")
            out_file.close()
            self.set_status(f"Keywords saved to: {out_file.name}")

    def export_logbox(self):
        if len(self.kw_locations) == 0:
            self.set_status("Nothing to export", "e")
            return
        else:
            out_file = asksaveasfile(mode="w", confirmoverwrite=True, title="Export log", 
                        initialfile="filtered_log.txt", filetypes = [("Text file", "*.txt")])
            if out_file == None:
                self.set_status("Export log cancelled")
            else:
                # end-1c removes an empty line at the end of the file
                out_file.writelines(self.log_box.get("1.0", "end-1c"))
                out_file.close()
                self.set_status(f"Log exported to: {out_file.name}")

    def search(self):
        # reset previous search results
        self.string_locations = []
        self.log_box.tag_delete("search_result")
        # get search string, get textbox content
        search_string = self.search_string.get()
        if search_string == "":
            self.set_status("Enter a search string to use Search", "e")
            return
        tb_content = self.log_box.get("1.0", "end")
        # populate list with result coordinates
        row_no = 1
        # all_matches = []
        for line in tb_content.splitlines():
            matches_on_line = list(re.finditer(search_string, line))
            if len(matches_on_line) > 0:
                for match in matches_on_line:
                    self.string_locations.append((f"{row_no}.{match.start()}", f"{row_no}.{match.end()}"))
                row_no += 1 # increment row number after current row matches have been added to the list
            else: 
                row_no += 1 # increment row number when no matches were found on the line
        # apply color tag to each location
        self.set_status(f"Found {len(self.string_locations)} result(s)")
        for location in self.string_locations:
                self.set_tag("search_result", location[0], location[1])
        # jump to first location
        try:
            self.log_box.see(self.string_locations[0][0])
        except IndexError:
            self.set_status("Filter the log to use Search", "e")
        # check if locations are found, set current_loc to first item in the list, enable next and previous buttons
        if len(self.string_locations) > 0:
            self.see_next_btn.configure(state="normal")
            self.see_prev_btn.configure(state="normal")
            self.current_loc = self.string_locations[0]

    def see_next(self):
        # delete previously set color tags
        self.log_box.tag_delete("selected")
        # get current location index, will be used to move to next, apply tag and jump to row
        idx = self.string_locations.index(self.current_loc)
        if idx < len(self.string_locations) - 1:
            self.current_loc = self.string_locations[idx + 1]
            self.log_box.see(self.current_loc[0])
            self.set_tag("selected", self.current_loc[0], self.current_loc[1])
        else: # move to first index if user reaches the last position
            self.current_loc = self.string_locations[0]
            self.log_box.see(self.current_loc[0])
            self.set_tag("selected", self.current_loc[0], self.current_loc[1])
            
    def see_previous(self):
        # delete previously set color tags
        self.log_box.tag_delete("selected")
        # get current location index, will be used to move to previous, apply tag and jump to row
        idx = self.string_locations.index(self.current_loc)
        if idx > 0:
            self.current_loc = self.string_locations[idx - 1]
            self.log_box.see(self.current_loc[0])
            self.set_tag("selected", self.current_loc[0], self.current_loc[1])
        else: # move to last index if user reaches the first position
            self.current_loc = self.string_locations[-1]
            self.log_box.see(self.current_loc[0])
            self.set_tag("selected", self.current_loc[0], self.current_loc[1])

    def set_tag(self, tag, start, end):
        # configure all tags for highlighting text
        self.log_box.tag_configure("filter_kw", foreground="#ffe599", background="#096e8d")
        self.log_box.tag_configure("search_result", foreground="#fff2cc", background="#db504a")
        self.log_box.tag_configure("selected", foreground="#d51b13", background="#fff2cc")
        # set tag
        self.log_box.tag_add(tag, start, end)

    def set_status(self, message, level=None):
        # sets status color to red if the message is an error
        if level == "e":
            self.status.set(message)
            self.status_bar.configure(fg="red")
        else:
            self.status.set(message)
            self.status_bar.configure(fg="black")


root = LogViewer()
root.mainloop()
