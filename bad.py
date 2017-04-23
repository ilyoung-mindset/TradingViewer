from random import *
import os
your_lucky_number = []
your_lucky_number.append(randint(1,50000))
run_time = 0
bad_luck_checker = 1
item_num = 0
total = 0
while item_num < 10:
    if randint(1,50000) in your_lucky_number:
        print('got in '+str(run_time))
        total += run_time
        run_time = 0
        your_lucky_number = [randint(1,50000)]
        item_num +=1

        print(item_num)
    else:
        bad_luck_checker = 1
    if item_num < 4:
        while bad_luck_checker:
            x = randint(1,50000)
            if x not in your_lucky_number:
                your_lucky_number.append(x)
                bad_luck_checker = 0
    run_time += 1
print('got 10 item in '+str(total))
os.system('pause')
