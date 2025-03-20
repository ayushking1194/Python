class Node:
    def __init__(self, value):
        self.value = value
        self.next = None     

class LinkedList:
    def __init__(self, value):
        new_node = Node(value)
        self.head = new_node
        self.tail = new_node
        self.length = 1

    def print_list(self):
        temp = self.head
        while temp is not None:
            print(temp.value, end='->')
            temp = temp.next
        print("None")

    def append(self,value):
        new_node = Node(value)
        temp = self.tail
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.length += 1
        return True
    
    def pop(self):
        if self.length == 0:
            return False
        temp = self.head
        pre = temp
        while(temp.next):
            pre = temp
            temp = temp.next
        print("Popped element =",temp.value)
        self.tail = pre
        self.tail.next = None
        self.length -= 1
        if self.length == 0:
            self.head = None
            self.tail = None
        return True
    
    def prepend(self,value):
        new_node = Node(value)
        if self.length == 0:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node
        self.length += 1
        return True


my_linked_list = LinkedList(11)
my_linked_list.print_list()
# my_linked_list.append("🎉")
# my_linked_list.append("🚀")
# my_linked_list.append(7)
# print("Before popping")
# my_linked_list.print_list()
# my_linked_list.pop()
# print("After popping")
my_linked_list.prepend(2)
my_linked_list.print_list()