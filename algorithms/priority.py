def priority_scheduler(processes):
    processes = sorted(processes, key=lambda p: (p['arrival_time'], p['priority']))
    completed = []
    current_time = 0
    waiting_times = []
    remaining = processes.copy()

    while remaining:
        available = [p for p in remaining if p['arrival_time'] <= current_time]
        if not available:
            current_time = remaining[0]['arrival_time']
            continue
        next_proc = min(available, key=lambda p: p['priority'])
        remaining.remove(next_proc)

        start = current_time
        end = start + next_proc['burst_time']
        waiting_time = start - next_proc['arrival_time']
        waiting_times.append(waiting_time)

        completed.append({
            'pid': next_proc['pid'],
            'start': start,
            'end': end
        })

        current_time = end

    avg_waiting_time = sum(waiting_times) / len(waiting_times)
    return {'timeline': completed, 'avg_waiting_time': avg_waiting_time}
