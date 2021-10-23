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
        data1 = np.array(img)
        if len(glob.glob(os.path.dirname(dc_path) + "/*after*"))>0:
            img = Image.open(glob.glob(os.path.dirname(dc_path) + "/*after*")[0])
            data2 = np.array(img)
        else:
            data2 = np.zeros((640,480,3))
        self._build_original_image_left(data1)
        self._build_original_image_right(data2)
        
    # ------------------------------------------------ INITIALIZATION ------------------------------------------------

    def _init_widget(self):
        self._build_selection_box()
        self._build_original_image_left(self.original_image_data)
        self._build_original_image_right(self.original_image_data)
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
                           upper_scale_value=None, color_rgb=BACKGROUND, original=True, figheight=3.5, figwidth=4.5, img = self.original_image, axs = self.original_image_graph, figu = self.original_image_graph)
            self.root.bind_all('<Left>', self.__next_not)
            self.root.bind_all('<Right>', self.__next_hot)
            self.root.bind_all('1', self.__next_one)
            self.root.bind_all('2', self.__next_two)
            #self.original_image.get_tk_widget().bind('<Motion>', self.__update_cursor)
            self.original_image.get_tk_widget().focus_force()
           
    def _build_original_image_right(self, data):
        if data is None:
            # Placeholder
            self.original_image_r = make_label(self.root, "Navigation:\n Mouse-Left or 'q' to place point\n '+' or 'w' to zoom in\n '-' or 's' to zoom out\n arrows to change image", row=1, column=2, rowspan=25,
                                             columnspan=1, inner_pady=30, inner_padx=40, outer_padx=(15, 10),
                                             outer_pady=(15, 10))
        else:
            #data = np.asarray(rgb_image_to_hsi_array(self.original_image_data)).reshape((480, 640))
            (self.original_image_graph_r, self.original_image_r, self.image_array_r) = \
                make_image(self.root, data, row=1, column=2, columnspan=1, rowspan=25, lower_scale_value=None,
                           upper_scale_value=None, color_rgb=BACKGROUND, original=True, figheight=3.5, figwidth=4.5, img = self.original_image_r, axs = self.original_image_graph_r, figu = self.original_image_graph_r)         
           
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
        contents = os.listdir(sub_dir)
        dc_path = [sub_dir + "/" + i for i in contents if "before" in i]  # takes first data cube it finds
        if len(dc_path) > 0:
            dc_path = dc_path[0]
            if dc_path in self.data_cube_paths:
                messagebox.showerror("Error", "That data has already been added.")
            else:
                self.data_cube_paths.append(dc_path)

    def __add_data_cube_subdirs(self):
        super_dir = self.__get_path_to_dir("Please select folder containing all the OP folders.")
        sub_dirs = self.__get_sub_folder_paths(super_dir, True)
        for sub_dir in sub_dirs:
            if "/hot/" not in sub_dir or "/not/" not in sub_dir:
                if len(glob.glob(sub_dir + "/*before*"))>=1:
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
        self.coords_list = [(None, None) for _ in range(1000000)]
        self.__remove_pt('all')
        self._build_counter(len(self.data_cube_paths))
    
    # ------------------------------------ Selection Listbox (control) ----------------------------
                
    def __next_hot(self, event = None):
        if len(self.selection_listbox.curselection())>0:
            sel = self.selection_listbox.curselection()[0]
        else:
            sel = self.current_dc_path
        dc_path = self.get_selected_data_cube_path()
        base_path = os.path.dirname(os.path.dirname(dc_path))
        if os.path.exists(base_path + "/hot/" + os.path.basename(os.path.dirname(dc_path))):
            shutil.rmtree(base_path + "/hot/" + os.path.basename(os.path.dirname(dc_path)))
        if not os.path.exists(base_path + "/hot"):
            os.mkdir(base_path + "/hot")
        if not os.path.exists(base_path + "/hot/" +os.path.basename(os.path.dirname(dc_path))):
            os.mkdir(base_path + "/hot/" +os.path.basename(os.path.dirname(dc_path)))
        copy_tree(os.path.dirname(dc_path), base_path + "/hot/" + os.path.basename(os.path.dirname(dc_path)))
        self.selection_listbox.selection_clear(0, END)
        self.selection_listbox.select_set(sel+1) #This only sets focus on the first item.
        self.selection_listbox.event_generate("<<ListboxSelect>>")
        
            
    def __next_not(self, event = None):
        if len(self.selection_listbox.curselection())>0:
            sel = self.selection_listbox.curselection()[0]
        else:
            sel = self.current_dc_path
        dc_path = self.get_selected_data_cube_path()
        base_path = os.path.dirname(os.path.dirname(dc_path))
        if os.path.exists(base_path + "/hot/" + os.path.basename(os.path.dirname(dc_path))):
            shutil.rmtree(base_path + "/hot/" + os.path.basename(os.path.dirname(dc_path)))
        self.selection_listbox.selection_clear(0, END)
        self.selection_listbox.select_set(sel+1) #This only sets focus on the first item.
        self.selection_listbox.event_generate("<<ListboxSelect>>")
        
    def __next_one(self, event = None):
        if len(self.selection_listbox.curselection())>0:
            sel = self.selection_listbox.curselection()[0]
        else:
            sel = self.current_dc_path
        dc_path = self.get_selected_data_cube_path()
        base_path = os.path.dirname(os.path.dirname(dc_path))
        if os.path.exists(base_path + "/hot/" + os.path.basename(os.path.dirname(dc_path))):
            shutil.rmtree(base_path + "/hot/" + os.path.basename(os.path.dirname(dc_path)))
        
        if not os.path.exists(base_path + "/hot"):
            os.mkdir(base_path + "/hot")
        if not os.path.exists(base_path + "/hot/" +os.path.basename(os.path.dirname(dc_path))):
            os.mkdir(base_path + "/hot/" +os.path.basename(os.path.dirname(dc_path)))
        shutil.copy(glob.glob(os.path.dirname(dc_path) + "/*before*")[0], base_path + "/hot/" +os.path.basename(os.path.dirname(dc_path)))
        self.selection_listbox.selection_clear(0, END)
        self.selection_listbox.select_set(sel+1) #This only sets focus on the first item.
        self.selection_listbox.event_generate("<<ListboxSelect>>")
        
    def __next_two(self, event = None):
        if len(self.selection_listbox.curselection())>0:
            sel = self.selection_listbox.curselection()[0]
        else:
            sel = self.current_dc_path
        dc_path = self.get_selected_data_cube_path()
        base_path = os.path.dirname(os.path.dirname(dc_path))
        if os.path.exists(base_path + "/hot/" + os.path.basename(os.path.dirname(dc_path))):
            shutil.rmtree(base_path + "/hot/" + os.path.basename(os.path.dirname(dc_path)))
        
        if not os.path.exists(base_path + "/hot"):
            os.mkdir(base_path + "/hot")
        if not os.path.exists(base_path + "/hot/" +os.path.basename(os.path.dirname(dc_path))):
            os.mkdir(base_path + "/hot/" +os.path.basename(os.path.dirname(dc_path)))
        shutil.copy(glob.glob(os.path.dirname(dc_path) + "/*after*")[0], base_path + "/hot/" +os.path.basename(os.path.dirname(dc_path)))
        self.selection_listbox.selection_clear(0, END)
        self.selection_listbox.select_set(sel+1) #This only sets focus on the first item.
        self.selection_listbox.event_generate("<<ListboxSelect>>")
    
    # ------------------------------------------------- Saving / Loading --------------------------------------------------
        
    def __save_mask(self):
        polygon = [point for point in self.coords_list if point != (None, None)]
        if len(polygon)>0:
            img = Image.new('L', (640, 480), 0)
            ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)
            mask_array = np.array(img)
            path = os.path.dirname(self.get_selected_data_cube_path())
            if not os.path.exists(path + '/'+self.listener.output_folder_hypergui):
                os.mkdir(path + '/'+self.listener.output_folder_hypergui)
            output_path = path + '/'+self.listener.output_folder_hypergui + "/mask" + '.csv'
            np.savetxt(output_path, mask_array, delimiter=",", fmt="%d")
        else:
            pass
        
    def __save_points(self):
        data = self.__get_coords_list()
        if len(data)>0:
            path = os.path.dirname(self.get_selected_data_cube_path())
            if self.delete_content:
                if os.path.exists(path + '/'+self.listener.output_folder_hypergui):
                    shutil.rmtree(path + '/'+self.listener.output_folder_hypergui)
            if not os.path.exists(path + '/'+self.listener.output_folder_hypergui):
                os.mkdir(path + '/'+self.listener.output_folder_hypergui)
            output_path = path + '/'+self.listener.output_folder_hypergui + "/MASK_COORDINATES" + '.csv'
            np.savetxt(output_path, data, delimiter=",", fmt="%1.2f")
        else:
            pass
    
    def __save_all(self):
        self.__save_coords(True)
        
    
        