import cv2
import numpy as np


class Image:
    id = 0

    def __init__(self):
        """
        Initialize an Image object.

        Attributes:
        - name (str): The name of the image extracted from the file path.
        - img (numpy.ndarray): The image data loaded from the specified path.
        - shape (tuple): The shape of the loaded image.
        - fft (numpy.ndarray): The 2D Fourier Transform of the image.
        - fft_shifted (numpy.ndarray): The shifted version of the Fourier Transform.
        - magnitude (numpy.ndarray): The magnitude spectrum of the shifted Fourier Transform.
        - phase (numpy.ndarray): The phase spectrum of the shifted Fourier Transform.
        - real (numpy.ndarray): The real part of the shifted Fourier Transform.
        - imaginary (numpy.ndarray): The imaginary part of the shifted Fourier Transform.
        - components_shifted (None): Placeholder for components of the shifted Fourier Transform.
        """
        self.id = Image.id
        Image.id += 1
        self.image = None
        self.shape = None

        self.fft = None
        self.fft_shifted = None
        self.magnitude = None
        self.phase = None
        self.real = None
        self.imaginary = None
        self.components_shifted = None

    def get_id(self):
        return self.id

    def get_image(self):
        return self.image.T

    def get_fft(self):
        return self.fft

    def get_fft_shifted(self):
        return self.fft_shifted

    def get_magnitude(self):
        return self.components_shifted[0].T

    def get_phase(self):
        return self.components_shifted[1].T

    def get_real(self):
        return self.components_shifted[2]

    def get_imaginary(self):
        return self.components_shifted[3]

    def load_img(self, image_path):
        """
        Load and process the image from the specified file path.

        Parameters:
        - show (bool, optional): If True, display the loaded image using cv2.imshow.
                                Default is True.

        Raises:
        - Exception: Raises an exception if there's an error loading or processing the image.

        Returns:
        - None
        """
        self.image = cv2.imread(image_path).astype(np.float32)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.shape = self.image.shape

    def reshape(self, new_height, new_width):
        """
        Resize the image to the specified dimensions.

        Parameters:
        - new_height (int): The new height of the image.
        - new_width (int): The new width of the image.

        Returns:
        - None
        """
        # Resize the image
        self.image = cv2.resize(self.image, (new_width, new_height))
        # Update the shape attribute
        self.shape = self.image.shape

    @classmethod
    def reshape_all(cls, image_instances):
        """
        Resize all images in a list of Image instances to the smallest dimensions among them.

        Parameters:
        - cls (class): The class reference.
        - image_instances (list): List of Image instances to be resized.

        Returns:
        - None
        """
        # Find the smallest image dimensions among all instances
        min_height = min(inst.image.shape[0] for inst in image_instances)
        min_width = min(inst.image.shape[1] for inst in image_instances)

        # Resize all images to the smallest dimensions
        for inst in image_instances:
            inst.reshape(min_height, min_width)
            inst.compute_fourier_transform()

    def compute_fourier_transform(self, show=True):
        """
        Compute the 2D Fourier Transform and related components of the image.

        Parameters:
        - show (bool, optional): If True, display visualizations of the Fourier Transform components.
                                Default is True.

        Returns:
        - None
        """
        # Compute the 2D Fourier Transform
        self.fft = np.fft.fft2(self.image)

        # Shift the zero-frequency component to the center
        self.fft_shifted = np.fft.fftshift(self.fft)

        # Compute the magnitude of the spectrum
        self.magnitude = np.abs(self.fft)

        # Compute the phase of the spectrum
        self.phase = np.angle(self.fft)

        # real ft components
        self.real = self.fft.real

        # imaginary ft components
        self.imaginary = self.fft.imag

        # Compute the components of the shifted Fourier Transform
        self.components_shifted = [
            np.log(np.abs(self.fft_shifted) + 1),
            np.angle(self.fft_shifted),
            np.log(self.fft_shifted.real + 1),
            np.log(self.fft_shifted.imag + 1),
        ]
