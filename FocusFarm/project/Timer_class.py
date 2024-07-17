import time

# timer class keeps track of the time. Helper class for the timer clock on the FarmWindow
# initialize with a duration in minutes (by default 50 min)
# get timer time in str (hours:minutes) format with get_timer_value
class Timer:

    def __init__(self):
        # Initialize time properties
        self.start_time = None
        self.end_time = None
        self.paused: bool = False
        self.pause_start_time = None 
        self.total_paused_time = 0 #might be required for break timing
        self.max_duration = None #is not always necessary
        self.display_interval = 30  # Display time every 30 seconds
        self.running: bool = False

    def start(self):
        #start timer or resume if  paused
        # if self.max_duration is not None:
        #     print(f"Maximum time limit set to {self.max_duration} seconds.")
        # else:
        #     print("No maximum time limit set.")

        if not self.paused:
            self.start_time = time.time() - self.total_paused_time
        else:
            self.total_paused_time += (time.time() - self.pause_start_time)
            self.paused = False

        self.running = True

    #stop timer
    def stop(self):
        if self.start_time is None:
            raise ValueError("Timer has not been started.")
        self.end_time = time.time()
        self.running = False
        
    #pause time  or check whether timer is paused
    def pause(self):
        if self.start_time is None:
            raise ValueError("Timer has not been started.")
        if not self.paused:
            self.pause_start_time = time.time()
            self.paused = True
        self.running = False

    # Toggle between starting and pausing the timer
    def toggle_running(self):
        if self.running:
            self.pause()
        else:
            self.start()

    # return total time passed starting at 0s
    def elapsed_time(self):
        #Also checks for a max time
        if self.start_time is None:
            # raise ValueError("Timer has not been started.")
            return 0

        if self.paused:
            self.total_paused_time = time.time() - self.pause_start_time


        if self.max_duration is not None:
            if self.end_time is None:
                elapsed = time.time() - self.start_time - self.total_paused_time
                return min(elapsed, self.max_duration)
            else:
                return min(self.end_time - self.start_time - self.total_paused_time, self.max_duration)
        else:
            if self.end_time is None:
                elapsed = time.time() - self.start_time - self.total_paused_time
                return elapsed
            else:
                return self.end_time - self.start_time - self.total_paused_time

    # returns hours and minutes as string
    def get_timer_value(self) -> str:
        total_seconds = int(self.elapsed_time())
        if self.max_duration is not None:
            remaining_seconds = max(0, self.max_duration - total_seconds)
            hours = remaining_seconds // 3600  
            minutes = (remaining_seconds % 3600) // 60 
            seconds = remaining_seconds % 60
        else:
            # Count up mode (no max time limit set)
            hours = total_seconds // 3600  
            minutes = (total_seconds % 3600) // 60 
            seconds = total_seconds % 60

        if hours != 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        return f"{minutes:02d}:{seconds:02d}"
        
    # max duration in minutes
    def set_max_duration(self, max_duration):
        if max_duration <= 0:
            print("Invalid maximum duration. Please enter a positive value.")
        else:
            self.max_duration = max_duration * 60

    #displays max  total time passed since task was started in seconds
    def display_elapsed_time(self):
        while not self.paused:
            elapsed_time = self.elapsed_time()
            if elapsed_time >= self.display_interval:
                print(f"Elapsed Time: {elapsed_time} seconds")
                time.sleep(self.display_interval)
            else:
                break


def main():
    #function for usage in the app
    timer = Timer()
    max_time_choice = input("Do you want to set a maximum time limit? (yes/no): ")

    if max_time_choice.lower() == "yes":
        max_duration = int(input("Enter the maximum duration in minutes: "))
        timer.set_max_duration(float(max_duration))
        print(f"Maximum duration set to {max_duration} minutes.")

    while True:
        #inputs for all functions of timer
        print("\nTimer App")
        print("1. Start")
        print("2. Pause")
        print("3. Stop")
        print("4. Display Elapsed Time")
        print("5. Exit")

        choice = input("Enter your choice: ")
        #choices
        if choice == "1":
            timer.start()
            print("Timer started.")
            if not timer.paused:
                timer.display_elapsed_time()
        elif choice == "2":
            timer.pause()
            print("Timer paused.")
        elif choice == "3":
            timer.stop()
            print("Timer stopped.")
            elapsed_time = timer.elapsed_time()
            print(f"Elapsed Time: {elapsed_time} seconds")
        elif choice == "4":
            elapsed_time = timer.elapsed_time()
            print(f"Elapsed Time: {elapsed_time} seconds")
        elif choice == "5":
            print("Exiting Timer App.")
            break
        elif timer.start_time is not None and timer.elapsed_time() % 30 == 0:
            # Check if elapsed time is a multiple of 30 seconds
            elapsed_time = timer.elapsed_time()
            print(f"Elapsed Time: {elapsed_time} seconds")
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
