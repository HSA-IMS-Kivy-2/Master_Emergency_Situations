'''
Created on 24.04.2014

@author: Adrian.Zuerl
'''
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.app import Builder
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.uix.scatter import Scatter
from kivy.animation import Animation
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.image import Image
#from kivy.uix.video import Video
from kivy.core.audio import SoundLoader

import logging
import random

Builder.load_file('person.kv')
Builder.load_file('level.kv')

KV_LANG_LEVELNAME = 'level'

currentLevel = 0 #muss bei erfolgreichem level hochgesetzt werden

isFinished = False

isHelpCalled = False

isFirstStart = True

levelProps = ["Tools", "Persons", "SceneImage", "Video", "Sound"]
level0 = {
          levelProps[0]: [['res/DLK.png', True], ['res/krankenwagen.png', False], ['res/verband.png', False]],
          levelProps[1]: [['res/feuerwehrmann.png', True], ['res/polizist.png', False], ['res/sani.png', False]],
          levelProps[2]: 'res/scene1.png',
          levelProps[3]: 'res/scene1_ok.png',
          levelProps[4]: 'res/sounds/meow.wav'
          }
level1 = {
          levelProps[0]: [['res/kran.png', False], ['res/TLF.png', True], ['res/handschellen.png', False]],
          levelProps[1]: [['res/tierarzt.png', False], ['res/sani.png', False], ['res/agt.png', True]],
          levelProps[2]: 'res/scene2.png',
          levelProps[3]: 'res/scene2_ok.png',
          levelProps[4]: 'res/sounds/fire.wav'
          }
level2 = {
          levelProps[0]: [['res/verband.png', False], ['res/handschellen.png', True], ['res/TLF.png', False]],
          levelProps[1]: [['res/polizist.png', True], ['res/feuerwehrmann.png', False], ['res/thw_mann.png', False]],
          levelProps[2]: 'res/scene3.png',
          levelProps[3]: 'res/scene3_ok.png',
          levelProps[4]: 'res/sounds/cuff.wav'
          }
level3 = {
          levelProps[0]: [['res/krankenwagen.png', True], ['res/DLK.png', False], ['res/handschellen.png', False]],
          levelProps[1]: [['res/polizist.png', False], ['res/sani.png', True], ['res/thw_mann.png', False]],
          levelProps[2]: 'res/scene4.png',
          levelProps[3]: 'res/scene4_ok.png',
          levelProps[4]: 'res/sounds/ambulance.wav'
          }
level4 = {
          levelProps[0]: [['res/TLF.png', False], ['res/DLK.png', False], ['res/kran.png', True]],
          levelProps[1]: [['res/tierarzt.png', False], ['res/sani.png', False], ['res/thw_mann.png', True]],
          levelProps[2]: 'res/scene5.png',
          levelProps[3]: 'res/scene5_ok.png',
          levelProps[4]: 'res/sounds/tree.wav'
          }
level5 = {
          levelProps[0]: [['res/krankenwagen.png', False], ['res/DLK.png', False], ['res/verband.png', True]],
          levelProps[1]: [['res/tierarzt.png', True], ['res/feuerwehrmann.png', False], ['res/agt.png', False]],
          levelProps[2]: 'res/scene6.png',
          levelProps[3]: 'res/scene6_ok.png',
          levelProps[4]: 'res/sounds/dog.wav'
          }

levels = [level0, level1, level2, level3, level4, level5]

class Helper(Scatter):
    
    animPosX = 0
    animPosY = 0
    img = None
    
    def __init__(self, size,pos,animPosX,animPosY, **kwargs):
        super(Helper, self).__init__(**kwargs)
        
        self.size=size
        self.do_translation=False
        
        self.pos= pos
        self.animPosX = animPosX
        self.animPosY = animPosY
        
    def setImage(self, imgSource, isLeft):
        self.img = Image(source=imgSource)
        self.img.size = [self.size[0]/1.2,self.size[1]/1.2]
        if isLeft:            
            self.img.pos = [-self.img.size[0]/2,-self.img.size[1]/2]
        else:
            self.img.pos = [self.img.size[0]/2,-self.img.size[1]/2]
            
        self.add_widget(self.img)
        
    def showAnimation(self, dur):
        anim = Animation(x=self.animPosX, y=self.animPosY,t='in_quart',duration=dur)
        anim.start(self)

