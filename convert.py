#!/usr/bin/env python3
import argparse, os, sys, math
import numpy as np

try:
    import trimesh
except ImportError:
    print("ERROR: pip install trimesh numpy pygltflib", file=sys.stderr)
    sys.exit(1)

# Optional simplifier (quadric error); pip install pyfqmr
try:
    from pyfqmr import FQMR
    HAS_FQMR = True
except Exception:
    HAS_FQMR = False


def load_mesh(path: str) -> trimesh.Trimesh:
    m = trimesh.load(path, force='mesh')
    if isinstance(m, trimesh.Scene):
        m = trimesh.util.concatenate(tuple(
            g for g in m.dump().geometry.values() if isinstance(g, trimesh.Trimesh)
        ))
    if not isinstance(m, trimesh.Trimesh):
        raise ValueError("Could not load a triangle mesh from file.")
    # Ensure triangles
    if not m.is_watertight:
        m.remove_unreferenced_vertices()
    if m.vertices.shape[0] == 0 or m.faces.shape[0] == 0:
        raise ValueError("Empty mesh after load.")
    return m


def transform_mesh(mesh: trimesh.Trimesh, z_up_to_y_up: bool, scale: float):
    # Build transform matrix
    T = np.eye(4)

    # Scale (mm->m = 0.001, etc.)
    S = np.diag([scale, scale, scale, 1.0])
    T = S @ T

    # Z-up (CAD) to Y-up (three.js): rotate -90° about X
    if z_up_to_y_up:
        rx = -math.pi / 2.0
        R = np.array([
            [1, 0,          0,         0],
            [0, math.cos(rx), -math.sin(rx), 0],
            [0, math.sin(rx),  math.cos(rx), 0],
            [0, 0,          0,         1],
        ])
        T = R @ T

    mesh.apply_transform(T)


def simplify_mesh(mesh: trimesh.Trimesh, target_ratio: float) -> trimesh.Trimesh:
    # Guard
    target_ratio = max(0.01, min(1.0, target_ratio))
    target_count = int(mesh.faces.shape[0] * target_ratio)

    if not HAS_FQMR:
        print("NOTE: pyfqmr not installed; skipping simplification.", file=sys.stderr)
        return mesh

    print(f"Simplifying faces: {mesh.faces.shape[0]} -> ~{target_count} ...", file=sys.stderr)
    fqmr = FQMR()
    fqmr.setMesh(mesh.vertices.astype(np.float64), mesh.faces.astype(np.int32))
    # Quality settings — tweak if needed
    fqmr.simplify(target_count, aggressiveness=7, preserveBorder=True, verbose=False)
    v, f = fqmr.getMesh()
    if v.shape[0] and f.shape[0]:
        out = trimesh.Trimesh(vertices=v, faces=f, process=True)
        out.remove_unreferenced_vertices()
        return out
    print("Simplification failed; using original mesh.", file=sys.stderr)
    return mesh


def export_glb(mesh: trimesh.Trimesh, out_path: str):
    # Center to make it nice for viewers
    mesh.remove_unreferenced_vertices()
    mesh.vertices -= mesh.bounding_box.centroid
    # Export GLB
    glb_bytes = trimesh.exchange.gltf.export_glb(mesh, include_normals=True)
    with open(out_path, "wb") as f:
        f.write(glb_bytes)


def pretty_size(n):
    for unit in ['B','KB','MB','GB']:
        if n < 1024.0:
            return f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}TB"


def main():
    ap = argparse.ArgumentParser(description="Convert STL -> GLB (and optionally simplify).")
    ap.add_argument("input", help="input .stl")
    ap.add_argument("output", nargs="?", help="output .glb (default: same name)")
    ap.add_argument("--mm", action="store_true", help="scale mm -> meters (x0.001)")
    ap.add_argument("--scale", type=float, default=1.0, help="uniform scale factor (applied after --mm)")
    ap.add_argument("--z-up", action="store_true", help="rotate -90° about X (Z-up to Y-up)")
    ap.add_argument("--simplify", type=float, default=1.0,
                    help="target face ratio (0.05=5%% of faces). Requires pyfqmr. Default: 1.0 (no simplify)")
    args = ap.parse_args()

    src = args.input
    dst = args.output or (os.path.splitext(src)[0] + ".glb")

    if not os.path.exists(src):
        ap.error(f"input not found: {src}")

    before = os.path.getsize(src)
    print(f"Input: {src} ({pretty_size(before)})", file=sys.stderr)

    mesh = load_mesh(src)

    # Scaling chain
    scale = args.scale * (0.001 if args.mm else 1.0)
    transform_mesh(mesh, z_up_to_y_up=args.z_up, scale=scale)

    # Optional simplify
    if args.simplify < 1.0:
        mesh = simplify_mesh(mesh, target_ratio=args.simplify)

    export_glb(mesh, dst)

    after = os.path.getsize(dst)
    print(f"Output: {dst} ({pretty_size(after)})", file=sys.stderr)
    if after < before:
        print(f"Saved: {pretty_size(before - after)}", file=sys.stderr)
    else:
        print("Note: GLB larger than STL (try --simplify and/or post-processing).", file=sys.stderr)


if __name__ == "__main__":
    main()
