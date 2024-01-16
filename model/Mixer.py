import numpy as np
from tqdm.auto import tqdm


class Mixer:
    def __init__(
        self,
        weights,
        types,
        img_id1,
        img_id2,
        img_id3,
        img_id4,
    ):
        """
        Initializes an instance of a custom object with image IDs, types, and weights.

        Parameters:
        - w1 (float): Weight for the first item.
        - w2 (float): Weight for the second item.
        - w3 (float): Weight for the third item.
        - w4 (float): Weight for the fourth item.
        - img_id1 (int): Image ID for the first item.
        - img_id2 (int): Image ID for the second item.
        - img_id3 (int): Image ID for the third item.
        - img_id4 (int): Image ID for the fourth item.
        - type_1 (str): Type of the first item, must be either 'real + img' or 'mag. + phase'.
        - type_2 (str): Type of the second item, must be either 'real + img' or 'mag. + phase'.
        - type_3 (str): Type of the third item, must be either 'real + img' or 'mag. + phase'.
        - type_4 (str): Type of the fourth item, must be either 'real + img' or 'mag. + phase'.

        Attributes:
        - img_id1 (int): Image ID for the first item.
        - img_id2 (int): Image ID for the second item.
        - img_id3 (int): Image ID for the third item.
        - img_id4 (int): Image ID for the fourth item.
        - types (list): List containing the types of all items.
        - weights (list): List containing the weights of all items.
        """
        self.img_id1 = img_id1
        self.img_id2 = img_id2
        self.img_id3 = img_id3
        self.img_id4 = img_id4
        self.types = types
        self.weights = weights

    def extract_img_from_gallery(self, gallery):
        """
        Extracts object from a given gallery based on the stored image IDs.

        Parameters:
        - gallery (dict): A dictionary representing a gallery of objects where keys are image IDs.

        Returns:
        - img1: The object corresponding to img_id1.
        - img2: The object corresponding to img_id2.
        - img3: The object corresponding to img_id3.
        - img4: The object corresponding to img_id4.
        """
        img1 = gallery[self.img_id1]
        img2 = gallery[self.img_id2]
        img3 = gallery[self.img_id3]
        img4 = gallery[self.img_id4]
        return img1, img2, img3, img4

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
        phase_mag = 0
        real_imag = 0
        for type in self.types:
            if type == "phase" or type == "magnitude":
                phase_mag += 1
            elif type == "real" or type == "imaginary":
                real_imag += 1
            else:
                pass

        if phase_mag == 0:
            return 1
        elif real_imag == 0:
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
        img_objs = self.extract_img_from_gallery(gallery)
        mask = np.ones(img_objs[0].shape)
        # inner mode
        # dimensions x1,x2, y1,y2
        if crop_mode == 1:
            mask = np.zeros(img_objs[0].shape)
            mask[
                dimensions[2] : dimensions[3] + 1, dimensions[0] : dimensions[1] + 1
            ] = 1

        elif crop_mode == 2:
            mask = np.ones(img_objs[0].shape)
            mask[
                dimensions[2] : dimensions[3] + 1, dimensions[0] : dimensions[1] + 1
            ] = 0

        mode = self.choose_mode()

        # Determine the total number of iterations for the progress bar
        total_iterations = len(img_objs)

        # Create a tqdm progress bar
        progress_bar = tqdm(
            total=total_iterations, desc="Processing images", unit="image"
        )

        if mode == 2:
            magnitudes = np.zeros(img_objs[0].shape)
            phases = np.zeros(img_objs[0].shape)

            for i, img_obj in enumerate(img_objs):
                if self.types[i] == "magnitude":
                    magnitudes += (
                        2 * self.weights[i] * np.abs(img_obj.get_fft_shifted())
                    )
                elif self.types[i] == "phase":
                    phases += 2 * self.weights[i] * np.angle(img_obj.get_fft_shifted())

                # Update the progress bar
                progress_bar.update(1)

            # Close the progress bar when the loop is done
            progress_bar.close()

            return np.clip(
                np.abs(
                    np.fft.ifft2((magnitudes * mask) * np.exp(1j * (phases * mask)))
                ),
                0,
                225,
            )

        elif mode == 1:
            real = np.zeros(img_objs[0].shape)
            imaginary = np.zeros(img_objs[0].shape)

            for i, img_obj in enumerate(img_objs):
                if self.types[i] == "real":
                    real += self.weights[i] * img_obj.real
                elif self.types[i] == "imaginary":
                    imaginary += self.weights[i] * img_obj.imaginary

                # Update the progress bar
                progress_bar.update(1)

            # Close the progress bar when the loop is done
            progress_bar.close()

            return np.clip(
                np.abs(np.fft.ifft2(real * mask + imaginary * mask * 1j)), 0, 225
            )
