def srtf_scheduler(processes):
    from copy import deepcopy
    import heapq

    time = 0
    completed = []
    processes = deepcopy(processes)
    ready_queue = []
    remaining = {p['pid']: p['burst_time'] for p in processes}
    arrival_map = {p['pid']: p['arrival_time'] for p in processes}
    last_pid = None

    timeline = []
    while remaining:
        for p in processes:
            if p['arrival_time'] == time:
                heapq.heappush(ready_queue, (p['burst_time'], p['pid'], p))

        if ready_queue:
            burst_time, pid, proc = heapq.heappop(ready_queue)
            if last_pid != pid:
                if timeline and timeline[-1]['end'] == time:
                    pass
                else:
                    timeline.append({'pid': pid, 'start': time, 'end': time+1})
            else:
                timeline[-1]['end'] += 1

            remaining[pid] -= 1
            if remaining[pid] > 0:
                heapq.heappush(ready_queue, (remaining[pid], pid, proc))
            else:
                del remaining[pid]
            last_pid = pid
        else:
            last_pid = None

        time += 1

    waiting_times = []
    for proc in processes:
        burst = proc['burst_time']
        start = next(t['start'] for t in timeline if t['pid'] == proc['pid'])
        wait = start - proc['arrival_time']
        waiting_times.append(wait)

    avg_waiting_time = sum(waiting_times) / len(waiting_times)
    return {'timeline': timeline, 'avg_waiting_time': avg_waiting_time}