class Card(Scatter):
    def __init__(self, **kwargs):    
        super(Card, self).__init__(**kwargs)
        self.create_property('initPosition')
        self.create_property('myId')
        self.create_property('isActive')
        self.create_property('isGoal')
    def setImage(self, source):
        self.ids.img.source = source
    
    #http://kivy.org/docs/guide/events.html#dispatching-a-property-event
    #https://groups.google.com/forum/#!msg/kivy-users/VAGH36-KZsE/QiRLTO4GjMUJ
    def on_touch_move(self, touch):        
        if self.collide_point(*touch.pos):
            self.isActive = True
            super(Card, self).on_touch_move(touch)
            return True
        self.isActive = False
        return super(Card, self).on_touch_move(touch)
    
class Person(Card):
    def setActive(self, widget):
        if self.isActive:            
            actualLevel.setPerson(widget)
                
    def personUp(self):
        if self.isActive:            
            actualLevel.snapPersonToTarget(self)
        
class Tool(Card):
    def setActive(self, widget):
        if self.isActive:            
            actualLevel.setTool(widget)
            
    def toolUp(self):
        if self.isActive:
            actualLevel.snapToolToTarget(self)
        
    

class Level(FloatLayout): #uebergeben an level.kv als rootwidget
    
    isPersonOnGoal = False
    isToolOnGoal = False

    activeTool = None
    activePerson = None
    
    levelInfos = None
    
    popup = None
    winSound = None
    failSound = None
    
    helpPopup = None
    
    def __init__(self, level, **kwargs):    
        super(Level, self).__init__(**kwargs)
        
        self.levelInfos = level
        
        self.setLevelImages()
        
        self.activeTool = Scatter()
        self.activePerson = Scatter()          
            
    def hidePopupTitle(self, popup):
        popupLabel = popup.children[0].children[2]
        popupLine = popup.children[0].children[1]
        popup.children[0].remove_widget(popupLabel)
        popup.children[0].remove_widget(popupLine)
        
    def showInitialHelp(self):        
        def go_next_callback(instance):
            self.ids.popupanchor.remove_widget(self.helpPopup)
            return False
        
        box = AnchorLayout(size_hint=(1, 1), anchor_x= "right", anchor_y= "bottom")
        
        img = Image(source='res/help.zip')
            
        img.anim_delay= 0.05
        box.add_widget(img)
        skipBtn = Button(font_size=80, font_name= 'res/fontawesome-webfont.ttf',markup=True, text='[color=49E449]'+unichr(61764)+'[/color]', background_color = [0,0,0,0], size_hint= (0.2, 0.2))
        skipBtn.bind(on_press=go_next_callback)
        box.add_widget(skipBtn)
        
        self.helpPopup = Popup(content=box,size_hint=(0.8, 0.7),auto_dismiss=False)
        self.hidePopupTitle(self.helpPopup)
        
        self.ids.popupanchor.add_widget(self.helpPopup)
        self.helpPopup.open()
        img.size=self.ids.popupanchor.size
        img.allow_stretch = True
        
    def setLevelImages(self):
        random.shuffle(self.levelInfos[levelProps[0]])
        random.shuffle(self.levelInfos[levelProps[1]])

        self.ids.tool1.setImage(self.levelInfos[levelProps[0]][0][0])
        self.ids.tool1.isGoal = self.levelInfos[levelProps[0]][0][1]
        
        self.ids.tool2.setImage(self.levelInfos[levelProps[0]][1][0])
        self.ids.tool2.isGoal = self.levelInfos[levelProps[0]][1][1]
        
        self.ids.tool3.setImage(self.levelInfos[levelProps[0]][2][0])
        self.ids.tool3.isGoal = self.levelInfos[levelProps[0]][2][1]
        
        self.ids.person1.setImage(self.levelInfos[levelProps[1]][0][0])
        self.ids.person1.isGoal = self.levelInfos[levelProps[1]][0][1]
        
        self.ids.person2.setImage(self.levelInfos[levelProps[1]][1][0])
        self.ids.person2.isGoal = self.levelInfos[levelProps[1]][1][1]
        
        self.ids.person3.setImage(self.levelInfos[levelProps[1]][2][0])
        self.ids.person3.isGoal = self.levelInfos[levelProps[1]][2][1]
        
        self.ids.sceneImage.source = self.levelInfos[levelProps[2]]
        
        self.winSound = SoundLoader.load(self.levelInfos[levelProps[4]])
        self.failSound = SoundLoader.load('res/sounds/fail.wav')
        
    def setIdentifiers(self):
        self.ids.tool1.myId = "tool1"
        self.ids.tool2.myId = "tool2"
        self.ids.tool3.myId = "tool3"
        self.ids.person1.myId = "person1"
        self.ids.person2.myId = "person2"
        self.ids.person3.myId = "person3"
        
    
    def setPositions(self):
        self.ids.tool1.initPosition = self.ids.tool1.pos
        self.ids.tool2.initPosition = self.ids.tool2.pos
        self.ids.tool3.initPosition = self.ids.tool3.pos
        
        self.ids.person1.initPosition = self.ids.person1.pos
        self.ids.person2.initPosition = self.ids.person2.pos
        self.ids.person3.initPosition = self.ids.person3.pos        
        
    
    def showHelp(self):
        if not isHelpCalled:
            global isHelpCalled
            isHelpCalled = True
            dismissBtn = Button(background_color = [0,0,0,0])
            
            helpT = Helper(self.ids.tool1.size, [self.size[0]/8, self.size[1]/2.5], self.size[0]/2-self.size[0]/4, self.size[1]/2)
            helpP = Helper(self.ids.person1.size, [self.size[0]-(self.size[0]/4), self.size[1]/1.5], self.size[0]/2, self.size[1]/2.1)
            
            helpT.setImage('res/hand_l.png', True)
            helpP.setImage('res/hand_r.png', False)            
            
            self.add_widget(helpT)
            self.add_widget(helpP)
            
            def dismiss_callback(instance):
                self.remove_widget(helpT)
                self.remove_widget(helpP)
                                   
                self.remove_widget(dismissBtn)
                
                global isHelpCalled
                isHelpCalled = False
                
            dismissBtn.bind(on_press=dismiss_callback)        
            self.add_widget(dismissBtn)  
            
            helpT.showAnimation(1)
            helpP.showAnimation(0.9)
         
    def setTool(self, widget):
        self.activeTool = widget
        
    def setPerson(self, widget):
        self.activePerson = widget
        
    def snap(self, widget, target, index):
        windowSize = self.size
        xTarget = 0
        yTarget = 0
        if index == 0: #tool
            xTarget = (windowSize[0]/2)-target.size[0]/4        
        if index == 1: #person
            xTarget = 0-(windowSize[0]/2)+target.size[0]/2+target.size[0]/4        
        anim = Animation(center_x=xTarget, center_y=yTarget,t='in_sine',duration=0.2)
        anim.start(widget)
        
    def snapOtherToolsBack(self, tool):
        for t in tool.parent.children: #alle anderen karten wieder an ihre alte position schieben
            if t.myId != tool.myId:
                anim = Animation(x=t.initPosition[0]*self.size[0], y=t.initPosition[1]*self.size[1],t='in_sine',duration=0.2)
                anim.start(t)
                    
    def snapOtherPersonsBack(self, person):
        for p in person.parent.children:
            if p.myId != person.myId:
                anim = Animation(x=p.initPosition[0]*self.size[0], y=p.initPosition[1]*self.size[1],t='in_sine',duration=0.2)
                anim.start(p)
        
    def snapToolToTarget(self, tool):
        if self.isToolOnGoal:
            self.snap(tool,self.ids.target1,0)
            
            self.snapOtherToolsBack(tool)
            
            self.handleGoal()
            
            if not tool.isGoal and self.isPersonOnGoal:
                if self.failSound:
                    self.failSound.play()
                    
            
                   
    def snapPersonToTarget(self, person):
        if self.isPersonOnGoal:
            self.snap(person,self.ids.target1,1)
            
            self.snapOtherPersonsBack(person)
                    
            self.handleGoal()
            
            if not person.isGoal and self.isToolOnGoal:
                if self.failSound:
                    self.failSound.play()
            
    def handleGoal(self):
        def go_next_callback(instance):
            self.popup.dismiss()
            main.switchLevel()
            return False
            
        if self.isToolOnGoal and self.isPersonOnGoal:
            if self.activeTool.isGoal and self.activePerson.isGoal:
                print "FINISHED? ",isFinished
                while not isFinished: #notwendig, weil sonst 2 mal aufgerufen (touch_events feuern alle 2 mal)
                    global isFinished
                    isFinished = True
                    
                    btnBGSource = ''
                         
                    if currentLevel <= len(levels)-1:
                        btnBGSource = unichr(61518)
                    else:
                        btnBGSource = unichr(61470)
                                           
                    box = AnchorLayout(size_hint=(1, 1), anchor_x= "right", anchor_y= "bottom")     
                    btn = Button(font_size=100, font_name= 'res/fontawesome-webfont.ttf', text=btnBGSource, background_color = [0,0,0,0.7])
                    btn.bind(on_press=go_next_callback)
                    
                    #vid = Video(source=self.levelInfos[levelProps[3]], play=True)                    
                    #box.add_widget(vid)
                    
                    #instead of laggy video insert just an image
                    img = Image(source=self.levelInfos[levelProps[3]])
                    img.allow_stretch = True
                    box.add_widget(img)
                    imgBtn = Button(font_size=60, font_name= 'res/fontawesome-webfont.ttf', text=btnBGSource, background_color = [0,0,0,0], size_hint= (0.15, 0.15))
                    imgBtn.bind(on_press=go_next_callback)
                    box.add_widget(imgBtn)
                    
                    def end_of_vid(video, eos):
                        logging.info("endofvid")
                        #video.play=False #not working on android...
                        box.add_widget(btn)
                        #video.unload() #not working on android...
                        #logging.info("video unloaded")
                        
                    def showit():
                        print "showing video popup"
                        self.popup.open()
                        if self.winSound:
                            self.winSound.play()

                    #vid.bind(loaded=lambda foo,bar: showit())
                    #vid.bind(eos=lambda video,eos:end_of_vid(video,eos))
                                                                          
                         
                    self.popup = Popup(content=box,size_hint=(0.8, 0.7),auto_dismiss=False)
                    
                    self.hidePopupTitle(self.popup)
                    
                    showit()
                    Clock.schedule_once(lambda wumpe:box.add_widget(btn), 8)

    def update(self, dt):
        if not isFinished:
            target = self.ids.target1
            if self.isCollision(self.activeTool, target) | self.isCollision(self.activePerson, target):
                target.background_color= [0,1,0,0.5]
                if self.isCollision(self.activeTool, target): 
                    self.isToolOnGoal = True
                else:
                    self.isToolOnGoal = False             
                if self.isCollision(self.activePerson, target):
                    self.isPersonOnGoal = True
                else:
                    self.isPersonOnGoal = False
                    
            else:
                target.background_color= [0,0,0,0.5]
                self.isPersonOnGoal = False
                self.isToolOnGoal = False
            
            #self.whatsActive()
        else:
            return False #remove the schedule
        
    
    def whatsActive(self):
        print "_____"
        try:
            print "activeTool?", self.activeTool.myId, "activePerson?", self.activePerson.myId
            print "tool?", self.isToolOnGoal, "person?", self.isPersonOnGoal
        except Exception as e:
            return
    

    def isCollision(self, first, target):
        #http://robertour.com/2013/10/11/to_window-to_local-methods-kivy/
        bildCoords = first.to_window(first.pos[0], first.pos[1])
        xBild = bildCoords[0]
        yBild = bildCoords[1]
        bildWidth = first.size[0]
        bildHeight = first.size[1]
        
        targetCoords = target.to_window(target.pos[0], target.pos[1])
        xTarget = targetCoords[0]
        yTarget = targetCoords[1]
        targetWidth = target.size[0]
        targetHeight = target.size[1]
        
        if xTarget < xBild and xTarget+targetWidth >= xBild+bildWidth and yTarget < yBild and yTarget+targetHeight >= yBild+bildHeight:
            return True
        else:
            return False
        
