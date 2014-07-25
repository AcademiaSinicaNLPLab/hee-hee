# -*- coding: utf-8 -*-
import sys
sys.path.append('/tools/CKIPServer')

import logging

from CKIPClient import *
import os, codecs

from functools import wraps
import signal, errno

from sys import stdout

class TimeoutError(Exception):
    pass


def timeout(seconds=10, error_messages=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            #print "Time out "
            raise TimeoutError(error_messages)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result
        return wraps(func)(wrapper)
    return decorator


class Tokenizer:
    """
    A python wrap for CKIP tokenizer under the client-server architecture.
    """
    options = { 'server': 'doraemon.iis.sinica.edu.tw',
                'port': 1502,

                'divide': 1000,
                'encoding': 'UTF-8',
                'pos': True,
                'uwe': True,
                'xml': False }    

    def __init__(self, **kwargs):
        """
        [options]
        server  :CKIP server address
                 default: doraemon.iis.sinica.edu.tw
        port    :CKIP server port
                 default: 1502
        """

        ## update options
        self.options.update(kwargs)

        ## set server, default: doraemon
        # server = 'doraemon.iis.sinica.edu.tw' if 'server' not in options else options['server']
        ## set port, default: 1502
        # port = 1502 if 'port' not in options else options['port']
        # connect to CkipServer
        self.srv = CkipSrv("wordseg","1234", server=self.options['server'], port=self.options['port'])

        ## set logging level
        ## default level: INFO
        loglevel = logging.DEBUG if 'verbose' in options and options['verbose'] == True else logging.INFO
        logging.basicConfig(format='[%(levelname)s] %(message)s', level=loglevel)

    @timeout(30)
    def tokenizeStr(self, text):
        """
        input: plain text
        output: tokenized results
        """
        try:
            res = self.srv.segStr(text, self.options)
        except TimeoutError:
            logging.warn("tokenizeStr timeout")
            return None
        else:
            logging.debug("got tokenized result: %s" % (res.strip().decode('utf-8')))
            return res

    def tokenizeFile(self, infile, outfile):
        """
        input: an file containing text (separated by '\\n')
        output: save tokenized text in file
        """
        with codecs.open(infile, 'r', 'utf-8') as f:
            lines = f.read().strip().split('\n')
        
        outf = codecs.open(outfile, 'w', 'utf-8')

        for i, l in enumerate(lines):    
            print str(i) + " " + l.encode('utf-8')
            # stdout.write("\r%d %s" % (i, l.encode('utf-8')))
            # stdout.flush()

            res = self.tokenizeStr(l.encode('utf-8'))
            if res is not None:
                outf.write(res.strip().decode('utf-8') + '\n')
        outf.close()

if __name__ == "__main__":

    tknz = Tokenizer()

    # bad sentence
    # print tknz.tokenizeStr('如果你需要時間好好冷靜的思考.......沒關係......我願意等你.......無論多久我都會等你........等你準備好了.........等你願意見我.......我不會再讓你擔心.......我也會按時吃飯........也會好好照顧自己.......你說的我都答應你........真的.......我說的都是真的.........請你相信 我.......... 小黑豬不會和小白豬分開的......就算有........也只是短暫的')
    
    # test sentence
    print tknz.tokenizeStr('我在臺灣清華大學念碩士')


