class TextElement:
    def __init__(self, screen, x, y, font, text, color=(255,255,255), shadow=False, show=True):
        self.screen = screen
        self.x = x
        self.y = y
        self.show = show
        self.font = font
        self.color = color
        self.display_shadow = shadow
        self.text = self.font.render(text, True, color)
        self.shadow = self.font.render(text, True, (0,0,0))
    
    def update_text(self, text):
        self.text = self.font.render(text, True, self.color)
        self.shadow = self.font.render(text, True, (0,0,0))
    
    def draw(self):
        if self.show is False:
            return
        if self.display_shadow is True:
            self.screen.blit(self.shadow, (self.x+1, self.y-1))
            self.screen.blit(self.shadow, (self.x+1, self.y+1))
            self.screen.blit(self.shadow, (self.x-1, self.y-1))
            self.screen.blit(self.shadow, (self.x-1, self.y+1))
        self.screen.blit(self.text, (self.x, self.y))