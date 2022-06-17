import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'  # kill warning about tensorflow
import tensorflow as tf
import numpy as np
import sys

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import losses
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import plot_model
from tensorflow.keras.models import load_model


class TestModel:
    
    _hunger_level = []
    
    def __init__(self, input_dim, model_to_test, num_actions,model_path):
        self._input_dim = input_dim
        self._model_to_test = model_to_test
        self._num_actions = num_actions
        self._hunger_level = [0.0 for i in range(num_actions)]
        
        if model_to_test == 3:
            self._model = self._load_my_model(model_path)


    def _load_my_model(self, model_folder_path):
        """
        Load the model stored in the folder specified by the model number, if it exists
        """
        model_file_path = os.path.join(model_folder_path, 'trained_model.h5')
        
        if os.path.isfile(model_file_path):
            loaded_model = load_model(model_file_path)
            return loaded_model
        else:
            sys.exit("Model number not found")

        

    def predict_one(self, state, old_action, traffic_volume, traffic_waiting, traffic_load):
        """
        Predict the action values from a single state
        #0 - PHASE_NS_GREEN , 1 - PHASE_NSL_GREEN , 2 - PHASE_EW_GREEN , 3 - PHASE_EWL_GREEN 
        new_action - the lanes that will get green light
        dgl - determinted green light lenth 
        """
        if self._model_to_test == 1:
            new_action = self.actual_traffic_control(state, old_action)
            dgl = 0
            return new_action,dgl
        elif self._model_to_test == 2:
            new_action = self.smart_traffic_control(state, old_action, traffic_volume, traffic_waiting, traffic_load)
            dgl = self.cal_dgl(new_action,traffic_volume)
            return new_action,dgl
        elif self._model_to_test == 3:
            state = np.reshape(state, [1, self._input_dim])
            new_action = np.argmax(self._model.predict(state))
            dgl = self.cal_dgl(new_action,traffic_volume)
            return new_action,dgl

    @property
    def input_dim(self):
        return self._input_dim
        
    
    def actual_traffic_control(self, state, old_action):
        """
        Implement the actual traffict control cycle without sensors on the road.
        
        Action :  0 - PHASE_NS_GREEN , 1 - PHASE_NSL_GREEN , 2 - PHASE_EW_GREEN , 3 - PHASE_EWL_GREEN 
        """
                                                    
        if old_action == -1 or old_action == 3 :
            return 0
        if old_action == 0:
            return 1
        if old_action == 1:
            return 2
        if old_action == 2:
            return 3    
                                                   
        
    def smart_traffic_control(self, state, old_action, traffic_volume, traffic_waiting, traffic_load):
        """
        Implement the smart traffict control cycle.
        
        Action :  0 - PHASE_NS_GREEN , 1 - PHASE_NSL_GREEN , 2 - PHASE_EW_GREEN , 3 - PHASE_EWL_GREEN 
        
        x2TL_3 are the "turn left only" lanes
        State lane (first digit) :               [0- W2TL_0 , W2TL_1 , W2TL_2] [1 - W2TL_3] [2- N2TL_0 , N2TL_1 , N2TL_2] [3 - N2TL_3]
                                                 [4- E2TL_0 , E2TL_1 , E2TL_2] [5 - E2TL_3] [6- S2TL_0 , S2TL_1 , S2TL_2] [7 - S2TL_3]
        
        State distance (meters) (seconds digit): [0- dis<7] [1- dis<14] [2- dis<21] [3- dis<28] [4- dis<40] 
                                                 [5- dis<60] [6- dis<100] [7- dis<160] [8- dis<400] [9- dis<750]  
                                                 
                                                 
        GLD :   a1*traffic_volume + a2*traffic_waiting + a3*hunger_level + a4*traffic_load                                       
                                                 
        """                                            
        
        gld_combined = self.cal_gld(traffic_volume, traffic_waiting, traffic_load, self._hunger_level)
        new_action =  np.argmax(gld_combined)
        occurences = np.count_nonzero(gld_combined == gld_combined[new_action])
        
        if occurences == 1:
            self.update_hunger_lvl(new_action)
            return new_action
        else:
            combine_tv = np.zeros(self._num_actions)
            combine_tw = np.zeros(self._num_actions)
            combine_tl = np.zeros(self._num_actions)
            
            combine_tv[0] = traffic_volume[2]+traffic_volume[6]
            combine_tv[1] = traffic_volume[3]+traffic_volume[7]
            combine_tv[2] = traffic_volume[0]+traffic_volume[4]
            combine_tv[3] = traffic_volume[1]+traffic_volume[5]
            
            combine_tw[0] = traffic_waiting[2]+traffic_waiting[6]
            combine_tw[1] = traffic_waiting[3]+traffic_waiting[7]
            combine_tw[2] = traffic_waiting[0]+traffic_waiting[4]
            combine_tw[3] = traffic_waiting[1]+traffic_waiting[5]
            
            combine_tl[0] = traffic_load[2]+traffic_load[6]
            combine_tl[1] = traffic_load[3]+traffic_load[7]
            combine_tl[2] = traffic_load[0]+traffic_load[4]
            combine_tl[3] = traffic_load[1]+traffic_load[5]
            
            tv_action =  np.argmax(combine_tv)
            tv_occurences = np.count_nonzero(combine_tv == combine_tv[tv_action])
            tw_action =  np.argmax(combine_tw)
            tw_occurences = np.count_nonzero(combine_tw == combine_tw[tw_action])
            tl_action =  np.argmax(combine_tl)
            tl_occurences = np.count_nonzero(combine_tl == combine_tl[tl_action])
            
            if tv_occurences == 1:
                self.update_hunger_lvl(tv_action)
                return tv_action
            elif tw_occurences == 1:
                 self.update_hunger_lvl(tw_action)
                 return tw_action
            elif tl_occurences == 1:
                 self.update_hunger_lvl(tl_action)
                 return tl_action
            elif old_action == -1:
                 self.update_hunger_lvl(0)
                 return 0
     
            self.update_hunger_lvl(old_action)
            return old_action
            
    
        
    def cal_gld(self, traffic_volume, traffic_waiting, traffic_load, hunger_level):     
        """
        Calculate the traffic load and taking in count the combined lanes 
        lanes base on state:  x2TL_3 are the "turn left only" lanes
        [0- W2TL_0 , W2TL_1 , W2TL_2] [1 - W2TL_3] [2- N2TL_0 , N2TL_1 , N2TL_2] [3 - N2TL_3]
        [4- E2TL_0 , E2TL_1 , E2TL_2] [5 - E2TL_3] [6- S2TL_0 , S2TL_1 , S2TL_2] [7 - S2TL_3]
        
         gld :  0 - PHASE_NS_GREEN , 1 - PHASE_NSL_GREEN , 2 - PHASE_EW_GREEN , 3 - PHASE_EWL_GREEN 
         
         gld[i] =   a1*traffic_volume + a2*traffic_waiting + a3*hunger_level + a4*traffic_load           
        """
        gld = np.zeros(self._num_actions)
        a1 = 0.25 #traffic_volume importance /weight
        a2 = 0.25 #traffic_waiting importance /weight
        a3 = 0.25 #hunger_level importance /weight
        a4 = 0.25 #traffic_load importance /weight
     
        gld[0] = (a1*(traffic_volume[2]+traffic_volume[6])) + (a2*(traffic_waiting[2]+traffic_waiting[6])) + (a3*(self._hunger_level[0])) + (a4*(traffic_load[2]+traffic_load[6])) 
        gld[1] = (a1*(traffic_volume[3]+traffic_volume[7])) + (a2*(traffic_waiting[3]+traffic_waiting[7])) + (a3*(self._hunger_level[1])) + (a4*(traffic_load[3]+traffic_load[7]))
        gld[2] = (a1*(traffic_volume[0]+traffic_volume[4])) + (a2*(traffic_waiting[0]+traffic_waiting[4])) + (a3*(self._hunger_level[2])) + (a4*(traffic_load[0]+traffic_load[4]))
        gld[3] = (a1*(traffic_volume[1]+traffic_volume[5])) + (a2*(traffic_waiting[1]+traffic_waiting[5])) + (a3*(self._hunger_level[3])) + (a4*(traffic_load[1]+traffic_load[5]))
         
        return gld
        
        
    def update_hunger_lvl(self,choosed):
        
        for i in range (self._num_actions):
            if i != choosed:
                self._hunger_level[i] += 1
            else:
                self._hunger_level[i] = 0  
                
    def cal_dgl(self, new_action,traffic_volume):
        """ 
        Action :  0 - PHASE_NS_GREEN , 1 - PHASE_NSL_GREEN , 2 - PHASE_EW_GREEN , 3 - PHASE_EWL_GREEN 
        0 = 2+6
        1 = 3+7
        2 = 0+4
        3 = 1+5
        """
        
        max_green_time=60
        min_green_time=6
        avg_cross_time=3
        if new_action == 0:
            dgl_lane_1 = max(min_green_time,min(max_green_time,traffic_volume[2]*avg_cross_time))
            dgl_lane_2 = max(min_green_time,min(max_green_time,traffic_volume[6]*avg_cross_time))
            dgl = max(dgl_lane_1,dgl_lane_2)
        elif new_action == 1:
            dgl_lane_1 = max(min_green_time,min(max_green_time,traffic_volume[3]*avg_cross_time))
            dgl_lane_2 = max(min_green_time,min(max_green_time,traffic_volume[7]*avg_cross_time))
            dgl = max(dgl_lane_1,dgl_lane_2)
       
        elif new_action == 2:
            dgl_lane_1 = max(min_green_time,min(max_green_time,traffic_volume[0]*avg_cross_time))
            dgl_lane_2 = max(min_green_time,min(max_green_time,traffic_volume[4]*avg_cross_time))
            dgl = max(dgl_lane_1,dgl_lane_2)
            
        elif new_action == 3:
            dgl_lane_1 = max(min_green_time,min(max_green_time,traffic_volume[1]*avg_cross_time))
            dgl_lane_2 = max(min_green_time,min(max_green_time,traffic_volume[5]*avg_cross_time))
            dgl = max(dgl_lane_1,dgl_lane_2)
            
        return dgl    

