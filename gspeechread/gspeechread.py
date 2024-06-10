#!/usr/bin/env python3

# V. 0.1

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GLib, GObject
from gi.repository.GdkPixbuf import Pixbuf
import os
import sys
from time import time, sleep
import subprocess

#from module_inout import speakThread

WINW = 800
WINH = 40

# the window for the microphone
mic_win = 0

# ddata = None

from cfg import *
lang_language = lang
# from sostituzioni import *
module_substitutions = "substitutions_{}".format(lang_language)
import importlib

try:
    lang_module = importlib.import_module(module_substitutions)
except:
    # default language en
    lang_module = importlib.import_module("substitutions_en")

signs_without_pre_space = lang_module.signs_without_pre_space
signs_end_of_sentence = lang_module.signs_end_of_sentence
signes_with_pre_space = lang_module.signes_with_pre_space
signs_with_spaces = lang_module.signs_with_spaces
signs_symbols = lang_module.signs_symbols
signs_without_spaces = lang_module.signs_without_spaces
DELETE = lang_module.DELETE
DELETE_WORD = lang_module.DELETE_WORD
DELETE_PAR = lang_module.DELETE_PAR
SEND=lang_module.SEND
DELETE_HISTORY=lang_module.DELETE_HISTORY
RETURN = lang_module.RETURN
DELETE=lang_module.DELETE
RETURN=lang_module.RETURN
MIC=lang_module.MIC
READ=lang_module.READ
QUESTION=lang_module.QUESTION
ANSWER=lang_module.ANSWER
START=lang_module.START
STOP=lang_module.STOP
MICROPHONE=lang_module.MICROPHONE
CLOSE=lang_module.CLOSE
STARTSTOP=lang_module.STARTSTOP
EXIT=lang_module.EXIT

import threading

# if len(sys.argv) == 2 and sys.argv[1] == "-p":
    # from pynput.keyboard import Controller, Key
    # keyboard = Controller()

import argparse
import queue
import sys
import sounddevice as sd
from vosk import Model, KaldiRecognizer

################################

# audio device list
audio_dev = sd.query_devices()
audio_dev_list = list(audio_dev)

ddev = None
# asamplerate = 44100
num_channels = 1


for adev in audio_dev_list:
   if adev["max_input_channels"] == 0:
       continue
   if adev["name"] == mic:
       ddev = adev["index"]
       asamplerate = int(adev["default_samplerate"])
       num_channels = int(adev["max_input_channels"])
       break
#
if msamplerate != -1:
    asamplerate = msamplerate

#
if numch != -1:
    num_channels = numch

q = queue.Queue()


is_ready = 1
if ddev == None:
    is_ready = 0
    
########################

from module_inout import speakClass

###########

thread_stop = False

w_text_buffer = None
w_text_bufferr = None

##################

is_started = 0
threadc = None
def t_start(_signal):
    global threadc
    if is_ready:
        global is_started
        is_started = 1
        threadc = cThread(sd, q, ddev, asamplerate, num_channels, w_text_buffer, _signal)
        threadc.start()

################## window ####################

