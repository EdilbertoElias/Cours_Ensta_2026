from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

N = 1000000  # 1 milhão de elementos para sentir a pressão
VAL_MAX = 1.0

if rank == 0:
    data = np.random.random(N).astype(np.float32)
    buckets = [[] for _ in range(size)]
    for x in data:
        index = int(x // (VAL_MAX / size))
        if index >= size: index = size - 1
        buckets[index].append(x)
else:
    buckets = None

# --- SINCRONIZAÇÃO E INÍCIO DA MEDIÇÃO ---
comm.Barrier() 
start_time = MPI.Wtime()

# Distribuição dos baldes
local_bucket = comm.scatter(buckets, root=0)

# Ordenação local (O coração do paralelismo)
local_bucket.sort()

# Reunião dos resultados
all_sorted_buckets = comm.gather(local_bucket, root=0)

# --- FIM DA MEDIÇÃO ---
end_time = MPI.Wtime()
t_exec = end_time - start_time

if rank == 0:
    print(f"\n" + "="*40)
    print(f"ANÁLISE DE DESEMPENHO - ENSTA 2026")
    print(f"Processos (p): {size}")
    print(f"Elementos (N): {N}")
    print(f"Tempo de Execução: {t_exec:.6f} segundos")
    print("="*40)