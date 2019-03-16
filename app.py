import tkinter as tk
from tkinter import messagebox
import sqlite3
from utils import Tv_series, Database_handler, fetch_tables

conn=sqlite3.connect("tv_series_db.db")
cur= conn.cursor()

show_names= fetch_tables(cur)
data= {}
db_handler= {}
for name in show_names:
    obj= Tv_series()
    db_handler[name]= Database_handler(cur, obj)
    db_handler[name].table_name= name.replace(' ', '_')
    data[name] = db_handler[name].fetch_data()


app= tk.Tk()
app.state('zoomed')
app.title('Episode Tracker')
LARGE_FONT= ("Arial", 11)
for row in range(30):
    app.rowconfigure(row, weight=1)    
for col in range(35):
    app.columnconfigure(col, weight=1)


buttons= {}       #Sidebar Button
text= {}          #Text 
seen_rbs= {}      #Seen Radiobuttons
unseen_rbs= {}    #Unseen Radiobuttons
var= {}           #Radiobutton Variables
labels= {}
context_menu_buttons= {}  #Context Menu for each sidebar button

#Add a new TV show and store it in the database
def add_new_show(frame, mainframe, cursor):
    new_win= tk.Toplevel(app)     #Create a new window

    screen_width= 500 
    screen_height=100
    x_pos= 400 
    y_pos= 100 
    new_win.geometry(f'{screen_width}x{screen_height}+{x_pos}+{y_pos}')    #To set the sceen position, width, height
    new_win.title('Add New TV Show')

    for row in range(4):
        new_win.rowconfigure(row, weight=1)    
    for col in range(35):
        new_win.columnconfigure(col, weight=1)

    show_name_= tk.StringVar()
    season_number_= tk.StringVar()
    dir_path_= tk.StringVar()

    label1= tk.Label(new_win, text='Enter Show Name: ')
    entry1= tk.Entry(new_win, width= 50, textvariable= show_name_)
    entry1.focus_set()

    label2= tk.Label(new_win, text='Enter Season Number: ')
    entry2= tk.Entry(new_win, width= 50, textvariable= season_number_)
    entry2.delete(0, tk.END)

    label3= tk.Label(new_win, text='Enter Directory Path: ')
    entry3= tk.Entry(new_win, width= 50, textvariable= dir_path_)
    entry3.delete(0, tk.END)
    
    label1.grid(row= 0, column= 0)
    entry1.grid(row= 0, column= 1, columnspan= 25)
    label2.grid(row= 1, column= 0)
    entry2.grid(row= 1, column= 1, columnspan= 25)
    label3.grid(row= 2, column= 0)
    entry3.grid(row= 2, column= 1, columnspan= 25)

    def get_and_store_data():
        show_name= str(show_name_.get()).strip()
        season_number= str(season_number_.get()).strip()
        dir_path= str(dir_path_.get()).strip()
        if show_name=="" or season_number== "" or dir_path== "":
            new_win.destroy()
            add_new_show(frame, mainframe, cursor)
            return
        table_name= show_name+ ' Season '+ season_number

        #TV Series Object
        obj= Tv_series(name= show_name, season= int(season_number), path= dir_path)
        if not obj.check_path():
            #If path is invalid, generate a error message
            messagebox.showerror('Invalid Path', "Entered path is not valid.")
            add_new_show(frame, cursor)
            return
        else:
            #Reading Directory and storing episode names
            obj.list_vids()
        try:
            db_handler[table_name]= Database_handler(cursor, obj)
            db_handler[table_name].create_table()
            db_handler[table_name].data_entry()
            conn.commit()
            data[table_name] = db_handler[table_name].fetch_data()
        except Exception as e:
            print(e)
            messagebox.showerror('Invalid Table Name', "Show Already Exists in the database.")

        new_win.destroy()
        create_show_buttons(frame, mainframe, cursor)
    new_win.bind('<Return>', lambda event: get_and_store_data())
    button= tk.Button(new_win, text= 'Submit', command= lambda : get_and_store_data())
    button.grid(row= 3, column=8 )
    