class mainWindow(Gtk.Window):
    
    def __init__(self, wtype):
        Gtk.Window.__init__(self, title="Gspeachread")
        self.wtype = wtype
        self.set_border_width(4)
        self.resize(1200, 800)
        self.connect("destroy", self.t_exit)
        #
        self._signal = SignalObject()
        self._signal.connect("notify::propInt", self.on_notify_signal_int)
        self._signal.connect("notify::propList", self.on_notify_signal_list)
        #
        if self.wtype:
            self.set_resizable(False)
        self.set_position(1)
        #
        self.vbox = Gtk.Box(orientation=1, spacing=10)
        self.add(self.vbox)
        #
        if self.wtype == 0:
            hbox = Gtk.Box(orientation=0, spacing=0)
            self.vbox.pack_start(hbox, False, False, 1)
        #
        if mic_on_at_start == 0:
            _mlabel = MIC+" OFF"
        else:
            _mlabel = MIC+" ON"
        self._startbtn = Gtk.Button(label=_mlabel)
        self._startbtn.connect("clicked", self._btnpause)
        if self.wtype == 0:
            hbox.pack_start(self._startbtn, True, False, 1)
        else:
            self.vbox.pack_start(self._startbtn, False, False, 1)
        #
        self.can_speak = 0
        self._speak_btn = Gtk.Button(label=READ+" OFF")
        self._speak_btn.connect("clicked", self.on_speak_btn)
        hbox.pack_start(self._speak_btn, False, False, 1)
        #
        self._micbtn = Gtk.Button(label=MICROPHONE)
        self._micbtn.connect("clicked", self.set_mic)
        if self.wtype == 0:
            hbox.pack_start(self._micbtn, True, False, 1)
        else:
            self.vbox.pack_start(self._micbtn, False, False, 1)
        #
        self._closebtn = Gtk.Button(label=CLOSE)
        self._closebtn.connect("clicked", self.t_exit)
        if self.wtype == 0:
            hbox.pack_start(self._closebtn, True, False, 1)
        else:
            self.vbox.pack_start(self._closebtn, False, False, 1)
        #
        if self.wtype == 0:
            ###### output box
            self.r_box = Gtk.Box(orientation=0, spacing=0)
            self.vbox.pack_start(self.r_box, True, True, 1)
            #
            scrolledwindowr = Gtk.ScrolledWindow()
            scrolledwindowr.set_hexpand(True)
            scrolledwindowr.set_vexpand(True)
            # disable horizontal scrollbar
            scrolledwindowr.set_policy(2, 1)
            self.r_box.pack_start(scrolledwindowr, True, True, 1)
            #
            self.textviewr = Gtk.TextView()
            self.textviewr.set_wrap_mode(2)
            self.textviewr.set_editable(False)
            scrolledwindowr.add(self.textviewr)
            self.textbufferr = self.textviewr.get_buffer()
            self.textbufferr.connect("changed", self.on_tbr_changed)
            global w_text_bufferr
            w_text_bufferr = self.textbufferr
            riter_start = self.textbufferr.get_start_iter()
            # mark
            self.riter_start = self.textbufferr.create_mark("IterStart",riter_start,True)
            del riter_start
            #
            self._text_full = ""
            #
            ###### input box
            scrolledwindow = Gtk.ScrolledWindow()
            scrolledwindow.set_hexpand(True)
            scrolledwindow.set_vexpand(True)
            # disable horizontal scrollbar
            scrolledwindow.set_policy(2, 1)
            self.vbox.pack_start(scrolledwindow, True, True, 1)
            self.textview = Gtk.TextView()
            # word
            self.textview.set_wrap_mode(2)
            scrolledwindow.add(self.textview)
            self.textbuffer = self.textview.get_buffer()
            global w_text_buffer
            w_text_buffer = self.textbuffer
            ####
            # buttons
            self.b_box = Gtk.Box(orientation=0, spacing=0)
            self.vbox.pack_start(self.b_box, False, False, 1)
            #
            self.send_btn = Gtk.Button(label=SEND)
            self.send_btn.connect("clicked", self.on_send_btn)
            self.b_box.pack_end(self.send_btn, False, False, 1)
        #
        global is_ready
        if is_ready == 0:
            global mic_win
            if not mic_win:
                win = MicWindow()
                win.show_all()
                mic_win = 1
        #
        self.show_all()
        #
        if mic_on_at_start:
            t_start(self._signal)
        #
        self.textview.grab_focus()
        #
        self._sc = speakClass(self._signal,self)
        
    
    def on_speak_btn(self, _btn):
        if self.can_speak == 0:
            _btn.set_label(READ+" ON")
            self.can_speak = 1
        elif self.can_speak == 1:
            _btn.set_label(READ+" OFF")
            self.can_speak = 0
    
    def on_send_btn(self, _btn):
        self._f_on_notify_signal_int(1)
        
    def on_notify_signal_int(self, obj, gparamstring):
        ret_sig = self._signal.propInt
        self._f_on_notify_signal_int(ret_sig)
        # speech terminate
        if ret_sig == -77:
            # clear the input widget
            iter_start = self.textbuffer.get_start_iter()
            iter_end = self.textbuffer.get_end_iter()
            self.textbuffer.delete(iter_start,iter_end)
            del iter_start
            del iter_end
            self._signal.propInt = -99
        
    def on_notify_signal_list(self, obj, gparamstring):
        pass
        
    def _f_on_notify_signal_int(self, ret_sig):
        if ret_sig == 1:
            # get the text from the input widget
            iter_start = self.textbuffer.get_start_iter()
            iter_end = self.textbuffer.get_end_iter()
            _text = self.textbuffer.get_text(iter_start, iter_end, True)
            del iter_start
            del iter_end
            #
            returned_text = self._sc.send_data(_text)
            self._text_full = returned_text
            # write the text to the output widget
            _text2 = "*"+QUESTION+":\n"+_text+"\n\n"+"*"+ANSWER+":\n"
            next_text = _text2+returned_text
            iterr = self.textbufferr.get_end_iter()
            self.textbufferr.insert(iterr, next_text+" ")
            del iterr
            #
            # move forward the mark in the text buffer
            riter_end = self.textbufferr.get_end_iter()
            self.textbufferr.move_mark(self.riter_start, riter_end)
            self.textviewr.scroll_to_iter(riter_end,0.0,True,1,1)
            del riter_end
    
    # output widget
    def on_tbr_changed(self, _tbobj):
        #
        if self._signal.propName == "-111":
            return
        #
        if self._text_full != "":
            self._signal.propName = "-111"
            #
            if self.can_speak == 1:
                _speakThread = speakThread(self._text_full, self._signal)
                _speakThread.start()
            else:
                self._signal.propInt = -77
            # 
            self._text_full = ""
            #
            self._signal.propName = ""
    
    def _btnpause(self, w):
        if w.get_label() == (MIC+" ON"):
            w.set_label(MIC+" OFF")
            self._micbtn.set_sensitive(True)
            self._signal.propInt = -111
            #
            self.textview.grab_focus()
        else:
            global mic_on_at_start
            self._micbtn.set_sensitive(False)
            #
            if mic_on_at_start == 0:
                mic_on_at_start = 1
                t_start(self._signal)
            #
            sleep(3)
            w.set_label(MIC+" ON")
            #
            self._signal.propInt = -99
            #
            self.textview.grab_focus()
    
    def t_exit(self, w):
        self._signal.propInt = -9
        Gtk.main_quit()
    
    def set_mic(self, widget):
        global mic_win
        if not mic_win:
            win = MicWindow()
            win.show_all()
            mic_win = 1

