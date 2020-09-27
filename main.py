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
            new_row, new_column = person.move_random(self.size)

        person.set_position(new_row,new_column)

        self.insert_person(person)

    def move_all_people(self):
        for person in self.people:
            self.move_person(person)

        

class Person:
    def __init__(self, row, column, index):
        self.susceptible = True
        self.infected = False
        self.recovered = False

        self.index = index

        self.quarantined = False #quarantined is for infected
        self.removed = False #removed is for contact tracing
        self.contact_list = []

        self.quarantine_day_count = 0

        self.recovery_day_count = 0
        self.days_to_recover = 14

        self.position = [row, column]

        self.nearby_people = []

        self.radius = 2

    # def set_susceptible(self):
    #     self.susceptible = True
    #     self.infected = False
    #     self.recovered = False

    def set_infected(self):
        self.susceptible = False
        self.infected = True
        self.recovered = False

    def set_recovered(self):
        self.susceptible = False
        self.infected = False
        self.recovered = True

    def set_position(self,row,column):
        self.position = [row,column]

    def move_random(self, size):
        direction = random.randint(0,8)
        row = self.position[0]
        column = self.position[1]
        #direction moved
        #012
        #345
        #678
        up = True
        down = True
        left = True
        right = True

        if row == 0:
            up = False
        if row == size-1:
            down = False
        if column == 0:
            left = False
        if column == size-1:
            right = False
    
        if direction == 0 and up and left:
            return row-1,column-1
        elif direction == 1 and up:
            return row-1,column
        elif direction == 2 and up and right:
            return row-1,column+1
        elif direction == 3 and left:
            return row,column-1
        elif direction == 4:
            return row, column
        elif direction == 5 and right:
            return row, column+1
        elif direction == 6 and down and left:
            return row+1,column-1
        elif direction == 7 and down:
            return row+1,column
        elif direction == 8 and down and right: #8
            return row+1,column+1
        #################################################
        else:
            return row, column

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

    def infect_nearby(self, probability, matrix_object):
        self.update_nearby_people(matrix_object)
        infections = []
        for person in self.nearby_people:
            choice = random.randint(1,100)
            if choice <= probability:
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
    def __init__(self, size, number_people, duration):
        self.matrix_size = size
        self.duration = duration
        self.number_people = number_people
        self.matrix = Matrix(self.matrix_size)
        self.people = []

        self.duration_of_simulation = 10

        self.tick_duration = 1 #seconds

        self.susceptible_per_tick = []
        self.infected_per_tick = []
        self.recovered_per_tick = []

        self.total_susceptible = []
        self.total_infected = []
        self.total_recovered = []

        self.create_people(number_people)


    def sleep(self):
        time.sleep(self.tick_duration)

    def random_position(self):
            return random.randint(0, self.matrix_size - 1), random.randint(0, self.matrix_size - 1)

    def create_people(self, amount):
        for i in range(amount):
            row, column = self.random_position()

            while self.matrix.position_taken(row,column):
                row, column = self.random_position()

            p = Person(row,column, i)
            self.people.insert(i,p)

            self.matrix.insert_person(p)

        #out of the for loop
        self.infect_random_person()

    def infect_random_person(self):
        index = random.randint(0,len(self.people)-1)
        self.people[index].set_infected()

    def print_matrix(self):
        for i in self.matrix.matrix:
            print(i)

    def remove_person(self, person):
        pos = person.position
        row = pos[0]
        column = pos[1]
        self.matrix.matrix[row][column] = self.matrix.empty
        person.removed = True

    def quarantine_person(self, person):
        pos = person.position
        row = pos[0]
        column = pos[1]
        self.matrix.matrix[row][column] = self.matrix.empty
        person.quarantine = True

    def update(self):
        self.matrix.get_people_list(self.people)

    def plot(self, l):
        plot.plot(l)
        plot.ylabel("Infection")
        plot.xlabel("Time")
        plot.show()

    def day_and_check_recovered(self):
        for person in self.people:
            if person.infected:
                person.recovery_day_pass()
                person.check_recovered()

    def tick(self):
        self.sleep()
        self.update()

        self.print_matrix()

        current_people = list(self.people)

        for person in current_people:
            if person.infected:
                #person.update_nearby_people(self.matrix)
                infections = person.infect_nearby(60, self.matrix)
                print(f"Person {person.index} List: {person.nearby_people}")
        for person in infections:
            person.set_infected()

        self.day_and_check_recovered()

        self.matrix.move_all_people()

        self.print_matrix()

        print("\n\n\n")

        #############
        self.infected_per_tick.insert(-1, len(infections))
        self.total_infected.insert(-1, sum(self.infected_per_tick))


        #############
        
    
    def run_simulation(self):
        for i in range(self.duration):
            print(f"Day {i}")
            self.tick()

        self.plot(self.total_infected)


# class Plot:
#     def __init__(self):
#         pass




            




if __name__ == "__main__":
    r = Run(10, 10, 20) #size, number of people, time
    #r.tick()
    r.run_simulation()