#Clear Main Screen 
def clear_screen():
    if 'header' in text:
        text['header'].grid_forget()
    for label in labels:
        labels[label].grid_forget()
    for key in seen_rbs:
        text[key].grid_forget()
        seen_rbs[key].grid_forget()
        unseen_rbs[key].grid_forget()


#Create list of buttons in sidebar
def create_show_buttons(frame, main_frame, cursor):
    show_names= fetch_tables(cursor)
    for name in buttons:
        buttons[name].grid_forget()
    for name in show_names:
        buttons[name]= tk.Button(frame, text= name, width= 30, 
            command= lambda frame= main_frame, epi_list= data[name], show_name= name: show_list(frame, epi_list, show_name))
        buttons[name].grid(padx= 20, pady= 5)
        context_menu_buttons[name]= tk.Menu(frame, tearoff= 0)
        context_menu_buttons[name].add_command(label= 'Delete', 
            command= lambda frame=  sidebar, mainframe= main_area, cursor= cur, 
            show_name= name: delete_show_helper(sidebar, main_area, cur, show_name) )
        buttons[name].bind("<Button-3>", lambda event, name= name: context_menu_buttons[name].tk_popup(event.x_root, event.y_root))
        

#Delete a Show
def delete_show_helper(frame, mainframe, cursor, show_name):
    try:
        db_handler[show_name].drop_table()
        del db_handler[show_name]
        del data[show_name]
        conn.commit()
        create_show_buttons(frame, mainframe, cursor)
        clear_screen()
    except Exception as e:
        print(e)
        messagebox.showerror('Incorrect Show Name', "Entered show name is not in the list.")


#To delete a particular show
def delete_show(frame, mainframe, cursor):
    new_win= tk.Toplevel(app)

    screenWidth= 500 
    screenHeight=60
    new_win.geometry(f'{screenWidth}x{screenHeight}+400+100')
    new_win.title('Delete Series')

    for row in range(30):
        new_win.rowconfigure(row, weight=1)    
    for col in range(35):
        new_win.columnconfigure(col, weight=1)

    show_name_= tk.StringVar()

    label1= tk.Label(new_win, text='Enter Show name: ')
    entry1= tk.Entry(new_win, width= 50, textvariable= show_name_)
    entry1.focus_set()
    entry1.delete(0, tk.END)
    
    label1.grid(row= 0, column= 0)
    entry1.grid(row= 0, column= 1, columnspan= 25)

    def get_and_delete_table():
        show_name= show_name_.get()
        delete_show_helper(frame, mainframe, cursor, show_name)
        new_win.destroy()

    button= tk.Button(new_win, text= 'Submit', command= lambda : get_and_delete_table())
    button.grid(row= 5, column=8 )


#Show list of episodes for a particular show
def show_list(frame, episode_list= [("", 0, 1)], show_name= ""):
    clear_screen()

    text['header']= tk.Text(frame, height= 1, font= LARGE_FONT, padx= 10, pady= 1, bg= 'yellow', bd= 5)
    text['header'].grid(row= 0, column= 1, rowspan= 1, columnspan= 7)
    text['header'].insert(tk.END, 'NAME')
    text['header'].configure(state='disabled')

    for i in range(len(episode_list)):

        var[i]= tk.IntVar()
        if episode_list[i][1]==1:
            text[i]= tk.Text(frame, height= 1, font= LARGE_FONT, padx= 10, pady= 1, fg= 'gray70')
        else:
            text[i]= tk.Text(frame, height= 1, font= LARGE_FONT, padx= 10, pady= 1, fg= 'black')
        seen_rbs[i]= tk.Radiobutton(frame, variable=var[i], value=1, text= 'SEEN', command= lambda epi_number= i,
           show_name = show_name: update(epi_number, show_name))
        unseen_rbs[i]= tk.Radiobutton(frame, variable=var[i], value=2, text= 'UNSEEN', command= lambda epi_number=i,
            show_name= show_name: update(epi_number, show_name))
        
        text[i].grid(row= i+1, column= 1, rowspan= 1, columnspan= 7)
        text[i].configure(state= 'normal')
        text[i].insert(tk.END, str(episode_list[i][0]))
        text[i].configure(state='disabled')     #To make textbox Read-Only
        
        seen_rbs[i].grid(row= i+1, column= 8, rowspan= 1, columnspan= 4)
        unseen_rbs[i].grid(row= i+1, column= 12, rowspan= 1, columnspan= 4)
        
        #Select appropriate radiobutton
        if episode_list[i][1]==1:
            seen_rbs[i].select()
        else:
            unseen_rbs[i].select()