class TrainModel:
    def __init__(self, num_layers, width, batch_size, learning_rate, input_dim, output_dim):
        self._input_dim = input_dim
        self._output_dim = output_dim
        self._batch_size = batch_size
        self._learning_rate = learning_rate
        self._model = self._build_model(num_layers, width)
        self._hunger_level = [0.0 for i in range(output_dim)]
        self._num_actions = output_dim

    def _build_model(self, num_layers, width):
        """
        Build and compile a fully connected deep neural network
        """
        inputs = keras.Input(shape=(self._input_dim,))
        x = layers.Dense(width, activation='relu')(inputs)
        for _ in range(num_layers):
            x = layers.Dense(width, activation='relu')(x)
        outputs = layers.Dense(self._output_dim, activation='linear')(x)

        model = keras.Model(inputs=inputs, outputs=outputs, name='my_model')
        model.compile(loss=losses.mean_squared_error, optimizer=Adam(lr=self._learning_rate))
        return model
    

    def predict_one(self, state, old_action, traffic_volume, traffic_waiting, traffic_load):
        """
        Predict the action values from a single state
        """
        new_action = self.smart_traffic_control(state, old_action, traffic_volume, traffic_waiting, traffic_load)
        dgl = self.cal_dgl(new_action,traffic_volume)
        return new_action,dgl


    def predict_batch(self, states):
        """
        Predict the action values from a batch of states
        """
        return self._model.predict(states)


    def train_batch(self, states, q_sa):
        """
        Train the nn using the updated q-values
        """
        self._model.fit(states, q_sa, epochs=1, verbose=0)


    def save_model(self, path):
        """
        Save the current model in the folder as h5 file and a model architecture summary as png
        """
        self._model.save(os.path.join(path, 'trained_model.h5'))
        plot_model(self._model, to_file=os.path.join(path, 'model_structure.png'), show_shapes=True, show_layer_names=True)


    def smart_traffic_control(self, state, old_action, traffic_volume, traffic_waiting, traffic_load):
        """
        Implement the smart traffict control cycle.
        
        Action :  0 - PHASE_NS_GREEN , 1 - PHASE_NSL_GREEN , 2 - PHASE_EW_GREEN , 3 - PHASE_EWL_GREEN 
        
        x2TL_3 are the "turn left only" lanes
        State lane (first digit) :               [0- W2TL_0 , W2TL_1 , W2TL_2] [1 - W2TL_3] [2- N2TL_0 , N2TL_1 , N2TL_2] [3 - N2TL_3]
                                                 [4- E2TL_0 , E2TL_1 , E2TL_2] [5 - E2TL_3] [6- S2TL_0 , S2TL_1 , S2TL_2] [7 - S2TL_3]
        
        State distance (meters) (seconds digit): [0- dis<7] [1- dis<14] [2- dis<21] [3- dis<28] [4- dis<40] 
                                                 [5- dis<60] [6- dis<100] [7- dis<160] [8- dis<400] [9- dis<750]  
                                                 
                                                 
        GLD :   a1*traffic_volume + a2*traffic_waiting + a3*hunger_level + a4*traffic_load                                       
                                                 
        """                                            
        
        gld_combined = self.cal_gld(traffic_volume, traffic_waiting, traffic_load, self._hunger_level)
        new_action =  np.argmax(gld_combined)
        occurences = np.count_nonzero(gld_combined == gld_combined[new_action])
        
        if occurences == 1:
            self.update_hunger_lvl(new_action)
            return new_action
        else:
            combine_tv = np.zeros(self._num_actions)
            combine_tw = np.zeros(self._num_actions)
            combine_tl = np.zeros(self._num_actions)
            
            combine_tv[0] = traffic_volume[2]+traffic_volume[6]
            combine_tv[1] = traffic_volume[3]+traffic_volume[7]
            combine_tv[2] = traffic_volume[0]+traffic_volume[4]
            combine_tv[3] = traffic_volume[1]+traffic_volume[5]
            
            combine_tw[0] = traffic_waiting[2]+traffic_waiting[6]
            combine_tw[1] = traffic_waiting[3]+traffic_waiting[7]
            combine_tw[2] = traffic_waiting[0]+traffic_waiting[4]
            combine_tw[3] = traffic_waiting[1]+traffic_waiting[5]
            
            combine_tl[0] = traffic_load[2]+traffic_load[6]
            combine_tl[1] = traffic_load[3]+traffic_load[7]
            combine_tl[2] = traffic_load[0]+traffic_load[4]
            combine_tl[3] = traffic_load[1]+traffic_load[5]
            
            tv_action =  np.argmax(combine_tv)
            tv_occurences = np.count_nonzero(combine_tv == combine_tv[tv_action])
            tw_action =  np.argmax(combine_tw)
            tw_occurences = np.count_nonzero(combine_tw == combine_tw[tw_action])
            tl_action =  np.argmax(combine_tl)
            tl_occurences = np.count_nonzero(combine_tl == combine_tl[tl_action])
            
            if tv_occurences == 1:
                self.update_hunger_lvl(tv_action)
                return tv_action
            elif tw_occurences == 1:
                 self.update_hunger_lvl(tw_action)
                 return tw_action
            elif tl_occurences == 1:
                 self.update_hunger_lvl(tl_action)
                 return tl_action
            elif old_action == -1:
                 self.update_hunger_lvl(0)
                 return 0
     
            self.update_hunger_lvl(old_action)
            return old_action
            
    
        
    def cal_gld(self, traffic_volume, traffic_waiting, traffic_load, hunger_level):     
        """
        Calculate the traffic load and taking in count the combined lanes 
        lanes base on state:  x2TL_3 are the "turn left only" lanes
        [0- W2TL_0 , W2TL_1 , W2TL_2] [1 - W2TL_3] [2- N2TL_0 , N2TL_1 , N2TL_2] [3 - N2TL_3]
        [4- E2TL_0 , E2TL_1 , E2TL_2] [5 - E2TL_3] [6- S2TL_0 , S2TL_1 , S2TL_2] [7 - S2TL_3]
        
         gld :  0 - PHASE_NS_GREEN , 1 - PHASE_NSL_GREEN , 2 - PHASE_EW_GREEN , 3 - PHASE_EWL_GREEN 
         
         gld[i] =   a1*traffic_volume + a2*traffic_waiting + a3*hunger_level + a4*traffic_load           
        """
        gld = np.zeros(self._num_actions)
        a1 = 0.25 #traffic_volume importance /weight
        a2 = 0.25 #traffic_waiting importance /weight
        a3 = 0.25 #hunger_level importance /weight
        a4 = 0.25 #traffic_load importance /weight
     
        gld[0] = (a1*(traffic_volume[2]+traffic_volume[6])) + (a2*(traffic_waiting[2]+traffic_waiting[6])) + (a3*(self._hunger_level[0])) + (a4*(traffic_load[2]+traffic_load[6])) 
        gld[1] = (a1*(traffic_volume[3]+traffic_volume[7])) + (a2*(traffic_waiting[3]+traffic_waiting[7])) + (a3*(self._hunger_level[1])) + (a4*(traffic_load[3]+traffic_load[7]))
        gld[2] = (a1*(traffic_volume[0]+traffic_volume[4])) + (a2*(traffic_waiting[0]+traffic_waiting[4])) + (a3*(self._hunger_level[2])) + (a4*(traffic_load[0]+traffic_load[4]))
        gld[3] = (a1*(traffic_volume[1]+traffic_volume[5])) + (a2*(traffic_waiting[1]+traffic_waiting[5])) + (a3*(self._hunger_level[3])) + (a4*(traffic_load[1]+traffic_load[5]))
         
        return gld
        
        
    def update_hunger_lvl(self,choosed):
        
        for i in range (self._num_actions):
            if i != choosed:
                self._hunger_level[i] += 1
            else:
                self._hunger_level[i] = 0  
                
    def cal_dgl(self, new_action,traffic_volume):
        """ 
        Action :  0 - PHASE_NS_GREEN , 1 - PHASE_NSL_GREEN , 2 - PHASE_EW_GREEN , 3 - PHASE_EWL_GREEN 
        0 = 2+6
        1 = 3+7
        2 = 0+4
        3 = 1+5
        """
        
        max_green_time=60
        min_green_time=6
        avg_cross_time=3
        if new_action == 0:
            dgl_lane_1 = max(min_green_time,min(max_green_time,traffic_volume[2]*avg_cross_time))
            dgl_lane_2 = max(min_green_time,min(max_green_time,traffic_volume[6]*avg_cross_time))
            dgl = max(dgl_lane_1,dgl_lane_2)
        elif new_action == 1:
            dgl_lane_1 = max(min_green_time,min(max_green_time,traffic_volume[3]*avg_cross_time))
            dgl_lane_2 = max(min_green_time,min(max_green_time,traffic_volume[7]*avg_cross_time))
            dgl = max(dgl_lane_1,dgl_lane_2)
       
        elif new_action == 2:
            dgl_lane_1 = max(min_green_time,min(max_green_time,traffic_volume[0]*avg_cross_time))
            dgl_lane_2 = max(min_green_time,min(max_green_time,traffic_volume[4]*avg_cross_time))
            dgl = max(dgl_lane_1,dgl_lane_2)
            
        elif new_action == 3:
            dgl_lane_1 = max(min_green_time,min(max_green_time,traffic_volume[1]*avg_cross_time))
            dgl_lane_2 = max(min_green_time,min(max_green_time,traffic_volume[5]*avg_cross_time))
            dgl = max(dgl_lane_1,dgl_lane_2)
            
        return dgl
        
        
    @property
    def input_dim(self):
        return self._input_dim


    @property
    def output_dim(self):
        return self._output_dim


    @property
    def batch_size(self):
        return self._batch_size
        