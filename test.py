import kivy
kivy.require('1.8.0') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.uix.video import Video
from kivy.uix.floatlayout import FloatLayout

class MyApp(App):

    def build(self):
        layout = FloatLayout(size=(300, 300))
        s1 = Scatter()
        #s2 = Scatter()
        
        image1 = Video(source='animation1.mp4', play=True)
        #image2 = Image(source='fish.jpg')
        
        s1.add_widget(image1,0)
        #s2.add_widget(image2,1)
        
        layout.add_widget(s1)
        #layout.add_widget(s2)
        
        return layout
        #return Label(text='Hello world')


if __name__ == '__main__':
    MyApp().run()