########################

class speakThread(threading.Thread):
    def __init__(self, _text, _signal):
        super(speakThread, self).__init__()
        self._text = _text
        self._signal = _signal
        
    def run(self):
        try:
            _cmd = ["./speakerVoice1.sh", self._text]
            subprocess.call(_cmd)
            self._signal.propInt = -77
            return
        except:
            self._signal.propInt = -77
            return

########################

class SignalObject(GObject.Object):
    
    def __init__(self):
        GObject.Object.__init__(self)
        self._name = ""
        self.value = -99
        self._list = []
    
    @GObject.Property(type=str)
    def propName(self):
        'Read-write integer property.'
        return self._name

    @propName.setter
    def propName(self, name):
        self._name = name
    
    @GObject.Property(type=int)
    def propInt(self):
        'Read-write integer property.'
        return self.value

    @propInt.setter
    def propInt(self, value):
        self.value = value
    
    @GObject.Property(type=object)
    def propList(self):
        'Read-write integer property.'
        return self._list

    @propList.setter
    def propList(self, data):
        self._list = []
        self._list.append(data)
        

class cThread(threading.Thread):
    def __init__(self, sd, q, ddev, samplerate, num_ch, w_text_buffer, _signal):
        super(cThread, self).__init__()
        self.ii = 0
        self.sd = sd
        self.q = q
        self.ddev = ddev
        self.samplerate = samplerate
        self.num_ch = num_ch
        self.w_text_buffer = w_text_buffer
        self._signal = _signal
        
    def _callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print("STATUS",status, file=sys.stderr)
        self.q.put(bytes(indata))
    
    def run(self):
        while True:
            with self.sd.RawInputStream(samplerate=self.samplerate, blocksize = 8000, device=self.ddev,
                dtype="int16", channels=self.num_ch, callback=self._callback):
                rec = KaldiRecognizer(Model("models/{}".format(lang_language)), self.samplerate)
                #
                # first word capitalized
                word_capitalized = 1
                #
                while self._signal.propInt != -9:
                    #
                    if self._signal.propName == "-111":
                        if not self.q.empty():
                            self.q.clear()
                        continue
                    data = self.q.get()
                    if rec.AcceptWaveform(data):
                        rddata = rec.Result().strip("\n")
                        #
                        text_to_send = rddata[2:-2].split(":")[1][2:-1]
                        #
                        if text_to_send == "":
                            continue
                        # type comma
                        elif text_to_send in signs_without_pre_space:
                            chart = signs_without_pre_space[text_to_send]
                            if self.w_text_buffer:
                                iter_start = self.w_text_buffer.get_end_iter()
                                iter_start.backward_char()
                                self.w_text_buffer.delete(iter_start, self.w_text_buffer.get_end_iter())
                                del iter_start
                                sleep(0.2)
                                self.w_text_buffer.insert(self.w_text_buffer.get_end_iter(), chart+" ")
                            else:
                                WM._delete_char()
                                WM._write_text(chart)
                                WM._write_text(" ")
                            #
                            if chart in signs_end_of_sentence:
                                word_capitalized = 1
                            continue
                        # one space before and after
                        elif text_to_send in signes_with_pre_space:
                            chart = signes_with_pre_space[text_to_send]
                            if self.w_text_buffer:
                                iter = self.w_text_buffer.get_end_iter()
                                self.w_text_buffer.insert(iter, chart)
                                del iter
                            else:
                                WM._write_text(chart)
                            continue
                        # one space after
                        elif text_to_send in signs_with_spaces:
                            chart = signs_with_spaces[text_to_send]
                            if self.w_text_buffer:
                                iter = self.w_text_buffer.get_end_iter()
                                self.w_text_buffer.insert(iter, chart+" ")
                                del iter
                            else:
                                WM._write_text(chart)
                                WM._write_text(" ")
                            continue
                        # symbols
                        elif text_to_send in signs_symbols:
                            chart = signs_symbols[text_to_send]
                            if self.w_text_buffer:
                                iter = self.w_text_buffer.get_end_iter()
                                self.w_text_buffer.insert(iter, chart+" ")
                                del iter
                            else:
                                WM._write_text(chart)
                                WM._write_text(" ")
                            continue
                        # without any spaces before and after
                        elif text_to_send in signs_without_spaces:
                            chart = signs_without_spaces[text_to_send]
                            if self.w_text_buffer:
                                iter_start = self.w_text_buffer.get_end_iter()
                                self.w_text_buffer.insert(iter_start, chart)
                                del iter_start
                            else:
                                WM._delete_char()
                                WM._write_text(chart)
                            continue
                        # delete the last character
                        elif text_to_send == DELETE:
                            if self.w_text_buffer:
                                iter_start = self.w_text_buffer.get_end_iter()
                                iter_start.backward_char()
                                self.w_text_buffer.delete(iter_start, self.w_text_buffer.get_end_iter())
                                del iter_start
                            else:
                                WM._delete_char()
                            continue
                        # delete an entire word (up to the previous space)
                        elif text_to_send == DELETE_WORD:
                            _i = 0
                            if self.w_text_buffer:
                                iter_start = self.w_text_buffer.get_end_iter()
                                iter_start.backward_char()
                                iter_start.backward_word_start()
                                _text = self.w_text_buffer.get_text(iter_start, self.w_text_buffer.get_end_iter(), True)
                                _i = len(_text)
                                self.w_text_buffer.delete(iter_start, self.w_text_buffer.get_end_iter())
                                del iter_start
                            else:
                                if _i:
                                    for i in range(_i-1):
                                        WM._delete_char()
                            continue
                        # delete an entiry paragraph (up to the previous period)
                        elif text_to_send == DELETE_PAR:
                            _i = 0
                            if self.w_text_buffer:
                                iter_start = self.w_text_buffer.get_end_iter()
                                iter_start.backward_char()
                                iter_start.backward_line()
                                _text = self.w_text_buffer.get_text(iter_start, self.w_text_buffer.get_end_iter(), True)
                                _i = len(_text)
                                self.w_text_buffer.delete(iter_start, self.w_text_buffer.get_end_iter())
                                del iter_start
                            else:
                                if _i:
                                    for i in range(_i-1):
                                        WM._delete_char()
                            word_capitalized = 1
                            continue
                        # send
                        elif text_to_send == SEND:
                            if text_to_send.strip():
                                self._signal.propInt = 1
                                word_capitalized = 1
                            continue
                        # new line
                        elif text_to_send == RETURN:
                            if self.w_text_buffer:
                                iter = self.w_text_buffer.get_end_iter()
                                self.w_text_buffer.insert(iter, "\n")
                                del iter
                            else:
                                WM._new_line()
                            #
                            word_capitalized = 1
                            continue
                        #
                        if word_capitalized:
                            text_to_send = text_to_send[0].upper()+text_to_send[1:]
                            word_capitalized = 0
                        #
                        if self.w_text_buffer:
                            iter = self.w_text_buffer.get_end_iter()
                            self.w_text_buffer.insert(iter, text_to_send+" ")
                            del iter
                        else:
                            WM._write_text(text_to_send)
                            WM._write_text(" ")
                    
                    #
                else:
                    break
            return

    
