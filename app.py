from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    print("打印字符, Flask!111111")
    return "Hello, Flask!222222"

if __name__ == '__main__':
    app.run(debug=True)


