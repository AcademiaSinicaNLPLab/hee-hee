from flask import Flask, render_template, url_for, make_response, Response, jsonify, request
import sys, json, os

sys.path.append('../')

from ChineseTokenizer import ChineseTokenizer
#from CKIPTokenizer import CKIPTokenizer

app = Flask(__name__)

#ckip_tknz  = CKIPTokenizer()
jieba_tknz = ChineseTokenizer()

@app.route('/')
def render_index():
    return render_template( 'index.html' )

@app.route('/api/tokenize/')
@app.route('/api/tokenize/<text>/')
def api_tokenize(text=""):
    #ckip_res  = ckip_tknz.tokenizeStr(text)
    jieba_res = jieba_tknz.tokenize(text)
    return jsonify({'raw':text, 'res':jieba_res, 'tokenizer':'jieba'})

if __name__ == "__main__":
    import getopt, sys
    _port = 5000
    app.debug = False
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],'p:d',['port=', 'debug'])
    except getopt.GetoptError:
        exit(2)

    for opt, arg in opts:
        if opt in ('-p', '--port'): _port = int(arg.strip())
        elif opt in ('-d','--debug'): app.debug = True

    app.run(host='0.0.0.0', port=_port)
