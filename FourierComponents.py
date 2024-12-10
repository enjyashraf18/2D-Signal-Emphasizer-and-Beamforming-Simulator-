from PyQt5 import QtCore
import cv2
import numpy as np
from scipy import fftpack
import logging
logging.basicConfig(filemode="a", filename="Logging_Info.log",
                    format="(%(asctime)s) | %(name)s| %(levelname)s | => %(message)s", level=logging.INFO)

class FourierComponents(QtCore.QObject):
    def __init__(self, original_image):
        super().__init__()
        self.original_image = original_image
        self.fourier_shift = self.calculate_ft()

    def get_selected_ft_components(self, selected):
        try:
            # print("iam here in the top of selected func call")
            if selected == "FT Magnitude":
                return self.get_ft_magnitude()
            elif selected == "FT Phase":
                return self.get_ft_phase()
            elif selected == "FT Real":
                print("he select real")
                return self.get_ft_real()
            elif selected == "FT Imaginary":
                return self.get_ft_imaginary()

        except Exception as e:
            print(f"Error in getting FT components: {e}")
            logging.error(f"Error in getting FT components: {e}")

    def calculate_ft(self):
        if self.original_image.dtype != np.float32:
            self.original_image = np.float32(self.original_image)  # convert to 32-bit float to meet dft requ
        fourier = cv2.dft(self.original_image, flags=cv2.DFT_COMPLEX_OUTPUT)
        self.fourier_shift = np.fft.fftshift(fourier)
        # self.fourier_shift = fftpack.fft2(self.original_image)
        # self.fourier_shift = fftpack.fftshift(self.fourier_shift)
        return self.fourier_shift

    def get_ft_magnitude(self):
        magnitude = 20 * np.log(cv2.magnitude(self.fourier_shift[:, :, 0], self.fourier_shift[:, :, 1]) + 1)
        magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        # print(f"Magnitude Shape: {magnitude.shape}")
        # magnitude = np.abs(self.fourier_shift)
        return magnitude

    def get_ft_phase(self):
        phase = np.angle(self.fourier_shift[:, :, 0] + 1j * self.fourier_shift[:, :, 1])
        phase = cv2.normalize(phase, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        # print(f"Phase Shape: {phase.shape}")
        # phase = np.angle(self.fourier_shift)
        return phase

    def get_ft_real(self):
        real = self.fourier_shift[:, :, 0]
        lower, upper = np.percentile(real, [2, 98])  # clip to remove outliers
        real_clipped = np.clip(real, lower, upper)
        real_normalized = cv2.normalize(real_clipped, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        # print(f"real_normalized main: {real_normalized}")
        # real = np.real(self.fourier_shift)
        return real_normalized
        # f_transform = np.fft.fft2(self.original_image)
        # f_transform_shifted = np.fft.fftshift(f_transform)
        # real_part = np.real(f_transform_shifted)
        # return real_part

    def get_ft_imaginary(self):
        imaginary = self.fourier_shift[:, :, 1]
        lower, upper = np.percentile(imaginary, [2, 98])
        imaginary_clipped = np.clip(imaginary, lower, upper)
        imaginary_transformed = np.log(np.abs(imaginary_clipped) + 1)
        imaginary_normalized = cv2.normalize(imaginary_transformed, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        # print(f"imaginary_normalized main: {imaginary_normalized}")
        # imaginary = np.imag(self.fourier_shift)
        return imaginary_normalized
