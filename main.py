from kivy.uix.camera import Camera
import os
import json
import shutil
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.filechooser import FileChooserIconView
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.logger import Logger

# Configuration
Window.clearcolor = (0.95, 0.95, 0.95, 1)
SAVE_FILE = "catalogue_tunisie.json"
PHOTOS_DIR = "photos_articles"

if not os.path.exists(PHOTOS_DIR):
    os.makedirs(PHOTOS_DIR)

# =================== LOGIQUE MÉTIER ===================
class Article:
    def __init__(self, nom, prix, photo_path=None, description=""):
        self.id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.nom = nom
        self.prix = float(prix)
        self.photo_path = photo_path
        self.description = description

# =================== COMPOSANTS INTERFACE ===================
class ArticleCard(BoxLayout):
    def __init__(self, article, **kwargs):
        super().__init__(**kwargs)
        self.article = article
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 250
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        
        # Image
        img_source = article.photo_path if article.photo_path and os.path.exists(article.photo_path) else "assets/default_product.png"
        self.add_widget(Image(source=img_source, size_hint=(1, 0.6), allow_stretch=True))
        
        # Infos
        info = BoxLayout(orientation='vertical', padding=10)
        info.add_widget(Label(text=article.nom, bold=True, color=(0.2, 0.2, 0.2, 1)))
        info.add_widget(Label(text=f"{article.prix:g} TND", color=(0.85, 0.1, 0.1, 1), bold=True))
        self.add_widget(info)

    def update_graphics(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

# =================== APPLICATION PRINCIPALE ===================
class CatalogueTunisieApp(App):
    def build(self):
        self.articles = []
        self.current_photo_path = None
        
        root = BoxLayout(orientation='vertical')
        
        # 1. Header Rouge
        header = BoxLayout(size_hint_y=0.1, padding=10)
        with header.canvas.before:
            Color(0.85, 0.1, 0.1, 1)
            self.rect_head = Rectangle(size=header.size, pos=header.pos)
        header.add_widget(Label(text="MON CATALOGUE TUNISIEN 🇹🇳", bold=True, font_size='20sp'))
        header.bind(size=self._update_rect, pos=self._update_rect)
        root.add_widget(header)

        # 2. Barre de Recherche
        search_layout = BoxLayout(size_hint_y=0.08, padding=[10, 5])
        self.search_input = TextInput(hint_text="🔍 Rechercher...", multiline=False)
        self.search_input.bind(text=self.filter_articles)
        search_layout.add_widget(self.search_input)
        root.add_widget(search_layout)

        # 3. Zone Articles
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=2, spacing=15, padding=15, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        root.add_widget(self.scroll)

        # 4. Bouton Ajouter
        btn_add = Button(text="➕ AJOUTER", size_hint_y=0.1, background_color=(0.2, 0.7, 0.3, 1), bold=True)
        btn_add.bind(on_press=self.open_add_form)
        root.add_widget(btn_add)

        self.load_articles()
        self.update_display()
        return root

    def _update_rect(self, instance, value):
        self.rect_head.pos = instance.pos
        self.rect_head.size = instance.size

    def filter_articles(self, instance, value):
        search_term = value.lower()
        self.grid.clear_widgets()
        for art in self.articles:
            if search_term in art.nom.lower():
                card = ArticleCard(art)
                card.bind(on_touch_down=self.on_card_click)
                self.grid.add_widget(card)

    def update_display(self):
        self.grid.clear_widgets()
        for art in self.articles:
            card = ArticleCard(art)
            card.bind(on_touch_down=self.on_card_click)
            self.grid.add_widget(card)

    def open_add_form(self, instance):
        self.current_photo_path = None
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.in_nom = TextInput(hint_text="Nom de l'article", multiline=False)
        self.in_prix = TextInput(hint_text="Prix", multiline=False, input_filter='float')
        
        # Ligne de boutons pour les photos
        photo_layout = BoxLayout(spacing=10, size_hint_y=None, height=50)
        
        btn_cam = Button(text="📸 CAMÉRA", background_color=(0.5, 0.5, 0.5, 1))
        btn_cam.bind(on_press=self.open_camera)
        
        btn_ph = Button(text="🖼 GALERIE", background_color=(0.5, 0.5, 0.5, 1))
        btn_ph.bind(on_press=self.open_gallery)
        
        photo_layout.add_widget(btn_cam)
        photo_layout.add_widget(btn_ph)
        
        btn_sv = Button(text="SAUVEGARDER", background_color=(0.2, 0.7, 0.3, 1), bold=True)
        btn_sv.bind(on_press=self.validate_save)
        
        content.add_widget(self.in_nom)
        content.add_widget(self.in_prix)
        content.add_widget(photo_layout)
        content.add_widget(btn_sv)
        
        self.pop = Popup(title="Nouvel Article", content=content, size_hint=(0.9, 0.6))
        self.pop.open()

    def open_gallery(self, instance):
        user_path = os.path.expanduser('~')
        content = BoxLayout(orientation='vertical')
        fc = FileChooserIconView(path=user_path, filters=['*.png', '*.jpg', '*.jpeg'])
        btn = Button(text="CHOISIR", size_hint_y=0.15)
        content.add_widget(fc)
        content.add_widget(btn)
        gal_pop = Popup(title="Galerie", content=content, size_hint=(0.9, 0.9))

        def select(obj):
            if fc.selection:
                dest = os.path.join(PHOTOS_DIR, f"img_{datetime.now().strftime('%M%S')}.jpg")
                shutil.copy2(fc.selection[0], dest)
                self.current_photo_path = dest
                gal_pop.dismiss()
                
        btn.bind(on_press=select)
        gal_pop.open()

    def open_camera(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10)
        try:
            # Initialise la caméra et lance la lecture
            self.cam = Camera(index=0, resolution=(640, 480), play=True)
            content.add_widget(self.cam)

            btn_capture = Button(text="📸 CAPTURER", size_hint_y=0.2, background_color=(0.1, 0.6, 0.9, 1))

            def capture_photo(obj):
                filename = f"cam_{datetime.now().strftime('%M%S')}.png"
                self.current_photo_path = os.path.join(PHOTOS_DIR, filename)
                # Sauvegarde l'image de la caméra
                self.cam.export_to_png(self.current_photo_path)
                cam_pop.dismiss()
                # Éteint la caméra pour libérer la ressource
                self.cam.play = False
                Logger.info(f"Photo capturée : {self.current_photo_path}")

            btn_capture.bind(on_press=capture_photo)
            content.add_widget(btn_capture)

            cam_pop = Popup(title="Appareil Photo", content=content, size_hint=(0.9, 0.9))
            # Éteindre la caméra si on ferme le popup sans capturer
            cam_pop.bind(on_dismiss=lambda x: setattr(self.cam, 'play', False))
            cam_pop.open()
        except Exception as e:
            Logger.error(f"Erreur caméra : {e}")

    def validate_save(self, instance):
        if self.in_nom.text and self.in_prix.text:
            art = Article(self.in_nom.text, self.in_prix.text, self.current_photo_path)
            self.articles.append(art)
            self.save_articles()
            self.update_display()
            self.pop.dismiss()

    def on_card_click(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.show_details(instance.article)

    def show_details(self, article):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Affichage de l'image en grand
        img_source = article.photo_path if article.photo_path and os.path.exists(article.photo_path) else "assets/default_product.png"
        content.add_widget(Image(source=img_source, size_hint_y=0.6))
        
        # Infos textuelles
        details_layout = BoxLayout(orientation='vertical', size_hint_y=0.2)
        details_layout.add_widget(Label(text=f"Nom: {article.nom}", bold=True, font_size='18sp'))
        details_layout.add_widget(Label(text=f"Prix: {article.prix:g} TND", color=(0.85, 0.1, 0.1, 1)))
        content.add_widget(details_layout)
        
        # Boutons d'action
        btns = BoxLayout(size_hint_y=0.2, spacing=10)
        
        btn_edit = Button(text="✏️ MODIFIER", background_color=(0.2, 0.5, 0.8, 1))
        btn_edit.bind(on_press=lambda x: [self.det_pop.dismiss(), self.open_edit_form(article)])
        
        btn_del = Button(text="🗑 SUPPRIMER", background_color=(0.8, 0.2, 0.2, 1))
        btn_del.bind(on_press=lambda x: self.confirm_delete(article))
        
        btns.add_widget(btn_edit)
        btns.add_widget(btn_del)
        content.add_widget(btns)
        
        self.det_pop = Popup(title=f"Détails : {article.nom}", content=content, size_hint=(0.9, 0.8))
        self.det_pop.open()
    def confirm_delete(self, article):
        """Affiche un petit message de confirmation avant de supprimer"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f"Supprimer définitivement\n{article.nom} ?"))
        
        btns = BoxLayout(spacing=10, size_hint_y=0.4)
        btn_oui = Button(text="OUI", background_color=(0.8, 0.2, 0.2, 1))
        btn_non = Button(text="NON")
        
        btns.add_widget(btn_oui)
        btns.add_widget(btn_non)
        content.add_widget(btns)
        
        conf_pop = Popup(title="Confirmation", content=content, size_hint=(0.7, 0.3))
        btn_non.bind(on_press=conf_pop.dismiss)
        btn_oui.bind(on_press=lambda x: [self.delete_art(article), conf_pop.dismiss(), self.det_pop.dismiss()])
        conf_pop.open()

    def open_edit_form(self, article):
        """Ouvre le formulaire avec les données déjà remplies"""
        self.open_add_form(None) # On ouvre le formulaire standard
        self.pop.title = f"Modifier {article.nom}"
        self.in_nom.text = article.nom
        self.in_prix.text = str(article.prix)
        self.current_photo_path = article.photo_path
        
        # On change l'action du bouton sauvegarder pour qu'il mette à jour au lieu d'ajouter
        self.pop.content.children[0].unbind(on_press=self.validate_save)
        
        def update_existing(instance):
            article.nom = self.in_nom.text
            article.prix = float(self.in_prix.text)
            article.photo_path = self.current_photo_path
            self.save_articles()
            self.update_display()
            self.pop.dismiss()
            
        self.pop.content.children[0].bind(on_press=update_existing)

    def delete_art(self, article):
        if article in self.articles:
            self.articles.remove(article)
            self.save_articles()
            self.update_display()
            self.det_pop.dismiss()

    def load_articles(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r') as f:
                for item in json.load(f):
                    self.articles.append(Article(item['nom'], item['prix'], item.get('photo_path')))

    def save_articles(self):
        with open(SAVE_FILE, 'w') as f:
            json.dump([vars(a) for a in self.articles], f)

if __name__ == '__main__':
    CatalogueTunisieApp().run()