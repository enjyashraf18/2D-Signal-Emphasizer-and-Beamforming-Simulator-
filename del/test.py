def get_resized_image_array(self, label):
    pixmap = label.pixmap()
    if pixmap:
        # Convert QPixmap to QImage
        image = pixmap.toImage()
        # Convert QImage to NumPy array
        width, height = image.width(), image.height()
        arr = np.zeros((height, width), dtype=np.uint8)
        for y in range(height):
            for x in range(width):
                pixel_value = image.pixel(x, y)
                arr[y, x] = np.uint8(pixel_value & 0xFF)  # Convert to 8-bit unsigned integer
        return arr
    else:
        return None
def set_all_to_smallest_size(self):
    sizes = [label.label.pixmap().size() for label in self.parent().before_labels.values() if label.label.pixmap()]
    if sizes:
        smallest_size = min(sizes, key=lambda x: x.width() * x.height())
        for label in self.parent().before_labels.values():
            if label.label.pixmap():
                label.label.setPixmap(
                    label.label.pixmap().scaled(smallest_size.width(), smallest_size.height(), Qt.IgnoreAspectRatio))
                # Get the resized image as a NumPy array
                label.resized_image_array = self.get_resized_image_array(label.label)
                label.calc_components()

def calc_components(self):
    if self.resized_image_array is None:
        return
    # Compute the Fourier Transform
    self.img_ft = fftpack.fft2(self.resized_image_array)
    self.img_ft = fftpack.fftshift(self.img_ft)
    # Calculate components
    self.magnitude = np.abs(self.img_ft)
    self.phase = np.angle(self.img_ft)
    self.real_part = np.real(self.img_ft)
    self.imaginary_part = np.imag(self.img_ft)
    self.calc_weighted_componenets()

self.output_labels = {}
for i in range(2):
    self.output_labels[f'label_{i + 1}_output'] = OutputLabel(parent=self,label_found_child=self.findChild(QLabel,f'label_{i + 1}_output'),label_index=i + 1)
result_real = np.sum(self.output_labels[f'label_{selected_label_index}_output'].real, axis=0)
result_imaginary = np.sum(self.output_labels[f'label_{selected_label_index}_output'].imaginary, axis=0)
self.output_labels[f'label_{selected_label_index}_output'].ifft2_convert_to_img(2, result_real, result_imaginary)
fft_array=magnitudes_real_array + 1j * phases_imag_array
output_image_array = np.round(np.real(fftpack.ifft2(fftpack.ifftshift(fft_array))))
magnitude_pixmap = ImageConverter.numpy_to_pixmap(output_image_array)
# by nada
filename = "output_image.png"  # Specify your desired filename
ImageConverter.save_pixmap(magnitude_pixmap, filename)
#by nada
self.output_label.setPixmap(magnitude_pixmap.scaled(self.output_label.size(), Qt.KeepAspectRatio))