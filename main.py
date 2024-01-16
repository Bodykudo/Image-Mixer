import random
from PyQt6 import QtCore
from PyQt6.QtCore import QTimer, QRectF
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QHBoxLayout,
)
import pyqtgraph as pg

from view.mainwindow import Ui_MainWindow
from model.Gallery import Gallery
from model.Image import Image
from model.ImageProcessingThread import ImageProcessingThread
from view.CustomImageView import CustomImageView

modes = ["Real", "Imaginary", "Magnitude", "Phase"]


class MainWindow(QMainWindow, Ui_MainWindow):
    image = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.gallery = Gallery()
        self.viewWidgets = [None, None, None, None]
        self.freqViewWidgets = [None, None, None, None]
        self.rois = [None, None, None, None]
        self.imagePaths = ["", "", "", ""]
        self.componentsIds = [0, 0, 0, 0]

        self.imageWidgets = [
            self.imageOneWidget,
            self.imageTwoWidget,
            self.imageThreeWidget,
            self.imageFourWidget,
        ]
        for i, widget in enumerate(self.imageWidgets):
            layout = QHBoxLayout()
            widget.setLayout(layout)
            widget.mouseDoubleClickEvent = lambda event, i=i: self.handleUploadImage(
                event, i
            )

        self.transWidgets = [
            self.imageOneComponentWidget,
            self.imageTwoComponentWidget,
            self.imageThreeComponentWidget,
            self.imageFourComponentWidget,
        ]
        for i, widget in enumerate(self.transWidgets):
            layout = QHBoxLayout()
            widget.setLayout(layout)

        self.currentSumOfComponents = 0
        self.remainderOfComponents = 100
        self.totalOfComponents = 100
        self.sliderValues = [0, 0, 0, 0]
        self.outputSliderValues = [0, 0, 0, 0]
        self.componentSliders = [
            self.componentOneRatioSlider,
            self.componentTwoRatioSlider,
            self.componentThreeRatioSlider,
            self.componentFourRatioSlider,
        ]
        for i, slider in enumerate(self.componentSliders):
            slider.setMinimum(0)
            slider.setMaximum(100)
            slider.setEnabled(False)
            slider.valueChanged.connect(
                lambda value, i=i: self.handleChangeWeightValue(value, i)
            )

        self.componentValueLabels = [
            self.componentOneRatioLabel,
            self.componentTwoRatioLabel,
            self.componentThreeRatioLabel,
            self.componentFourRatioLabel,
        ]

        self.currentOutput = 0
        self.outputWidgets = [self.outputOneWidget, self.outputTwoWidget]
        for i, widget in enumerate(self.outputWidgets):
            layout = QHBoxLayout()
            widget.setLayout(layout)
        self.outputSelect.currentIndexChanged.connect(self.handleChangeOutputChannel)

        self.imageModesCombobox = [
            self.imageOneModeSelect,
            self.imageTwoModeSelect,
            self.imageThreeModeSelect,
            self.imageFourModeSelect,
        ]
        for i, combobox in enumerate(self.imageModesCombobox):
            combobox.clear()
            for mode in modes:
                combobox.addItem(mode)
            combobox.setEnabled(False)
            combobox.currentIndexChanged.connect(
                lambda index, i=i: self.handleChangeImageMode(index, i)
            )
            model = combobox.model()
            model.item(2).setEnabled(False)
            model.item(3).setEnabled(False)

        self.componentsTypes = ["real", "real", "real", "real"]
        self.mixerModeSelect.currentIndexChanged.connect(self.handleChangeMixerMode)

        self.currentState = {
            "pos": (0.000000, 0.000000),
            "size": (50.000000, 50.000000),
            "angle": 0.0,
        }
        self.cropMode = 0
        self.cropModeSelect.currentIndexChanged.connect(self.handleChangeCropMode)

        self.convertButton.clicked.connect(self.handleConvert)

        self.progressBar.setVisible(False)
        self.stopButton.setVisible(False)
        self.stopButton.clicked.connect(self.cancelProgressBar)
        self.stopped = False

    def handleUploadImage(self, event, index):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.handleBrowseImage(index)

    def handleBrowseImage(self, index):
        img = QFileDialog.getOpenFileName(
            self, "Open file", ".\\", "Image files (*.jpg *.png)"
        )
        if img:
            image = Image()
            image.load_img(img[0])
            image.compute_fourier_transform()
            self.imageModesCombobox[index].setEnabled(True)
            self.imageModesCombobox[index].setCurrentIndex(
                0 if self.mixerModeSelect.currentIndex() == 0 else 2
            )
            self.gallery.add_image(image, index)

            Image.reshape_all(self.gallery.get_gallery().values())
            current_images = self.gallery.get_gallery()
            self.componentsIds[index] = index
            self.componentSliders[index].setEnabled(True)
            for i in current_images:
                if self.viewWidgets[i] == None:
                    newGraph = CustomImageView(parent=self.imageWidgets[i])
                    self.viewWidgets[i] = newGraph
                    self.imageWidgets[i].layout().addWidget(self.viewWidgets[i])
                    self.viewWidgets[i].ui.roiBtn.hide()
                    self.viewWidgets[i].ui.menuBtn.hide()
                    self.viewWidgets[i].ui.histogram.hide()

                self.viewWidgets[i].setImage(current_images[i].get_image())

                if self.freqViewWidgets[i] == None:
                    realGraph = pg.ImageView()
                    self.freqViewWidgets[i] = realGraph
                    self.transWidgets[i].layout().addWidget(self.freqViewWidgets[i])
                    self.freqViewWidgets[i].ui.roiBtn.hide()
                    self.freqViewWidgets[i].ui.menuBtn.hide()
                    self.freqViewWidgets[i].ui.histogram.hide()
                    self.freqViewWidgets[i].getView().setMouseEnabled(x=False, y=False)

                currentMode = self.componentsTypes[i]
                if currentMode == "magnitude":
                    self.freqViewWidgets[i].setImage(current_images[i].get_magnitude())
                elif currentMode == "phase":
                    self.freqViewWidgets[i].setImage(current_images[i].get_phase())
                elif currentMode == "real":
                    self.freqViewWidgets[i].setImage(current_images[i].get_real())
                elif currentMode == "imaginary":
                    self.freqViewWidgets[i].setImage(current_images[i].get_imaginary())

                if self.rois[i] == None:
                    ROI_Maxbounds = QRectF(0, 0, 100, 100)
                    ROI_Maxbounds.adjust(
                        0,
                        0,
                        self.freqViewWidgets[i].getImageItem().width() - 100,
                        self.freqViewWidgets[i].getImageItem().height() - 100,
                    )
                    roi = pg.ROI(
                        pos=self.currentState["pos"],
                        size=self.currentState["size"],
                        hoverPen="b",
                        resizable=True,
                        invertible=True,
                        rotatable=False,
                        maxBounds=ROI_Maxbounds,
                    )
                    if self.cropMode == 0:
                        roi.hide()
                    self.rois[i] = roi
                    roi.sigRegionChangeFinished.connect(lambda: self.modify_regions(i))
                    self.freqViewWidgets[i].getView().addItem(roi)

    def sumSlidersValues(self):
        return sum(self.sliderValues)

    def modify_regions(self, index):
        newState = self.rois[index].getState()
        self.currentState = newState
        for roi in self.rois:
            if roi:
                roi.setState(newState, update=False)
                roi.stateChanged(finish=False)

    def handleChangeWeightValue(self, value, index):
        self.sliderValues[index] = value
        self.componentValueLabels[index].setText(str(value) + "%")
        self.componentSliders[index].setValue(value)
        currentSumOfComponents = self.sumSlidersValues()
        if currentSumOfComponents > 100:
            self.outputSliderValues = [
                (value / currentSumOfComponents) * 1 for value in self.sliderValues
            ]
        else:
            self.outputSliderValues = [(value / 100) for value in self.sliderValues]

    def handleChangeOutputChannel(self, index):
        self.currentOutput = index

    def handleChangeImageMode(self, index, i):
        if i + 1 > len(self.gallery.get_gallery()):
            return

        mode = modes[index]
        image = self.gallery.get_gallery()[i]

        graph = self.freqViewWidgets[i]
        if mode == "Magnitude":
            graph.setImage(image.get_magnitude())
        elif mode == "Phase":
            graph.setImage(image.get_phase())
        elif mode == "Real":
            graph.setImage(image.get_real())
        elif mode == "Imaginary":
            graph.setImage(image.get_imaginary())

        self.componentsTypes[i] = mode.lower()

    def handleChangeMixerMode(self, index):
        if index == 0:
            for combobox in self.imageModesCombobox:
                model = combobox.model()
                model.item(0).setEnabled(True)
                model.item(1).setEnabled(True)
                model.item(2).setEnabled(False)
                model.item(3).setEnabled(False)
                combobox.setCurrentIndex(0)
                self.componentsTypes = ["real", "real", "real", "real"]
        else:
            for combobox in self.imageModesCombobox:
                model = combobox.model()
                model.item(0).setEnabled(False)
                model.item(1).setEnabled(False)
                model.item(2).setEnabled(True)
                model.item(3).setEnabled(True)
                combobox.setCurrentIndex(2)
                self.componentsTypes = [
                    "magnitude",
                    "magnitude",
                    "magnitude",
                    "magnitude",
                ]

    def handleChangeCropMode(self, index):
        self.cropMode = index
        for roi in self.rois:
            if roi:
                if index == 0:
                    roi.hide()
                else:
                    roi.show()

    def handleConvert(self):
        # Show progress bar
        self.progressBar.setVisible(True)
        self.stopButton.setVisible(True)
        self.progressBar.setValue(0)

        # Start a QTimer to periodically update the progress bar value
        self.progressTimer = QTimer()
        self.progressTimer.timeout.connect(self.updateProgressBar)
        self.progressTimer.start(100)  # update every 100 ms

        # Start image processing in a separate thread
        self.stopped = False
        self.thread = ImageProcessingThread(
            self.outputSliderValues,
            self.componentsIds,
            self.componentsTypes,
            self.gallery,
            self.cropMode,
            self.currentState,
        )
        self.thread.processingDone.connect(self.delayShowImage)
        self.thread.start()

    def updateProgressBar(self):
        value = self.progressBar.value()
        if value < 99:
            self.progressBar.setValue(value + random.randint(3, 6))
        else:
            self.progressTimer.stop()

    def delayShowImage(self, output):
        QTimer.singleShot(2000, lambda: self.showImage(output))

    def showImage(self, output):
        if not self.stopped:
            outputWidget = self.outputWidgets[self.currentOutput]
            layout = outputWidget.layout()
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            outputImage = pg.image(output)
            outputImage.ui.roiBtn.hide()
            outputImage.ui.menuBtn.hide()
            outputImage.ui.histogram.hide()
            outputWidget.layout().addWidget(outputImage)

        # Hide progress bar
        self.progressTimer.stop()
        self.progressBar.setValue(100)
        QTimer.singleShot(2000, self.hideProgressbar)

    def hideProgressbar(self):
        self.progressBar.setVisible(False)
        self.stopButton.setVisible(False)

    def cancelProgressBar(self):
        # Terminate the thread if progress bar is cancelled
        if self.thread.isRunning():
            self.thread.terminate()
        self.progressTimer.stop()
        self.stopped = True
        self.hideProgressbar()


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
