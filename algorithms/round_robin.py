def round_robin_scheduler(processes, quantum):
    from collections import deque
    from copy import deepcopy

    processes = sorted(processes, key=lambda p: p['arrival_time'])
    queue = deque()
    remaining = {p['pid']: p['burst_time'] for p in processes}
    arrival_times = {p['pid']: p['arrival_time'] for p in processes}
    process_map = {p['pid']: p for p in processes}

    time = 0
    timeline = []
    waiting_times = {}
    last_executed = {}

    i = 0
    while remaining:
        while i < len(processes) and processes[i]['arrival_time'] <= time:
            queue.append(processes[i]['pid'])
            i += 1

        if not queue:
            time += 1
            continue

        pid = queue.popleft()
        bt = remaining[pid]
        exec_time = min(quantum, bt)

        timeline.append({'pid': pid, 'start': time, 'end': time + exec_time})
        time += exec_time
        remaining[pid] -= exec_time

        while i < len(processes) and processes[i]['arrival_time'] <= time:
            queue.append(processes[i]['pid'])
            i += 1

        if remaining[pid] > 0:
            queue.append(pid)
        else:
            waiting_times[pid] = time - arrival_times[pid] - process_map[pid]['burst_time']

    avg_waiting_time = sum(waiting_times.values()) / len(waiting_times)
    return {'timeline': timeline, 'avg_waiting_time': avg_waiting_time}
