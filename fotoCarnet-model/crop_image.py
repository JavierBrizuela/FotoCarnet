class CropImage:
    def __init__(
                    self, 
                    image,
                    face_x: int,
                    face_y: int,
                    face_w: int,
                    face_h: int,
                    top_hair: int,
                    width: float = 4.0,
                    height: float = 4.0,
                    dpi: int = 300,
                    face_percentage: int = 70, 
                )
        self.image = image
        self.face_x = face_x
        self.face_y = face_y
        self.face_w = face_w
        self.face_h = face_h
        self.top_hair = top_hair
        self.width = width
        self.height = height
        self.dpi = dpi
        self.face_percentage = face_percentage
        
    