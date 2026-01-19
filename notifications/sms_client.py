import time
import random


def send_sms(phone_number: str, message: str):
    """
    Mock SMS provider with timeout & failure simulation.
    """

    simulated_latency = random.uniform(0.5, 3.0)

    if simulated_latency > 2.0:
        raise TimeoutError("SMS provider timeout")

    time.sleep(simulated_latency)

    if random.choice([False, False, True]):
        raise Exception("SMS provider error")

    print(f" SMS sent to {phone_number}: {message}")
