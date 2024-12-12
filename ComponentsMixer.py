import numpy as np
import cv2
from PIL import Image
from scipy import fftpack
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import QtCore
import time
import threading
import math
import logging

logging.basicConfig(filemode="a", filename="Logging_Info.log",
                    format="(%(asctime)s) | %(name)s| %(levelname)s | => %(message)s", level=logging.INFO)


class ComponentsMixer:
    def __init__(self, mode, images, components_combo_boxes,  output_labels, progress_bar, region_combobox):
        self.image_viewers = images
        self.images_components = [i.ft_component for i in images]  # list of ft components of images
        self.weights = [100]*4  # from sliders
        self.size = None
        self.components_types = [i.currentText() for i in components_combo_boxes]
        self.input_values = [np.zeros(self.size) for _ in range(4)]
        self.real_result = None
        self.imaginary_result = None
        self.phase_result = None
        self.magnitude_result = None
        self.mode = mode
        self.output_channel = 1
        self.image_viewers = images
        self.output_labels = output_labels
        self.progress_bar = progress_bar
        self.empty_count = 0
        # self.region_combobox = region_combobox
        # self.region_combobox.currentIndexChanged.connect(self.on_region_change)
        self.thread = threading.Thread(target=self.update_progress_bar)

        # self.components_combo_boxes = components_combo_boxes
        # for i in range(4):
        #     self.components_combo_boxes[i].currentIndexChanged.connect(self.on_combo_box_changed)

        # input is a list of ft_components of the 4 images
        # output is one list of the combined ft_components

    def set_component_type_and_value(self, component_type, ft_component, index, size):
        logging.info(f"Setting Component Type: {component_type}")
        print("Set component called")
        # index -= 1  # to be 0-based index
        self.size = size
        self.components_types[index] = component_type
        self.input_values[index] = np.zeros(self.size)
        self.input_values[index] = ft_component
        # print(f"component: {ft_component}")
        # print(f"input: {self.input_values[index]}")
        self.reconstruct_mixed_image()

    def reconstruct_mixed_image(self):
        # if self.size == 0:
        #     print("HERE MF")
        #     self.size = (250, 250)  # placeholder value
        real = np.zeros(self.size)
        imaginary = np.zeros(self.size)

        magnitude = np.zeros(self.size)
        phase = np.zeros(self.size)

        self.empty_count = 0
        if self.mode == "real_img":
            print("Real/Imaginary Mode")
            logging.info("Mixing in Real/Imaginary Mode")
            for i in range(4):
                if self.components_types[i] == "FT Real":
                    real += self.input_values[i] * (self.weights[i]/100)
                elif self.components_types[i] == "FT Imaginary":
                    imaginary += self.input_values[i] * (self.weights[i]/100)
                else:
                    self.empty_count += 1
            if self.empty_count == 4:
                self.output_labels[0].clear()
                self.output_labels[1].clear()
                return
            fft_array = real + 1j * imaginary
        else:
            print("Magnitude/Phase Mode")
            logging.info("Mixing in Magnitude/Phase Mode")
            for i in range(4):
                if self.components_types[i] == "FT Magnitude":
                    magnitude += self.input_values[i] * (self.weights[i]/100)
                elif self.components_types[i] == "FT Phase":
                    phase = self.input_values[i] * (self.weights[i]/100)
                else:
                    self.empty_count += 1
            if self.empty_count == 4:
                self.output_labels[0].clear()
                self.output_labels[1].clear()
                return
            fft_array = magnitude * np.exp(1j * phase)

        output_image_array = np.round(np.real(fftpack.ifft2(fftpack.ifftshift(fft_array))))
        # if self.mode == "real_img": # el 3aks
        #     output_image_array = np.clip(output_image_array, 0, 255)  # Clip values to [0, 255]
        #     output_image_array = output_image_array.astype(np.uint8)
        magnitude_pixmap = ImageConverter.numpy_to_pixmap(output_image_array)

        # Saving image locally (just for testing)
        filename = "Reconstructed Images/reconstructed_image.png"
        ImageConverter.save_pixmap(magnitude_pixmap, filename)
        self.show_image(magnitude_pixmap)

    def change_weights(self, value, index):
        self.weights[index] = value  # to be 0-based index
        print(f"Weight at index {index} = {value}")
        self.reconstruct_mixed_image()

    def show_image(self, mixed_pixmap):
        self.thread = threading.Thread(target=self.update_progress_bar)
        self.thread.start()
        if self.output_channel == 1:
            channel = self.output_labels[0]
        else:
            channel = self.output_labels[1]
        channel.clear()
        channel.setPixmap(mixed_pixmap.scaled(
            channel.size(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        ))
        channel.setAlignment(QtCore.Qt.AlignCenter)

    def set_mode(self, mode):
        self.mode = mode
        self.reconstruct_mixed_image()

    def set_output(self, output):
        print(f"Setting output channel...")
        logging.info(f"Current Output Channel: {output}")
        self.output_channel = output
        # self.reconstruct_mixed_image()

    import time

    def update_progress_bar(self):
        print(f"empty: {self.empty_count}")
        images_count = 4 - self.empty_count  # for easier calculations
        increments = [0, 25, 33, 50, 65, 80, 100]
        if images_count == 4:
            logging.info(f"Processing 4 images")
            t = 5
            j = 1
        elif images_count == 3:
            logging.info(f"Processing 3 images")
            t = 3
            j = 2
        elif images_count == 2:
            logging.info(f"Processing 2 images")
            t = 3
            j = 3
        else:
            logging.info(f"Processing 1 image")
            t = 2
            j = 4

        for i in range(j, 5):
            time.sleep(0.5)
            self.progress_bar.setValue(increments[i])
            time.sleep(0.5)

        self.progress_bar.setValue(100)
        time.sleep(1)
        self.progress_bar.setValue(0)

    # def on_region_change(self):
    #     self.fourier = FourierComponents()

    # def on_region_change(self):
    #     region_type = self.region_combobox.currentText()
    #
    #     if region_type == "Inner Region":
    #         self.new_components = [np.zeros(self.size) for _ in range(4)]
    #         for i in range(4):
    #             self.new_components[self.x_start:self.x_end, self.y_start: self.y_end] = new_comp[self.x_start:self.x_end,
    #                                                                                 self.y_start: self.y_end]
    #
    #     else:
    #         self.new_components = self.input_values.copy()
    #         new_comp[self.x_start:self.x_end, self.y_start: self.y_end] = 0
    #         return new_comp
    #
    # def zero_out_component(self, new_comp):
    #     size = (250, 250)
    #     if self.region_type == "inner":
    #         new_inner_comp = np.zeros(size)
    #         # new_comp[:self.x_start, :] = 0
    #         # new_comp[self.x_end:, :] = 0
    #         # new_comp[:, :self.y_start] = 0
    #         # new_comp[:, self.y_end:] = 0
    #         new_inner_comp[self.x_start:self.x_end, self.y_start: self.y_end] = new_comp[self.x_start:self.x_end,
    #                                                                             self.y_start: self.y_end]
    #         return new_inner_comp
    #     elif self.region_type == "outer":
    #         new_comp[self.x_start:self.x_end, self.y_start: self.y_end] = 0
    #     return new_comp

class ImageConverter:
    @staticmethod
    def numpy_to_pixmap(array):
        if array.size == 0:
            return None
        array_min = array.min()
        array_max = array.max()
        # Check if max and min are the same to avoid division by zero
        if array_max == array_min:
            array = np.zeros_like(array)
        else:
            array = (array - array_min) / (array_max - array_min) * 255
        array = np.clip(array, 0, 255).astype(np.uint8)
        if len(array.shape) == 2:
            # For 2D arrays
            height, width = array.shape
            bytes_per_line = width
            img = QImage(array.data.tobytes(), width, height, bytes_per_line, QImage.Format_Grayscale8)
        # elif len(array.shape) == 3:
        #     # For 3D arrays
        #     height, width, channel = array.shape
        #     bytes_per_line = 3 * width
        #     img = QImage(array.data.tobytes(), width, height, bytes_per_line, QImage.Format_RGB888)
        else:
            print("Unsupported array shape.")
            logging.error("Image reconstruction failed. Unsupported array shape.")
            return None
        return QPixmap.fromImage(img)

    @staticmethod
    def save_pixmap(pixmap, filename):
        if pixmap.isNull():
            print("Cannot save an empty pixmap.")
            logging.warning("Cannot save an empty pixmap.")
            return False
        success = pixmap.save(filename)
        if success:
            print(f"Image saved successfully as {filename}.")
            logging.info(f"Image saved successfully as {filename}.")
        else:
            print("Failed to save the image.")
            logging.error("Failed to save the image.")
        return success