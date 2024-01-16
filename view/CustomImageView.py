import numpy as np
from PyQt6 import QtCore
import pyqtgraph as pg


class CustomViewBox(pg.ViewBox):
    def __init__(self, imageViewComponent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dragStartPos = None
        self.child = imageViewComponent
        self.currentBrightness = 0
        self.currentContrast = 0

    def mouseDragEvent(self, event, axis=None):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            dx, dy = 0, 0
            if self.dragStartPos is not None:
                dx = event.pos().x() - self.dragStartPos.x()
                dy = event.pos().y() - self.dragStartPos.y()
            self.dragStartPos = event.pos()
            if abs(dx) > 2:
                self.currentBrightness += dx
            if abs(dy) > 2:
                self.currentContrast += dy * 0.01
            newImage = np.clip(
                (self.child.originalImage + self.currentBrightness)
                * (1 + self.currentContrast),
                0,
                255.0,
            )
            self.child.setImage(newImage)
            event.accept()

    def mouseClickEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            self.dragStartPos = None
            self.currentBrightness = 0
            self.currentContrast = 0
            self.child.setImage(self.child.originalImage)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.dragStartPos = None
        super(CustomViewBox, self).mouseReleaseEvent(event)


class CustomImageView(pg.ImageView):
    def __init__(self, *args, **kwargs):
        kwargs["view"] = CustomViewBox(imageViewComponent=self)
        super().__init__(*args, **kwargs)
        self.imageItem = self.getImageItem()
        self.originalImage = None
        self.firstTime = True

    def setImage(self, img, *args, **kwargs):
        super().setImage(img, *args, **kwargs)
        self.imageItem = self.getImageItem()
        if self.firstTime:
            self.firstTime = False
            self.originalImage = self.getImageItem().image

    def __del__(self):
        self.imageItem = None
        self.originalImage = None
