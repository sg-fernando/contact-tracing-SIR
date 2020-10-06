import random
import time
import math

import matplotlib.pyplot as plot

class Matrix:
    def __init__(self,size):
        self.matrix = []
        self.empty = '-'
        self.size = size
        self.people = []

        self.create_area()

    def get_people_list(self, l):
        self.people = l

    def create_area(self):
        for i in range(self.size):
            temp = []
            for i in range(self.size):
                temp.insert(0, self.empty)
            self.matrix.insert(0,temp)

    def position_taken(self, row, column):
        if self.matrix[row][column] == self.empty:
            return False
        return True

    def insert_person(self,person):
        row = person.position[0]
        column = person.position[1]
        self.matrix[row][column] = person

    def move_person(self, person):
        row = person.position[0]
        column = person.position[1]
        self.matrix[row][column] = self.empty

        new_row, new_column = person.move_random(self.size)

        while self.position_taken(new_row,new_column):
            person.current_direction = person.current_direction + (math.pi / 2) #turn to the right to avoid running in to somone
            new_row, new_column = person.move_random(self.size)

        person.set_position(new_row,new_column)

        self.insert_person(person)

    def move_all_people(self):
        for person in self.people:
            self.move_person(person)

        

class Person:
    def __init__(self, row, column, index, initial_direction):
        self.susceptible = True
        self.infected = False
        self.recovered = False

        self.index = index

        self.quarantined = False #quarantined is for close contacts
        self.removed = False #removed is for tested positive
        self.test_positive = False
        self.contact_list = [[]]

        self.quarantine_day_count = 0

        self.recovery_day_count = 0
        self.days_to_recover = 20
        self.mean_recovery = 35
        self.standard_deviation_recovery = 10
        self.quarantine_duration = 14
        self.contact_memory = 3

        self.log_mean_recovery = math.log( (self.mean_recovery**2) / math.sqrt(self.mean_recovery**2 + self.standard_deviation_recovery**2) )
        self.log_standard_deviation_recovery = math.sqrt(math.log( 1 + (self.standard_deviation_recovery**2) / (self.mean_recovery**2) ))

        self.position = [row, column]
        self.current_direction = initial_direction
        self.direction_magnitude = 3
        #self.direction_transformation = [[4,7,6,3,0,1,2,5,8], [4,6,3,0,1,2,5,8,7], [4,3,0,1,2,5,8,7,6], [4,2,1,0,3,6,7,8,5], [0,0,0,0,0,0,0,0,0], [4,0,1,2,5,8,7,6,3], [4,1,0,3,6,7,8,5,2], [4,0,3,6,7,8,5,2,1], [4,3,6,7,8,5,2,1,0]]

        self.nearby_people = []

        self.radius = 12
        self.infection_probability = 10 #percent

    # def set_susceptible(self):
    #     self.susceptible = True
    #     self.infected = False
    #     self.recovered = False

    def set_infected(self):
        self.days_to_recover = int(random.lognormvariate(self.log_mean_recovery,self.log_standard_deviation_recovery))
        self.susceptible = False
        self.infected = True
        self.recovered = False
        

    def set_recovered(self):
        self.susceptible = False
        self.infected = False
        self.recovered = True

    def quarantine_close_contacts(self, efficiency):
        temp = []
        for i in self.contact_list:
            for j in i:
                temp.insert(0,j)

        return random.sample(temp, int(efficiency * len(temp)))

    def set_position(self,row,column):
        self.position = [row,column]
        
    def move_random(self, size):
        
        row = self.position[0]
        column = self.position[1]

        direction = random.gauss(0, 1.5) # from -pi to pi

        if direction > math.pi:
            direction = math.pi
        elif direction < -1*math.pi:
            direction = -1*math.pi
        
        self.current_direction = self.current_direction + direction # add directions to get new direction.

        if self.current_direction > math.pi:
            self.current_direction = self.current_direction - (2*math.pi)
        elif self.current_direction < -1*math.pi:
            self. current_direction = self.current_direction + (2*math.pi)

        row_component = self.direction_magnitude * math.sin(self.current_direction)
        col_component = self.direction_magnitude * math.cos(self.current_direction)

        new_row = round(row + row_component) #int() always rounds down which causes people to bunch up at 0,0
        new_column = round(column + col_component)

        col_difference = 0
        row_difference = 0

        if new_row >= size:
            row_difference = new_row - (size - 1)
            new_row = size - 1
        elif new_row < 0:
            row_difference = -1 * new_row
            new_row = 0
        
        if new_column >= size:
            col_difference = new_column - (size - 1)
            new_column = size - 1
        elif new_column < 0:
            col_difference = -1 * new_column
            new_column = 0

        if col_difference == 0: #avoid a divide by zero situation
            if new_row < 0:
                self.current_direction = math.pi * (1/2) #straight down.
            elif new_row >= size:
                self.current_direction = math.pi * (-1/2) #straight up.

        if new_row < 0 and new_column < 0:
            self.current_direction = math.atan(row_difference / col_difference)
        elif new_row < 0 and new_column >= size:
            self.current_direction = math.pi - math.atan(row_difference / col_difference)
        elif new_row >= size and new_column < 0:
            self.current_direction = -1 * math.atan(row_difference / col_difference)
        elif new_row >= size and new_column >= size:
            self.current_direction = math.pi + math.atan(row_difference / col_difference)  
        elif col_difference != 0 and row_difference == 0:
            if new_column < 0:
                self.current_direction = 0 #straight right
            elif new_column >= size:
                self.current_direction = math.pi #straight left

        if self.current_direction > math.pi: # turn from 0 to 2pi into -pi to pi
            self.current_direction = self.current_direction - (2*math.pi)

        return new_row, new_column

    def update_nearby_people(self, matrix_object):
        self.nearby_people = []
        
        row = self.position[0]
        column = self.position[1]

        row_min = 0
        #already set to zero
        if (row-self.radius > 0):
            row_min = row-self.radius

        row_max = matrix_object.size - 1

        if (row+self.radius < row_max):
            row_max = row+self.radius+1

        column_min = 0
        #already set to zero
        if (column-self.radius > 0):
            column_min = column-self.radius

        column_max = matrix_object.size - 1

        if (column+self.radius < column_max):
            column_max = column+self.radius+1

        for t_row in range(row_min,row_max + 1):
            for t_column in range(column_min,column_max + 1):
                if (t_row == row) and (t_column == column):
                    continue
                if self.in_radius(self.position, [t_row,t_column]):
                    if matrix_object.matrix[t_row][t_column] != matrix_object.empty:
                        self.nearby_people.insert(0,matrix_object.matrix[t_row][t_column])

    def update_close_contacts(self, matrix_object):
        self.update_nearby_people(matrix_object)

        del self.contact_list[0]
        self.contact_list.insert(-1,self.nearby_people)

    def infect_nearby(self, matrix_object):
        self.update_nearby_people(matrix_object)
        infections = []
        for person in self.nearby_people:
            choice = random.randint(1,100)
            if choice <= self.infection_probability and person.susceptible:
                infections.insert(0,person)
        return infections
            
    def in_radius(self, center, point):
        a = center[1] - point[1]
        b = center[0] - point[0]

        d = math.sqrt(a**2 + b**2)

        if (d <= self.radius):
            return True
        return False

    def check_recovered(self):
        if self.recovery_day_count == self.days_to_recover:
            self.set_recovered()
            return True
        else:
            return False

    def recovery_day_pass(self):
        self.recovery_day_count += 1

    def quarantine_day_pass(self):
        self.quarantine_day_count += 1

    def __repr__(self):
        if self.susceptible:
            return f'{self.index}:S'
        elif self.infected:
            return f'{self.index}:I'
        return f'{self.index}:R'


