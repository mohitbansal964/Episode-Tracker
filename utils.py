import os
import sqlite3

class Tv_series:
	vid_ext= ['.mkv', '.mp4', '.avi', '.flv']
	def __init__(self, name= "", season= 0, path= ""):
		self.name= name
		self.season= season
		self.path= path
		self.videos_name= []

	def check_path(self):
		return os.path.isdir(self.path)

	def list_vids(self):
		if not self.check_path():
			print("Directory does not exist.")
			return
		list_of_files= os.listdir(self.path)
		for file in list_of_files:
			file_ext= os.path.splitext(file)[1]
			if file_ext in Tv_series.vid_ext:
				self.videos_name.append(file)


class Database_handler:
    def __init__(self, cur, obj):
        self.cur= cur
        self.obj= obj
        self.table_name= self.obj.name.replace(' ', '_')+ '_Season_'+ str(self.obj.season)

    def create_table(self):
        self.cur.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name}(Name VARCHAR(100) PRIMARY KEY, Seen BOOLEAN, Unseen BOOLEAN)")

    def one_data_entry(self, vid= "", seen= False, unseen= True):
        self.cur.execute(f'INSERT INTO {self.table_name}(Name, Seen, Unseen) VALUES(?, ?, ?)', (vid, seen, unseen))
        
    def data_entry(self):
        for vid in self.obj.videos_name:
            self.one_data_entry(vid, False, True)

    def drop_table(self):
        self.cur.execute(f'DROP TABLE IF EXISTS {self.table_name}')

    def update(self, seen, episode_name):
        if seen:
            self.cur.execute(f'UPDATE {self.table_name} SET Seen= 1, Unseen= 0 WHERE Name= ?;', (episode_name, ))
        else:
            self.cur.execute(f'UPDATE {self.table_name} SET Seen= 0, Unseen= 1 WHERE Name= ?;', (episode_name, ))

    def delete_row(self, episode_name):
        self.cur.execute(f'DELETE FROM {self.table_name} WHERE Name= ?', (episode_name, ))

    def fetch_data(self):
        data= []
        for row in self.cur.execute(f'SELECT * FROM {self.table_name}'):
            data.append(list(row))
        return data

def fetch_tables(cur):
    tables=[]
    for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table';"):
    	table_name= row[0].replace('_', ' ')
    	tables.append(table_name)
    return sorted(tables)

if __name__== '__main__':
    series_name= input("Enter series name: ")
    season_no= int(input("Enter season number: "))
    dir_path= input("Enter directory's absolute path: ")

    obj= Tv_series(series_name, season_no, dir_path)
    obj.list_vids()

    conn=sqlite3.connect("tv_series_db.db")
    c=conn.cursor()

    db_handler= Database_handler(c, obj)
    db_handler.create_table()
    db_handler.data_entry()
    # db_handler.drop_table()
    # db_handler.update(seen= True, episode_name= 'Brooklyn.Nine-Nine.S03E01.HDTV.x264-BATV.mp4')
    # db_handler.delete_row(episode_name= 'Brooklyn.Nine-Nine.S03E01.HDTV.x264-BATV.mp4')
    data= db_handler.fetch_data()
    print(data)
    conn.commit()
    conn.close()




