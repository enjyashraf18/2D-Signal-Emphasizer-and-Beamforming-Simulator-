from PyQt5 import QtCore
import cv2
import numpy as np


class FourierComponents(QtCore.QObject):
    def __init__(self, original_image):
        super().__init__()
        self.original_image = original_image
        self.fourier_shift = self.calculate_ft()

    def get_selected_ft_components(self, selected):
        try:
            print("iam here in the top of selected func call")
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

    def calculate_ft(self):
        if self.original_image.dtype != np.float32:
            self.original_image = np.float32(self.original_image)  # convert to 32-bit float to meet dft requ
        fourier = cv2.dft(self.original_image, flags=cv2.DFT_COMPLEX_OUTPUT)
        self.fourier_shift = np.fft.fftshift(fourier)
        return self.fourier_shift

    def get_ft_magnitude(self):
        magnitude = 20 * np.log(cv2.magnitude(self.fourier_shift[:, :, 0], self.fourier_shift[:, :, 1]) + 1)
        magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        return magnitude

    def get_ft_phase(self):
        phase = np.angle(self.fourier_shift[:, :, 0] + 1j * self.fourier_shift[:, :, 1])
        phase = cv2.normalize(phase, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        return phase

    def get_ft_real(self):
        real = self.fourier_shift[:, :, 0]
        lower, upper = np.percentile(real, [2, 98])  # clip to remove outliers
        real_clipped = np.clip(real, lower, upper)
        real_normalized = cv2.normalize(real_clipped, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        return real_normalized

    def get_ft_imaginary(self):
        imaginary = self.fourier_shift[:, :, 1]
        lower, upper = np.percentile(imaginary, [2, 98])
        imaginary_clipped = np.clip(imaginary, lower, upper)
        imaginary_transformed = np.log(np.abs(imaginary_clipped) + 1)
        imaginary_normalized = cv2.normalize(imaginary_transformed, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        return imaginary_normalized
