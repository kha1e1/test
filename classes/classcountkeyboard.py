

class Button:
    def __init__(self):
        self.clicks =0


    def clickvpered(self):
        self.clicks += 1


    def clicknazad(self):
        self.clicks-=1


    def reset(self):
        self.clicks = 0



    def click_count(self):
        return self.clicks
Button=Button()