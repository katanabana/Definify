from flask import Flask, session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key'


@app.route('/')
def start():
    a = object()
    session['a'] = a
    print(a is session.get(a))
    return 's'


app.run()
