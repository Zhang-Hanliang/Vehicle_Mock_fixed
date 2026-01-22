#!/usr/bin/env python3
"""
Vehicle Mock Application
A simple mock application for testing purposes
"""

class Vehicle:
    """Mock Vehicle class for testing"""
    
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year
        self.speed = 0
    
    def accelerate(self, amount):
        """Increase vehicle speed"""
        self.speed += amount
        return self.speed
    
    def brake(self, amount):
        """Decrease vehicle speed"""
        self.speed = max(0, self.speed - amount)
        return self.speed
    
    def get_info(self):
        """Get vehicle information"""
        return f"{self.year} {self.make} {self.model} - Current Speed: {self.speed} mph"


def main():
    """Main application entry point"""
    print("Vehicle Mock Application")
    print("=" * 50)
    
    # Create a mock vehicle
    vehicle = Vehicle("Tesla", "Model 3", 2024)
    print(f"Created: {vehicle.get_info()}")
    
    # Test acceleration
    vehicle.accelerate(30)
    print(f"After acceleration: {vehicle.get_info()}")
    
    # Test braking
    vehicle.brake(10)
    print(f"After braking: {vehicle.get_info()}")
    
    print("\nVehicle Mock Application is running successfully!")


if __name__ == "__main__":
    main()
