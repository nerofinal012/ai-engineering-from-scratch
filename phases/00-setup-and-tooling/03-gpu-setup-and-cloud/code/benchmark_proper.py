import torch
import time

size = 4000
device = torch.device("cuda")

# Warm up
a = torch.randn(size, size, device=device)
b = torch.randn(size, size, device=device)
for _ in range(3):
    _ = a @ b
torch.cuda.synchronize()

# CPU timing
a_cpu = torch.randn(size, size)
b_cpu = torch.randn(size, size)
start = time.time()
c_cpu = a_cpu @ b_cpu
cpu_time = time.time() - start
print(f"CPU: {cpu_time:.3f}s")

# GPU timing (with synchronize)
a_gpu = a_cpu.to("cuda")
b_gpu = b_cpu.to("cuda")
torch.cuda.synchronize()
start = time.time()
c_gpu = a_gpu @ b_gpu
torch.cuda.synchronize()  # critical
gpu_time = time.time() - start
print(f"GPU: {gpu_time:.3f}s")
print(f"Speedup: {cpu_time / gpu_time:.1f}x")
