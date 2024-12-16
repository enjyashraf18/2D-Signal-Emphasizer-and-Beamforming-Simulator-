import numpy as np
import cv2
from PIL import Image
from scipy import fftpack
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import QtCore
import time
import threading
import math
import random
import logging

logging.basicConfig(filemode="a", filename="Logging_Info.log",
                    format="(%(asctime)s) | %(name)s| %(levelname)s | => %(message)s", level=logging.INFO)


class ComponentsMixer:
    def __init__(self, mode, images, components_combo_boxes,  output_labels, progress_bar, region_combobox):
        self.image_viewers = images
        self.images_components = [i.ft_component for i in images]  # list of ft components of images
        self.weights = [100]*4  # from sliders
        self.size = (250, 250)
        self.components_types = [i.currentText() for i in components_combo_boxes]
        self.input_values = [np.zeros(self.size) for _ in range(4)]
        self.original_inputs = [np.zeros(self.size) for _ in range(4)]
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
        self.region_combobox = region_combobox
        self.region_combobox.currentIndexChanged.connect(self.on_region_change)
        self.thread = threading.Thread(target=self.update_progress_bar)

        self.increments = None
        self.current_step = None
        self.progress_timer = None
        self.all_fouriers = [None for _ in range(4)]

    def set_component_type_and_value(self, component_type, ft_component, index, size, is_changing_region):
        logging.info(f"Setting Component Type: {component_type}")
        print("Set component called")
        # index -= 1  # to be 0-based index
        self.size = size
        self.components_types[index] = component_type
        self.input_values[index] = np.zeros(self.size)
        self.input_values[index] = ft_component
        print(f"Component in set: {ft_component}")
        if not is_changing_region:  # I'm setting the original component
            logging.info("Setting original values of components.")
            self.original_inputs[index] = np.zeros(self.size)
            self.original_inputs[index] = ft_component
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
                if self.weights[i] == 0:
                    continue
                if self.components_types[i] == "FT Real":
                    real += self.original_inputs[i] * (self.weights[i]/100)
                elif self.components_types[i] == "FT Imaginary":
                    imaginary += self.original_inputs[i] * (self.weights[i]/100)
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
                if self.weights[i] == 0:
                    continue
                if self.components_types[i] == "FT Magnitude":
                    magnitude += self.original_inputs[i] * (self.weights[i]/100)
                elif self.components_types[i] == "FT Phase":
                    phase = self.original_inputs[i] * (self.weights[i]/100)
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
        self.weights[index] = value
        if value == 0:
            logging.warning(f"Weight of image {index} = {value}")
        else:
            logging.info(f"Weight of image {index} = {value}")
        print(f"Weight at index {index} = {value}")
        self.reconstruct_mixed_image()

    def set_mode(self, mode):
        self.mode = mode
        self.reconstruct_mixed_image()

    def set_output(self, output):
        print(f"Setting output channel...")
        logging.info(f"Current Output Channel: {output}")
        self.output_channel = output
        # self.reconstruct_mixed_image()

    def show_image(self, mixed_pixmap):
        self.progress_bar.setValue(0)
        self.progress_timer = QtCore.QTimer()
        r = random.randint(1,2)
        if r == 1:
            self.increments = [0, 25, 50, 75, 100]
        else:
            self.increments = [0, 33, 60, 85, 100]
        self.current_step = 0

        # Connect the timer to the progress update function
        self.progress_timer.timeout.connect(lambda: self.update_progress_bar(mixed_pixmap))
        self.progress_timer.start(500)  # Update every 500ms

    def update_progress_bar(self, mixed_pixmap):
        if self.current_step < len(self.increments):
            self.progress_bar.setValue(self.increments[self.current_step])
            self.current_step += 1
        else:
            self.progress_timer.stop()  # Stop the timer when progress is complete
            self.progress_bar.setValue(0)
            # Display the image
            self.display_image(mixed_pixmap)

    def display_image(self, mixed_pixmap):
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

    def on_region_change(self):
        region_type = self.region_combobox.currentText()
        for i in range(4):
            component_type = self.components_types[i]
            if self.all_fouriers[i] is not None:
                selected_region_components = self.all_fouriers[i].zero_out_component(region_type, self.original_inputs, self.size)
                print(f"Component in on region: {selected_region_components}")
                self.change_region(selected_region_components)

    def change_region(self, region_components):
        for i in range(4):
            self.input_values[i] = region_components[i]
        self.reconstruct_mixed_image()


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