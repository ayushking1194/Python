# OOP in Python: A comprehensive overview with examples

# Class Definition
# In Python, a class is a blueprint for creating objects. It defines the properties and behaviors that the objects will have.

class Car:
    # Constructor (__init__): This method initializes the attributes of the class.
    def __init__(self, make, model, year):
        # Instance variables (attributes) for each car object
        # self :- it ties methods and attributes to a specific instance of the class, enabling the object to manage and interact with its own state
        #      :- distinguishes between instance variables (belonging to the specific object) and class variables (which are shared by all instances of the class)
        self.make = make
        self.model = model
        self.year = year

    # Method (Behavior of the class): A function that belongs to the class
    def display_info(self):
        return f"{self.year} {self.make} {self.model}"

    def start_engine(self):
        return f"The engine of {self.make} {self.model} is now running."

# Creating an object of the class
my_car = Car("Toyota", "Corolla", 2020)

# Accessing object properties
print(my_car.display_info())  # Output: 2020 Toyota Corolla
print(my_car.start_engine())  # Output: The engine of Toyota Corolla is now running.

# ------------------------------------------
# Inheritance in Python
# Inheritance allows a class (child class) to inherit attributes and methods from another class (parent class).
# The child class can also add its own attributes and methods or override parent class methods.

class ElectricCar(Car):  # ElectricCar inherits from Car
    def __init__(self, make, model, year, battery_size):
        # Call the parent class constructor using super()
        super().__init__(make, model, year)
        self.battery_size = battery_size

    # Overriding a method from the parent class
    def start_engine(self):
        return f"The electric engine of {self.make} {self.model} is silently running."

    def display_battery(self):
        return f"Battery size: {self.battery_size} kWh"

# Creating an object of the child class
my_electric_car = ElectricCar("Tesla", "Model S", 2022, 100)

# Accessing attributes and methods from both the parent and child class
print(my_electric_car.display_info())  # Output: 2022 Tesla Model S
print(my_electric_car.start_engine())  # Output: The electric engine of Tesla Model S is silently running.
print(my_electric_car.display_battery())  # Output: Battery size: 100 kWh

# ------------------------------------------
# Polymorphism in Python
# Polymorphism means "many forms". It allows methods to be used interchangeably, even if the method names are the same.
# This can occur when a child class overrides a method of the parent class.

# Example: Polymorphism with different implementations of the start_engine method
cars = [Car("Toyota", "Camry", 2019), ElectricCar("Tesla", "Model 3", 2021, 75)]

# Iterating over a list of car objects and calling the same method
for car in cars:
    print(car.start_engine())  
    # Output:
    # The engine of Toyota Camry is now running.
    # The electric engine of Tesla Model 3 is silently running.

# ------------------------------------------
# Encapsulation in Python
# Encapsulation is the concept of hiding the internal details of an object and only exposing necessary information.
# This is done using private (hidden) and public attributes.

class Employee:
    def __init__(self, name, salary):
        self.name = name  # Public attribute
        self.__salary = salary  # Private attribute (cannot be accessed directly outside the class)

    # Getter method for the private attribute (encapsulation)
    def get_salary(self):
        return self.__salary

    # Setter method for the private attribute (encapsulation)
    def set_salary(self, salary):
        if salary > 0:  # Adding validation
            self.__salary = salary
        else:
            print("Invalid salary value.")

# Creating an object of the Employee class
emp = Employee("John", 50000)

# Accessing public and private attributes using methods
print(emp.name)  # Output: John
# print(emp.__salary)  # This would throw an error as __salary is private
print(emp.get_salary())  # Output: 50000

# Updating the private salary attribute using the setter method
emp.set_salary(55000)
print(emp.get_salary())  # Output: 55000

# ------------------------------------------
# Abstraction in Python
# Abstraction is the concept of hiding complex implementation details and showing only the necessary functionality.
# This can be achieved using abstract base classes (ABC) in Python.

from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def sound(self):
        pass  # Abstract method, must be implemented by subclasses

class Dog(Animal):
    def sound(self):
        return "Woof!"

class Cat(Animal):
    def sound(self):
        return "Meow!"

# Creating objects of the subclasses
dog = Dog()
cat = Cat()

# Calling the implemented methods
print(dog.sound())  # Output: Woof!
print(cat.sound())  # Output: Meow!

# Note: You cannot instantiate an object of the abstract class directly:
# animal = Animal()  # This will raise an error because Animal is abstract.

# ------------------------------------------
# Example of Multiple Inheritance
# In Python, a class can inherit from multiple parent classes (this is called multiple inheritance).

class Mother:
    def cook(self):
        return "Mother is cooking."

class Father:
    def drive(self):
        return "Father is driving."

class Child(Mother, Father):
    def play(self):
        return "Child is playing."

# Creating an object of the Child class
child = Child()

# The child object can access methods from both parent classes
print(child.cook())   # Output: Mother is cooking.
print(child.drive())  # Output: Father is driving.
print(child.play())   # Output: Child is playing.

# ------------------------------------------
# Conclusion:
# This script covers the key concepts of Object-Oriented Programming (OOP) in Python:
# - Classes and Objects
# - Inheritance (Single and Multiple)
# - Polymorphism
# - Encapsulation (Private and Public Attributes)
# - Abstraction (Abstract Classes and Methods)

