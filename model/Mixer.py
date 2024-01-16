import numpy as np


class Mixer:
    def __init__(
        self,
        weights,
        types,
        image1_id,
        image2_id,
        image3_id,
        image4_id,
    ):
        """
        Initializes an instance of a custom object with image IDs, types, and weights.

        Parameters:
        - weights (list): List containing the weights of all items.
        - types (list): List containing the types of all items.
        - image1_id (int): Image ID for the first item.
        - image2_id (int): Image ID for the second item.
        - image3_id (int): Image ID for the third item.
        - image4_id (int): Image ID for the fourth item.

        Attributes:
        - weights (list): List containing the weights of all items.
        - types (list): List containing the types of all items.
        - image1_id (int): Image ID for the first item.
        - image2_id (int): Image ID for the second item.
        - image3_id (int): Image ID for the third item.
        - image4_id (int): Image ID for the fourth item.
        """
        self.image1_id = image1_id
        self.image2_id = image2_id
        self.image3_id = image3_id
        self.image4_id = image4_id
        self.types = types
        self.weights = weights

    def extract_image(self, gallery):
        """
        Extracts object from a given gallery based on the stored image IDs.

        Parameters:
        - gallery (dict): A dictionary representing a gallery of objects where keys are image IDs.

        Returns:
        - image1: The object corresponding to image1_id.
        - image2: The object corresponding to image2_id.
        - image3: The object corresponding to image3_id.
        - image4: The object corresponding to image4_id.
        """
        image1 = gallery[self.image1_id]
        image2 = gallery[self.image2_id]
        image3 = gallery[self.image3_id]
        image4 = gallery[self.image4_id]
        return image1, image2, image3, image4

    def choose_mode(self):
        """
        Determines the mode based on the types stored in the object.

        Returns:
        - int: Mode identifier.
            1: If all types are either "phase" or "magnitude".
            2: If all types are either "real" or "imaginary".

        Raises:
        - ValueError: If the types are not valid (neither all "phase" or "magnitude", nor all "real" or "imaginary").
        """
        phase_magnitude = 0
        real_imaginary = 0
        for type in self.types:
            if type == "phase" or type == "magnitude":
                phase_magnitude += 1
            elif type == "real" or type == "imaginary":
                real_imaginary += 1
            else:
                pass

        if phase_magnitude == 0:
            return 1
        elif real_imaginary == 0:
            return 2
        else:
            raise ValueError("Invalid types")

    def inverse_fft(self, gallery, crop_mode=None, dimensions=None):
        """
        Performs inverse FFT on images extracted from the given gallery based on stored parameters.

        Parameters:
        - gallery (dict): A dictionary representing a gallery of images where keys are image IDs.
        - crop_mode (int): 1 for inner, 2 for outer
        - dimensions (list): x1,x2,y1,y2
        Returns:
        - ndarray: Reconstructed image using inverse FFT.

        Raises:
        - ValueError: If the mode determined by the types is not supported (not all "magnitude" or "phase").
        """
        images = self.extract_image(gallery)
        mask = np.ones(images[0].shape)

        # inner mode
        if crop_mode == 1:
            mask = np.zeros(images[0].shape)
            mask[
                dimensions[2] : dimensions[3] + 1, dimensions[0] : dimensions[1] + 1
            ] = 1

        # outer mode
        elif crop_mode == 2:
            mask = np.ones(images[0].shape)
            mask[
                dimensions[2] : dimensions[3] + 1, dimensions[0] : dimensions[1] + 1
            ] = 0

        mode = self.choose_mode()

        # magnitude and phase mode
        if mode == 2:
            magnitudes = np.zeros(images[0].shape)
            phases = np.zeros(images[0].shape)

            for i, image in enumerate(images):
                if self.types[i] == "magnitude":
                    magnitudes += 2 * self.weights[i] * np.abs(image.get_fft_shifted())
                elif self.types[i] == "phase":
                    phases += 2 * self.weights[i] * np.angle(image.get_fft_shifted())

            return np.clip(
                np.abs(
                    np.fft.ifft2((magnitudes * mask) * np.exp(1j * (phases * mask)))
                ),
                0,
                225,
            )

        # real and imaginary mode
        elif mode == 1:
            real = np.zeros(images[0].shape)
            imaginary = np.zeros(images[0].shape)

            for i, image in enumerate(images):
                if self.types[i] == "real":
                    real += self.weights[i] * image.real
                elif self.types[i] == "imaginary":
                    imaginary += self.weights[i] * image.imaginary

            return np.clip(
                np.abs(np.fft.ifft2(real * mask + imaginary * mask * 1j)), 0, 225
            )
