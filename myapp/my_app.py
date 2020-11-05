from flask import Flask, redirect, url_for, request, jsonify

app = Flask(__name__)


@app.route('/success/<name>')
def success(name):
    return 'welcome %s' % name


@app.route('/', methods=['POST', 'GET'])
def login():
    return jsonify(args=request.args.get("name"), form=request.form.get('data'))


if __name__ == '__main__':
    app.run(port=8888,host='0.0.0.0')
