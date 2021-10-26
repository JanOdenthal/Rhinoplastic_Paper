#Added by Jan Odenthal, University of Heidelberg,  odenthal@stud.uni-heidelberg.de
#Commissioned by Universitätsklinikum Heidelberg, Klinik für Allgemein-, Viszeral- und Transplantationschirurgie

from HyperGuiModules.utility import *
from HyperGuiModules.constants import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw
import numpy as np
import os
import glob
import shutil
from distutils.dir_util import copy_tree
import csv



class BP:
    def __init__(self, bp_frame):
        self.root = bp_frame
        
        #Lists
        self.data_cube_paths = []
        self.sub_dirs = []
        
        # GUI
        self.select_data_cube_button = None
        self.select_output_dir_button = None
        self.render_data_cube_button = None
        self.selection_listbox = None
        self.data_cube_path_label = None
        self.output_dir_label = None
        self.delete_button = None
        self.data_cube_path_label = None
        self.path_label = None
        self.save_label = None

        self.original_image_graph = None
        self.original_image_data = None
        self.original_image = None
        self.image_array = None

        self.original_image_graph_r = None
        self.original_image_data_r = None
        self.original_image_r = None
        self.image_array_r = None

        self.tif_save_path_end = None
        self.current_dc_path = None
        
        self.mask_raw = None
    
        self.idx_dict = dict({0:0})
        self.image_width = 640
        
        self._init_widget()


    # ---------------------------------------------- UPDATER AND GETTERS ----------------------------------------------
        

    def get_selected_data_cube_path(self):
        index = self.selection_listbox.curselection()[0]
        return self.data_cube_paths[index]

    def get_selected_data_paths(self):
        selection = self.selection_listbox.curselection()
        selected_data_paths = [self.data_cube_paths[self.idx_dict[i]] for i in selection]
        return selected_data_paths

    def update_original_image(self, original_image_data):
        self.original_image_data = original_image_data
        self._build_original_image(self.original_image_data)
        self._draw_points()
        
    def __update_selected_data_cube(self, event):
        if len(self.selection_listbox.curselection())>0:
            dc_path = self.get_selected_data_cube_path()
            if self.current_dc_path is not self.selection_listbox.curselection()[0]:
                if len(self.selection_listbox.curselection())>0:
                    self.current_dc_path = self.selection_listbox.curselection()[0]
        else:
            dc_path = self.data_cube_paths[0]
            self.current_dc_path = 0
        img = Image.open(dc_path)
        self.data1 = np.array(img)
        self._build_original_image_left(self.data1)
        self.original_image_data = self.data1 
        self.image_width = self.data1.shape[1]
        self.coords_list = [(None, None), (None, None), (None, None), (None, None)]
        filename = os.path.basename(dc_path)
        path = os.path.dirname(dc_path) + "/annotated/" + filename[:-4] + "_COORDINATES.csv"
        print("searching in " + path)
        if os.path.exists(path):
            with open(path) as csvfile:
                coords = []
                print("reading mask")
                read_csv = csv.reader(csvfile, delimiter=',')
                for row in read_csv:
                    coords.append(((int(float(row[0]) - 1)), (int(float(row[1]) - 1))))
                csvfile.close()
                self.coords_list = [point if point[0] >=0 else (None, None) for point in coords]
            self._draw_points()
            
        
    # ------------------------------------------------ INITIALIZATION ------------------------------------------------

    def _init_widget(self):
        self._build_selection_box()
        self._build_original_image_left(self.original_image_data)
        #self._build_select_superdir_button()
        self._build_select_all_subfolders_button()
        self._build_trash_button()
        self._build_counter(0)
        
    # ----------------------------------------------- BUILDERS (MISC) -----------------------------------------------
        
    def _build_trash_button(self):
        self.trash_button = make_button(self.root, text='Clean List', width=9, command=self.__trash_list,
                                               row=26, column=1, columnspan=1, inner_pady=5, outer_padx=0,
                                               outer_pady=(10, 15))


    def _build_select_superdir_button(self):
        self.select_data_cube_button = make_button(self.root, text="Open OP\nFolder",
                                                   command=self.__add_data_cube_dirs, inner_padx=10, inner_pady=10,
                                                   outer_padx=15, row=25, rowspan = 1, column=0, width=11, outer_pady=(5, 5))
    def _build_labelling_entry(self):
        labelling_text = make_text(self.root, content = "File-Filter:", row=24, column=0, width=14, bg=tkcolour_from_rgb((BACKGROUND)), padx=0, state=NORMAL, pady=0) 
        self.labelling_entry = make_entry(self.root, row=25, column=0, width=11)
        self.labelling_entry.bind("<KeyRelease>", self.__update_labelling)
    
    def _build_counter(self, n):
        self.lcounter_text = make_text(self.root, content = "N: " + str(n), row=23, column=0, width=14, bg=tkcolour_from_rgb((BACKGROUND)), padx=0, state=NORMAL, pady=0) 
        
    def _build_select_all_subfolders_button(self):
        self.select_data_cube_button = make_button(self.root, text="Open Project\nFolder",
                                                   command=self.__add_data_cube_subdirs, inner_padx=10, inner_pady=10,
                                                   outer_padx=15, row=26, rowspan=1, column=0, width=11, outer_pady=(5, 5))



    def _build_selection_box(self):
        self.selection_listbox = make_listbox(self.root, row=2, column=0, rowspan=21, padx=(0, 15), pady=(0, 15), height = 35, selectmode = "SINGLE")
        self.selection_listbox.bind('<<ListboxSelect>>', self.__update_selected_data_cube)
    
    # ---------------------------------------------- IMAGE -----------------------------------------------
        
    def _build_original_image_left(self, data):
        if data is None:
            # Placeholder
            self.original_image = make_label(self.root, "Navigation:\n Mouse-Left or 'q' to place point\n '+' or 'w' to zoom in\n '-' or 's' to zoom out\n arrows to change image", row=1, column=1, rowspan=25,
                                             columnspan=1, inner_pady=30, inner_padx=40, outer_padx=(15, 10),
                                             outer_pady=(15, 10))
        else:
            #data = np.asarray(rgb_image_to_hsi_array(self.original_image_data)).reshape((480, 640))
            (self.original_image_graph, self.original_image, self.image_array) = \
                make_image(self.root, data, row=1, column=1, columnspan=1, rowspan=25, lower_scale_value=None,
                           upper_scale_value=None, color_rgb=BACKGROUND, original=True, figheight=7, figwidth=9, img = self.original_image, axs = self.original_image_graph, figu = self.original_image_graph)
            self.root.bind_all('<Left>', self.__left)
            self.root.bind_all('<Right>', self.__right)
            self.original_image.get_tk_widget().bind('<Button-1>', self.__get_coords)
            #self.original_image.get_tk_widget().bind('<Motion>', self.__update_cursor)
            self.original_image.get_tk_widget().focus_force()
           
    def __add_from_data_cube_paths(self, event = None):
        self.selection_listbox.delete(0,'end')
        cc=0
        for dc_path in self.data_cube_paths:
            concat_path = os.path.basename(os.path.normpath(dc_path)) 
            self.selection_listbox.insert(END, concat_path)
            self.selection_listbox.config(width=18)
            cc=cc+1
        self._build_counter(cc)
        
    def __add_data_cube(self, sub_dir):
        dc_path = [sub_dir for i in [sub_dir] if ".png" in i or ".jpg" in i or ".heic" in i or ".heif" in i]  # takes first data cube it finds
        if len(dc_path) > 0:
            dc_path = dc_path[0]
            if dc_path in self.data_cube_paths:
                messagebox.showerror("Error", "That data has already been added.")
            else:
                self.data_cube_paths.append(dc_path)

    def __add_data_cube_subdirs(self):
        super_dir = self.__get_path_to_dir("Please select folder containing all the OP folders.")
        sub_dirs = glob.glob(super_dir + "/**/*")
        for sub_dir in sub_dirs:
            if "annotated" not in sub_dir:
                if "Kopie." not in sub_dir:
                    self.__add_data_cube(sub_dir)
        self.__add_from_data_cube_paths()

    def __get_path_to_dir(self, title):
        path = filedialog.askdirectory(parent=self.root, title=title)
        return path

    @staticmethod
    def __get_sub_folder_paths(path_to_main_folder, recursive = False): 
        sub_folders = sorted(glob.glob(path_to_main_folder+"/**/", recursive = recursive))
        return sub_folders
    
    def _insert_data_cube_paths(self):
        for dc_path in self.data_cube_paths:
            concat_path = os.path.basename(os.path.normpath(dc_path))
            self.selection_listbox.insert(END, concat_path)
            self.selection_listbox.config(width=18)
        self._build_counter(len(self.data_cube_paths))
    
    def __trash_list(self):
        self.data_cube_paths = []
        self.selection_listbox.delete(0,'end')
        self.coords_list = [(None, None), (None, None), (None, None), (None, None)]
        self.__remove_pt('all')
        self._build_counter(len(self.data_cube_paths))
    
    # ------------------------------------ Selection Listbox (control) ----------------------------
                
    def __right(self, event = None):
        if len(self.selection_listbox.curselection())>0:
            sel = self.selection_listbox.curselection()[0]
        else:
            sel = self.current_dc_path
        dc_path = self.get_selected_data_cube_path()
        filename = os.path.basename(dc_path)[:-4]
        image = self.copy_data
        base_path = os.path.dirname(dc_path)
        if not os.path.exists(base_path + "/annotated"):
            os.mkdir(base_path + "/annotated")
        image.save(base_path + "/annotated/" + filename + "_annotated.png")
        print("image save to: " + base_path + "/annotated/" + filename + "_annotated.png")
        self.__save_points()
        file=base_path + "/annotated/orientation.txt"
        with open(file, 'w') as filetowrite:
            filetowrite.write('right')
        self.selection_listbox.selection_clear(0, END)
        self.selection_listbox.select_set(sel+1) #This only sets focus on the first item.
        self.selection_listbox.event_generate("<<ListboxSelect>>")
        
            
    def __left(self, event = None):
        if len(self.selection_listbox.curselection())>0:
            sel = self.selection_listbox.curselection()[0]
        else:
            sel = self.current_dc_path
        dc_path = self.get_selected_data_cube_path()
        filename = os.path.basename(dc_path)[:-4]
        image = self.copy_data
        base_path = os.path.dirname(dc_path)
        if not os.path.exists(base_path + "/annotated"):
            os.mkdir(base_path + "/annotated")
        image.save(base_path + "/annotated/" + filename + "_annotated.png")
        print("image save to: " + base_path + "/annotated/" + filename + "_annotated.png")
        self.__save_points()
        file=base_path + "/annotated/orientation.txt"
        with open(file, 'w') as filetowrite:
            filetowrite.write('left')
        self.selection_listbox.selection_clear(0, END)
        self.selection_listbox.select_set(sel+1) #This only sets focus on the first item.
        self.selection_listbox.event_generate("<<ListboxSelect>>")
    
    # ------------------------------------------------- Saving / Loading --------------------------------------------------
                
    def __save_points(self):
        data = self.coords_list
        path = os.path.dirname(self.get_selected_data_cube_path())
        filename = os.path.basename(self.get_selected_data_cube_path())[:-4]
        output_path_ = path + '/annotated/'+filename +"_COORDINATES" + '.csv'
        np.savetxt(output_path_, data, delimiter=",", fmt="%1.2f")
    
    def __save_all(self):
        self.__save_coords(True)
        
    def __get_coords(self, event):
        print("get_coords")
        pos = self.original_image_graph.axes[0].get_position()
        axesX0 = pos.x0
        axesY0 = pos.y0
        axesX1 = pos.x1
        axesY1 = pos.y1
        canvas = event.widget
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        canvas.canvasx
        cx = canvas.winfo_rootx()
        cy = canvas.winfo_rooty()
        minX=width*axesX0
        maxX=width*axesX1
        minY=height*axesY0
        maxY=height*axesY1
        axWidth=maxX-minX
        conversionFactor = self.image_width/axWidth
        Xc=int((event.x-minX)*conversionFactor)
        Yc=int((event.y-minY)*conversionFactor)
        if self.coords_list[0][0] is None:
            self.coords_list[0] = (Xc, Yc)
        elif self.coords_list[1][0] is None:
            self.coords_list[1] = (Xc, Yc)
        elif self.coords_list[2][0] is None:
            self.coords_list[2] = (Xc, Yc)
        elif self.coords_list[3][0] is None:
            self.coords_list[3] = (Xc, Yc)
        else:
            self.coords_list = [(None, None),(None, None),(None, None),(None, None)]
        self._draw_points()
        
    def _draw_points(self):
        if self.original_image_data is not None:
            copy_data = self.data1.copy()
            cc = [(255, 0, 0), (0, 255, 0), (0,0,255), (255, 255, 0)]
            ii= 0
            for point in [point for point in self.coords_list if point[0] is not None]:
                if point[0] is not None:
                    y = int(point[0])
                    x = int(point[1])
                    for xi in range(-4, 5):
                        copy_data[(x + xi) % 480, y, :3] = cc[ii]
                    for yi in range(-4, 5):
                        copy_data[x, (y + yi) % 640, :3] = cc[ii]
                ii = ii+1
            im = Image.fromarray(copy_data)
            self.copy_data = im
            self._build_original_image_left(np.array(im))
        
        
    
        