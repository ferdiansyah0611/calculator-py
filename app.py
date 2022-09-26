import sqlite3
from datetime import datetime

import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty

from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

Window.size = (360, 480)
Window.clearcolor = '#121212'
sm = ScreenManager()
screens = []
primary = '#F5A541'


class Database:
	def __init__(self):
		self.connect = sqlite3.connect('db.sqlite3')
		self.execute = self.connect.execute
		self.execute('''CREATE TABLE IF NOT EXISTS history
		(
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			value TEXT NOT NULL,
			result TEXT NULL,
			last_action TEXT NOT NULL
		)
		''')

	def add_history(self, data):
		value = data['value']
		result = data['result']
		last_action = datetime.now()
		self.execute(f"INSERT INTO history (value, result, last_action) VALUES ('{value}', '{result}', '{last_action}')")
		self.connect.commit()

	def delete_history(self):
		self.execute(f"DELETE FROM history")
		self.connect.commit()

	def next(self, name, last_index, total):
		data = self.execute(f'SELECT * FROM {name} WHERE id > {last_index} LIMIT {total}')
		return data.fetchall()

	def previous(self, name, first_index, total):
		data = self.execute(f'SELECT * FROM {name} WHERE id < {first_index} LIMIT {total}')
		return data.fetchall()

class HISTORY(Screen):
	item = []
	page = 0
	total = 20
	response = None
	def __init__(self, **kwargs):
		super(HISTORY, self).__init__(**kwargs)
	def build(self, is_next):
		global db
		container = BoxLayout(orientation='vertical')
		root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height - 50))
		grid = self.grid = GridLayout(cols=1, padding=[10, 10], size_hint_y=None, spacing=10)
		grid.bind(minimum_height=grid.setter('height'))

		def back(instance):
			sm.switch_to(screens[0], direction='right')
		def clear_all(instance):
			db.delete_history()
			self.on_pre_leave()

		if self.page == 0:
			response = self.response = db.next('history', self.page, self.total)

		elif is_next:
			if self.response and len(self.response):
				response = self.response = db.next('history', self.response[-1][0], self.total)
			else:
				response = self.response = db.next('history', self.page, self.total)
		else:
			if self.response and len(self.response):
				response = self.response = db.previous('history', self.response[0][0], self.total)
			else:
				response = self.response = db.previous('history', self.page, self.total)

		for i in response:
			item = BoxLayout(size_hint_y=None, height=50)
			_id = Label(text=str(i[0]), size_hint_x=None, width=50)
			label = Label(text=i[1], size_hint_x=None, width=200)
			label_1 = Label(text='= ' + i[2], size_hint_x=None, width=50, halign='right', valign='middle')
			label_1.text_size = label_1.size

			item.add_widget(_id)
			item.add_widget(label)
			item.add_widget(label_1)
			grid.add_widget(item)
			self.item.append(item)

		action = BoxLayout(padding=[10, 10])
		action.add_widget(Button(text='Next', on_press=self.next, background_color='#706F6F'))
		action.add_widget(Button(text='Previous', on_press=self.previous, background_color='#706F6F'))
		action.add_widget(Button(text='Back', on_press=back, background_color='#706F6F'))
		action.add_widget(Button(text='Clear All', on_press=clear_all, background_color='red'))

		root.add_widget(grid)
		container.add_widget(root)
		container.add_widget(action)
		self.add_widget(container)

	def next(self, instance):
		if len(self.response) < self.total: return
		self.page += 1
		self.on_pre_leave()
		self.build(True)

	def previous(self, instance):
		if self.page == 0: return
		self.page -= 1
		self.on_pre_leave()
		self.build(False)

	def on_pre_enter(self):
		self.build(False)

	def on_pre_leave(self):
		for i in self.item:
			self.grid.remove_widget(i)

class HOME(Screen):
	operator = ['/', '*', '+', '-', '%']
	def __init__(self, **kwargs):
		super(HOME, self).__init__(**kwargs)
		global db, sm, screens
		# config
		layout = BoxLayout(orientation='vertical')
		template = GridLayout(cols=2, spacing=5)
		numbering = GridLayout(cols=4, padding=[10, 19])
		# action
		def inject_text(instance):
			value = ''
			if instance.text == 'x':
				value = '*'
			else:
				value = instance.text

			if self.result.text and self.result.text[-1] in self.operator and value in self.operator:
				return

			self.result.text = self.result.text + value
		def counting(instance):
			try:
				commit = dict()
				commit['value'] = self.result.text

				result = eval(self.result.text)
				self.result.text = str(result)

				commit['result'] = str(result)
				db.add_history(commit)
			except:
				pass
		def deleting(instance):
			self.result.text = self.result.text[0:-1]
		def minus(instance):
			current = self.result.text
			if current and current[0] == "-":
				self.result.text = current[1:len(current)]
			else:
				self.result.text = '-' + current
		def ac(instance):
			self.result.text = ''
		def switch_to_history(instance):
			sm.switch_to(screens[1], direction='left')

		# mc mr m+ m- ms M
		listing = [
			('AC', ac, None, primary),
			('<', deleting, None, primary),
			('±', minus),
			('/', inject_text),
			('7', inject_text),
			('8', inject_text),
			('9', inject_text),
			('x', inject_text),
			('4', inject_text),
			('5', inject_text),
			('6', inject_text),
			('-', inject_text),
			('1', inject_text),
			('2', inject_text),
			('3', inject_text),
			('+', inject_text),
			('%', inject_text),
			('0', inject_text),
			('.', inject_text),
			('=', counting, primary),
		]
		for i in listing:
			arg = dict()
			arg['text'] = i[0]
			arg['on_press'] = i[1]
			if i[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
				arg['background_color'] = '#494949'
			else:
				arg['background_color'] = '#706F6F'

			numbering.add_widget(Button(**arg, size_hint_y=None, height=50))

		# result
		self.result = Label(text='', size_hint_y=None, height=100, font_size=20)

		box_memory = BoxLayout(size_hint_y=None)
		box_memory.add_widget(Button(text='History', color='#C0BFBF', on_press=switch_to_history, size_hint_y=None, height=25, background_color=(0, 0, 0, 0)))

		layout.add_widget(self.result)
		layout.add_widget(box_memory)
		layout.add_widget(numbering)
		self.add_widget(layout)

class Calculator0611(App):
	def build(self):
		global screens, db
		db = Database()
		screens = [
			HOME(name='home'),
			HISTORY(name='history'),
		]
		for i in screens:
			sm.add_widget(i)
		return sm

if __name__ == '__main__':
	Calculator0611().run() 