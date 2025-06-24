#!/usr/bin/env python3


import pygame as pg




class Button(object):
    """A fairly straight forward button class."""

    def __init__(self, rect, color, function, **kwargs):
        self.rect = pg.Rect(rect)
        self.color = color
        self.function = function
        self.clicked = False
        self.hovered = False
        self.hover_text = None
        self.clicked_text = None
        self.process_kwargs(kwargs)
        self.render_text()
        self.has_been_activated = False     #like a switch button

    def process_kwargs(self, kwargs):
        """Various optional customization you can change by passing kwargs."""
        settings = {
            "text": None,
            "font": pg.font.Font(None, 16),
            "call_on_release": False,
            "hover_color": None,
            "clicked_color": None,
            "font_color": pg.Color("black"),
            "hover_font_color": None,
            "clicked_font_color": None,
            "click_sound": None,
            "hover_sound": None,
            "border_color" : pg.Color("black"),
            "enable_render" : True,
            "alternate_text" : None,
            "alternate_color" : None,
            "func_arg" : None,
        }
        for kwarg in kwargs:
            if kwarg in settings:
                settings[kwarg] = kwargs[kwarg]
            else:
                raise AttributeError("Button has no keyword: {}".format(kwarg))
        self.__dict__.update(settings)

    def render_text(self):
        """Pre render the button text."""
        if self.alternate_text:     #Hacky stuff here
            if self.hover_font_color:
                color = self.hover_font_color
                self.hover_text = self.font.render(self.alternate_text, True, color)
            if self.clicked_font_color:
                color = self.clicked_font_color
                self.clicked_text = self.font.render(self.alternate_text, True, color)
            self.alternate_text = self.font.render(self.alternate_text, True, self.font_color)

        if self.text:
            if self.hover_font_color:
                color = self.hover_font_color
                self.hover_text = self.font.render(self.text, True, color)
            if self.clicked_font_color:
                color = self.clicked_font_color
                self.clicked_text = self.font.render(self.text, True, color)
            self.text = self.font.render(self.text, True, self.font_color)

    def check_event(self, event):
        """The button needs to be passed events from your program event loop."""
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.on_click(event)
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.on_release(event)

    def on_click(self, event):
        if self.rect.collidepoint(event.pos):
            self.clicked = True
            self.has_been_activated = not self.has_been_activated
            if not self.call_on_release and self.function != None:
                if self.func_arg:
                    self.function(self.func_arg)
                else: self.function()
            elif self.function == None :
                return 1
        elif self.function == None :
            return 0

    def on_release(self, event):
        if self.clicked and self.call_on_release:
            self.function()
        self.clicked = False

    def check_hover(self):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            if not self.hovered:
                self.hovered = True
                if self.hover_sound:
                    self.hover_sound.play()
        else:
            self.hovered = False

    def update(self, surface):
        """Update needs to be called every frame in the main loop."""
        color = self.color
        text = self.text
        alternate_text = self.alternate_text
        alternate_color = self.alternate_color
        self.check_hover()
        if self.clicked and self.clicked_color:
            color = self.clicked_color
            if self.clicked_font_color:
                text = self.clicked_text
        elif self.hovered and self.hover_color:
            color = self.hover_color
            if self.hover_font_color:
                text = self.hover_text
        if self.enable_render == True:
            surface.fill(self.border_color, self.rect)
            if self.alternate_color and self.has_been_activated == True:
                surface.fill(alternate_color, self.rect.inflate(-4, -4))
            else:
                surface.fill(color, self.rect.inflate(-4, -4))

        if self.alternate_text and self.has_been_activated == True:
            text_rect = alternate_text.get_rect(center=self.rect.center)
            surface.blit(alternate_text, text_rect)
        elif self.text:
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text, text_rect)
