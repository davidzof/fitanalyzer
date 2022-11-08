import configparser
import logging
from tkinter.messagebox import showinfo

from fit_analyzer.model import analysis
from fit_analyzer.model.fitfileparse import load_fitfile, load_hrv

logger = logging.getLogger("configuration")
logger.setLevel(logging.DEBUG)


class Singleton(object):
    _instances = {}

    def __new__(class_, *args, **kwargs):
        if class_ not in class_._instances:
            class_._instances[class_] = super(Singleton, class_).__new__(class_, *args, **kwargs)
        return class_._instances[class_]


class Configuration(Singleton):
    filename = None
    name_changed = False

    def __init__(self):
        self.hrv=None
        self.dfr=None
        self.clients = {}
        # Read Configuration
        config = configparser.ConfigParser()
        config.read('properties.ini')
        self.min_hr = int(config['DEFAULT']['MinHR'])
        self.max_hr = int(config['DEFAULT']['MaxHR'])
        self.zones = eval(config['HEARTRATE_ZONES']['zones'])

        #with open('properties.ini', 'w') as configfile:
        #    config.write(configfile)

    def setFileName(self, filename):
        self.filename = filename
        self.name_changed = True

    def getZones(self):
        return self.zones

    def getMaxMinHR(self):
        return self.max_hr, self.min_hr

    def getFileName(self):
        return self.filename

    def getFitData(self):
        """

        Returns
        -------

        """
        if self.filename is None:
            showinfo(
                title='Error',
                message="You need to load a FIT file first")
            return
        elif self.name_changed is True or self.dfr is None:
            self.dfr = load_fitfile(self.filename, self.max_hr, self.min_hr)
            self.name_changed = False

        return self.dfr

    def getHRVData(self, master):
        """

        Returns
        -------

        """
        if self.filename is None:
            showinfo(
                title='Error',
                message="You need to load a FIT file first")
            return
        elif self.name_changed is True or self.hrv is None:
            df = load_hrv(self.filename)
            self.hrv = analysis.computeFeatures(df, 0, master)
            self.name_changed = False

        return self.hrv
        pass
