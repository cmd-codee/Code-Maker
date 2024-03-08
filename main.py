#Project Libraries: 1. flask - pip(pip3) install flask
from flask import Flask, render_template, redirect, request, make_response
import sqlite3
app = Flask(__name__)
connect = sqlite3.connect('Code_Maker.db', check_same_thread=False)
cursor = connect.cursor()
cursor.execute('''
	CREATE TABLE IF NOT EXISTS Data (
	id INTEGER NOT NULL,
	password TEXT NOT NULL
	)
	''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Files (
    id INTEGER PRIMARY KEY, 
	room_id INTEGER NOT NULL,
	name TEXT NOT NULL,
    file TEXT
	)
''')
#Создание таблиц Data и Files
@app.route('/')
def startpage():
	if request.cookies.get('code') == None:
		return render_template("start.html")
	else:
		return redirect('/code')
	#Стартовая страница 
@app.route("/~", methods=['POST', 'GET'])
def home():
	if request.cookies.get('code') == None:
		if request.method == "POST":
			id = request.form['ID']
			password = request.form['password']
			info = cursor.execute('SELECT * FROM Data WHERE id=?', (id,))
			if info.fetchone() is None: 
				cursor.execute('INSERT INTO Data VALUES (?, ?)', (id, password))
				connect.commit()
				r = make_response(redirect('/code'))
				r.set_cookie('code', id, max_age=60*60*24*365)
				return r
			#Создание аккаунта
			else:
				cursor.execute(f"SELECT id, password FROM Data WHERE id = '{id}' AND password = '{password}'")
				connect.commit() 
				if cursor.fetchone():
					response = make_response(redirect('/code'))
					response.set_cookie('code', id, max_age=60*60*24*365)
					return response
				#Вход в систему
				else:
					error = "❗Неверный пароль❗"
					return render_template('homepage.html', error=error)
				#Тут будет выводится сообщение об ошибке
		return render_template('homepage.html')
	else:
		return redirect('/code')
@app.route('/code', methods=['POST', 'GET'])
def codepage():
	cookie = make_response(redirect('/code'))
	get = request.cookies.get('code')
	gf = request.cookies.get('file')
	if get != None:
		if request.method == 'POST':
			get_f = request.form['name']
			text = request.form['text']
			if text != None:
				sql1 = "SELECT * FROM Files WHERE room_id = ? AND name = ?"
				for row1 in cursor.execute(sql1, (get, gf, )):
					f_id = row1[0]
					print(f_id)
					cursor.execute("Update Files set file = ? where id = ?", (text, row1[0]))
					connect.commit()
					return redirect('/code')
				    #Изменение файла
			if get_f != None:
				check = cursor.execute('SELECT * FROM Files WHERE name=?', (get_f, ))
				if check.fetchone() is None:
					null = ''
					cursor.execute("INSERT INTO Files(room_id, name, file) VALUES (?, ?, ?)", (get, get_f, null))
					cookie.set_cookie('file', f'{get_f}', max_age=60*60*24*365)
					return cookie
					#Добавление файла и его открытие
				else:
					cookie.set_cookie('file', f'{get_f}', max_age=60*60*24*365)
					return cookie
				    #Открыти файла
		if gf != None:
			sql = "SELECT * FROM Files WHERE room_id = ? AND name = ?"
			for row in cursor.execute(sql, (get, gf, )):
				content = row[3]
				return render_template('codepage.html', get=get, content=content, gf=gf)
			else:
				return render_template('codepage.html', get=get, gf=gf)
		else:
			return render_template('codepage.html', get=get)
		#Данная конструкция необходима для получение содержания файла
	else:
		return redirect('/~')
@app.route('/l')
def l():
	respon = make_response(redirect('/~'))
	respon.delete_cookie('code')
	respon.delete_cookie('file')
	return respon
#Выход из системы
@app.route('/._')
def d():
	cursor.execute('DELETE FROM Data WHERE id = ?', (str(request.cookies.get('code')),))
	cursor.execute('DELETE FROM Files WHERE room_id = ?', (str(request.cookies.get('code')),))
	connect.commit()
	re = make_response(redirect('/~'))
	re.delete_cookie('code')
	re.delete_cookie('file')
	return re
#Удаление комнаты
@app.errorhandler(404)
def error(e):
	if request.cookies.get('code') is None:
		return redirect('/~')
	else:
		return redirect('/code')
	#Сделал что-бы не перегружались страницы
@app.route('/df')
def df():
	if request.cookies.get('file') != None:
		cookies = make_response(redirect('/code'))
		cursor.execute("DELETE FROM Files WHERE room_id=? AND name=?", (request.cookies.get('code'), request.cookies.get('file')))
		cookies.delete_cookie('file')
		return cookies
		connect.commit()
	else:
		return redirect('/code')
if __name__ == "__main__":
	app.run()#Для теста в скобки добавте debug=True
