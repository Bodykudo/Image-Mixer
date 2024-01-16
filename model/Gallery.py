from model.Image import Image


class Gallery:
    def __init__(self):
        self.ids_to_objects = {}

    def add_image(self, image_object, image_id):
        self.ids_to_objects[image_id] = image_object

    def get_gallery(self):
        return self.ids_to_objects
