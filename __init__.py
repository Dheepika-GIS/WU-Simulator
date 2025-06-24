def classFactory(iface):
    from .wu_simulator import WUSimulator
    return WUSimulator(iface)
