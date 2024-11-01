import random

class GeneralServices:
    def random_generator():
        random_id = str(random.randint(100000000000000, 999999999999999))
        return random_id