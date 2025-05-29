from collections import deque
from copy import deepcopy

def round_robin_scheduler(processes, quantum):


    processes = deepcopy(processes)
    time = 0
    queue = deque()
    timeline = []
    remaining_bt = {p['pid']: p['burst_time'] for p in processes}
    arrival_times = {p['pid']: p['arrival_time'] for p in processes}
    finish_times = {}
    arrived = set()

    while len(finish_times) < len(processes):
        # Insertar procesos que llegan en este ciclo
        for p in processes:
            if p['arrival_time'] <= time and p['pid'] not in arrived:
                queue.append(p['pid'])
                arrived.add(p['pid'])

        if not queue:
            time += 1
            continue

        pid = queue.popleft()
        exec_time = min(quantum, remaining_bt[pid])
        timeline.append({
            'pid': pid,
            'start': time,
            'end': time + exec_time
        })

        time += exec_time
        remaining_bt[pid] -= exec_time

        # Revisar si otros procesos llegan durante este tiempo
        for p in processes:
            if p['arrival_time'] > time - exec_time and p['arrival_time'] <= time and p['pid'] not in arrived:
                queue.append(p['pid'])
                arrived.add(p['pid'])

        if remaining_bt[pid] > 0:
            queue.append(pid)
        else:
            finish_times[pid] = time

    # Calcular tiempo de espera: Finish - Arrival - Burst
    waiting_times = []
    for p in processes:
        pid = p['pid']
        wt = finish_times[pid] - p['arrival_time'] - p['burst_time']
        waiting_times.append(wt)

    avg_waiting_time = sum(waiting_times) / len(waiting_times)
    return {'timeline': timeline, 'avg_waiting_time': avg_waiting_time}
