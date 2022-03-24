from datetime import datetime

with open("itworks.txt", 'a') as file:
    file.write(f'\nThis file was updated at {datetime.now()}')
