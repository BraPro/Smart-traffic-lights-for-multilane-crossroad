import numpy as np
import math

class TrafficGenerator:
    def __init__(self, max_steps, n_cars_generated, cars_generated, car_accel, car_decel, max_speed ):
        self.cars_generated = cars_generated # cars flow per episode
        self._n_cars_generated = n_cars_generated  # how many cars per episode
        self._max_steps = max_steps
        self.car_accel = car_accel
        self.car_decel = car_decel
        self.max_speed = max_speed

    def generate_routefile(self, seed):
        """
        Generation of the route of every car for one episode
        """
        np.random.seed(seed)  # make tests reproducible

        # the generation of cars is distributed according to a weibull distribution
        timings = np.random.weibull(2, self._n_cars_generated)
        timings = np.sort(timings)

        # reshape the distribution to fit the interval 0:max_steps
        car_gen_steps = []
        min_old = math.floor(timings[1])
        max_old = math.ceil(timings[-1])
        min_new = 0
        max_new = self._max_steps
        for value in timings:
            car_gen_steps = np.append(car_gen_steps, ((max_new - min_new) / (max_old - min_old)) * (value - max_old) + max_new)

        car_gen_steps = np.rint(car_gen_steps)  # round every value to int -> effective steps when a car will be generated
        
        car_route_list = []
        for i in range(12):
            for j in range(int(self.cars_generated[i][1])):
                car_route_list.append(self.cars_generated[i][0])
                
        np.random.shuffle(car_route_list)        

        # produce the file for cars generation, one car per line
        with open("intersection/episode_routes.rou.xml", "w") as routes:
            print("""<routes>
            <vType accel="%s" decel="%s" id="standard_car" length="5.0" minGap="2.5" maxSpeed="%s" sigma="0.5" /> 

            <route id="W_N" edges="W2TL TL2N"/>
            <route id="W_E" edges="W2TL TL2E"/>
            <route id="W_S" edges="W2TL TL2S"/>
            <route id="N_W" edges="N2TL TL2W"/>
            <route id="N_E" edges="N2TL TL2E"/>
            <route id="N_S" edges="N2TL TL2S"/>
            <route id="E_W" edges="E2TL TL2W"/>
            <route id="E_N" edges="E2TL TL2N"/>
            <route id="E_S" edges="E2TL TL2S"/>
            <route id="S_W" edges="S2TL TL2W"/>
            <route id="S_N" edges="S2TL TL2N"/>
            <route id="S_E" edges="S2TL TL2E"/>""" % (self.car_accel, self.car_decel, self.max_speed), file=routes)
            

            for car_counter, step in enumerate(car_gen_steps):
                print('    <vehicle id="%s_%i" type="standard_car" route="%s" depart="%s" departLane="random" departSpeed="10" />' % (car_route_list[car_counter], car_counter, car_route_list[car_counter] ,step), file=routes)
                
            print("</routes>", file=routes)
