#!/usr/bin/env python3
# ******************************************************************************************************************
#
#
#    pyiradio.py
# ----------------------
# Uwe Berger, 2022, 2023
#
#
#
# ---------
# Have fun!
#
# ******************************************************************************************************************
import tkinter as tk
from tkinter import ttk

from tkinter import messagebox

import urllib.request
from PIL import Image, ImageTk
import io

import vlc
from vlc import Meta
from vlc import State

from threading import Timer

import os

import textwrap

import my_func

# ...defines...
btn_dx = 55
btn_dy = 55
icon_dx = btn_dx
icon_dy = btn_dy

favicon_dx = 220
favicon_dy = 220

script_path = os.path.split(os.path.abspath(__file__))[0]

# ******************************************************************************************************************
class WebImage:
    def __init__(self, url, dx, dy):
        try:
            with urllib.request.urlopen(url) as u:
                raw_data = u.read()
            img = Image.open(io.BytesIO(raw_data))
        except:
            img = Image.open(F"{script_path}/icons/icon_radio.png")
        img_x = img.width
        img_y = img.height
        if img_x != dx:
            img_y = round(img_y * dx/img_x)
            img_x = dx
        if img_y != dy:
            img_x = round(img_x * dy/img_y)
            img_y = dy
        img = img.resize((img_x, img_y), Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(img)

    def get(self):
        return self.img

# ******************************************************************************************************************
class App:

    # ******************************************************************
    def __init__(self, master):
        self.instance = vlc.Instance('--input-repeat=-1', '--fullscreen')
        self.player=self.instance.media_player_new()
        self.app_frame = tk.Frame(master)
        self.app_frame.pack()
        self.mute = False
        self.state = False
        # Icons
        self.icon_pause = my_func.get_icon(f"{script_path}/icons/icon_pause.png", icon_dx, icon_dy)
        self.icon_play = my_func.get_icon(f"{script_path}/icons/icon_play.png", icon_dx, icon_dy)
        self.icon_player = my_func.get_icon(f"{script_path}/icons/icon_player.png", icon_dx, icon_dy)
        self.icon_mute = my_func.get_icon(f"{script_path}/icons/icon_mute.png", icon_dx, icon_dy)
        self.icon_unmute = my_func.get_icon(f"{script_path}/icons/icon_unmute.png", icon_dx, icon_dy)
        self.icon_volume_minus = my_func.get_icon(f"{script_path}/icons/icon_volume_minus.png", icon_dx, icon_dy)
        self.icon_volume_plus = my_func.get_icon(f"{script_path}/icons/icon_volume_plus.png", icon_dx, icon_dy)
        self.icon_stop = my_func.get_icon(f"{script_path}/icons/icon_stop.png", icon_dx, icon_dy)
        self.icon_search = my_func.get_icon(f"{script_path}/icons/icon_search.png", icon_dx, icon_dy)
        self.icon_favorite = my_func.get_icon(f"{script_path}/icons/icon_favorite.png", icon_dx, icon_dy)
        self.icon_filter = my_func.get_icon(f"{script_path}/icons/icon_filter.png", icon_dx, icon_dy)
        self.icon_delete = my_func.get_icon(f"{script_path}/icons/icon_abort.png", icon_dx, icon_dy)
        self.icon_exit = my_func.get_icon(f"{script_path}/icons/icon_quit.png", icon_dx, icon_dy)
        self._create_app_favorites(master)

    # ******************************************************************
    def _create_app_favorites(self, master):
        # old app-frame destroy...
        try:
            self.f_app.destroy()
        except:
            pass
        # ...and create new app-frame...
        master.title("pyIRadio (favorites)")
        self.f_app = tk.Frame(self.app_frame, bd=2)
        self.f_app.pack(side=tk.TOP, fill=tk.BOTH)
        f0 = tk.Frame(self.f_app, bd=2)
        f0.pack(side=tk.TOP, fill=tk.X)
        # ...favorites
        f1 = tk.LabelFrame(f0, bd=2, text="Favorites:")
        f1.pack(side=tk.LEFT, fill=tk.X)
        self.stations_lb=tk.Listbox(f1, width=30, height=10, font=("Arial", 18))
        self.stations_lb.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)
        self.favorites_scrollbar = tk.Scrollbar(f1, width=32)
        self.favorites_scrollbar.pack(side = tk.RIGHT, fill = tk.BOTH)
        self.stations_lb.config(yscrollcommand = self.favorites_scrollbar.set)
        self.favorites_scrollbar.config(command = self.stations_lb.yview)
        self.stations_lb.bind('<<ListboxSelect>>', self._favoriteslist_select) 
        self._fill_favorites_list()
        # ...stationinfos
        self.station_info = self._my_textbox(master, f0, "Stationinfo:", 38, 18)
        # ...buttons
        self.f4 = tk.LabelFrame(self.f_app, bd=2, text="Actions:")
        self.f4.pack(side=tk.TOP, fill=tk.X)
        self.btn_play = self._my_button(self.f4, tk.LEFT, self.icon_play, lambda:self._player_start(master))
        self.btn_play.configure(state="disable")
        self.btn_delete = self._my_button(self.f4, tk.LEFT, self.icon_delete, self._delete_favorite)
        self.btn_delete.configure(state="disable")
        self.btn_search = self._my_button(self.f4, tk.LEFT, self.icon_search, lambda:self._search_start(master))
        self.btn_exit = self._my_button(self.f4, tk.RIGHT, self.icon_exit, master.destroy)
        # ...set (possibly) saved listbox-index and stationinfos
        try:
            self.stations_lb.selection_set(self.selected_favorite)
            self._fill_station_info()
            self.btn_delete.configure(state="normal")
            self.btn_play.configure(state="normal")
            self._favoriteslist_select(0)
        except:
            self._clear_textbox(self.station_info)
            pass
        #
        self.player_start_from = "favorites"

    # ******************************************************************
    def _create_app_search(self, master):
        # old app-frame destroy...
        try:
            self.f_app.destroy()
        except:
            pass
        # ...and create new app-frame...
        master.title("pyIRadio (search)")
        self.f_app = tk.Frame(self.app_frame, bd=2)
        self.f_app.pack(side=tk.TOP, fill=tk.BOTH)
        f0 = tk.Frame(self.f_app, bd=2)
        f0.pack(side=tk.TOP, fill=tk.X)
        # filter-values
        f1 = tk.LabelFrame(f0, bd=2, text="Search filter:")
        f1.pack(side=tk.LEFT, fill=tk.Y)
        # ...name (entry)
        self.filter_name = self._my_entry(f1, "Name:")
        # ...tag (entry)
        self.filter_tags = self._my_entry(f1, "Tags:")
        # ...country (combobox)
        self.filter_country = self._my_combobox(f1, "Country:")
        # ...countrycode (combobox)
        self.filter_countrycode = self._my_combobox(f1, "Countrycode:")
        # ...state (combobox)
        self.filter_state = self._my_combobox(f1, "State:")
        # ...language (entry)
        self.filter_language = self._my_entry(f1, "Language:")
        # result-list
        f2 = tk.LabelFrame(f0, bd=2, text="Search result:")
        f2.pack(side=tk.LEFT, fill=tk.Y)
        self.stationlist_numbers=tk.Label(f2)
        self.stationlist_numbers.pack(side=tk.BOTTOM)
        self.stations_lb=tk.Listbox(f2, width=30, height=15)
        self.stations_lb.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)
        self.stations_scrollbar = tk.Scrollbar(f2, width=32)
        self.stations_scrollbar.pack(side = tk.RIGHT, fill = tk.BOTH)
        self.stations_lb.config(yscrollcommand = self.stations_scrollbar.set)
        self.stations_scrollbar.config(command = self.stations_lb.yview)
        self.stations_lb.bind('<<ListboxSelect>>', self._stationlist_select)
        # station-info-text with scrollbar
        self.station_info = self._my_textbox(master, f0, "Stationinfo:", 30, 19, )
        # ...buttons
        self.f4 = tk.LabelFrame(self.f_app, bd=2, text="Actions:")
        self.f4.pack(side=tk.TOP, fill=tk.X)
        self.btn_search = self._my_button(self.f4, tk.LEFT, self.icon_filter, self._fill_stationlist)
        self.btn_favorite = self._my_button(self.f4, tk.LEFT, self.icon_favorite, self._add_to_favorites)
        self.btn_favorite.configure(state="disable")
        self.btn_play = self._my_button(self.f4, tk.LEFT, self.icon_play, lambda:self._player_start(master))
        self.btn_play.configure(state="disable")
        self.btn_stop = self._my_button(self.f4, tk.LEFT, self.icon_stop, lambda:self._create_app_favorites(master))
        self.btn_exit = self._my_button(self.f4, tk.RIGHT, self.icon_exit, master.destroy)
        # Comboboxen fuellen
        self.filter_countrycode['values'] = my_func.get_all_countrycodes()
        self.filter_country['values'] = my_func.get_all_countrys()
        self.filter_state['values'] = my_func.get_all_states()
        # restore saves values
        try:
            self.filter_name.insert(0, self.save_filter_name)
            self.filter_tags.insert(0, self.save_filter_tags)
            self.filter_country.insert(0, self.save_filter_country)
            self.filter_countrycode.insert(0, self.save_filter_countrycode)
            self.filter_state.insert(0, self.save_filter_state)
            self.filter_language.insert(0, self.save_filter_language)
            self._fill_stationlist()
            self.stations_lb.selection_set(self.save_filter_selection)
            self._stationlist_select(0)
        except:
            pass
        #
        self.player_start_from = "search"
        
    # ******************************************************************
    def _create_app_player(self, master):

        if len(self.stations_lb.curselection()) != 1:
            return
        # old app-frame destroy...
        try:
            self.f_app.destroy()
        except:
            pass
        # ...and create new app-frame...
        master.title(f"pyIRadio - {self.stationinfo['name']}")
        self.f_app = tk.Frame(self.app_frame, bd=2)
        self.f_app.pack(side=tk.TOP, fill=tk.BOTH)
        f0 = tk.Frame(self.f_app, bd=2)
        f0.pack(side=tk.TOP, fill=tk.X)
        # ...titleinformations (stream)
        f1 = tk.LabelFrame(f0, bd=2, text="Streaminfo:")
        f1.pack(side=tk.LEFT, fill=tk.BOTH)
        lable_font=("Arial", 22, "bold")
        self.title=self._my_lable(f1, "Title:", 30, lable_font)
        self.nowplaying=self._my_lable(f1, "Now playing:", 30, lable_font)
        self.genre=self._my_lable(f1, "Genre:", 30, lable_font)
        
        # ...stationinfos
        f2 = tk.LabelFrame(f0, bd=2, text="Stationinfo:")
        f2.pack(side=tk.LEFT, fill=tk.BOTH)
        self.station_info = self._my_textbox(master, f2, "", 35, 4, )
        #self._print_txt(self.station_info, 'Name:', self.stationinfo['name'], '')
        self._print_txt(self.station_info, 'Country:', self.stationinfo['country'], '')
        self._print_txt(self.station_info, 'State:', self.stationinfo['state'], '')
        self._print_txt(self.station_info, 'Codec:', self.stationinfo['codec'], '')
        self._print_txt(self.station_info, 'Bitrate:', self.stationinfo['bitrate'], f'Kb/s')
        # ...stationicon
        try:
            self.img = WebImage(self.stationinfo['favicon'], favicon_dx, favicon_dy).get()
            self.imagelab = tk.Label(f2, image=self.img)
            #self.imagelab.pack(side=tk.LEFT)
            self.imagelab.pack()
        except:
            pass
        # ...buttons
        self.f4 = tk.LabelFrame(self.f_app, bd=2, text="Actions:")
        self.f4.pack(side=tk.TOP, fill=tk.X)
        self.btn_play = self._my_button(self.f4, tk.LEFT, self.icon_play, self._player_pause_play_toggle)
        self.btn_mute = self._my_button(self.f4, tk.LEFT, self.icon_mute, self._player_mute_toggle)
        self.btn_volume_decr = self._my_button(self.f4, tk.LEFT, self.icon_volume_minus, lambda:self._set_volume(-5))
        self.btn_volume_incr = self._my_button(self.f4, tk.LEFT, self.icon_volume_plus, lambda:self._set_volume(+5))
        self.btn_stop = self._my_button(self.f4, tk.LEFT, self.icon_stop, lambda:self._player_close(master))
        self.btn_exit = self._my_button(self.f4, tk.RIGHT, self.icon_exit, lambda:self._quit_all(master))
        # ...and play the url!
        self.media=self.instance.media_new(self.stationinfo['url'])
        self.media.get_mrl()
        self.player.set_media(self.media)
        self.player.play()
        self.player.audio_set_volume(100)
        self.btn_play.configure(image=self.icon_pause)
        self.player.audio_set_mute(False)
        self._get_media_infos()
        
    # ******************************************************************
    def _fill_favorites_list(self):
        self.favorites = my_func.get_all_favorites()
        self.stations_lb.delete(0, 'end')
        for l in self.favorites:
            self.stations_lb.insert('end', l['name'])        

    # ******************************************************************
    def _my_button(self, w, side, icon, cmd):
        b = tk.Button(w, height=btn_dy, width=2*btn_dx, image=icon, command=cmd)
        b.pack(side=side)
        return b
        
    # ******************************************************************
    def _my_lable(self, w, title, width, font):
        f = tk.LabelFrame(w, bd=2, text=title)
        f.pack(side=tk.TOP, pady=5, padx=5, fill=tk.X)
        l=tk.Label(f, width=width, text=title, font=font)
        l.pack(anchor=tk.NW)
        return l
        

    # ******************************************************************
    def _my_textbox(self, master, w, title, width, height, scrollbar=0):        
        f = tk.LabelFrame(w, bd=2, text=title)
        f.pack(side=tk.TOP, fill=tk.BOTH)
        textbox = tk.Text(f, wrap="word", bg=master.cget("background"), relief=tk.FLAT, width=width, height=height)
        textbox.pack(side=tk.LEFT, fill=tk.Y)
        if scrollbar:
            textbox_scrollbar = tk.Scrollbar(f, command = textbox.yview, width=32)
            textbox_scrollbar.pack(side = tk.LEFT, fill = tk.BOTH)
            textbox.config(yscrollcommand = textbox_scrollbar.set)        
        return textbox

    # ******************************************************************
    def _print_txt(self, w, lable, txt, pre):
        w.configure(state="normal")
        if len(str(txt)) > 0:
            w.insert(tk.END, f"{lable}{txt}{pre}\n")
        w.configure(state="disable")

    # ******************************************************************
    def _clear_textbox(self, w):
        w.configure(state="normal")
        w.delete("1.0", "end")
        w.configure(state="disable")

    # ******************************************************************
    def _player_start(self, master):
        self._create_app_player(master)

    # ******************************************************************
    def _player_close(self, master):
        self.player.stop()
        self.refresh_timer.cancel()
        if self.player_start_from == "favorites":
           self._create_app_favorites(master)
        elif self.player_start_from == "search":
           self._create_app_search(master)
        else: 
           self._create_app_favorites(master)

    # ******************************************************************
    def _get_media_infos(self):
        self.nowplaying.configure(text=textwrap.fill(str(self.media.get_meta(Meta.NowPlaying)), 30))
        self.title.configure(text=textwrap.fill(str(self.media.get_meta(Meta.Title)), 30))
        self.genre.configure(text=textwrap.fill(str(self.media.get_meta(Meta.Genre)), 30))
        self.refresh_timer=Timer(5.0, self._get_media_infos)
        self.refresh_timer.start()

    # ******************************************************************
    def _favoriteslist_select(self, event):
        selection = self.stations_lb.curselection()
        # save selected listbox-index
        self.selected_favorite = selection[0]
        ret = my_func.get_stationinfo(self.favorites[selection[0]]['stationuuid'])
        self.stationinfo = ret[0]
        self._fill_station_info()
        self.btn_delete.configure(state="normal")
        self.btn_play.configure(state="normal")

        
    # ******************************************************************
    def _fill_station_info(self, post='\n'):
        self._clear_textbox(self.station_info)
        self._print_txt(self.station_info, 'Name:', self.stationinfo['name'], post)
        self._print_txt(self.station_info, 'Homepage:', self.stationinfo['homepage'], post)
        self._print_txt(self.station_info, 'Country:', self.stationinfo['country'], post)
        self._print_txt(self.station_info, 'State:', self.stationinfo['state'], post)
        self._print_txt(self.station_info, 'Language:', self.stationinfo['language'], post)
        self._print_txt(self.station_info, 'Tags:', self.stationinfo['tags'], post)
        self._print_txt(self.station_info, 'Codec:', self.stationinfo['codec'], post)
        self._print_txt(self.station_info, 'Bitrate:', self.stationinfo['bitrate'], f'Kb/s{post}')

    # ******************************************************************
    def _player_pause_play_toggle(self):
        if self.state:
            self.player.audio_set_mute(False)
            self.state=False
            self.btn_play.configure(image=self.icon_pause)
        else:
            self.player.audio_set_mute(True)
            self.state=True
            self.btn_play.configure(image=self.icon_play)

    # ******************************************************************
    def _player_mute_toggle(self):
        if self.mute:
            self.player.audio_set_mute(False)
            self.mute=False
            self.btn_mute.configure(image=self.icon_mute)
        else:
            self.player.audio_set_mute(True)
            self.mute=True
            self.btn_mute.configure(image=self.icon_unmute)

    # ******************************************************************
    def _set_volume(self, incr):
        volume = self.player.audio_get_volume()
        volume_new = volume + incr
        if volume_new > 100:
            volume_new = 100
        if volume_new < 0:
            volume_new = 0
        self.player.audio_set_volume(volume_new)

    # ******************************************************************
    def _search_start(self, master):
        self._create_app_search(master)

    # *******************************************************************************************************************
    def _fill_stationlist(self):
        global stations
        # ...
        stations = []
        stations = my_func.get_filtered_stationnames(
                                        self.filter_name.get(),
                                        self.filter_tags.get(),
                                        self.filter_country.get(),
                                        self.filter_countrycode.get(),
                                        self.filter_state.get(),
                                        self.filter_language.get()
                                        )
        if len(stations) > my_func.max_search_result_count:
            messagebox.showinfo("pyIRadio search...", "Too many stations found, please narrow down your search!")
        else:
            self.stations_lb.delete(0, 'end')
            for l in stations:
                self.stations_lb.insert('end', l['name'])
            self._set_stationnumbers(stations)
        self.btn_favorite.configure(state="disable")
        self._clear_textbox(self.station_info)

    # *******************************************************************************************************************
    def _set_stationnumbers(self, stations):
        sel_count=len(stations)
        all_count=my_func.get_station_count()
        s = f'{sel_count}/{all_count}'
        self.stationlist_numbers.configure(text=s)
        
	# *******************************************************************************************************************
    def _add_to_favorites(self):
        sql = my_func.get_create_sql(my_func.favorites_struct, my_func.tab_favorites)
        my_func.sql_execute(sql)
        v={'stationuuid':self.stationinfo['stationuuid']}
        sql = my_func.get_insert_sql(my_func.favorites_struct, v, my_func.tab_favorites)
        my_func.sql_execute(sql)
        messagebox.showinfo("pyIRadio Favorites", f"Station \"{self.stationinfo['name']}\" added to favorites.")        

    # *****************************
    def _delete_favorite(self):
        global favorites_w
        my_func.delete_favorite(self.stationinfo['stationuuid'])
        self._fill_favorites_list()
        self.btn_play.configure(state="disable")
        self.btn_delete.configure(state="disable")
        self._clear_textbox(self.station_info)
        messagebox.showinfo("pyIRadio Favorites", f"Station \"{self.stationinfo['name']}\" deleted from favorites.")

    # *******************************************************************************************************************
    def _stationlist_select(self, event):
        global stations 
        selection = self.stations_lb.curselection()
        if selection:
            self._clear_textbox(self.station_info)
            ret = my_func.get_stationinfo(stations[selection[0]]['stationuuid'])
            # ...theoretisch gibt es genau einen Eintrag!
            self.stationinfo = ret[0]
            # ...stationinfo-Labels setzen
            self._fill_station_info(post='\n')
            self.btn_favorite.configure(state="normal")
            # save values
            self.save_filter_name = self.filter_name.get()
            self.save_filter_tags = self.filter_tags.get()
            self.save_filter_country = self.filter_country.get()
            self.save_filter_countrycode = self.filter_countrycode.get()
            self.save_filter_state = self.filter_state.get()
            self.save_filter_language = self.filter_language.get()
            self.save_filter_selection = selection[0]
            self.btn_play.configure(state="normal")
        
    # ******************************************************************
    def _my_entry(self, w, text):
        entry_f = tk.LabelFrame(w, bd=2, text=text)
        entry_f.pack(side=tk.TOP, pady=4, padx=5, fill=tk.X)
        entry=tk.Entry(entry_f)
        entry.pack(side=tk.LEFT)
        entry_clear = tk.Button(entry_f, text="x", padx=0, pady=0, command=lambda:entry.delete(0, 'end'))
        entry_clear.pack(side=tk.RIGHT)
        return entry

    # ******************************************************************
    def _my_combobox(self, w, text):
        combobox_f = tk.LabelFrame(w, bd=2, text=text,)
        combobox_f.pack(side=tk.TOP, pady=4, padx=5, fill=tk.X)
        combobox=ttk.Combobox(combobox_f)
        combobox.pack(side=tk.LEFT)
        combobox_clear = tk.Button(combobox_f, text="x", padx=0, pady=0, command=lambda:combobox.delete(0, 'end'))
        combobox_clear.pack(side=tk.RIGHT)
        return combobox

    # ******************************************************************
    def _quit_all(self, master):
        self.player.stop()
        self.refresh_timer.cancel()
        master.destroy()

# **********************************************************************
def main(): 
    root = tk.Tk()
    root.title("pyIRadio")
    #root.geometry("800x400")
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    if h > 500:
        root.geometry("800x430")
    else:
        root.geometry("%dx%d+0+0" % (w, h))
    
    root.iconphoto(False, tk.PhotoImage(file=f"{script_path}/icons/favicon.png"))
    app = App(root)
    root.mainloop()


# **********************************************************************
# **********************************************************************
# **********************************************************************
if __name__ == '__main__':
    main()
