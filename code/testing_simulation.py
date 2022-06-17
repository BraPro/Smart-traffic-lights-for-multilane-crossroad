import traci
import numpy as np
import random
import timeit
import os


# phase codes based on environment.net.xml
PHASE_NS_GREEN = 0  # action 0 code 00
PHASE_NS_YELLOW = 1
PHASE_NSL_GREEN = 2  # action 1 code 01
PHASE_NSL_YELLOW = 3
PHASE_EW_GREEN = 4  # action 2 code 10
PHASE_EW_YELLOW = 5
PHASE_EWL_GREEN = 6  # action 3 code 11
PHASE_EWL_YELLOW = 7


class Simulation:
    def __init__(self, Model, TrafficGen, sumo_cmd, max_steps, green_duration, yellow_duration, num_states, num_actions):
        self._Model = Model
        self._TrafficGen = TrafficGen
        self._step = 0
        self._sumo_cmd = sumo_cmd
        self._max_steps = max_steps
        self._green_duration = green_duration
        self._yellow_duration = yellow_duration
        self._num_states = num_states
        self._num_actions = num_actions
        self._reward_episode = []
        self._queue_length_episode = []
        self._num_of_incoming_cars = []
        self._sum_of_incoming_cars_per_lane = []
        self._queue_length_episode_per_lane = []
        self._wait_time_per_lane = []

    def run(self, episode):
        """
        Runs the testing simulation
        """
        start_time = timeit.default_timer()

        # first, generate the route file for this simulation and set up sumo
        self._TrafficGen.generate_routefile(seed=episode)
        traci.start(self._sumo_cmd)
        print("Simulating...")

        # inits
        self._step = 0
        self._waiting_times = {}
        old_total_wait = 0
        old_action = -1 # dummy init

        while self._step < self._max_steps:

            # get current state of the intersection
            current_state = self._get_state()

            # calculate reward of previous action: (change in cumulative waiting time between actions)
            # waiting time = seconds waited by a car since the spawn in the environment, cumulated for every car in incoming lanes
            current_total_wait = self._collect_waiting_times()
            reward = old_total_wait - current_total_wait

            # choose the light phase to activate, based on the current state of the intersection
            action,dgl = self._choose_action(current_state, old_action)

            # if the chosen phase is different from the last phase, activate the yellow phase
            if self._step != 0 and old_action != action:
                self._set_yellow_phase(old_action)
                self._simulate(self._yellow_duration, reward, current_state)

            # execute the phase selected before
            if dgl == 0:
                self._set_green_phase(action)
                self._simulate(self._green_duration, reward, current_state)
            else:
                self._set_green_phase(action)
                self._simulate(dgl, reward, current_state)

            # saving variables for later & accumulate reward & incoming cars
            old_action = action
            old_total_wait = current_total_wait

            #self._reward_episode.append(reward)                            need to check deeply
            #self._num_of_incoming_cars.append(np.sum(current_state))
             

        #print("Total reward:", np.sum(self._reward_episode))
        traci.close()
        simulation_time = round(timeit.default_timer() - start_time, 1)

        return simulation_time


    def _simulate(self, steps_todo, reward, current_state):
        """
        Proceed with the simulation in sumo
        """
        if (self._step + steps_todo) >= self._max_steps:  # do not do more steps than the maximum allowed number of steps
            steps_todo = self._max_steps - self._step

        while steps_todo > 0:
            traci.simulationStep()  # simulate 1 step in sumo
            self._step += 1 # update the step counter
            steps_todo -= 1
            sum_N, sum_S, sum_E , sum_W = self._collect_waiting_times_per_lane()
            waiting_time_per_lane = [sum_N, sum_S, sum_E , sum_W]
            self._wait_time_per_lane.append(waiting_time_per_lane)
            halt_N, halt_S, halt_E, halt_W = self._get_queue_length() 
            queue_length_per_lane = [halt_N, halt_S, halt_E, halt_W] 
            queue_length = halt_N + halt_S + halt_E + halt_W
            self._queue_length_episode.append(queue_length)
            self._reward_episode.append(reward)                          
            self._num_of_incoming_cars.append(np.sum(current_state))
            self._queue_length_episode_per_lane.append(queue_length_per_lane)
            current_state_combined_lanes = [np.sum(current_state[20:40]),np.sum(current_state[60:80]),np.sum(current_state[40:60]),np.sum(current_state[0:20])]
            self._sum_of_incoming_cars_per_lane.append(current_state_combined_lanes)

    def _collect_waiting_times_per_lane(self):
            """
            Retrieve the waiting time of every car in the incoming roads per lane
            """
            sum_N = 0
            sum_S = 0
            sum_E = 0
            sum_W = 0
            car_list = traci.vehicle.getIDList()
            for car_id in car_list:
                wait_time = traci.vehicle.getAccumulatedWaitingTime(car_id)
                road_id = traci.vehicle.getRoadID(car_id)  # get the road id where the car is located
                if road_id == "N2TL":  # consider only the waiting times of cars in incoming roads
                    sum_N += wait_time
                elif road_id == "S2TL":
                    sum_S += wait_time
                elif road_id == "E2TL":  
                    sum_E += wait_time
                elif road_id == "W2TL": 
                    sum_W += wait_time
                    
            return sum_N, sum_S, sum_E , sum_W



    def _collect_waiting_times(self):
        """
        Retrieve the waiting time of every car in the incoming roads
        """
        incoming_roads = ["E2TL", "N2TL", "W2TL", "S2TL"]
        car_list = traci.vehicle.getIDList()
        for car_id in car_list:
            wait_time = traci.vehicle.getAccumulatedWaitingTime(car_id)
            road_id = traci.vehicle.getRoadID(car_id)  # get the road id where the car is located
            if road_id in incoming_roads:  # consider only the waiting times of cars in incoming roads
                self._waiting_times[car_id] = wait_time
            else:
                if car_id in self._waiting_times: # a car that was tracked has cleared the intersection
                    del self._waiting_times[car_id] 
        total_waiting_time = sum(self._waiting_times.values())
        return total_waiting_time


    def _choose_action(self, state,old_action):
        """
        Pick the best action known based on the current state of the env
        """
        
        traffic_volume,traffic_waiting,traffic_load = self._get_info()
         #0 - PHASE_NS_GREEN , 1 - PHASE_NSL_GREEN , 2 - PHASE_EW_GREEN , 3 - PHASE_EWL_GREEN 
        return self._Model.predict_one(state, old_action, traffic_volume, traffic_waiting, traffic_load)


    def _set_yellow_phase(self, old_action):
        """
        Activate the correct yellow light combination in sumo
        """
        yellow_phase_code = old_action * 2 + 1 # obtain the yellow phase code, based on the old action (ref on environment.net.xml)
        traci.trafficlight.setPhase("TL", yellow_phase_code)


    def _set_green_phase(self, action_number):
        """
        Activate the correct green light combination in sumo
        """

        if action_number == 0:                                                 
            traci.trafficlight.setPhase("TL", PHASE_NS_GREEN)
        elif action_number == 1:
            traci.trafficlight.setPhase("TL", PHASE_NSL_GREEN)
        elif action_number == 2:
            traci.trafficlight.setPhase("TL", PHASE_EW_GREEN)
        elif action_number == 3:
            traci.trafficlight.setPhase("TL", PHASE_EWL_GREEN)


    def _get_queue_length(self):
        """
        Retrieve the number of cars with speed = 0 in every incoming lane
        """
        halt_N = traci.edge.getLastStepHaltingNumber("N2TL")
        halt_S = traci.edge.getLastStepHaltingNumber("S2TL")
        halt_E = traci.edge.getLastStepHaltingNumber("E2TL")
        halt_W = traci.edge.getLastStepHaltingNumber("W2TL")
       
        return halt_N, halt_S, halt_E, halt_W


    def _get_state(self):
        """
        Retrieve the state of the intersection from sumo, in the form of cell occupancy
        """
        state = np.zeros(self._num_states)
        car_list = traci.vehicle.getIDList()

        for car_id in car_list:
            lane_pos = traci.vehicle.getLanePosition(car_id)
            lane_id = traci.vehicle.getLaneID(car_id)
            lane_pos = 750 - lane_pos  # inversion of lane pos, so if the car is close to the traffic light -> lane_pos = 0 --- 750 = max len of a road

            # distance in meters from the traffic light -> mapping into cells
            if lane_pos < 7:
                lane_cell = 0
            elif lane_pos < 14:
                lane_cell = 1
            elif lane_pos < 21:
                lane_cell = 2
            elif lane_pos < 28:
                lane_cell = 3
            elif lane_pos < 40:
                lane_cell = 4
            elif lane_pos < 60:
                lane_cell = 5
            elif lane_pos < 100:
                lane_cell = 6
            elif lane_pos < 160:
                lane_cell = 7
            elif lane_pos < 400:
                lane_cell = 8
            elif lane_pos <= 750:
                lane_cell = 9

            # finding the lane where the car is located 
            # x2TL_3 are the "turn left only" lanes
            if lane_id == "W2TL_0" or lane_id == "W2TL_1" or lane_id == "W2TL_2":
                lane_group = 0
            elif lane_id == "W2TL_3":
                lane_group = 1
            elif lane_id == "N2TL_0" or lane_id == "N2TL_1" or lane_id == "N2TL_2":
                lane_group = 2
            elif lane_id == "N2TL_3":
                lane_group = 3
            elif lane_id == "E2TL_0" or lane_id == "E2TL_1" or lane_id == "E2TL_2":
                lane_group = 4
            elif lane_id == "E2TL_3":
                lane_group = 5
            elif lane_id == "S2TL_0" or lane_id == "S2TL_1" or lane_id == "S2TL_2":
                lane_group = 6
            elif lane_id == "S2TL_3":
                lane_group = 7
            else:
                lane_group = -1

            if lane_group >= 1 and lane_group <= 7:
                car_position = int(str(lane_group) + str(lane_cell))  # composition of the two postion ID to create a number in interval 0-79
                valid_car = True
            elif lane_group == 0:
                car_position = lane_cell
                valid_car = True
            else:
                valid_car = False  # flag for not detecting cars crossing the intersection or driving away from it

            if valid_car:
                state[car_position] += 1  # write the position of the car car_id in the state array in the form of "cell occupied"

          
                
        return state
    
    def _get_info(self):
        """
        lanes base on state:  x2TL_3 are the "turn left only" lanes
        [0- W2TL_0 , W2TL_1 , W2TL_2] [1 - W2TL_3] [2- N2TL_0 , N2TL_1 , N2TL_2] [3 - N2TL_3]
        [4- E2TL_0 , E2TL_1 , E2TL_2] [5 - E2TL_3] [6- S2TL_0 , S2TL_1 , S2TL_2] [7 - S2TL_3]

        """
        traffic_volume = np.zeros(8)  #number of waiting cars
        traffic_waiting = np.zeros(8) #accomulate time of the waiting 
        traffic_load = np.zeros(8)   #the load / conhestion on the lane
        
        traffic_volume[0] += traci.lane.getLastStepHaltingNumber("W2TL_0")
        traffic_volume[0] += traci.lane.getLastStepHaltingNumber("W2TL_1")
        traffic_volume[0] += traci.lane.getLastStepHaltingNumber("W2TL_2")
        traffic_volume[1] += traci.lane.getLastStepHaltingNumber("W2TL_3")
        
        traffic_volume[2] += traci.lane.getLastStepHaltingNumber("N2TL_0")
        traffic_volume[2] += traci.lane.getLastStepHaltingNumber("N2TL_1")
        traffic_volume[2] += traci.lane.getLastStepHaltingNumber("N2TL_2")
        traffic_volume[3] += traci.lane.getLastStepHaltingNumber("N2TL_3")
        
        traffic_volume[4] += traci.lane.getLastStepHaltingNumber("E2TL_0")
        traffic_volume[4] += traci.lane.getLastStepHaltingNumber("E2TL_1")
        traffic_volume[4] += traci.lane.getLastStepHaltingNumber("E2TL_2")
        traffic_volume[5] += traci.lane.getLastStepHaltingNumber("E2TL_3")
        
        traffic_volume[6] += traci.lane.getLastStepHaltingNumber("S2TL_0")
        traffic_volume[6] += traci.lane.getLastStepHaltingNumber("S2TL_1")
        traffic_volume[6] += traci.lane.getLastStepHaltingNumber("S2TL_2")
        traffic_volume[7] += traci.lane.getLastStepHaltingNumber("S2TL_3")
        
        
        traffic_waiting[0] += traci.lane.getWaitingTime("W2TL_0")
        traffic_waiting[0] += traci.lane.getWaitingTime("W2TL_1")
        traffic_waiting[0] += traci.lane.getWaitingTime("W2TL_2")
        traffic_waiting[1] += traci.lane.getWaitingTime("W2TL_3")
        
        traffic_waiting[2] += traci.lane.getWaitingTime("N2TL_0")
        traffic_waiting[2] += traci.lane.getWaitingTime("N2TL_1")
        traffic_waiting[2] += traci.lane.getWaitingTime("N2TL_2")
        traffic_waiting[3] += traci.lane.getWaitingTime("N2TL_3")
        
        traffic_waiting[4] += traci.lane.getWaitingTime("E2TL_0")
        traffic_waiting[4] += traci.lane.getWaitingTime("E2TL_1")
        traffic_waiting[4] += traci.lane.getWaitingTime("E2TL_2")
        traffic_waiting[5] += traci.lane.getWaitingTime("E2TL_3")
        
        traffic_waiting[6] += traci.lane.getWaitingTime("S2TL_0")
        traffic_waiting[6] += traci.lane.getWaitingTime("S2TL_1")
        traffic_waiting[6] += traci.lane.getWaitingTime("S2TL_2")
        traffic_waiting[7] += traci.lane.getWaitingTime("S2TL_3")
        
        
        traffic_load[0] += traci.lane.getLastStepOccupancy("W2TL_0")
        traffic_load[0] += traci.lane.getLastStepOccupancy("W2TL_1")
        traffic_load[0] += traci.lane.getLastStepOccupancy("W2TL_2")
        traffic_load[1] += traci.lane.getLastStepOccupancy("W2TL_3")
        
        traffic_load[2] += traci.lane.getLastStepOccupancy("N2TL_0")
        traffic_load[2] += traci.lane.getLastStepOccupancy("N2TL_1")
        traffic_load[2] += traci.lane.getLastStepOccupancy("N2TL_2")
        traffic_load[3] += traci.lane.getLastStepOccupancy("N2TL_3")
        
        traffic_load[4] += traci.lane.getLastStepOccupancy("E2TL_0")
        traffic_load[4] += traci.lane.getLastStepOccupancy("E2TL_1")
        traffic_load[4] += traci.lane.getLastStepOccupancy("E2TL_2")
        traffic_load[5] += traci.lane.getLastStepOccupancy("E2TL_3")
        
        traffic_load[6] += traci.lane.getLastStepOccupancy("S2TL_0")
        traffic_load[6] += traci.lane.getLastStepOccupancy("S2TL_1")
        traffic_load[6] += traci.lane.getLastStepOccupancy("S2TL_2")
        traffic_load[7] += traci.lane.getLastStepOccupancy("S2TL_3")
        
        traffic_load[0] /= 3
        traffic_load[2] /= 3 
        traffic_load[4] /= 3
        traffic_load[6] /= 3
      
        return  traffic_volume,traffic_waiting,traffic_load


    @property
    def queue_length_episode(self):
        return self._queue_length_episode

    @property
    def queue_length_episode_per_lane(self):
        return self._queue_length_episode_per_lane   

    @property
    def reward_episode(self):
        return self._reward_episode
        
    @property
    def incoming_cars_episode(self):
        return self._num_of_incoming_cars   

    @property
    def incoming_cars_episode_per_lane(self):
        return self._sum_of_incoming_cars_per_lane   
    
   



