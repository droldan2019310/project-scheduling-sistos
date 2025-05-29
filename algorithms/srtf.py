from copy import deepcopy
import heapq

def srtf_scheduler(processes):

    time = 0
    processes = deepcopy(processes)

    # Estado de ejecución
    remaining_bt = {p['pid']: p['burst_time'] for p in processes}
    arrival_times = {p['pid']: p['arrival_time'] for p in processes}
    finish_times = {}
    timeline = []

    ready_queue = []
    current_pid = None
    last_time = 0

    while remaining_bt:
        # Cargar procesos que llegan en este ciclo
        for p in processes:
            if p['arrival_time'] == time:
                heapq.heappush(ready_queue, (p['burst_time'], p['pid'], p))

        if ready_queue:
            # Seleccionamos el proceso con menor burst restante
            burst, pid, proc = heapq.heappop(ready_queue)

            # Si el proceso cambia, registramos el anterior
            if current_pid != pid:
                if current_pid is not None:
                    timeline[-1]["end"] = time
                timeline.append({"pid": pid, "start": time, "end": time + 1})
                current_pid = pid
            else:
                timeline[-1]["end"] += 1

            remaining_bt[pid] -= 1
            time += 1

            if remaining_bt[pid] > 0:
                heapq.heappush(ready_queue, (remaining_bt[pid], pid, proc))
            else:
                finish_times[pid] = time
                del remaining_bt[pid]
                current_pid = None
        else:
            time += 1

    # Calcular tiempo de espera por fórmula: finish - arrival - burst
    waiting_times = []
    for p in processes:
        pid = p['pid']
        wt = finish_times[pid] - p['arrival_time'] - p['burst_time']
        waiting_times.append(wt)

    avg_waiting_time = sum(waiting_times) / len(waiting_times)
    return {
        "timeline": timeline,
        "avg_waiting_time": avg_waiting_time
    }
