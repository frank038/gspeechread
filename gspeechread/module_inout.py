
class speakClass():
    def __init__(self, _signal, _parent):
        # CODE 55 for any kind of error, if no the expected output will be send
        # CODE 66 after any text has been sent
        # self._signal.propList = ["TEXT_SEND", CODE]
        self._signal = _signal
        self._parent = _parent
        
    
    def send_data(self, _text):
        self._signal.propList = ["TEXT_SEND",66]
        return _text+"\n\n"

