class Vertex():
    x = None
    y = None 
    xy = None

    def __init__(self, x:float, y:float):
        self.x = x
        self.y = y
        self.xy = [x,y]

    def get_xy(self) -> list:
        return self.xy
    
    def get_y(self) -> float:
        return self.y
    
    def get_x(self) -> float:
        return self.x