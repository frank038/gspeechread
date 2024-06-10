# gspeechread
A simple speech-to-text and text-to-speech program/frontend.

Made for fun. Free to use and modify.

Requirements:
- python3
- gtk3 binding
- everything else needed by the other internal module (just launch this program from terminal and read the errors).

This program is divided in two sections: the first section is for the output, the second is for the input. The input can come from a microphone (which is enabled by default, it can be stopped but never deactivated) using the included vosk text-to-speech engine, or a keyboard. The submit button just send the input to the module module_inout.py that elaborates the text received and sends back another text (actually, this module just sends back what has been received, because it is a demonstration module). After the text has been written in the output section, it can be also read by a text-to-speech program if enabled by using the script speakerVoice1.sh (actually setted for epeak-ng with the en voice).

Two voices included, english (the default) and italian. More voices can be added. In the config file cfg.py just choose the language you want to use, e.g. en or it or else (voices in the models folder).

While this program has been written for a personal specific use case, I've made it generic: write the input, elaborate the input, send and write the output, read it.

If used with a microphone, relaunch the program after any change.

Some personalizations in the cfg.py config module.

Important: Download this program from the release link, because of the two model languages included needed by vosk.

May have a lot of issues, but it works as intended so far.

In speech-to-text mode, the following fixed list of commands are accepted:

DELETE="backspace"
DELETE_WORD="delete word"
DELETE_PAR="delete paragraph"
RETURN="new line"
SEND="submit"
DELETE_HISTORY="delete chronology"

and some customizable pattern substitutions are also accepted (all in the cfg.py file).

