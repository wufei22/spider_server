from tasks import func
import time

for i in range(100):
    func.delay(2, i)
    time.sleep(1)
