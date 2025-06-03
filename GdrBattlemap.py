import pygame
import os
import sys
import pygame.colordict
from pygame import gfxdraw
from tkinter import Tk, colorchooser, filedialog

class DnDBattlemap:
    def __init__(self):
        pygame.init()
        self.screen_width, self.screen_height = 1200, 800
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), 
            pygame.RESIZABLE
        )
        pygame.display.set_caption("GdrBattlemap")
        self.fullscreen = False
        self.original_size = (self.screen_width, self.screen_height)

        # Gestione del path per l'eseguibile
        def resource_path(relative_path):
            try:
                base_path = sys._MEIPASS  # cartella temporanea usata da PyInstaller
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)

        # Carica l'icona
        try:
            icon_path = resource_path('jku1fnv5f7461.png')
            icon = pygame.image.load(icon_path)
            pygame.display.set_icon(icon)
        except Exception as e:
            print("Errore nel caricamento dell'icona - usando icona default:", e)

        # Variabili immagine
        self.original_img = None  # Per conservare l'immagine originale
        self.scale_factor = 1.0  # Fattore di scala corrente
        self.offset_x = 0  # Offset per centrare l'immagine
        self.offset_y = 0
                
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.LIGHT_GRAY = (230, 230, 230)
        self.current_color = (255, 0, 0)  # Default red
        
        # App state
        self.bg_image = None
        self.bg_rect = None
        self.grid_size = 50  # default grid size in pixels
        self.show_grid = True
        self.tokens = []
        self.selected_token = None
        self.dragging = False
        self.hex_color = "#FF0000"
        
        # UI elements
        self.font = pygame.font.SysFont('Arial', 16)
        self.bold_font = pygame.font.SysFont('Arial', 16, bold=True)
        self.load_button = pygame.Rect(10, 10, 180, 30)
        self.grid_button = pygame.Rect(10, 50, 180, 30)
        self.size_up_button = pygame.Rect(10, 90, 85, 30)
        self.size_down_button = pygame.Rect(105, 90, 85, 30)
        self.add_token_button = pygame.Rect(10, 130, 180, 30)
        self.color_picker_button = pygame.Rect(10, 170, 180, 30)
        self.hex_input_rect = pygame.Rect(10, 210, 180, 30)
        self.delete_button = pygame.Rect(10, 250, 180, 30)
        
        self.hex_text = "FF0000"
        self.hex_active = False
        
        self.running = True
        
    def handle_resize(self, event):
        if not self.fullscreen:
            self.screen_width, self.screen_height = event.size
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height),
                pygame.RESIZABLE
            )
        
    def load_image(self):
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Select Battlemap Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        root.destroy()
        
        if file_path:
            try:
                self.original_img = pygame.image.load(file_path)
                self.bg_image = self.original_img.copy()
                self.update_image_position()
            except Exception as e:
                print(f"Error loading image: {e}")

    def update_image_position(self):
        if not self.original_img:
            return
            
        # Calcola la scala mantenendo le proporzioni
        img_width, img_height = self.original_img.get_size()
        available_width = self.screen_width - 200  # Lascia spazio per il pannello UI
        available_height = self.screen_height
        
        scale_w = available_width / img_width
        scale_h = available_height / img_height
        self.scale_factor = min(scale_w, scale_h)
        
        # Scala l'immagine
        new_size = (int(img_width * self.scale_factor), int(img_height * self.scale_factor))
        self.bg_image = pygame.transform.scale(self.original_img, new_size)
        
        # Calcola l'offset per centrare
        self.offset_x = (self.screen_width - 200 - new_size[0]) // 2 + 200
        self.offset_y = (self.screen_height - new_size[1]) // 2
        
        self.bg_rect = self.bg_image.get_rect(topleft=(self.offset_x, self.offset_y))
        
        # Aggiorna posizione token
        for token in self.tokens:
            # Converti dalla posizione originale alla posizione scalata
            original_pos = self.get_original_position(token['pos'])
            token['pos'] = self.get_scaled_position(original_pos)

    def get_original_position(self, scaled_pos):
        """Converti coordinate scalate a originali"""
        if not self.bg_rect:
            return scaled_pos
        orig_x = (scaled_pos[0] - self.offset_x) / self.scale_factor
        orig_y = (scaled_pos[1] - self.offset_y) / self.scale_factor
        return (orig_x, orig_y)

    def get_scaled_position(self, original_pos):
        """Converti coordinate originali a scalate"""
        if not self.bg_rect:
            return original_pos
        scaled_x = original_pos[0] * self.scale_factor + self.offset_x
        scaled_y = original_pos[1] * self.scale_factor + self.offset_y
        return (scaled_x, scaled_y)

    def handle_resize(self, event):
        if not self.fullscreen:
            self.screen_width, self.screen_height = event.size
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height),
                pygame.RESIZABLE
            )
            self.update_image_position()

    def get_cell_center(self, pos):
        """Ora lavora con coordinate originali"""
        if not self.bg_rect:
            return pos
            
        # Converti a coordinate originali
        orig_pos = self.get_original_position(pos)
        
        # Calcola centro cella nelle coordinate originali
        cell_x = int(orig_pos[0] // self.grid_size * self.grid_size) + self.grid_size // 2
        cell_y = int(orig_pos[1] // self.grid_size * self.grid_size) + self.grid_size // 2
        
        # Ritorna a coordinate scalate
        return self.get_scaled_position((cell_x, cell_y))
        
    def open_color_picker(self):
        """Open a color picker dialog"""
        root = Tk()
        root.withdraw()
        color = colorchooser.askcolor(title="Choose Token Color", initialcolor=self.current_color)
        root.destroy()
        
        if color[0]:  # User didn't cancel
            self.current_color = tuple(int(c) for c in color[0])
            self.hex_text = self.rgb_to_hex(self.current_color)
    
    def rgb_to_hex(self, rgb):
        """Convert RGB tuple to HEX string"""
        return "#{:02X}{:02X}{:02X}".format(*rgb)
    
    def try_hex_to_rgb(self, hex_str):
        """Try to convert HEX string to RGB tuple"""
        hex_str = hex_str.strip("#")
        try:
            if len(hex_str) == 3:
                return tuple(int(c*2, 16) for c in hex_str)
            elif len(hex_str) == 6:
                return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            return None
        return None
    
    def draw_grid(self):
        """Draw a grid over the background image"""
        if not self.bg_image or not self.show_grid:
            return
            
        rect = self.bg_rect
        # Vertical lines
        for x in range(rect.left, rect.right + 1, self.grid_size):
            pygame.draw.line(self.screen, self.BLACK, (x, rect.top), (x, rect.bottom), 1)
        # Horizontal lines
        for y in range(rect.top, rect.bottom + 1, self.grid_size):
            pygame.draw.line(self.screen, self.BLACK, (rect.left, y), (rect.right, y), 1)
    
    def draw_tokens(self):
        """Draw all tokens on the battlemap"""
        for token in self.tokens:
            # Draw circle with anti-aliasing
            pygame.gfxdraw.filled_circle(
                self.screen, 
                token['pos'][0], 
                token['pos'][1], 
                self.grid_size // 2 - 5, 
                token['color']
            )
            pygame.gfxdraw.aacircle(
                self.screen, 
                token['pos'][0], 
                token['pos'][1], 
                self.grid_size // 2 - 5, 
                self.BLACK
            )
            
            # Draw selection highlight
            if token == self.selected_token:
                pygame.gfxdraw.aacircle(
                    self.screen, 
                    token['pos'][0], 
                    token['pos'][1], 
                    self.grid_size // 2 - 2, 
                    self.WHITE
                )
    
    def get_cell_center(self, pos):
        """Get the center position of the grid cell that contains the given position"""
        if not self.bg_rect:
            return pos
            
        # Calculate position relative to the image
        rel_x = pos[0] - self.bg_rect.left
        rel_y = pos[1] - self.bg_rect.top
        
        # Find cell coordinates
        cell_x = int(rel_x // self.grid_size)
        cell_y = int(rel_y // self.grid_size)
        
        # Calculate center of the cell
        center_x = self.bg_rect.left + cell_x * self.grid_size + self.grid_size // 2
        center_y = self.bg_rect.top + cell_y * self.grid_size + self.grid_size // 2
        
        return (center_x, center_y)
    
    def add_token(self, pos):
        """Add a new token at the specified position"""
        if not self.bg_rect or not self.bg_rect.collidepoint(pos):
            return
            
        center_pos = self.get_cell_center(pos)
        self.tokens.append({
            'pos': center_pos,
            'color': self.current_color
        })
    
    def delete_token(self):
        """Delete the selected token"""
        if self.selected_token:
            self.tokens.remove(self.selected_token)
            self.selected_token = None
    
    def draw_ui(self):
        """Draw the user interface controls"""
        # Side panel background
        pygame.draw.rect(self.screen, self.GRAY, (0, 0, 200, self.screen_height))
        
        # Buttons
        pygame.draw.rect(self.screen, self.LIGHT_GRAY, self.load_button)
        pygame.draw.rect(self.screen, self.LIGHT_GRAY, self.grid_button)
        pygame.draw.rect(self.screen, self.LIGHT_GRAY, self.size_up_button)
        pygame.draw.rect(self.screen, self.LIGHT_GRAY, self.size_down_button)
        pygame.draw.rect(self.screen, self.LIGHT_GRAY, self.add_token_button)
        pygame.draw.rect(self.screen, self.LIGHT_GRAY, self.color_picker_button)
        pygame.draw.rect(self.screen, self.LIGHT_GRAY, self.delete_button)
        
        # Current color preview
        pygame.draw.rect(self.screen, self.current_color, (150, 180, 30, 20))
        
        # Hex input
        pygame.draw.rect(self.screen, self.WHITE if not self.hex_active else self.LIGHT_GRAY, self.hex_input_rect)
        pygame.draw.rect(self.screen, self.BLACK, self.hex_input_rect, 1)
        
        # Button labels
        self.draw_text("Carica immagine", self.load_button.center, self.BLACK)
        self.draw_text(f"Griglia: {'ON' if self.show_grid else 'OFF'}", self.grid_button.center, self.BLACK)
        self.draw_text("+ ", self.size_up_button.center, self.BLACK)
        self.draw_text(" -", self.size_down_button.center, self.BLACK)
        self.draw_text(f" Griglia: {self.grid_size}px ", (100, 105), self.BLACK)
        self.draw_text("Aggiungi Token", self.add_token_button.center, self.BLACK)
        self.draw_text("Scegli Colore", self.color_picker_button.center, self.BLACK)
        self.draw_text("Cancella Token", self.delete_button.center, self.BLACK)
        
        # Hex input text
        hex_surface = self.font.render(self.hex_text, True, self.BLACK)
        self.screen.blit(hex_surface, (self.hex_input_rect.x + 5, self.hex_input_rect.y + 7))
        
        # Instructions
        instructions = [
            "Comandi:",
            "Premere F per Fullscreen"
        ]
        
        for i, line in enumerate(instructions):
            y_pos = 300 + i*20
            if i == 0:
                self.draw_text(line, (100, y_pos), self.BLACK, bold=True)
            else:
                self.draw_text(line, (20 if i > 10 else 100, y_pos), self.BLACK)
    
    def draw_text(self, text, pos, color, bold=False):
        """Helper function to draw text"""
        font = self.bold_font if bold else self.font
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=pos) if isinstance(pos, tuple) else text_surface.get_rect(topleft=pos)
        self.screen.blit(text_surface, text_rect)
    
    def handle_events(self):
        """Handle user input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check UI buttons first
                    if self.load_button.collidepoint(event.pos):
                        self.load_image()
                    elif self.grid_button.collidepoint(event.pos):
                        self.show_grid = not self.show_grid
                    elif self.size_up_button.collidepoint(event.pos):
                        self.grid_size = min(100, self.grid_size + 5)
                    elif self.size_down_button.collidepoint(event.pos):
                        self.grid_size = max(5, self.grid_size - 5)
                    elif self.add_token_button.collidepoint(event.pos):
                        pass  # Handled below (need to click on map)
                    elif self.color_picker_button.collidepoint(event.pos):
                        self.open_color_picker()
                    elif self.hex_input_rect.collidepoint(event.pos):
                        self.hex_active = True
                    elif self.delete_button.collidepoint(event.pos):
                        self.delete_token()
                    else:
                        # Check if clicked on a token
                        clicked_token = None
                        for token in reversed(self.tokens):  # Check from top (last drawn)
                            distance = ((token['pos'][0] - event.pos[0]) ** 2 + 
                                       (token['pos'][1] - event.pos[1]) ** 2) ** 0.5
                            if distance <= self.grid_size // 2:
                                clicked_token = token
                                break
                        
                        if clicked_token:
                            self.selected_token = clicked_token
                            self.dragging = True
                        elif self.bg_rect and self.bg_rect.collidepoint(event.pos):
                            self.add_token(event.pos)
                            self.selected_token = self.tokens[-1] if self.tokens else None
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragging:
                    self.dragging = False
                    if self.selected_token:
                        self.selected_token['pos'] = self.get_cell_center(event.pos)
            
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                if self.selected_token:
                    # While dragging, follow mouse but will snap when dropped
                    self.selected_token['pos'] = event.pos
            
            elif event.type == pygame.KEYDOWN and self.hex_active:
                if event.key == pygame.K_RETURN:
                    self.hex_active = False
                    # Try to convert HEX to RGB
                    rgb = self.try_hex_to_rgb(self.hex_text)
                    if rgb:
                        self.current_color = rgb
                elif event.key == pygame.K_BACKSPACE:
                    self.hex_text = self.hex_text[:-1]
                else:
                    # Only allow hex characters (0-9, A-F)
                    if event.unicode.upper() in "0123456789ABCDEF" and len(self.hex_text) < 6:
                        self.hex_text += event.unicode.upper()
                        # Try to update color as user types
                        if len(self.hex_text) in (3, 6):
                            rgb = self.try_hex_to_rgb(self.hex_text)
                            if rgb:
                                self.current_color = rgb
                                
            elif event.type == pygame.VIDEORESIZE:
                self.handle_resize(event)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:  # Premi F per toggle fullscreen
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode(
                            (0, 0), 
                            pygame.FULLSCREEN
                        )
                    else:
                        self.screen = pygame.display.set_mode(
                            self.original_size, 
                            pygame.RESIZABLE
                        )
    
    def run(self):
        """Main application loop"""
        while self.running:
            self.handle_events()
            
            # Drawing
            self.screen.fill(self.WHITE)
            
            if self.bg_image:
                self.screen.blit(self.bg_image, self.bg_rect)
                self.draw_grid()
                self.draw_tokens()
            
            self.draw_ui()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = DnDBattlemap()
    app.run()