#Update Seen, Unseen in Database
def update(epi_number, show_name):
    if 'update' in labels:
        labels['update'].grid_forget()

    val= int(var[epi_number].get())
    if val==1:     
        #Seen
        text[epi_number].configure(fg= 'gray70')
        label_text= str(epi_number+1)+ "th Episode Seen"
        data[show_name][epi_number][1]= 1
        data[show_name][epi_number][2]= 0
        db_handler[show_name].update(True, data[show_name][epi_number][0])   #Update Seen= True for a particular episode 
        conn.commit()
    elif val==2:
        #Unseen
        text[epi_number].configure(fg= 'black')
        label_text= str(epi_number+1)+ "th Episode Unseen"
        data[show_name][epi_number][1]= 1
        data[show_name][epi_number][2]= 0
        db_handler[show_name].update(False, data[show_name][epi_number][0])
        conn.commit()
    
    labels['update']= tk.Label(main_area, text= label_text, font= LARGE_FONT)
    labels['update'].grid(row= 27, column= 5)

#Update the list of episodes of a tv show
def update_show(frame, mainframe, cursor):
    new_win= tk.Toplevel(app)     #Create a new window

    screen_width= 500 
    screen_height=100
    x_pos= 400 
    y_pos= 100 
    new_win.geometry(f'{screen_width}x{screen_height}+{x_pos}+{y_pos}')    #To set the sceen position, width, height
    new_win.title('Update TV Show')

    for row in range(4):
        new_win.rowconfigure(row, weight=1)    
    for col in range(35):
        new_win.columnconfigure(col, weight=1)

    show_name_= tk.StringVar()
    dir_path_= tk.StringVar()

    label1= tk.Label(new_win, text='Enter Show Name: ')
    entry1= tk.Entry(new_win, width= 50, textvariable= show_name_)
    entry1.focus_set()

    label2= tk.Label(new_win, text='Enter Directory Path: ')
    entry2= tk.Entry(new_win, width= 50, textvariable= dir_path_)
    
    label1.grid(row= 0, column= 0)
    entry1.grid(row= 0, column= 1, columnspan= 25)
    label2.grid(row= 1, column= 0)
    entry2.grid(row= 1, column= 1, columnspan= 25)

    def get_and_update_data():
        show_name_list= str(show_name_.get()).strip()
        dir_path= str(dir_path_.get()).strip()
        if show_name_list not in db_handler:
            messagebox.showerror('Incorrect Show Name', "Entered show name is not in the list.")
            return
        show_name= show_name_list.split(' Season ')[0]
        season_number= int(show_name_list.split(' Season ')[1])
        table_name= show_name+ ' Season '+ str(season_number)

        #TV Series Object
        obj= Tv_series(name= show_name, season= int(season_number), path= dir_path)
        if not obj.check_path():
            #If path is invalid, generate a error message
            messagebox.showerror('Invalid Path', "Entered path is not valid.")
            return
        else:
            #Reading Directory and storing episode names
            obj.list_vids()

        old_list= []
        new_list= obj.videos_name
        for name in data[table_name]:
            old_list.append(name[0])
        for name in new_list:
            if name not in old_list:
                db_handler[table_name].one_data_entry(name, seen= False, unseen= True)
        conn.commit()
        data[table_name]= db_handler[table_name].fetch_data()
        new_win.destroy()
        show_list(mainframe, data[table_name], table_name)

    button= tk.Button(new_win, text= 'Submit', command= lambda : get_and_update_data())
    button.grid(row= 3, column=8 )
    


