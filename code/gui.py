from __future__ import absolute_import
from __future__ import print_function
from tkinter import *
import tkinter.ttk as ttk
from PIL import Image , ImageTk
from tkinter.messagebox import showinfo
#----------now for simualtion uses-----------------#
from memory import Memory
from testing_simulation import Simulation
from training_simulation import TSimulation
from generator import TrafficGenerator
from model import TestModel , TrainModel
from visualization import Visualization
from utils import set_sumo, set_test_path, set_train_path
import datetime



       

class MyWindow:
    def __init__(self, win, width, height, f2):
        self.f2=f2
        background = 'assets/logo650x500.jpg'
        photo = ImageTk.PhotoImage(Image.open(background))
        canvas = Canvas(win, width=width, height=height)
        canvas.imageList = []
        canvas.pack()
        canvas.create_image(0, 0, anchor="nw", image=photo)
        canvas.imageList.append(photo)    
        
        combostyle = ttk.Style()
        combostyle.theme_create('combostyle', parent='alt',
                                 settings = {'TCombobox':
                                             {'configure':
                                              {'relief':'RIDGE',
                                               'background': 'palegreen2',
                                               'selectbackground': 'palegreen2',
                                               'selectforeground': 'black'
                                               }}}
                                 )
       
        combostyle.theme_use('combostyle') 
        
        self.lbl0 = Text(win, state='disabled', width=62, height=2,relief=RIDGE,bg='khaki2', font=('Arial', 8, 'bold'),bd=1)
        self.lbl0.configure(state='normal')
        self.lbl0.insert('end', 'Set the values and run the trainer, if you choose with gui sumo\nwill open and you need to close it manually as the simulation ends.')
        self.lbl0.configure(state='disabled')
       
        self.lbl1=Label(win, text='Set number (0-3000)', relief=RIDGE, width=17)
        self.lbl1we=Label(win, text=' W_E Cars ', relief=RIDGE, width=8)
        self.lbl1ew=Label(win, text=' E_W Cars', relief=RIDGE, width=8)
        self.lbl1ns=Label(win, text=' N_S Cars', relief=RIDGE, width=8)
        self.lbl1sn=Label(win, text=' S_N Cars', relief=RIDGE, width=8)
        self.lbl1wn=Label(win, text=' W_N Cars', relief=RIDGE, width=8)
        self.lbl1ws=Label(win, text=' W_S Cars', relief=RIDGE, width=8)
        self.lbl1nw=Label(win, text='  N_W Cars', relief=RIDGE, width=8)
        self.lbl1ne=Label(win, text=' N_E Cars', relief=RIDGE, width=8)
        self.lbl1en=Label(win, text='E_N Cars', relief=RIDGE, width=8)
        self.lbl1es=Label(win, text='E_S Cars ', relief=RIDGE, width=8)
        self.lbl1sw=Label(win, text=' S_W Cars', relief=RIDGE, width=8)
        self.lbl1se=Label(win, text='S_E Cars', relief=RIDGE, width=8)
     
        
        self.lbl10=Label(win, text='Simulation (Sec)', relief=RIDGE, width=15)
        self.lbl11=Label(win, text='Green light (Sec)', relief=RIDGE, width=15)
        self.lbl12=Label(win, text='Seed (0-30000)', relief=RIDGE, width=15)
        
        self.lbl20=Label(win, text='Car accel (M/S^2)', relief=RIDGE, width=15)
        self.lbl21=Label(win, text='Car decel (M/S^2)', relief=RIDGE, width=15)
        self.lbl22=Label(win, text='Max speed (M/S)', relief=RIDGE, width=15)
        
        
        
        self.lbl3=Label(win, text='TL algorithm', relief=RIDGE, width=15)
        self.lbl4=Label(win, text='Active gui (click)', relief=RIDGE, width=15)
        
        self.t10=Spinbox(win, from_=0, to=86400 , relief=RIDGE, bd=2, width=8)
        self.t10.insert(0,540)
        
        vargreen = StringVar()
        self.t11=Spinbox(win, from_=6, to=60 , relief=RIDGE, bd=2, width=8,textvariable=vargreen)
        vargreen.set("10")
        
        self.t1we=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1we.insert(0,10)
        self.t1ew=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1ew.insert(0,10)
        self.t1ns=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1ns.insert(0,10)
        self.t1sn=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1sn.insert(0,10)
        self.t1wn=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1wn.insert(0,10)
        self.t1ws=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1ws.insert(0,10)
        self.t1nw=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1nw.insert(0,10)
        self.t1ne=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1ne.insert(0,10)
        self.t1en=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1en.insert(0,10)
        self.t1es=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1es.insert(0,10)
        self.t1sw=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1sw.insert(0,10)
        self.t1se=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1se.insert(0,10)
        

        self.t12=Spinbox(win,from_=0, to=30000 , relief=RIDGE, bd=2, width=8)
        self.t12.insert(0,1000)
        
        var0 = StringVar()
        self.t20=Spinbox(win,format="%.1f",increment=0.1,from_=0, to=100 , relief=RIDGE, bd=2, width=8, textvariable=var0)
        var0.set("1.0")
        
        var1 = StringVar()
        self.t21=Spinbox(win,format="%.1f",increment=0.1,from_=0, to=100 , relief=RIDGE, bd=2, width=8, textvariable=var1)
        var1.set("4.5")
        
        var2 = StringVar()
        self.t22=Spinbox(win,from_=0, to=100 , relief=RIDGE, bd=2, width=8, textvariable=var2)
        var2.set("25")
        
        
        
        self.t3=ttk.Combobox(win, values=["Basic", "Smart","Q-learn"] ,state = "readonly" ,width=8,height=8)
        self.t3.set("Basic")
        
        
        self.lbl1.place(x=124, y=80)
        self.lbl1we.place(x=124, y=310)
        self.t1we.place(x=184, y=310)
        self.lbl1ew.place(x=124, y=240)
        self.t1ew.place(x=184, y=240)
        self.lbl1ns.place(x=124, y=100)
        self.t1ns.place(x=184, y=100)
        self.lbl1sn.place(x=124, y=170)
        self.t1sn.place(x=184, y=170)
        self.lbl1wn.place(x=124, y=330)
        self.t1wn.place(x=184, y=330)
        self.lbl1ws.place(x=124, y=350)
        self.t1ws.place(x=184, y=350)
        self.lbl1nw.place(x=124, y=120)
        self.t1nw.place(x=184, y=120)
        self.lbl1ne.place(x=124, y=140)
        self.t1ne.place(x=184, y=140)
        self.lbl1en.place(x=124, y=260)
        self.t1en.place(x=184, y=260)
        self.lbl1es.place(x=124, y=280)
        self.t1es.place(x=184, y=280)
        self.lbl1sw.place(x=124, y=190)
        self.t1sw.place(x=184, y=190)
        self.lbl1se.place(x=124, y=210)
        self.t1se.place(x=184, y=210)
        
        
        self.lbl10.place(x=350, y=100)
        self.t10.place(x=461, y=100)
        self.lbl11.place(x=350, y=120)
        self.t11.place(x=461, y=120)
        self.lbl12.place(x=350, y=140)  
        self.t12.place(x=461, y=140)
        
        self.lbl20.place(x=350, y=170)  
        self.t20.place(x=461, y=170)
        self.lbl21.place(x=350, y=190)  
        self.t21.place(x=461, y=190)
        self.lbl22.place(x=350, y=210)  
        self.t22.place(x=461, y=210)
        
        
        
        
        
        self.lbl3.place(x=350, y=260) 
        self.t3.place(x=461, y=260)
        
       
        
        self.b3=Button(win,relief=RIDGE, command = self.gui)
        self.io_LEDRedOn=PhotoImage(file="assets/LED-Red-On.png")
        self.io_LEDGreenOn=PhotoImage(file="assets/LED-Green-On.png")
        self.b3.config(text = "False", image=self.io_LEDRedOn, width="15",height="15")
        self.lbl4.place(x=350, y=330)
        self.b3.place(x=461, y=330)
       
        
        self.lbl0.place(x=104, y=400)
        self.b1=Button(win, text='Exit', command=self.close ,bg='#ff8181', font=('Arial', 11, 'bold'),relief=RIDGE)
        self.b2=Button(win, text='Run Simulator', command=self.run,  bg='palegreen2', font=('Arial', 11, 'bold'),relief=RIDGE)
        self.b1.place(x=64, y=400)
        self.b2.place(x=480, y=400)
        
        self.b4=Button(win, text='Change to the Train Window (click)',bg='PaleTurquoise3', font=('Arial', 11, 'bold'),relief=RIDGE,command=lambda:self.f2.tkraise())
        self.b4.place(x=180, y=440)
        
      
        
    def close(self):
        window.destroy()
    
    def gui(self):
        
        if self.b3.config('text')[-1] == 'False':
            self.b3.config(text="True", image =  self.io_LEDGreenOn)
        else: 
            self.b3.config(text="False", image =  self.io_LEDRedOn)
    
    def plots(self):
        self.Visu.save_data_and_plot(data=self.Simu.reward_episode, filename='reward', xlabel='Step', ylabel='Reward')
        self.Visu.save_data_and_plot(data=self.Simu.queue_length_episode, filename='queue', xlabel='Step', ylabel='Queue lenght (vehicles)')
        self.Visu.save_data_and_plot(data=self.Simu.incoming_cars_episode, filename='vehicles', xlabel='Step', ylabel='Incoming vehicles')  
        self.Visu.save_data_and_plot_multi_lanes(data=self.Simu.queue_length_episode_per_lane, filename='queue_per_lane', xlabel='Step', ylabel='Queue lenght per lane ')
        self.Visu.save_data_and_plot_multi_lanes(data=self.Simu.incoming_cars_episode_per_lane, filename='vehicles_per_lane', xlabel='Step', ylabel='Incoming vehicles per lane')
        self.Visu.save_data_and_plot_multi_lanes(data=self.Simu._wait_time_per_lane, filename='time_per_lane', xlabel='Step', ylabel='Waiting time per lane')
        
    def run(self):
        
        #[simulation]
        
        if self.b3.config('text')[-1] == 'True':
            gui = True
        else:
            gui = False
        
        
        if self.t3.get() == "Basic":
            model_to_test = 1
        elif self.t3.get() == "Smart":
            model_to_test = 2 
        else:
            model_to_test = 3
        
        
        car_accel =self.t20.get()
        car_decel =self.t21.get()
        max_speed =self.t22.get()

        cars_generated = [
            ('W_N', self.t1wn.get()),
            ('W_E', self.t1we.get()),
            ('W_S', self.t1ws.get()),
            ('N_W', self.t1nw.get()),
            ('N_E', self.t1ne.get()),
            ('N_S', self.t1ns.get()),
            ('E_W', self.t1ew.get()),
            ('E_N', self.t1en.get()),
            ('E_S', self.t1es.get()),
            ('S_W', self.t1sw.get()),
            ('S_N', self.t1sn.get()),
            ('S_E', self.t1se.get()),
        ]
        
        
        n_cars_generated = 0
        for i in range(0, len(cars_generated)):
            n_cars_generated += int(cars_generated[i][1])
        
       
        max_steps = int(self.t10.get())
        green_duration = int(self.t11.get())
        episode_seed = int(self.t12.get())
        
        #developer values
        yellow_duration = 2
       
        
        #[agent]
        num_states = 80
        num_actions = 4
        
        #[dir]
        models_path_name = "models"
        sumocfg_file_name = "sumo_config.sumocfg"
        
        
    
        sumo_cmd = set_sumo(gui, sumocfg_file_name, max_steps)
        model_path, plot_path = set_test_path(models_path_name, model_to_test)
    
        self.Model = TestModel(
            input_dim=num_states,
            model_to_test=model_to_test,
            num_actions = num_actions,
            model_path = model_path
        )
    
        self.TrafficGen = TrafficGenerator(
            max_steps, 
            n_cars_generated,
            cars_generated,
            car_accel,
            car_decel,
            max_speed
        )
    
        self.Visu = Visualization(
            plot_path, 
            dpi=96
        )
            
        self.Simu = Simulation(
            self.Model,
            self.TrafficGen,
            sumo_cmd,
            max_steps,
            green_duration,
            yellow_duration,
            num_states,
            num_actions
        )
        
        self.b2.config(text = "Simulating... Wait",bg='red',font=('Arial', 11, 'bold'),relief=RIDGE)
        self.b2.update_idletasks()
    
        print('\n----- Test episode')
        simulation_time = self.Simu.run(episode_seed)  # run the simulation
        print('Simulation time:', simulation_time, 's')
        print("----- Simulation info saved at:", plot_path)
        
        resultmsg='Simulation time:'+str(simulation_time)+'s\nSimulation info saved at:'+plot_path
        self.b2.config(text = "Run Simulator", bg='palegreen2', font=('Arial', 11, 'bold'),relief=RIDGE)
        self.plots()
        showinfo("Simulation Ended", resultmsg)
        
        with open(plot_path+"/testing_settings.ini", "w") as routes:
            print("""
[Simulation]
Simulation steps (secs) = "%s"
Green light (secs) = "%s"
Episode seed = "%s"
Car accel = "%s"
Car decel = "%s"
Car Max speed = "%s"
TL algorithm = "%s"
Active gui = "%s"

N_S cars = "%s"
N_W cars = "%s"
N_E cars = "%s"
 
S_N cars = "%s"
S_W cars = "%s"
S_E cars = "%s"

E_W cars = "%s"
E_N cars = "%s"
E_S cars = "%s"

W_E cars = "%s"
W_N cars = "%s"
W_S cars = "%s"
   
"%s" """ % (self.t10.get(),self.t11.get(),self.t12.get(),self.t20.get(),self.t21.get(),self.t22.get(),self.t3.get(),self.b3.config('text')[-1],
                                       self.t1ns.get(),self.t1nw.get(),self.t1ne.get(),
                                       self.t1sn.get(),self.t1sw.get(),self.t1se.get(),
                                       self.t1ew.get(),self.t1en.get(),self.t1es.get(),
                                       self.t1we.get(),self.t1wn.get(),self.t1ws.get(),resultmsg), file=routes)  
            
            
        


