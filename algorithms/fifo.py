# algorithms/fifo.py

from typing import List, Dict

def fifo_scheduler(processes: List[Dict]) -> Dict:
    """
    Simula el algoritmo FIFO.
    """
    processes_sorted = sorted(processes, key=lambda p: p['arrival_time'])
    current_time = 0
    timeline = []
    waiting_times = []

    for process in processes_sorted:
        arrival = process['arrival_time']
        burst = process['burst_time']
        pid = process['pid']

        if current_time < arrival:
            current_time = arrival

        start = current_time
        end = current_time + burst
        waiting_time = start - arrival
        waiting_times.append(waiting_time)

        timeline.append({
            'pid': pid,
            'start': start,
            'end': end
        })

        current_time = end

    avg_waiting_time = sum(waiting_times) / len(waiting_times)

    return {
        'timeline': timeline,
        'avg_waiting_time': avg_waiting_time
    }
