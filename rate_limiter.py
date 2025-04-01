import time
from threading import Lock
import logging

class RateLimiter:
    """
    A simple rate limiter that limits requests to a specified rate.
    """
    
    def __init__(self, max_requests, time_period):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests (int): Maximum number of requests allowed in the time period
            time_period (float): Time period in seconds
        """
        self.max_requests = max_requests
        self.time_period = time_period
        self.request_timestamps = []
        self.lock = Lock()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def wait_if_needed(self):
        """
        Check if a request can be made and wait if needed.
        
        Returns:
            bool: True if the request is allowed, False otherwise
        """
        with self.lock:
            current_time = time.time()
            
            # Remove timestamps older than the time period
            self.request_timestamps = [ts for ts in self.request_timestamps 
                                      if current_time - ts < self.time_period]
            
            # If we're at the limit, calculate wait time
            if len(self.request_timestamps) >= self.max_requests:
                oldest_timestamp = min(self.request_timestamps)
                wait_time = oldest_timestamp + self.time_period - current_time
                
                if wait_time > 0:
                    self.logger.info(f"Rate limit reached. Waiting {wait_time:.2f} seconds.")
                    time.sleep(wait_time)
            
            # Add current timestamp to the list
            self.request_timestamps.append(time.time())
            return True

# Create a global instance for OpenAI API requests
# Limit to 3 requests per 60 seconds
openai_limiter = RateLimiter(max_requests=2, time_period=60.0)