class MyTrainWindow:
    def __init__(self, win, width, height, f1):
        self.f1=f1
        background = 'assets/logot650x500.jpg'
        photo = ImageTk.PhotoImage(Image.open(background))
        canvas = Canvas(win, width=width, height=height)
        canvas.imageList = []
        canvas.pack()
        canvas.create_image(0, 0, anchor="nw", image=photo)
        canvas.imageList.append(photo)    
        
        
        self.lbl0 = Text(win, state='disabled', width=62, height=2,relief=RIDGE,bg='khaki2', font=('Arial', 8, 'bold'),bd=1)
        self.lbl0.configure(state='normal')
        self.lbl0.insert('end', 'Set the values and run the trainer, if you choose with gui sumo\nwill open and you need to close it manually as the epoch ends.')
        self.lbl0.configure(state='disabled')
       
        self.lbl1=Label(win, text='Set number (0-3000)', relief=RIDGE, width=17)
        self.lbl1we=Label(win, text=' W_E Cars ', relief=RIDGE, width=8)
        self.lbl1ew=Label(win, text=' E_W Cars', relief=RIDGE, width=8)
        self.lbl1ns=Label(win, text=' N_S Cars', relief=RIDGE, width=8)
        self.lbl1sn=Label(win, text=' S_N Cars', relief=RIDGE, width=8)
        self.lbl1wn=Label(win, text=' W_N Cars', relief=RIDGE, width=8)
        self.lbl1ws=Label(win, text=' W_S Cars', relief=RIDGE, width=8)
        self.lbl1nw=Label(win, text='  N_W Cars', relief=RIDGE, width=8)
        self.lbl1ne=Label(win, text=' N_E Cars', relief=RIDGE, width=8)
        self.lbl1en=Label(win, text='E_N Cars', relief=RIDGE, width=8)
        self.lbl1es=Label(win, text='E_S Cars ', relief=RIDGE, width=8)
        self.lbl1sw=Label(win, text=' S_W Cars', relief=RIDGE, width=8)
        self.lbl1se=Label(win, text='S_E Cars', relief=RIDGE, width=8)
     
        
        self.lbl10=Label(win, text='Simulation (Sec)', relief=RIDGE, width=15)
        self.lbl11=Label(win, text='Green light (Sec)', relief=RIDGE, width=15)
        self.lbl12=Label(win, text='Seed (0-30000)', relief=RIDGE, width=15)
        
        self.lbl20=Label(win, text='Car accel (M/S^2)', relief=RIDGE, width=15)
        self.lbl21=Label(win, text='Car decel (M/S^2)', relief=RIDGE, width=15)
        self.lbl22=Label(win, text='Max speed (M/S)', relief=RIDGE, width=15)
        
        
        self.lbl30=Label(win, text='Total episodes', relief=RIDGE, width=15)
        self.lbl31=Label(win, text='Batch size', relief=RIDGE, width=15)
        self.lbl32=Label(win, text='Training epochs', relief=RIDGE, width=15)
        
        
        
        
        self.lbl4=Label(win, text='Active gui (click)', relief=RIDGE, width=15)
        
        self.t10=Spinbox(win, from_=0, to=86400 , relief=RIDGE, bd=2, width=8)
        self.t10.insert(0,540)
        
        self.t11=Spinbox(win, from_=0, to=60 , relief=RIDGE, bd=2, width=8)
        self.t11.insert(0,1)
        
        self.t1we=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1we.insert(0,10)
        self.t1ew=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1ew.insert(0,10)
        self.t1ns=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1ns.insert(0,10)
        self.t1sn=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1sn.insert(0,10)
        self.t1wn=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1wn.insert(0,10)
        self.t1ws=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1ws.insert(0,10)
        self.t1nw=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1nw.insert(0,10)
        self.t1ne=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1ne.insert(0,10)
        self.t1en=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1en.insert(0,10)
        self.t1es=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1es.insert(0,10)
        self.t1sw=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1sw.insert(0,10)
        self.t1se=Spinbox(win, from_=0, to=3000 , relief=RIDGE, bd=2, width=8)
        self.t1se.insert(0,10)
        

        
        self.t12=Spinbox(win, from_=0, to=30000 , relief=RIDGE, bd=2, width=8)
        self.t12.insert(0,1000)
        
        var0 = StringVar()
        self.t20=Spinbox(win,format="%.1f",increment=0.1,from_=0, to=100 , relief=RIDGE, bd=2, width=8, textvariable=var0)
        var0.set("1.0")
        
        var1 = StringVar()
        self.t21=Spinbox(win,format="%.1f",increment=0.1,from_=0, to=100 , relief=RIDGE, bd=2, width=8, textvariable=var1)
        var1.set("4.5")
        
        var2 = StringVar()
        self.t22=Spinbox(win,from_=0, to=100 , relief=RIDGE, bd=2, width=8, textvariable=var2)
        var2.set("25")
        
        
        var30 = StringVar()
        self.t30=Spinbox(win,from_=0, to=100 , relief=RIDGE, bd=2, width=8, textvariable=var30)
        var30.set("10")
        
        var31 = StringVar()
        self.t31=Spinbox(win,from_=0, to=100 , relief=RIDGE, bd=2, width=8, textvariable=var31)
        var31.set("100")
        
        var32 = StringVar()
        self.t32=Spinbox(win,from_=0, to=100 , relief=RIDGE, bd=2, width=8, textvariable=var32)
        var32.set("800")
        
        
        self.lbl1.place(x=124, y=80)
        self.lbl1we.place(x=124, y=310)
        self.t1we.place(x=184, y=310)
        self.lbl1ew.place(x=124, y=240)
        self.t1ew.place(x=184, y=240)
        self.lbl1ns.place(x=124, y=100)
        self.t1ns.place(x=184, y=100)
        self.lbl1sn.place(x=124, y=170)
        self.t1sn.place(x=184, y=170)
        self.lbl1wn.place(x=124, y=330)
        self.t1wn.place(x=184, y=330)
        self.lbl1ws.place(x=124, y=350)
        self.t1ws.place(x=184, y=350)
        self.lbl1nw.place(x=124, y=120)
        self.t1nw.place(x=184, y=120)
        self.lbl1ne.place(x=124, y=140)
        self.t1ne.place(x=184, y=140)
        self.lbl1en.place(x=124, y=260)
        self.t1en.place(x=184, y=260)
        self.lbl1es.place(x=124, y=280)
        self.t1es.place(x=184, y=280)
        self.lbl1sw.place(x=124, y=190)
        self.t1sw.place(x=184, y=190)
        self.lbl1se.place(x=124, y=210)
        self.t1se.place(x=184, y=210)
        
        
        self.lbl10.place(x=350, y=100)
        self.t10.place(x=461, y=100)
        self.lbl11.place(x=350, y=120)
        self.t11.place(x=461, y=120)
        self.lbl12.place(x=350, y=140)  
        self.t12.place(x=461, y=140)
        
        self.lbl20.place(x=350, y=170)  
        self.t20.place(x=461, y=170)
        self.lbl21.place(x=350, y=190)  
        self.t21.place(x=461, y=190)
        self.lbl22.place(x=350, y=210)  
        self.t22.place(x=461, y=210)
        
        
        
        self.lbl30.place(x=350, y=240) 
        self.t30.place(x=461, y=240)
        self.lbl31.place(x=350, y=260) 
        self.t31.place(x=461, y=260)
        self.lbl32.place(x=350, y=280) 
        self.t32.place(x=461, y=280)
        
       
        
        self.b3=Button(win,relief=RIDGE, command = self.gui)
        self.io_LEDRedOn=PhotoImage(file="assets/LED-Red-On.png")
        self.io_LEDGreenOn=PhotoImage(file="assets/LED-Green-On.png")
        self.b3.config(text = "False", image=self.io_LEDRedOn, width="15",height="15")
        self.lbl4.place(x=350, y=330)
        self.b3.place(x=461, y=330)
       
        
        self.lbl0.place(x=104, y=400)
        self.b1=Button(win, text='Exit', command=self.close ,bg='#ff8181', font=('Arial', 11, 'bold'),relief=RIDGE)
        self.b2=Button(win, text='Train Model', command=self.run,  bg='palegreen2', font=('Arial', 11, 'bold'),relief=RIDGE)
        self.b1.place(x=64, y=400)
        self.b2.place(x=480, y=400)
        
        self.b4=Button(win, text='Change to the Simulator Window (click)',bg='PaleTurquoise3', font=('Arial', 11, 'bold'),relief=RIDGE,command=lambda:self.f1.tkraise())
        self.b4.place(x=180, y=440)
        
      
        
    def close(self):
        window.destroy()
    
    def gui(self):
        
        if self.b3.config('text')[-1] == 'False':
            self.b3.config(text="True", image =  self.io_LEDGreenOn)
        else: 
            self.b3.config(text="False", image =  self.io_LEDRedOn)
    
    def plots(self):
        
        self.Visu.save_data_and_plot(data=self.Simulation.reward_store, filename='reward', xlabel='Episode', ylabel='Cumulative negative reward')
        self.Visu.save_data_and_plot(data=self.Simulation.cumulative_wait_store, filename='delay', xlabel='Episode', ylabel='Cumulative delay (s)')
        self.Visu.save_data_and_plot(data=self.Simulation.avg_queue_length_store, filename='queue', xlabel='Episode', ylabel='Average queue length (vehicles)')

        
    
    def run(self):
        
        #[simulation]
        
        if self.b3.config('text')[-1] == 'True':
            gui = True
        else:
            gui = False
        
            
        car_accel =self.t20.get()
        car_decel =self.t21.get()
        max_speed =self.t22.get()    
            

        cars_generated = [
            ('W_N', self.t1wn.get()),
            ('W_E', self.t1we.get()),
            ('W_S', self.t1ws.get()),
            ('N_W', self.t1nw.get()),
            ('N_E', self.t1ne.get()),
            ('N_S', self.t1ns.get()),
            ('E_W', self.t1ew.get()),
            ('E_N', self.t1en.get()),
            ('E_S', self.t1es.get()),
            ('S_W', self.t1sw.get()),
            ('S_N', self.t1sn.get()),
            ('S_E', self.t1se.get()),
        ]
        
        
        n_cars_generated = 0
        for i in range(0, len(cars_generated)):
            n_cars_generated += int(cars_generated[i][1])
        
       
        max_steps = int(self.t10.get())
        green_duration = int(self.t11.get())
        episode_seed = int(self.t12.get())
        
        
        #[agent]
        yellow_duration = 2
        num_states = 80
        num_actions = 4
        gamma = 0.75
        
        
        total_episodes = int(self.t30.get())
        num_layers = 4
        width_layers = 400
        batch_size = int(self.t31.get())
        learning_rate = 0.001
        training_epochs =int(self.t32.get())
        
        memory_size_min = 600
        memory_size_max = 50000
        
        #[dir]
        models_path_name = "models"
        sumocfg_file_name = "sumo_config.sumocfg"
        
        
    

    
        sumo_cmd = set_sumo(gui, sumocfg_file_name, max_steps)
        path = set_train_path(models_path_name)
    
        self.Model = TrainModel(
            num_layers, 
            width_layers, 
            batch_size, 
            learning_rate, 
            input_dim=num_states, 
            output_dim=num_actions
        )
    
        self.memory = Memory(
            memory_size_max, 
            memory_size_min
        )
    
        self.TrafficGen = TrafficGenerator(
            max_steps, 
            n_cars_generated,
            cars_generated,
            car_accel,
            car_decel,
            max_speed
        )
    
        self.Visu = Visualization(
            path, 
            dpi=96
        )
            
        self.Simulation = TSimulation(
            self.Model,
            self.memory,
            self.TrafficGen,
            sumo_cmd,
            gamma,
            max_steps,
            green_duration,
            yellow_duration,
            num_states,
            num_actions,
            training_epochs
        )
        
        self.b2.config(text = "Training... Wait",bg='red',font=('Arial', 11, 'bold'),relief=RIDGE)
        self.b2.update_idletasks()
        
        episode = 0
        timestamp_start = datetime.datetime.now()
        
        while episode < total_episodes:
            print('\n----- Episode', str(episode+1), 'of', str(total_episodes))
            epsilon = 1.0 - (episode / total_episodes)  # set the epsilon for this episode according to epsilon-greedy policy
            simulation_time, training_time = self.Simulation.run(episode, epsilon)  # run the simulation
            print('Simulation time:', simulation_time, 's - Training time:', training_time, 's - Total:', round(simulation_time+training_time, 1), 's')
            episode += 1
    
        
    
        self.Model.save_model(path)
        self.plots()
         
        print("\n----- Start time:", timestamp_start)
        print("----- End time:", datetime.datetime.now())
        print("----- Session info saved at:", path)
        resultmsg='\n----- Start time:'+str(timestamp_start)+"\n----- End time:"+str(datetime.datetime.now())+'\nSession info saved at:'+path
        self.b2.config(text = 'Train Model', bg='palegreen2', font=('Arial', 11, 'bold'),relief=RIDGE)
        showinfo("Simulation Ended", resultmsg)
        
        with open(path+"/training_settings.ini", "w") as routes:
            print("""
[Simulation]
Simulation steps (secs) = "%s"
Green light (secs) = "%s"
Episode seed = "%s"
Car accel = "%s"
Car decel = "%s"
Car Max speed = "%s"
Total episodes = "%s"
Batch size = "%s"
Training epochs = "%s"
Active gui = "%s"

N_S cars = "%s"
N_W cars = "%s"
N_E cars = "%s"
 
S_N cars = "%s"
S_W cars = "%s"
S_E cars = "%s"

E_W cars = "%s"
E_N cars = "%s"
E_S cars = "%s"

W_E cars = "%s"
W_N cars = "%s"
W_S cars = "%s"
   
"%s" """ % (self.t10.get(),self.t11.get(),self.t12.get(),self.t20.get(),self.t21.get(),self.t22.get(),
                                       self.t30.get(),self.t31.get(),self.t32.get(),self.b3.config('text')[-1],
                                       self.t1ns.get(),self.t1nw.get(),self.t1ne.get(),
                                       self.t1sn.get(),self.t1sw.get(),self.t1se.get(),
                                       self.t1ew.get(),self.t1en.get(),self.t1es.get(),
                                       self.t1we.get(),self.t1wn.get(),self.t1ws.get(),resultmsg), file=routes)  



 
    
width = 650
height = 500
window=Tk()


window.iconbitmap("assets/icon.ico")
window.title('Smart traffic lights for multilane crossroad')
window.geometry(str(width)+"x"+str(height)+"+10+10")
window.resizable(False, False)


f1 = Frame(window)
f2 = Frame(window)

for frame in (f1, f2):
    frame.grid(row=0, column=0, sticky='news')
    
    
mywin=MyWindow(f1, width, height, f2)
mytwin=MyTrainWindow(f2, width, height, f1)



f1.tkraise()
window.mainloop()







