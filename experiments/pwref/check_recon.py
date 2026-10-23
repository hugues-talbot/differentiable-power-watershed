"""Check my reading of the reference's geodesic reconstruction of the weights:
O[e] = max over seed-adjacent edges s of  min_{e' on a path s -> e in the line graph} G[e']
(reconstruction by dilation of the seed-adjacent weights under the weights), against its dump."""
import heapq, os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pwref_compare import write_pgm, random_small_cases, ref_edges

def recon_python(H, W, G, seed_pix):
    u, v = ref_edges(H, W); M = u.size
    inc = [[] for _ in range(H * W)]
    for e in range(M):
        inc[u[e]].append(e); inc[v[e]].append(e)
    O = np.zeros(M, np.int64); done = np.zeros(M, bool)
    heap = []
    for p in np.flatnonzero(seed_pix):
        for e in inc[p]:
            heapq.heappush(heap, (-int(G[e]), e))
    while heap:
        pr, e = heapq.heappop(heap); pr = -pr
        if done[e]:
            continue
        done[e] = True; O[e] = pr
        for p in (u[e], v[e]):
            for f in inc[p]:
                if not done[f]:
                    heapq.heappush(heap, (-min(pr, int(G[f])), f))
    return O

rng = np.random.default_rng(2)
os.makedirs("tmp_recon", exist_ok=True)
bad = 0
for name, img8, spec in random_small_cases(rng, 30):
    H, W = img8.shape
    if spec[0] == "two":
        seeds8 = np.full(img8.shape, 128, np.uint8); seeds8[spec[1] & (spec[2] > 0.5)] = 255; seeds8[spec[1] & (spec[2] < 0.5)] = 0; labels = "two"; seed_pix = spec[1].ravel()
    else:
        seeds8 = spec[1].astype(np.uint8); labels = "multi"; seed_pix = spec[1].ravel() > 0
    write_pgm("tmp_recon/i.pgm", img8); write_pgm("tmp_recon/s.pgm", seeds8)
    subprocess.run(["./pwref_wrap", "tmp_recon/i.pgm", "tmp_recon/s.pgm", "prog", "tmp_recon/o", labels, "stoch"], check=True, capture_output=True)
    normal = np.fromfile("tmp_recon/o.normal.u32", np.uint32).astype(np.int64); recon = np.fromfile("tmp_recon/o.recon.u32", np.uint32).astype(np.int64)
    mine = recon_python(H, W, normal, seed_pix)
    nd = int((mine != recon).sum()); bad += nd
    if nd:
        print(name, "differs on", nd, "edges", np.flatnonzero(mine != recon)[:5], mine[mine != recon][:5], recon[mine != recon][:5])
print("edges where my reconstruction differs from the reference's dump, 30 cases:", bad)
