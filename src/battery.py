'''
Project: ESC180 Project 1 - Battery
File: battery.py (main and only file)
Author: Tony, Terry
Additional Note:
    i. The entire code assumes discrete time (int), continuous charge, and continuous temp (both float)
    ii. Certain helper functions are added for better readability, all required functions are implemented
'''

def initialize():
    '''Initializes the global variables needed for the simulation.
    Note: this function is incomplete, and you may want to modify it.
    '''
    global cur_temp # in degrees Celsius
    global cur_charge # in percentage points
    global cur_time # in minutes
    global good_battery_health
    global overcharge_cases

    cur_time = 0
    good_battery_health = True
    cur_temp = 20.0
    cur_charge = 50.0
    overcharge_cases = []

def can_fast_charge(charge, temp, health):
    return temp <= 40.0 and charge < 80.0 and health

def duration_fast_charge_possible():
    if not can_fast_charge(cur_charge, cur_temp, good_battery_health):
        return 0.0
    else:
        charge_limit = (80.0 - cur_charge) / 3.0
        temp_limit = (40.0 -cur_temp) / 0.5
        return min(charge_limit, temp_limit)

def get_cur_temp():
    return cur_temp

def get_cur_charge():
    return cur_charge

def get_cur_battery_health():
    return good_battery_health

def check_overcharge(old_charge, charge, time, cases, health):
    bad_health_cap = max(80.0, charge) if not health else 100.0

    if old_charge < 90 and charge >= 90:
        cases.append(time)
        if len(cases) >= 3:
            if time - cases[-3] <= 360:
                health = False
                bad_health_cap = max(80.0, charge)

    return health, bad_health_cap

def charge_time_needed(minutes):
    global cur_charge, cur_temp, cur_time, good_battery_health, overcharge_cases
    charge_needed = minutes * 2

    if charge_needed > 100 or charge_needed < 0:
        return None
    elif charge_needed <= cur_charge:
        return 0

    s_cur_charge = cur_charge
    s_cur_temp = cur_temp
    s_good_battery_health = good_battery_health
    s_cur_time = cur_time
    s_overcharge_cases = overcharge_cases.copy()
    s_is_fast_charging = can_fast_charge(s_cur_charge, s_cur_temp, s_good_battery_health)
    s_good_battery_health, s_bad_health_cap = check_overcharge(0.0, s_cur_time, s_cur_charge, s_overcharge_cases, s_good_battery_health)

    start_time = s_cur_time

    while s_cur_charge < charge_needed:
        s_cur_charge, s_cur_temp, s_cur_time, s_good_battery_health, s_is_fast_charging, s_bad_health_cap = simulate_charge_minute(s_cur_charge, s_cur_temp, s_cur_time, s_good_battery_health, s_overcharge_cases, s_is_fast_charging, s_bad_health_cap)

    return s_cur_time - start_time

def simulate_charge_minute(charge, temp, time, health, cases, is_fast_charging, bad_health_cap):
    time += 1
    old_charge = charge
    is_full = (charge >= bad_health_cap and not health) or (charge >= 100.0 and health)

    if is_fast_charging and not can_fast_charge(charge, temp, good_battery_health):
        is_fast_charging = False

    if is_full:
        temp += 0.25
    elif is_fast_charging:
        charge += 3.0
        temp += 0.5
    else:
        charge += 1.0
        temp += 0.25

    charge = min(charge, bad_health_cap) if not health else min(charge, 100.0)
    health, bad_health_cap = check_overcharge(old_charge, charge, time, cases, health)

    return charge, temp, time, health, is_fast_charging, bad_health_cap

def simulate_use_minute(charge, temp, time):
    '''Return charge, temp, and time after one minute of use.'''
    time += 1
    if charge > 0.0:
        charge = max(0.0, charge - 2.0)
        temp += 1.0
    else:
        temp = max(0.0, temp - 1.0)

    return charge, temp, time

def simulate_idle_minute(charge, temp, time):
    '''Return charge, temp, and time after one minute of idling.'''
    time += 1
    charge = max(0.0, charge - 0.5)
    temp = max(0.0, temp - 1.0)

    return charge, temp, time

def simulate_activity(activity, duration):
    global cur_charge, cur_temp, cur_time, good_battery_health, overcharge_cases
    if activity not in ("charge", "use", "idle"):
        return

    if activity == "charge":
        is_fast_charging = can_fast_charge(cur_charge, cur_temp, good_battery_health)
        good_battery_health, bad_health_cap = check_overcharge(0.0, cur_charge, cur_time, overcharge_cases, good_battery_health)

        for i in range(duration):
            cur_charge, cur_temp, cur_time, good_battery_health, is_fast_charging, bad_health_cap = simulate_charge_minute(cur_charge, cur_temp, cur_time, good_battery_health, overcharge_cases, is_fast_charging, bad_health_cap)

    elif activity == "use":
        for i in range(duration):
            cur_charge, cur_temp, cur_time = simulate_use_minute(cur_charge, cur_temp, cur_time)

    elif activity == "idle":
        for i in range(duration):
            cur_charge, cur_temp, cur_time = simulate_idle_minute(cur_charge, cur_temp, cur_time)

if __name__ == '__main__':
    initialize()

    print(duration_fast_charge_possible()) # 10
    print(charge_time_needed(50)) # 30

    simulate_activity("charge",30)
    print(get_cur_charge()) # 100
    print(get_cur_temp()) # 30

    simulate_activity("use",50)
    print(get_cur_charge()) # 0
    print(get_cur_temp()) # 80

    simulate_activity("use",10)
    print(get_cur_charge()) # 0
    print(get_cur_temp()) # 70

    simulate_activity("charge",100)
    print(get_cur_charge()) # 100
    print(get_cur_temp()) # 95

    simulate_activity("idle",100)
    print(get_cur_charge()) # 50
    print(get_cur_temp()) # 0
    print(get_cur_battery_health()) # True
    print(duration_fast_charge_possible()) # 10

    simulate_activity("charge",80)
    print(get_cur_charge()) # 90
    print(get_cur_temp()) # 22.5
    print(get_cur_battery_health()) # False

    simulate_activity("use",40)
    print(get_cur_charge()) # 10
    print(get_cur_temp()) # 62.5

    simulate_activity("charge",80)
    print(get_cur_charge()) # 80
    print(get_cur_temp()) # 82.5

    initialize()
    # add your tests here
