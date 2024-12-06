import numpy as np
import cv2
from PIL import Image


class ComponentsMixer:
    def __init__(self, images, components, weights):
        self.images_components = [i.ft_component for i in images]  # list of ft components of images
        self.weights = [weight/100 for weight in weights]  # from sliders
        self.components_types = [i.currentText() for i in components]
        self.input_values = [[] for _ in range(4)]
        self.real_result = None
        self.imaginary_result = None
        self.phase_result = None
        self.magnitude_result = None
        self.mode = None

        # input is a list of ft_components of the 4 images
        # output is one list of the combined ft_components

    def set_component_type_and_value(self, fourier_shift, selected_option, ft_component, index):
        self.components_types[index] = selected_option
        self.input_values[index] = ft_component
        self.fourier_shift = fourier_shift
        self.mix_components()

    def mix_components(self):
        # input: [[], [], [], []]
        # output: [w1.input[i][0] + w2.input[i][,
        do_mix = True
        print("Inside mix_components")
        for i in range(4):
            if len(self.input_values[i]) == 0:
                do_mix = False
            else:
                self.real_result = [0]*len(self.input_values[i])
                self.imaginary_result = [0] * len(self.input_values[i])
                self.phase_result = [0] * len(self.input_values[i])
                self.magnitude_result = [0] * len(self.input_values[i])

        if do_mix:
            print(f"Mixing...")
            selected_component = self.components_types[0]

            # Determining mixing mode
            if selected_component == "FT Real" or selected_component == "FT Imaginary":
                self.mode = "real_img"
            else:
                self.mode = "phase_mag"

            if self.mode == "real_img":
                for i in range(4):
                    for j in range(len(self.input_values[0])):  # loop through each data point
                        if self.components_types[i] == "FT Real":
                            self.real_result[j] += self.weights[i]*self.input_values[i][j]
                        else:
                            self.imaginary_result[j] += self.weights[i]*self.input_values[i][j]

                complex_array = np.zeros(self.fourier_shift.shape, dtype=np.float32)
                complex_array[:, :, 0] = self.real_result
                complex_array[:, :, 1] = self.imaginary_result

                # Perform the inverse DFT
                img_back = cv2.idft(np.fft.ifftshift(complex_array))
                img_back = cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1])

                # Normalize the result to the range [0, 255]
                img_back = cv2.normalize(img_back, None, 0, 255, cv2.NORM_MINMAX)
                img_back = np.uint8(img_back)  # Convert to 8-bit image
                cv2.imwrite('reconstructed_image.png', img_back)

                # complex_array = self.real_result + 1j * self.imaginary_result
                # image = np.fft.ifft2(complex_array)  # Take the absolute value to get the magnitude of the image
                # image_magnitude = np.abs(image)  # Normalize the image to the range 0-255
                # image_magnitude_normalized = (255 * (image_magnitude / np.max(image_magnitude))).astype(np.uint8)  # Convert to a Pillow Image object
                # image_pil = Image.fromarray(image_magnitude_normalized)  # Save the image
                # image_pil.save('reconstructed_image.png')
            else:
                for i in range(4):
                    for j in range(len(self.input_values[0])):
                        if self.components_types[j] == "FT Phase":
                            self.phase_result[j] += self.weights[i]*self.input_values[i][j]
                        else:
                            self.magnitude_result[j] += self.weights[i] * self.input_values[i][j]

    def change_weights(self, value, index):
        print(f"Inside change_weights")
        self.weights[index] = value
        self.mix_components()
