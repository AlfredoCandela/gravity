import numpy as np
import matplotlib.pyplot as plt
import copy


class Simulation: 
    def __init__(self, balls_params, limits_x, limits_y, frames_per_second, gravitational_constant):
        self.initial_balls = []
        for params_for_ball in balls_params:
            self.initial_balls.append(self.Ball(params_for_ball))
        self.quantity = len(self.initial_balls)
        self.limits_x = limits_x
        self.limits_y = limits_y
        self.frames_per_second = frames_per_second
        self.gravitational_constant = gravitational_constant


    def get_force_two_balls(self, atracted, atractor, gravitational_constant):
        vector_between_both = atractor.position - atracted.position

        distance = np.linalg.norm(vector_between_both)
        force = gravitational_constant*atracted.mass*atractor.mass/(distance**2)

        ratio = force / distance
        x_force = ratio * (vector_between_both[0])
        y_force = ratio * (vector_between_both[1])

        return np.array([x_force, y_force])


    def get_total_forces(self, gravitational_constant):
        for ball_id in range(self.quantity):
            self.balls_now[ball_id].force_vector = np.array([0,0], dtype=float)

        for atracted_ball_id in range(self.quantity):
            for atractor_ball_id in range(atracted_ball_id + 1, self.quantity):
                dual_atraction = self.get_force_two_balls(self.balls_now[atracted_ball_id],
                                                    self.balls_now[atractor_ball_id],
                                                    gravitational_constant)
                self.balls_now[atracted_ball_id].force_vector += dual_atraction
                self.balls_now[atractor_ball_id].force_vector -= dual_atraction


    def move_all_balls(self):
        for ball_id in range(self.quantity):
            self.balls_now[ball_id].position += self.balls_now[ball_id].speed/self.frames_per_second


    def register_trace_all_balls(self):
        for ball_id in range(self.quantity):
            position = np.copy(self.balls_now[ball_id].position)
            self.balls_now[ball_id].trace.append(position)


    def accelerate_all_balls(self):
        for ball_id in range(self.quantity):
            acceleration = self.balls_now[ball_id].force_vector / self.balls_now[ball_id].mass
            self.balls_now[ball_id].speed += acceleration / self.frames_per_second


    def draw_all_balls(self):
        for ball in self.balls_now:
            plt.plot(ball.position[0],ball.position[1],
                    'o',
                    markersize=ball.mass+2,
                    c=ball.colour)


    def draw_all_traces(self):
        for ball in self.balls_now:
            trace_x = [point[0] for point in ball.trace]
            trace_y = [point[1] for point in ball.trace]
            plt.plot(trace_x,trace_y,c=ball.colour)


    class Ball:
        def __init__(self, params):
            position = [float(params["Position X"]), float(params["Position Y"])]
            speed = [float(params["Speed X"]), float(params["Speed Y"])]

            self.mass = float(params["Mass"])
            self.position = np.array(position, dtype=float)
            self.speed = np.array(speed, dtype=float)
            self.colour = params["Colour"]
            self.trace = []
            self.force_vector = np.array([0,0], dtype=float)


    def iterate(self, frame):
        if frame == 0:
            self.balls_now = copy.deepcopy(self.initial_balls)

        plt.clf()
        plt.xlim(*self.limits_x)
        plt.ylim(*self.limits_y)
        plt.grid()  

        self.register_trace_all_balls()
        
        self.draw_all_traces()
        self.draw_all_balls()

        self.get_total_forces(self.gravitational_constant)
        self.accelerate_all_balls()
        self.move_all_balls()