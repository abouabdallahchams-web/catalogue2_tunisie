from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window

class CatalogueTunisie(App):
    def build(self):
        # On définit un fond de page (gris très clair)
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        
        # Organisation principale
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        # Titre de l'application
        self.label_titre = Label(
            text="MON CATALOGUE\nTUNISIE",
            font_size='32sp',
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            halign='center'
        )
        
        # Bouton d'action
        btn_voir = Button(
            text="VOIR LES OFFRES",
            size_hint=(1, 0.2),
            background_color=(0.1, 0.6, 0.3, 1), # Vert
            color=(1, 1, 1, 1),
            font_size='20sp'
        )
        # On dit au bouton de changer le texte quand on clique
        btn_voir.bind(on_press=self.changer_message)
        
        # Ajout des éléments au layout
        layout.add_widget(self.label_titre)
        layout.add_widget(btn_voir)
        
        return layout

    def changer_message(self, instance):
        self.label_titre.text = "Chargement des\nCatalogues..."

if __name__ == '__main__':
    CatalogueTunisie().run()