actualLevel = Level(levels[0])
   
class MainScreenApp(App):   
    def build(self):
        self.title = 'Master Emergency Situations - A game for Toddlers'
        self.switchLevel()
        pass
    
    def switchLevel(self):
        global isFinished
        isFinished = False
        
        if currentLevel <= len(levels)-1:
            self.addNewLevel()
            actualLevel.setPositions()
            actualLevel.setIdentifiers()
        else:
            self.createRestart()

    def createRestart(self):
        self.restart()
        self.switchLevel()
        
    def restart(self):
        global currentLevel
        currentLevel = 0
        
        for i in range(len(self.root.ids.screen_manager.screens)):
            self.root.ids.screen_manager.screens.pop()
            print "removed screen at index", i
            
        print "screenmanager clear!", len(self.root.ids.screen_manager.screens)
        
    
    def addNewLevel(self):
        print "adding new level"      
        scr = Screen(name= KV_LANG_LEVELNAME +str(currentLevel))
        global actualLevel
        actualLevel = Level(levels[currentLevel])
        Clock.schedule_interval(actualLevel.update, 1.0 / 60.0)
        scr.add_widget(actualLevel)
        
        try:
            self.root.ids.screen_manager.switch_to(scr) #letzen alten screen entfernen
            if isFirstStart:
                actualLevel.showInitialHelp()
                global isFirstStart
                isFirstStart = False
        except Exception as e:
            print e
            
        print "screenmanager now contains:", self.root.ids.screen_manager.screens
        
        global currentLevel
        currentLevel += 1
        
        self.root.ids.title.text = 'Master Emergency Situations - [color=00E1D0]A game for Toddlers[/color]'
        
    def showHelp(self):
        actualLevel.showHelp()
        

main = MainScreenApp()
if __name__ == '__main__':
    main.run()