class Run:
    def __init__(self, size, number_people, duration, num_groups, tracing_efficiency, test_frequencey, test_delay, testing):
        self.matrix_size = size
        self.duration = duration
        self.number_people = number_people
        self.matrix = Matrix(self.matrix_size)
        self.people = []
        self.groups = []

        self.test_frequencey = test_frequencey
        self.test_delay = test_delay

        self.tick_duration = 0 #seconds

        self.susceptible_per_tick = []
        self.infected_per_tick = []
        self.recovered_per_tick = []

        self.total_susceptible = []
        self.total_infected = []
        self.total_recovered = []

        self.x_axis = []
        self.contact_tracing_efficiency = tracing_efficiency
        self.testing = testing
        self.number_groups = num_groups

        self.create_people(number_people, self.number_groups)


    def sleep(self):
        time.sleep(self.tick_duration)

    def random_position(self):
            return random.randint(0, self.matrix_size - 1), random.randint(0, self.matrix_size - 1)

    def random_direction(self):
        init_dir = random.randint(0,3)

        if init_dir == 0:
            return 0
        elif init_dir == 1:
            return math.pi / 2
        elif init_dir == 2:
            return math.pi
        elif init_dir == 3:
            return (-1/2) * math.pi
        else:
            print("error - no inital direction generated")

    def create_people(self, amount, num_groups):
        current_group = 0
        for i in range(num_groups):
            self.groups.insert(i,[])

        for i in range(amount):
            row, column = self.random_position()

            while self.matrix.position_taken(row,column):
                row, column = self.random_position()

            initial_direction = self.random_direction()

            p = Person(row,column, i, initial_direction)
            self.people.insert(i,p)
            self.groups[current_group].insert(i,p)

            if current_group == num_groups - 1:
                current_group = 0
            else:
                current_group += 1

            self.matrix.insert_person(p)

        #out of the for loop
        self.infect_random_person()

    def infect_random_person(self):
        index = random.randint(0,len(self.people)-1)
        self.people[index].set_infected()

    def print_matrix(self):
        for i in self.matrix.matrix:
            print(i)

    def remove_person(self, person):  #For people who have tested positive
        pos = person.position
        row = pos[0]
        column = pos[1]
        self.matrix.matrix[row][column] = self.matrix.empty
        person.removed = True
        print(f"removed person:{person}")

    def quarantine_person(self, person): #For close contacts of actual positives
        pos = person.position
        row = pos[0]
        column = pos[1]
        self.matrix.matrix[row][column] = self.matrix.empty
        person.quarantined = True
        print(f"quarantined person:{person}")
        

    def test_results_group(self, group):
        for person in self.groups[group]:
            if person.test_positive and not(person.removed):
                self.remove_person(person)
                person.test_positive = False
                for contact in person.quarantine_close_contacts(self.contact_tracing_efficiency):
                    if not(contact.removed or contact.quarantined):
                        self.quarantine_person(contact)

    def test_group(self, group):
        for person in self.groups[group]:
            if person.infected:
                person.test_positive = True

    def update(self):
        self.matrix.get_people_list(self.people)

    def re_insert_person(self, person):
        row, column = self.random_position()

        while self.matrix.position_taken(row,column):
            row, column = self.random_position()

        initial_direction = self.random_direction()

        person.position = [row, column]
        person.current_direction = initial_direction
        person.test_positive = False

        self.matrix.insert_person(person)

    def day_and_check_recovered(self):
        for person in self.people:
            if person.infected:
                person.recovery_day_pass()
                if person.check_recovered() and person.removed:
                    print(f"{person} recovered!")
                    self.re_insert_person(person)

            if person.quarantined:
                person.quarantine_day_pass()
                if person.quarantine_day_count == person.quarantine_duration:
                    print(f"{person} finished quarantine!")
                    self.re_insert_person(person)
 
    def count_susceptible(self):
        count = 0
        for person in self.people:
            if person.susceptible:
                count += 1
        self.total_susceptible.append(count)

    def count_infected(self):
        count = 0
        for person in self.people:
            if person.infected:
                count += 1
        self.total_infected.append(count)

    def count_recovered(self):
        count = 0
        for person in self.people:
            if person.recovered:
                count += 1
        self.total_recovered.append(count)


    def tick(self):
        #self.sleep()
        self.update()

        #self.print_matrix()

        current_people = list(self.people)

        infections = []
        for person in current_people:
            if person.infected:
                #person.update_nearby_people(self.matrix)
                infections = person.infect_nearby(self.matrix)
                #print(f"Person {person.index} List: {person.nearby_people}")
            person.update_close_contacts(self.matrix)
        for person in infections:
            person.set_infected()

        self.day_and_check_recovered()


        self.matrix.move_all_people()

        #self.print_matrix()

        

        #############
        # self.infected_per_tick.append(len(infections))
        # self.total_infected.append(sum(self.infected_per_tick))
        self.count_susceptible()
        self.count_infected()
        self.count_recovered()
        #print(self.total_infected[-1])


        #############
    
        #print("\n\n\n")
    
    def run_simulation(self):
        current_group = 0
        results_day = []
        
        for i in range(self.number_groups):
            results_day.insert(0,0)

        for day in range(self.duration):
            #print(f"Day {i}")
            self.tick()

            if (day+1)%self.test_frequencey == 0 and self.testing:
                self.test_group(current_group)
                results_day[current_group] = day+1+self.test_delay

                if current_group == self.number_groups - 1:
                    current_group = 0
                else:
                    current_group += 1

            for i in range(self.number_groups):
                if results_day[i] == day+1:
                    self.test_results_group(i)

            #print(i)
            if self.total_recovered[-1] == self.number_people:
                print("done")
                break
        
        # define plot
        print(f"Maximum infected: {max(self.total_infected)}")
        plot.plot(self.total_susceptible, color="blue")
        plot.plot(self.total_infected, color="red")
        plot.plot(self.total_recovered, color="green")
        plot.ylabel("SIR")
        plot.xlabel("Time")
        plot.show()


if __name__ == "__main__":
    size = 30
    num_p = (size**2) * .15
    num_p = int(num_p)

    r = Run(size, num_p, 200, 3, 0.8, 4, 2, True) #size, number of people, time, number of groups, tracing efficiency, test frequencey, testing delay, testing (bool)
    #r.tick()
    r.run_simulation()
