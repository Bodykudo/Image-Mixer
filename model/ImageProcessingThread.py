from PyQt6.QtCore import QThread, pyqtSignal
from model.Mixer import Mixer


class ImageProcessingThread(QThread):
    processingDone = pyqtSignal(object)

    def __init__(
        self, weights, componentsIds, componentsTypes, gallery, cropMode, currentState
    ):
        QThread.__init__(self)
        self.weights = weights
        self.componentsIds = componentsIds
        self.componentsTypes = componentsTypes
        self.gallery = gallery
        self.cropMode = cropMode
        self.currentState = currentState

    def run(self):
        currentMixer = Mixer(self.weights, self.componentsTypes, *self.componentsIds)
        coords = [
            self.currentState["pos"][0],
            self.currentState["pos"][0] + self.currentState["size"][0],
            self.currentState["pos"][1],
            self.currentState["pos"][1] + self.currentState["size"][1],
        ]
        coords = [int(coord) for coord in coords]
        output = currentMixer.inverse_fft(
            self.gallery.get_gallery(), self.cropMode, coords
        ).T
        self.processingDone.emit(output)