#Main Area
main_area= tk.Frame(app, borderwidth= 5)
main_area.grid(row= 0, column= 1, rowspan= 30, columnspan= 34, sticky = tk.E+ tk.N+ tk.S+ tk.W)


#Sidebar
sidebar= tk.Frame(app, bg= 'gray', relief='sunken', borderwidth=5)
sidebar.grid(row= 0, column= 0, rowspan= 29, columnspan= 1, sticky = tk.W+ tk.N+ tk.S+ tk.E)
label= tk.Label(sidebar, text= 'TV Shows', font= LARGE_FONT, bg= 'cyan', bd= 5, relief= 'sunken')
label.grid(padx= 90, pady= 5)


#Bottombar
bottombar= tk.Frame(app, bg= 'gray', relief='sunken', borderwidth=5)
bottombar.grid(row= 29, column= 0, rowspan= 1, columnspan= 1, sticky=  tk.N+ tk.S+ tk.E+ tk.W )


#Add new folder button
add_button= tk.Button(bottombar, text= 'Add', width= 10, 
    command= lambda  frame=  sidebar, mainframe= main_area, cursor= cur: add_new_show(frame, mainframe, cursor))
add_button.grid(row= 29, column= 0, columnspan= 2, sticky= tk.N+ tk.W, padx= 30, pady= 15)


#Delete Button
dlt_button= tk.Button(bottombar, text= 'Delete', width= 10, 
    command= lambda frame=  sidebar, mainframe= main_area, cursor= cur: delete_show(frame, mainframe, cursor))
dlt_button.grid(row= 29, column= 2, columnspan= 2, sticky= tk.N+ tk.E, padx= 10, pady= 15)


#Update folder button
update_button= tk.Button(bottombar, text= 'Update', width= 10, 
    command= lambda frame=  sidebar, mainframe= main_area, cursor= cur: update_show(frame, mainframe, cursor))
update_button.grid(row= 30, column= 0, columnspan= 2, sticky= tk.S+ tk.W, padx= 30)

#Clear Screen Button
clear_screen_button= tk.Button(bottombar, text= 'Clear Screen', width= 10,
    command= lambda : clear_screen())
clear_screen_button.grid(row= 30, column= 2, columnspan= 2, sticky= tk.S+ tk.E, padx= 10)


#Menu bar
menubar= tk.Menu(app)

editmenu= tk.Menu(menubar, tearoff= 0)
editmenu.add_command(label="Add", 
    command= lambda  frame=  sidebar, mainframe= main_area, cursor= cur: add_new_show(frame, mainframe, cursor))
editmenu.add_command(label="Delete", 
    command= lambda frame=  sidebar, mainframe= main_area, cursor= cur: delete_show(frame, mainframe, cursor))
editmenu.add_command(label="Update", 
    command= lambda frame=  sidebar, mainframe= main_area, cursor= cur: update_show(frame, mainframe, cursor))
editmenu.add_separator()
editmenu.add_command(label="Exit", command= app.quit)
menubar.add_cascade(label="Edit", menu=editmenu)

#Context menu
context_menu= tk.Menu(sidebar, tearoff= 0)
context_menu.add_command(label= 'Add', 
    command= lambda  frame=  sidebar, mainframe= main_area, cursor= cur: add_new_show(frame, mainframe, cursor))
context_menu.add_command(label= 'Delete', 
    command= lambda frame=  sidebar, mainframe= main_area, cursor= cur: delete_show(frame, mainframe, cursor))
context_menu.add_command(label= 'Update', 
    command= lambda frame=  sidebar, mainframe= main_area, cursor= cur: update_show(frame, mainframe, cursor))

sidebar.bind("<Button-3>", lambda event: context_menu.tk_popup(event.x, event.y_root))

create_show_buttons(sidebar, main_area, cur)

app.config(menu= menubar)
app.mainloop()
conn.close()