"""
Queue Simulation Engine
Implements discrete event simulation for various queuing models
"""

import heapq
import random
import math
from dataclasses import dataclass
from typing import List, Tuple
from collections import deque


@dataclass
class Customer:
    """Represents a customer in the queue"""
    id: int
    arrival_time: float
    service_start_time: float = None
    departure_time: float = None

    @property
    def waiting_time(self):
        if self.service_start_time is None:
            return None
        return self.service_start_time - self.arrival_time

    @property
    def system_time(self):
        if self.departure_time is None:
            return None
        return self.departure_time - self.arrival_time


class QueueSimulation:
    """
    Discrete event simulation for queuing systems
    Supports M/M/1, M/M/c, and other queuing models
    """

    def __init__(self, num_servers=1, arrival_rate=1.0, service_rate=1.5):
        """
        Initialize the queue simulation

        Args:
            num_servers: Number of servers (c in M/M/c)
            arrival_rate: Lambda (arrivals per time unit)
            service_rate: Mu (services per time unit per server)
        """
        self.num_servers = num_servers
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate

        # Simulation state
        self.current_time = 0.0
        self.event_queue = []  # Priority queue of (time, event_type, data)
        self.waiting_queue = deque()  # Customers waiting for service
        self.busy_servers = 0
        self.next_customer_id = 0

        # Statistics
        self.customers_arrived = 0
        self.customers_served = 0
        self.total_waiting_time = 0.0
        self.total_system_time = 0.0
        self.queue_length_sum = 0.0
        self.last_event_time = 0.0
        self.max_queue_length = 0

        # History for plotting
        self.time_history = []
        self.queue_length_history = []
        self.customers_in_system_history = []

    def reset(self):
        """Reset the simulation to initial state"""
        self.__init__(self.num_servers, self.arrival_rate, self.service_rate)

    def schedule_event(self, time: float, event_type: str, data=None):
        """Schedule an event in the future"""
        heapq.heappush(self.event_queue, (time, event_type, data))

    def generate_interarrival_time(self):
        """Generate exponentially distributed interarrival time"""
        return random.expovariate(self.arrival_rate)

    def generate_service_time(self):
        """Generate exponentially distributed service time"""
        return random.expovariate(self.service_rate)

    def update_statistics(self, time_delta: float):
        """Update time-weighted statistics"""
        queue_length = len(self.waiting_queue)
        self.queue_length_sum += queue_length * time_delta
        self.max_queue_length = max(self.max_queue_length, queue_length)

    def handle_arrival(self, customer: Customer):
        """Handle customer arrival event"""
        self.customers_arrived += 1

        if self.busy_servers < self.num_servers:
            # Server available, start service immediately
            self.busy_servers += 1
            customer.service_start_time = self.current_time
            service_time = self.generate_service_time()
            departure_time = self.current_time + service_time
            self.schedule_event(departure_time, 'departure', customer)
        else:
            # All servers busy, join the queue
            self.waiting_queue.append(customer)

        # Schedule next arrival
        next_arrival_time = self.current_time + self.generate_interarrival_time()
        next_customer = Customer(id=self.next_customer_id, arrival_time=next_arrival_time)
        self.next_customer_id += 1
        self.schedule_event(next_arrival_time, 'arrival', next_customer)

    def handle_departure(self, customer: Customer):
        """Handle customer departure event"""
        customer.departure_time = self.current_time
        self.customers_served += 1
        self.total_waiting_time += customer.waiting_time
        self.total_system_time += customer.system_time

        if self.waiting_queue:
            # Serve next customer from queue
            next_customer = self.waiting_queue.popleft()
            next_customer.service_start_time = self.current_time
            service_time = self.generate_service_time()
            departure_time = self.current_time + service_time
            self.schedule_event(departure_time, 'departure', next_customer)
        else:
            # No one waiting, server becomes idle
            self.busy_servers -= 1

    def run(self, max_time: float = None, max_customers: int = None):
        """
        Run the simulation

        Args:
            max_time: Maximum simulation time (None for unlimited)
            max_customers: Maximum number of customers to serve (None for unlimited)
        """
        # Schedule first arrival
        first_arrival_time = self.generate_interarrival_time()
        first_customer = Customer(id=self.next_customer_id, arrival_time=first_arrival_time)
        self.next_customer_id += 1
        self.schedule_event(first_arrival_time, 'arrival', first_customer)

        while self.event_queue:
            # Get next event
            event_time, event_type, data = heapq.heappop(self.event_queue)

            # Check termination conditions
            if max_time and event_time > max_time:
                break
            if max_customers and self.customers_served >= max_customers:
                break

            # Update statistics
            time_delta = event_time - self.last_event_time
            self.update_statistics(time_delta)

            # Update current time
            self.current_time = event_time
            self.last_event_time = event_time

            # Record history
            self.time_history.append(self.current_time)
            self.queue_length_history.append(len(self.waiting_queue))
            self.customers_in_system_history.append(
                len(self.waiting_queue) + self.busy_servers
            )

            # Handle event
            if event_type == 'arrival':
                self.handle_arrival(data)
            elif event_type == 'departure':
                self.handle_departure(data)

    def get_statistics(self):
        """Get current simulation statistics"""
        if self.customers_served == 0:
            return {
                'customers_arrived': self.customers_arrived,
                'customers_served': 0,
                'avg_waiting_time': 0,
                'avg_system_time': 0,
                'avg_queue_length': 0,
                'max_queue_length': 0,
                'server_utilization': 0,
                'current_queue_length': len(self.waiting_queue),
                'busy_servers': self.busy_servers,
            }

        avg_waiting_time = self.total_waiting_time / self.customers_served
        avg_system_time = self.total_system_time / self.customers_served
        avg_queue_length = self.queue_length_sum / self.current_time if self.current_time > 0 else 0
        server_utilization = (self.customers_served * (self.total_system_time / self.customers_served - avg_waiting_time)) / (self.current_time * self.num_servers) if self.current_time > 0 else 0

        return {
            'customers_arrived': self.customers_arrived,
            'customers_served': self.customers_served,
            'avg_waiting_time': avg_waiting_time,
            'avg_system_time': avg_system_time,
            'avg_queue_length': avg_queue_length,
            'max_queue_length': self.max_queue_length,
            'server_utilization': server_utilization,
            'current_queue_length': len(self.waiting_queue),
            'busy_servers': self.busy_servers,
            'current_time': self.current_time,
        }

    def get_theoretical_statistics(self):
        """Calculate theoretical statistics for M/M/c queue"""
        rho = self.arrival_rate / (self.num_servers * self.service_rate)

        if rho >= 1:
            return {
                'utilization': rho,
                'note': 'System is unstable (ρ >= 1)'
            }

        if self.num_servers == 1:
            # M/M/1 formulas
            L = self.arrival_rate / (self.service_rate - self.arrival_rate)
            Lq = (self.arrival_rate ** 2) / (self.service_rate * (self.service_rate - self.arrival_rate))
            W = 1 / (self.service_rate - self.arrival_rate)
            Wq = self.arrival_rate / (self.service_rate * (self.service_rate - self.arrival_rate))
        else:
            # M/M/c formulas (Erlang C)
            c = self.num_servers
            lambda_rate = self.arrival_rate
            mu = self.service_rate

            # Calculate P0
            sum_term = sum((c * rho) ** n / math.factorial(n) for n in range(c))
            erlang_c_term = ((c * rho) ** c) / (math.factorial(c) * (1 - rho))
            P0 = 1 / (sum_term + erlang_c_term)

            # Erlang C formula (probability of waiting)
            C = erlang_c_term * P0

            Lq = C * rho / (1 - rho)
            Wq = Lq / lambda_rate
            W = Wq + 1 / mu
            L = lambda_rate * W

        return {
            'utilization': rho,
            'avg_customers_in_system': L,
            'avg_customers_in_queue': Lq,
            'avg_time_in_system': W,
            'avg_time_in_queue': Wq,
        }