################## Microphone ##################

class MicWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="")
        self.connect("destroy", self.wclose)
        self.set_border_width(4)
        self.resize(WINW, WINH)
        self.set_keep_above(True)
        #
        self.set_resizable(False)
        self.set_position(1)
        #
        self.vbox = Gtk.Box(orientation=1, spacing=10)
        self.add(self.vbox)
        #
        self.label1 = Gtk.Label(label="{}".format(MICROPHONE))
        # 
        self.vbox.pack_start(self.label1, True, True, 1)
        #
        self.label2 = Gtk.Label(label="{}".format("(Restart the program)"))
        self.vbox.pack_start(self.label2, True, True, 1)
        #
        self.miccombo = Gtk.ComboBoxText()
        self.miccombo.props.hexpand = True
        #
        for adev in audio_dev_list:
            if adev["max_input_channels"] == 0:
                continue
            self.miccombo.append(str(adev["index"]), adev["name"])
        #
        mmm = self.miccombo.get_model()
        #
        for ie in range(len(mmm)):
            if str(mmm[ie][0]) == str(mic):
                self.miccombo.set_active(ie)
                break
        #
        self.miccombo.connect('changed', self.miccombo_changed)
        #
        self.vbox.pack_start(self.miccombo, True, True, 1)
        #
        self.button2 = Gtk.Button(label=CLOSE)
        self.button2.connect("clicked", self.cclose)
        self.button2.props.valign = 2
        self.vbox.pack_start(self.button2, True, True, 1)
        #
        
    def miccombo_changed(self, w):
        global mic
        mic = self.miccombo.get_active_text()
    
    def wclose(self, w):
        if mic == "":
            self.destroy()
        #
        global mic_win
        mic_win = 0
        #
        with open("cfg.py", "w") as ff:
            ff.write('mic="{}"\n'.format(mic))
            ff.write("asamplerate={}\n".format(asamplerate))
            ff.write("msamplerate={}\n".format(msamplerate))
            ff.write("numch={}\n".format(numch))
            ff.write('lang="{}"\n'.format(lang_language))
            ff.write('mic_on_at_start="{}"'.format(mic_on_at_start))
        #
        # self._signal.propInt = -9
        #
        self.destroy()
        Gtk.main_quit()
    
    def cclose(self, w):
        self.destroy()
    
    
########

m = mainWindow(0)

Gtk.main()

