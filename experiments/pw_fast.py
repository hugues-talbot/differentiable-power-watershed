#!/usr/bin/env python3
"""
Numba back end for the exact Power Watershed limit (q = 2, p -> inf).

Same plateau semantics as pw_conditioning.power_watershed and pw_layer.power_watershed_multi,
and bit-for-bit the same results: the compiled part is only the plateau bookkeeping (sorted-edge
pass, union-find over merged nodes, components of each cost level in the merged graph, merges of
the unambiguous components), which is where the NumPy version spends its time (whole-array passes
per cost level on 8-bit costs, a Python edge loop on continuous costs).  The Random Walker solves
on the ambiguous plateaus use the very same code paths as the NumPy version (dense solve per
component for levels of at most `small` edges, one block sparse LU for larger levels, the same
unknown ordering, the same accumulation order of the right-hand sides, the same representatives
of merged components), so that even the ties at exactly 0.5 come out identical.

Protocol: the kernel `_levels` processes cost levels until it meets one with an ambiguous
component (>= 2 distinct known values and at least one unknown node); it returns that level's
ambiguous components (pairs of merged-node roots in level order, unknown roots ascending), the
Python side solves and writes the values, and the kernel resumes at the next level.

Dependencies: numpy, scipy, numba (import fails without numba; the callers fall back to NumPy).
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from numba import njit


@njit(cache=True)
def _find(parent, a):
    r = a
    while parent[r] != r:
        r = parent[r]
    while parent[a] != r:
        nxt = parent[a]
        parent[a] = r
        a = nxt
    return r


@njit(cache=True)
def _lfind(lp, a):
    r = a
    while lp[r] != r:
        r = lp[r]
    while lp[a] != r:                    # path compression (large flat plateaus otherwise chain up)
        nxt = lp[a]
        lp[a] = r
        a = nxt
    return r


@njit(cache=True)
def _levels(order, starts, ends, lev0, u, v, parent, key, small, lp, cid, pu, pv, touched):
    """Process levels lev0, lev0+1, ... ; stop after the first level with ambiguous components.

    key: float64 per node, NaN = unknown (a value for the scalar code, a vector id for the
    multi-label code).  lp, cid: int64 scratch of size n filled with -1.  pu, pv: int64 scratch
    of the size of the largest level.  touched: int64 scratch of size n.
    Returns (next level, pairs (pu, pv, component) of the ambiguous components in level order,
    unknown roots of those components ascending with their component index, number of
    ambiguous components)."""
    nlev = starts.size
    empty = np.empty(0, np.int64)
    lev = lev0
    while lev < nlev:
        s = starts[lev]
        e = ends[lev]
        lev += 1
        if e - s == 1:
            # a single edge: the scalar rules of the NumPy fast path (representatives included)
            eidx = order[s]
            ru = _find(parent, u[eidx])
            rv = _find(parent, v[eidx])
            if ru == rv:
                continue
            ku = not np.isnan(key[ru])
            kv = not np.isnan(key[rv])
            if ku and kv:
                if key[ru] != key[rv]:
                    continue
                parent[ru] = rv
            elif ku:
                parent[rv] = ru
            else:
                parent[ru] = rv
            continue
        # pairs of distinct roots, in level order
        npairs = 0
        for idx in range(s, e):
            eidx = order[idx]
            ru = _find(parent, u[eidx])
            rv = _find(parent, v[eidx])
            if ru == rv:
                continue
            pu[npairs] = ru
            pv[npairs] = rv
            npairs += 1
        if npairs == 0:
            continue
        # components of the level in the merged graph (local union-find over the roots)
        nt = 0
        for p in range(npairs):
            a = pu[p]
            b = pv[p]
            if lp[a] == -1:
                lp[a] = a
                touched[nt] = a
                nt += 1
            if lp[b] == -1:
                lp[b] = b
                touched[nt] = b
                nt += 1
            ra = _lfind(lp, a)
            rb = _lfind(lp, b)
            if ra != rb:
                lp[ra] = rb
        # per component: number of distinct known keys (0, 1, >= 2), unknown members, representative
        ncomp = 0
        for t in range(nt):
            r = touched[t]
            c = _lfind(lp, r)
            lp[r] = c                        # full compression: lp[r] is now the component root
            if cid[c] == -1:
                cid[c] = ncomp
                ncomp += 1
        cmin = np.full(ncomp, np.inf)
        cmax = np.full(ncomp, -np.inf)
        cunk = np.zeros(ncomp, np.int64)
        crep = np.full(ncomp, -1, np.int64)
        for t in range(nt):
            r = touched[t]
            c = cid[lp[r]]
            if np.isnan(key[r]):
                cunk[c] += 1
            else:
                if key[r] < cmin[c]:
                    cmin[c] = key[r]
                if key[r] > cmax[c]:
                    cmax[c] = key[r]
            if crep[c] == -1:
                crep[c] = r
            elif e - s <= small:
                if r < crep[c]:
                    crep[c] = r         # NumPy small path: members[0] of the sorted members
            else:
                if r > crep[c]:
                    crep[c] = r         # NumPy general path: last assignment wins -> largest root
        # ambiguous components get an index; the others are merged
        namb = 0
        aidx = np.full(ncomp, -1, np.int64)
        nunk = 0
        for c in range(ncomp):
            if cmax[c] > cmin[c]:
                if cunk[c] > 0:
                    aidx[c] = namb
                    namb += 1
                    nunk += cunk[c]
        for t in range(nt):
            r = touched[t]
            c = cid[lp[r]]
            if cmax[c] > cmin[c]:
                continue
            rep = crep[c]
            parent[r] = rep
            if cmin[c] < np.inf:
                key[rep] = cmin[c]
        if namb == 0:
            for t in range(nt):
                r = touched[t]
                cid[lp[r]] = -1
                lp[r] = -1
            continue
        # output: pairs of the ambiguous components in level order, unknown roots ascending
        nout = 0
        for p in range(npairs):
            if aidx[cid[lp[pu[p]]]] >= 0:
                nout += 1
        opu = np.empty(nout, np.int64)
        opv = np.empty(nout, np.int64)
        opc = np.empty(nout, np.int64)
        k = 0
        for p in range(npairs):
            a = aidx[cid[lp[pu[p]]]]
            if a >= 0:
                opu[k] = pu[p]
                opv[k] = pv[p]
                opc[k] = a
                k += 1
        unk = np.empty(nunk, np.int64)
        k = 0
        for t in range(nt):
            r = touched[t]
            a = aidx[cid[lp[r]]]
            if a >= 0 and np.isnan(key[r]):
                unk[k] = r
                k += 1
        unk = np.sort(unk)
        unkc = np.empty(nunk, np.int64)
        for k in range(nunk):
            unkc[k] = aidx[cid[lp[unk[k]]]]
        for t in range(nt):
            r = touched[t]
            cid[lp[r]] = -1
            lp[r] = -1
        return lev, opu, opv, opc, unk, unkc, namb
    return lev, empty, empty, empty, empty, empty, 0


@njit(cache=True)
def _roots(parent):
    n = parent.size
    out = np.empty(n, np.int64)
    for i in range(n):
        out[i] = _find(parent, i)
    return out


def _prepare(n, cint, small):
    order = np.argsort(cint, kind="stable")
    cs = cint[order]
    bounds = np.flatnonzero(np.diff(cs)) + 1
    starts = np.concatenate([[0], bounds]).astype(np.int64)
    ends = np.concatenate([bounds, [cs.size]]).astype(np.int64)
    sizes = ends - starts
    scratch = dict(lp=np.full(n, -1, np.int64), cid=np.full(n, -1, np.int64),
                   pu=np.empty(int(sizes.max()), np.int64), pv=np.empty(int(sizes.max()), np.int64),
                   touched=np.empty(n, np.int64))
    stats = dict(plateaus=int(starts.size), solved_plateaus=0, solved_nodes=0, max_solve=0)
    return order, starts, ends, sizes, scratch, stats


def _dense_system(opu, opv, opc, unk, unkc, c, rhs):
    """A, b of one ambiguous component as the NumPy small path builds them (pairs in level order,
    unknowns ascending); rhs(known root) -> contribution to b (scalar or vector)."""
    unknown = unk[unkc == c]
    pos = {int(r): k for k, r in enumerate(unknown)}
    k = len(unknown)
    sel = opc == c
    A = np.zeros((k, k))
    b = None
    for a, bb in zip(opu[sel], opv[sel]):
        pa, pb = pos.get(int(a)), pos.get(int(bb))
        if pa is not None:
            A[pa, pa] += 1
        if pb is not None:
            A[pb, pb] += 1
        if pa is not None and pb is not None:
            A[pa, pb] -= 1; A[pb, pa] -= 1
        elif pa is not None:
            if b is None:
                b = np.zeros((k,) + np.shape(rhs(int(bb))))
            b[pa] += rhs(int(bb))
        elif pb is not None:
            if b is None:
                b = np.zeros((k,) + np.shape(rhs(int(a))))
            b[pb] += rhs(int(a))
    return A, b, unknown


def _sparse_system(n, au, av, unknown, rhs_of, width):
    """A, b of all ambiguous components of a level at once, as the NumPy general path builds
    them (one block system, unknowns ascending, right-hand side accumulated in two passes)."""
    lpos = -np.ones(n, dtype=np.int64); lpos[unknown] = np.arange(unknown.size)
    w1 = np.ones(au.size)
    fu, fv = lpos[au] >= 0, lpos[av] >= 0
    inner = fu & fv
    k = unknown.size
    # degree of every unknown within the level (integer counts, as the NumPy bincount over n)
    deg = np.bincount(np.concatenate([lpos[au[fu]], lpos[av[fv]]]), minlength=k).astype(np.float64)
    rows = np.concatenate([lpos[au[inner]], lpos[av[inner]], np.arange(k)])
    cols = np.concatenate([lpos[av[inner]], lpos[au[inner]], np.arange(k)])
    vals = np.concatenate([-w1[inner], -w1[inner], deg])
    A = sp.csc_matrix((vals, (rows, cols)), shape=(k, k)); A.sum_duplicates()
    b = np.zeros(k) if width is None else np.zeros((k, width))
    m = fu & ~fv; np.add.at(b, lpos[au[m]], rhs_of(av[m]))
    m = ~fu & fv; np.add.at(b, lpos[av[m]], rhs_of(au[m]))
    return A, b


class _Table:
    """Known K-vectors of the multi-label code (one-hot seeds, then one row per solved node),
    kept in a growing array; `T` is the view of the rows filled so far."""

    def __init__(self, K):
        self.buf = np.eye(K); self.n = K

    @property
    def T(self):
        return self.buf[:self.n]

    def extend(self, rows):
        m = rows.shape[0]
        if self.n + m > self.buf.shape[0]:
            new = np.empty((max(2 * self.buf.shape[0], self.n + m), self.buf.shape[1])); new[:self.n] = self.buf[:self.n]; self.buf = new
        self.buf[self.n:self.n + m] = rows
        ids = np.arange(self.n, self.n + m, dtype=np.float64); self.n += m
        return ids


def power_watershed_fast(n, u, v, cint, seed_mask, seed_val, small=64):
    """Drop-in for pw_conditioning.power_watershed (same arguments, same results, same stats)."""
    u = np.ascontiguousarray(u, dtype=np.int64); v = np.ascontiguousarray(v, dtype=np.int64)
    parent = np.arange(n, dtype=np.int64)
    val = np.full(n, np.nan)
    val[seed_mask] = seed_val[seed_mask]
    order, starts, ends, sizes, sc, stats = _prepare(n, np.asarray(cint), small)
    lev = 0
    while lev < starts.size:
        lev, opu, opv, opc, unk, unkc, namb = _levels(order, starts, ends, lev, u, v, parent, val, small,
                                                      sc["lp"], sc["cid"], sc["pu"], sc["pv"], sc["touched"])
        if namb == 0:
            break
        if sizes[lev - 1] <= small:
            for c in range(namb):
                A, b, unknown = _dense_system(opu, opv, opc, unk, unkc, c, lambda r: val[r])
                val[unknown] = np.linalg.solve(A, b)
                stats["solved_plateaus"] += 1
                stats["solved_nodes"] += int(unknown.size)
                stats["max_solve"] = max(stats["max_solve"], int(unknown.size))
        else:
            A, b = _sparse_system(n, opu, opv, unk, lambda r: val[r], None)
            val[unk] = spla.splu(A).solve(b)
            stats["solved_plateaus"] += 1
            stats["solved_nodes"] += int(unk.size)
            stats["max_solve"] = max(stats["max_solve"], int(unk.size))
    x = val[_roots(parent)]
    stats["unassigned"] = int(np.isnan(x).sum())
    return x, stats


def power_watershed_multi_fast(n, u, v, cint, seed_mask, seed_lab, K, small=64, want_probs=False):
    """Drop-in for pw_layer.power_watershed_multi (same arguments, same results, same stats)."""
    u = np.ascontiguousarray(u, dtype=np.int64); v = np.ascontiguousarray(v, dtype=np.int64)
    parent = np.arange(n, dtype=np.int64)
    key = np.full(n, np.nan)                                      # vector id of a root, NaN unknown
    key[seed_mask] = seed_lab[seed_mask]
    table = _Table(K)
    order, starts, ends, sizes, sc, stats = _prepare(n, np.asarray(cint), small)
    lev = 0
    while lev < starts.size:
        lev, opu, opv, opc, unk, unkc, namb = _levels(order, starts, ends, lev, u, v, parent, key, small,
                                                      sc["lp"], sc["cid"], sc["pu"], sc["pv"], sc["touched"])
        if namb == 0:
            break
        if sizes[lev - 1] <= small:
            for c in range(namb):
                A, b, unknown = _dense_system(opu, opv, opc, unk, unkc, c, lambda r: table.T[int(key[r])])
                sol = np.linalg.solve(A, b)
                key[unknown] = table.extend(sol)
                stats["solved_plateaus"] += 1
                stats["solved_nodes"] += int(unknown.size)
                stats["max_solve"] = max(stats["max_solve"], int(unknown.size))
        else:
            T = table.T
            A, b = _sparse_system(n, opu, opv, unk, lambda rr: T[key[rr].astype(np.int64)], K)
            sol = spla.splu(A).solve(b)
            key[unk] = table.extend(sol)
            stats["solved_plateaus"] += 1
            stats["solved_nodes"] += int(unk.size)
            stats["max_solve"] = max(stats["max_solve"], int(unk.size))
    T = table.T
    ids = key[_roots(parent)]
    unknown = np.isnan(ids)
    ids = np.where(unknown, 0, ids).astype(np.int64)
    stats["unassigned"] = int(unknown.sum())
    labels = np.where(~unknown, T[ids].argmax(1), -1)
    if want_probs:
        probs = np.where(~unknown[None], T[ids].T, np.nan)
        return (labels, probs), stats
    return labels, stats
