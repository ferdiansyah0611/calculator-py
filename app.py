from tkinter import *
from tkinter import ttk

class Calculator():
	operator = ("+", "-", "/", "*", ".")
	def __init__(self):
		self.root = Tk()
		self.style = ttk.Style()
		self.style.configure('W.TButton', foreground='black', font=('Arial', 8 ))
		self.root.title("Calculator App")
		# state
		self.input = StringVar()
		# template
		self.mainframe = ttk.Frame(self.root, padding="3 3 12 12")
		self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
		self.root.columnconfigure(0, weight=1)
		self.root.rowconfigure(0, weight=1)
		# input
		self.inputs = ttk.Entry(self.mainframe, state='readonly', textvariable=self.input)
		self.inputs.grid(column=0, row=0, sticky=(W, E), columnspan=3, padx=1)
		# runner±
		# start
		self.number_btn()
		self.resulting()
		self.deleting()
		self.root.mainloop()

	def number_btn(self):
		def minus():
			current = self.input.get()
			if current and current[0] == "-":
				self.input.set(current[1:len(current)])
			else:
				self.input.set('-' + current)

		def making_btn(arg):
			text = arg[0]
			column = arg[1]
			row = arg[2]
			custom_event = False
			def event():
				current = self.input.get()
				if current and current[-1] in self.operator and text in self.operator:
					return
				self.input.set(current + text)

			if len(arg) == 4:
				custom_event = arg[3]
			btn = ttk.Button(self.mainframe, text=text, command=custom_event or event, style='W.TButton')
			btn.grid(column=column, row=row, sticky=W)
		
		listing = [
			("9", 0, 1),
			("8", 1, 1),
			("7", 2, 1),
			("6", 0, 2),
			("5", 1, 2),
			("4", 2, 2),
			("3", 0, 3),
			("2", 1, 3),
			("1", 2, 3),
			("0", 1, 4),
			("+", 3, 1),
			("-", 3, 2),
			("/", 3, 3),
			("*", 3, 4),
			("±", 0, 4, minus),
			(".", 2, 4),
		]

		for btn in listing:
			making_btn(btn)

	def resulting(self):
		def submit():
			self.input.set(eval(self.input.get()))
				
		btn = ttk.Button(self.mainframe, text="=", command=submit)
		btn.grid(column=3, row=5, sticky=W)

	def deleting(self):
		def delete():
			current = self.input.get()
			if current:
				self.input.set(current[0:-1])

		btn = ttk.Button(self.mainframe, text="x", command=delete)
		btn.grid(column=3, row=0, sticky=W)

if __name__ == '__main__':
	Calculator()