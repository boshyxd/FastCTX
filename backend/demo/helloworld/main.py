def greet(name):
    return f"Hello, {name}!"

def calculate_sum(a, b):
    return a + b

class HelloWorld:
    def __init__(self, message="Hello World"):
        self.message = message
    
    def display(self):
        print(self.message)
    
    def get_message(self):
        return self.message

if __name__ == "__main__":
    hw = HelloWorld()
    hw.display()
    
    print(greet("FastCTX"))
    print(f"Sum: {calculate_sum(5, 3)}")