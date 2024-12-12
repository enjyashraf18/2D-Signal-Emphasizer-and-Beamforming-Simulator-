from PyQt5 import QtCore
import cv2
import numpy as np
import pyqtgraph as pg
import logging
logging.basicConfig(filemode="a", filename="Logging_Info.log",
                    format="(%(asctime)s) | %(name)s| %(levelname)s | => %(message)s", level=logging.INFO)

class FourierComponents(QtCore.QObject):
    def __init__(self, original_image, ft_widget, ROI_rectangles):
        super().__init__()
        self.original_image = original_image
        self.fourier_shift = self.calculate_ft()
        self.ft_widget = ft_widget


        self.final_mouse_pos = None
        self.roi = None
        self.x_start = None
        self.y_start = None
        self.x_end = None
        self.y_end = None
        self.ROI_rectangles= ROI_rectangles

        self.selected = None
        self.region_type = "inner"
        self.real_comp = None
        self.img_comp = None
        self.mag_comp = None
        self.phase_comp = None

    def get_selected_ft_components(self, selected):
        try:
            print("iam here in the top of selected func call")
            self.selected = selected
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

    def zero_out_component(self, new_comp):
        size = (250, 250)
        if self.region_type == "Inner Region":
            new_inner_comp = np.zeros(size)
            # new_comp[:self.x_start, :] = 0
            # new_comp[self.x_end:, :] = 0
            # new_comp[:, :self.y_start] = 0
            # new_comp[:, self.y_end:] = 0
            new_inner_comp[self.x_start:self.x_end, self.y_start: self.y_end] = new_comp[self.x_start:self.x_end, self.y_start: self.y_end]
            return new_inner_comp
        elif self.region_type == "Outer Region":
            new_comp[self.x_start:self.x_end, self.y_start: self.y_end] = 0
            return new_comp

    def region_mixer_output(self, region_type):
        self.region_type = region_type
        print(f"self.selected = {self.selected}")
        if self.selected == "FT Real":
            new_comp = self.real_comp.copy()
            return self.zero_out_component(new_comp)

        elif self.selected == "FR Imaginary":
            new_comp = self.img_comp.copy()
            return self.zero_out_component(new_comp)

        elif self.selected == "FT Magnitude":
            new_comp = self.mag_comp.copy()
            return self.zero_out_component(new_comp)

        elif self.selected == "FT Phase":
            new_comp = self.phase_comp.copy()
            return self.zero_out_component(new_comp)

    def draw_rectangle(self, detect_first_time):
        if not detect_first_time:
            detect_first_time = True
        scale = 0.6
        roi_width = self.ft_widget.width()
        roi_height = self.ft_widget.height()

        roi_center_x = roi_width // 2
        roi_center_y = roi_height // 2
        pos_x = roi_center_x - roi_width /3
        pos_y = roi_center_y - roi_height /3
        # self.roi = pg.RectROI()

        self.roi = pg.RectROI(
            [pos_x, pos_y],
            [roi_width * scale, roi_height * scale],
            pen=pg.mkPen("b", width=2), resizable = True , movable=True, invertible= True, rotatable= False
        )

        self.roi.addScaleHandle([0, 0], [1, 1])
        # top right
        self.roi.addScaleHandle([1, 0], [0, 1])
        #bottom left
        self.roi.addScaleHandle([0, 1], [1, 0])
        #bottom right
        self.roi.addScaleHandle([1, 1], [0, 0])

        self.ft_widget.scene().addItem(self.roi)
        self.roi.sigRegionChanged.connect(self.rect_boundries)
        self.ROI_rectangles.append(self.roi)
        print(f"hena length el roi rects {len(self.ROI_rectangles)}")
        return detect_first_time

    def remove_rectangle(self):
        self.ft_widget.scene().removeItem(self.roi)
        self.roi =None

    def rect_boundries(self):
        if self.roi is None:
            return None
        pos = self.roi.pos()
        size = self.roi.size()
        self.x_start = int(pos[0])
        self.y_start = int(pos[1])
        self.x_end = int(pos[0] + size[0])
        self.y_end = int(pos[1] + size[1])
        for roi in self.ROI_rectangles:
            roi.setPos(pos)
            roi.setSize(size)
        print((self.x_start, self.x_end, self.y_start, self.y_end))
        return self.x_start, self.x_end,self.y_start, self.y_end

    def calculate_ft(self):
        if self.original_image.dtype != np.float32:
            self.original_image = np.float32(self.original_image)  # convert to 32-bit float to meet dft requ
        fourier = cv2.dft(self.original_image, flags=cv2.DFT_COMPLEX_OUTPUT)
        self.fourier_shift = np.fft.fftshift(fourier)
        return self.fourier_shift

    def get_ft_magnitude(self):
        magnitude = 20 * np.log(cv2.magnitude(self.fourier_shift[:, :, 0], self.fourier_shift[:, :, 1]) + 1)
        magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        self.mag_comp = magnitude
        return magnitude

    def get_ft_phase(self):
        phase = np.angle(self.fourier_shift[:, :, 0] + 1j * self.fourier_shift[:, :, 1])
        phase = cv2.normalize(phase, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        self.phase_comp = phase
        return phase

    def get_ft_real(self):
        real = self.fourier_shift[:, :, 0]
        lower, upper = np.percentile(real, [2, 98])  # clip to remove outliers
        real_clipped = np.clip(real, lower, upper)
        real_normalized = cv2.normalize(real_clipped, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        self.real_comp = real_normalized
        return real_normalized

    def get_ft_imaginary(self):
        imaginary = self.fourier_shift[:, :, 1]
        lower, upper = np.percentile(imaginary, [2, 98])
        imaginary_clipped = np.clip(imaginary, lower, upper)
        imaginary_transformed = np.log(np.abs(imaginary_clipped) + 1)
        imaginary_normalized = cv2.normalize(imaginary_transformed, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        self.img_comp = imaginary_normalized

        return imaginary_normalized
