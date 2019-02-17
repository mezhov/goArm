import logging


def getLogger(name):
    LOG = logging.getLogger(name)
    LOG.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(name)s - %(message)s')
    fh = logging.FileHandler('log.txt')
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    LOG.addHandler(fh)
    LOG.addHandler(ch)
    return LOG
